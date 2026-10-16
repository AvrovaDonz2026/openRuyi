#!/usr/bin/python3
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0
"""Inventory namespaced RPM capabilities using RPM file metadata.

This is not a replacement for the RPM dependency solver. It checks simple,
unversioned capability names and reports namespaced version constraints or
rich dependencies as unverified with a nonzero status. Pass all packages
which may provide a private ``sglang(...)`` or ``sglang-extras(...)``
capability as positional RPMs or with ``--provider-rpm``.
"""

from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path
import re
import subprocess
import sys
from typing import NamedTuple


_IGNORED_CAPABILITY_PREFIXES = ("rpmlib(",)
_RICH_OPERATORS = (" with ", " without ", " if ", " unless ", " or ", " and ")
_VERSION_OPERATOR = re.compile(r"\s+(?:<=>|<=|>=|=|<|>|~{1,2})\s+")


class RpmMetadata(NamedTuple):
    path: Path
    provides: tuple[str, ...]
    requires: tuple[str, ...]


def _capability_name(expression: str) -> str:
    """Return the name portion of an RPM dependency expression."""
    return expression.strip().split(None, 1)[0]


def _contains_namespace(expression: str, namespaces: tuple[str, ...]) -> bool:
    """Return whether an expression contains a namespaced capability.

    Rich dependencies commonly start with ``(``, so looking only at the first
    token misses expressions such as ``(sglang(foo) with sglang(bar))``.
    """
    return any(f"{namespace}(" in expression for namespace in namespaces)


def _is_rich_dependency(expression: str) -> bool:
    stripped = expression.strip()
    return stripped.startswith("(") or any(operator in stripped for operator in _RICH_OPERATORS)


def _is_versioned_dependency(expression: str) -> bool:
    return bool(_VERSION_OPERATOR.search(expression))


def _is_ignored(expression: str, ignored_prefixes: tuple[str, ...]) -> bool:
    name = _capability_name(expression)
    return any(name.startswith(prefix) for prefix in ignored_prefixes)


def _query(rpm: str, package: Path, field: str, dbpath: str | None = None) -> tuple[str, ...]:
    command = [rpm]
    if dbpath:
        command.extend(("--dbpath", dbpath))
    command.extend(("-qp", f"--{field}", str(package)))
    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"rpm executable not found: {rpm}") from exc
    if result.returncode:
        detail = result.stderr.strip() or f"exit status {result.returncode}"
        raise RuntimeError(f"rpm -qp --{field} {package}: {detail}")
    return tuple(line.strip() for line in result.stdout.splitlines() if line.strip())


def read_metadata(rpm: str, package: Path, dbpath: str | None = None) -> RpmMetadata:
    if not package.is_file():
        raise FileNotFoundError(package)
    return RpmMetadata(
        path=package,
        provides=_query(rpm, package, "provides", dbpath),
        requires=_query(rpm, package, "requires", dbpath),
    )


def unresolved_requirements(
    packages: tuple[RpmMetadata, ...],
    *,
    provider_packages: tuple[RpmMetadata, ...] = (),
    only_namespaces: tuple[str, ...] = (),
    allow_patterns: tuple[str, ...] = (),
    ignored_prefixes: tuple[str, ...] = _IGNORED_CAPABILITY_PREFIXES,
) -> tuple[tuple[Path, str], ...]:
    """Return requirements whose capability name has no package provider.

    If ``only_namespaces`` is non-empty, requirements outside those RPM
    namespace wrappers are omitted.  ``allow_patterns`` uses shell-style
    matching against the complete requirement expression and is useful for
    documenting capabilities deliberately supplied by the base distribution.
    """
    provides = {
        _capability_name(capability)
        for package in (*packages, *provider_packages)
        for capability in package.provides
    }
    unresolved: list[tuple[Path, str]] = []
    for package in packages:
        for requirement in package.requires:
            name = _capability_name(requirement)
            if _is_ignored(requirement, ignored_prefixes):
                continue
            if only_namespaces and not _contains_namespace(requirement, only_namespaces):
                continue
            if _is_rich_dependency(requirement) or _is_versioned_dependency(requirement):
                continue
            if any(fnmatch.fnmatchcase(requirement, pattern) for pattern in allow_patterns):
                continue
            if name not in provides:
                unresolved.append((package.path, requirement))
    return tuple(unresolved)


def unverified_requirements(
    packages: tuple[RpmMetadata, ...],
    *,
    only_namespaces: tuple[str, ...] = (),
) -> tuple[tuple[Path, str], ...]:
    """Return namespaced requirements this inventory checker cannot evaluate.

    RPM's version comparison and rich-dependency boolean evaluation belong to
    the RPM dependency solver.  Without a transaction against a target RPM
    database, these requirements are deliberately reported as unverified
    instead of being treated as resolved by capability name alone.
    """
    unverified: list[tuple[Path, str]] = []
    for package in packages:
        for requirement in package.requires:
            if _is_ignored(requirement, _IGNORED_CAPABILITY_PREFIXES):
                continue
            if only_namespaces and not _contains_namespace(requirement, only_namespaces):
                continue
            if _is_rich_dependency(requirement) or _is_versioned_dependency(requirement):
                unverified.append((package.path, requirement))
    return tuple(unverified)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rpm", nargs="+", type=Path, help="RPMs to inspect")
    parser.add_argument(
        "--provider-rpm",
        action="append",
        default=[],
        type=Path,
        help="additional RPM supplying capabilities (repeatable)",
    )
    parser.add_argument(
        "--rpm-command",
        default="rpm",
        help="rpm executable used for -qp queries (default: rpm)",
    )
    parser.add_argument(
        "--dbpath",
        help="temporary RPM database path passed to rpm (useful on macOS)",
    )
    parser.add_argument(
        "--namespace",
        dest="namespaces",
        action="append",
        default=[],
        help="limit checks to a capability namespace (repeatable)",
    )
    parser.add_argument(
        "--allow",
        dest="allow_patterns",
        action="append",
        default=[],
        metavar="PATTERN",
        help="allow an unresolved requirement matching shell PATTERN (repeatable)",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="allow an inventory that matched no requirements",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    target_paths = tuple(dict.fromkeys(args.rpm))
    provider_paths = tuple(path for path in args.provider_rpm if path not in target_paths)
    try:
        metadata = tuple(
            read_metadata(args.rpm_command, path, args.dbpath) for path in target_paths
        )
        provider_metadata = tuple(
            read_metadata(args.rpm_command, path, args.dbpath) for path in provider_paths
        )
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"check_sglang_rpm_closure: {exc}", file=sys.stderr)
        return 2

    unresolved = unresolved_requirements(
        metadata,
        provider_packages=provider_metadata,
        only_namespaces=tuple(args.namespaces),
        allow_patterns=tuple(args.allow_patterns),
    )
    unverified = unverified_requirements(
        metadata,
        only_namespaces=tuple(args.namespaces),
    )
    checked = sum(
        1
        for package in metadata
        for requirement in package.requires
        if not args.namespaces
        or _contains_namespace(requirement, tuple(args.namespaces))
    )
    print(f"capability inventory: inspected {checked} namespaced requirements across {len(metadata)} RPMs")
    if args.namespaces and checked == 0 and not args.allow_empty:
        print(
            "no requirements matched the selected namespace; "
            "refusing to claim a non-empty inventory (use --allow-empty for an explicit probe)",
            file=sys.stderr,
        )
        return 3
    if unresolved:
        for package, requirement in unresolved:
            print(f"UNRESOLVED {package}: {requirement}")
        return 1
    if unverified:
        for package, requirement in unverified:
            print(f"UNVERIFIED {package}: {requirement}")
        return 2
    print("capability inventory: no unresolved simple requirements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

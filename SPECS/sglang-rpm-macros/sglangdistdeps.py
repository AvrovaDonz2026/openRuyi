#!/usr/bin/python3
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0
"""Namespace selected Python distribution dependencies for SGLang trees.

The system generator remains authoritative for metadata parsing, markers and
version conversion.  Its namespace is then applied only to private
distributions, leaving dependencies supplied by the base distribution global.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys


CORE = frozenset({
    "torch", "torchaudio", "torchvision", "triton",
    "xgrammar", "llguidance", "mistral-common", "sglang-kernel",
    "sglang-kernel-cpu", "sglang",
    "sglang-cpu",
    "grpcio", "grpcio-tools", "grpcio-health-checking", "grpcio-reflection",
    "grpcio-status", "torchcodec",
    "apache-tvm-ffi", "smg-grpc-proto", "smg-grpc-servicer",
    "transformers", "tokenizers", "huggingface-hub", "click",
})
EXTRAS = frozenset({
    "fsspec", "datasets", "pandas", "pillow", "sgl-eval", "moviepy",
})

_DIST = re.compile(
    r"(?:(?P<wrapped>[A-Za-z0-9_.+-]+)\((?P<wcap>"
    r"python(?:[0-9]+(?:\.[0-9]+)?)?dist\((?P<wname>[^()]+)\))\)"
    r"|(?P<rawcap>python(?:[0-9]+(?:\.[0-9]+)?)?dist\((?P<rawname>[^()]+)\)))"
)
_ABI = re.compile(
    r"(?P<wrapped>[A-Za-z0-9_.+-]+)\(python\(abi\)(?P<suffix>[^)]*)\)"
)


def _normalize_dist_name(name: str) -> str:
    """Return a PEP 503 name for profile matching, preserving extras output."""
    base = name.split("[", 1)[0]
    return re.sub(r"[-_.]+", "-", base).lower()


def _private_namespace(
    name: str, profile: str, private_dists: frozenset[str] = frozenset()
) -> str | None:
    normalized = _normalize_dist_name(name)
    if normalized in CORE or normalized in private_dists:
        # Extras packages use the same private core stack.
        return "sglang"
    if profile == "extras" and normalized in EXTRAS:
        return "sglang-extras"
    return None


def _torch_flavor(package_name: str) -> str:
    if package_name.endswith("-rocm"):
        return "rocm"
    if package_name in {"python-sglang-cuda", "python-sglang-kernel"}:
        return "cuda"
    return "cpu"


def _rewrite_capabilities(
    text: str,
    profile: str,
    provides: bool = False,
    default_namespace: str | None = None,
    private_dists: frozenset[str] = frozenset(),
    torch_flavor: str | None = None,
) -> str:
    """Canonicalize private Python capabilities and unwrap system ones."""

    def replace_dist(match: re.Match[str]) -> str:
        capability = match.group("wcap") or match.group("rawcap")
        name = match.group("wname") or match.group("rawname")
        if _normalize_dist_name(name) == "torch" and torch_flavor:
            capability = re.sub(
                r"python(?:[0-9]+(?:\.[0-9]+)?)?dist\(torch\)",
                lambda match: match.group(0).replace(
                    "(torch)", f"(torch-{torch_flavor})"
                ),
                capability,
            )
        private_namespace = _private_namespace(name, profile, private_dists)
        if private_namespace is None:
            if provides:
                # All metadata selected by the private-path attribute belongs
                # to a private tree. Keep unknown provider names in the
                # namespace selected by the file attribute, even if a
                # generator accidentally supplied another namespace.
                provider_namespace = default_namespace
                if provider_namespace:
                    return f"{provider_namespace}({capability})"
            return capability
        return f"{private_namespace}({capability})"

    def replace_abi(match: re.Match[str]) -> str:
        # python(abi) is supplied by the interpreter/base distribution.
        return "python(abi)" + match.group("suffix")

    return _ABI.sub(replace_abi, _DIST.sub(replace_dist, text))


def _namespace_requirements(
    text: str, profile: str, torch_flavor: str | None = None
) -> str:
    """Namespace only private requirements in a generated requirements file."""
    return _rewrite_capabilities(text, profile, torch_flavor=torch_flavor)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("core", "extras"), required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--package-name", default="")
    parser.add_argument("--generator", default="/usr/lib/rpm/pythondistdeps.py")
    parser.add_argument(
        "--private-dists",
        default="",
        help="comma-separated extra private distribution names for build requirements",
    )
    parser.add_argument("--rewrite-requires", type=argparse.FileType("r+"))
    args, passthrough = parser.parse_known_args()
    private_dists = frozenset(
        _normalize_dist_name(name)
        for name in args.private_dists.split(",")
        if name.strip()
    )
    torch_flavor = _torch_flavor(args.package_name) if args.package_name else None
    if args.rewrite_requires:
        path = args.rewrite_requires
        content = path.read()
        path.seek(0)
        path.write(_rewrite_capabilities(
            content,
            args.profile,
            private_dists=private_dists,
            torch_flavor=torch_flavor,
        ))
        path.truncate()
        return 0
    if not any(flag in passthrough for flag in (
        "--provides", "-P", "--requires", "-R", "--recommends", "-r",
        "--conflicts", "-C",
    )):
        parser.error("one of --provides, --requires, --recommends or --conflicts is required")
    command = [args.generator, "--namespace", args.namespace]
    if args.package_name:
        command.extend(("--package-name", args.package_name))
    command.extend(passthrough)
    provides = "--provides" in passthrough or "-P" in passthrough
    try:
        result = subprocess.run(
            command,
            check=False,
            input=sys.stdin.read(),
            text=True,
            stdout=subprocess.PIPE,
        )
    except OSError as exc:
        print(f"sglangdistdeps: cannot execute {args.generator}: {exc}", file=sys.stderr)
        return 127
    for line in result.stdout.splitlines():
        print(_rewrite_capabilities(
            line,
            args.profile,
            provides=provides,
            default_namespace=args.namespace,
            private_dists=private_dists,
            torch_flavor=torch_flavor,
        ))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

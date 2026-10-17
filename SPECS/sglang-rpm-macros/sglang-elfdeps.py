#!/usr/bin/python3
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0
"""Namespace private SGLang ELF capabilities while preserving system deps."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys


# These names are produced by PyTorch and the selected native SGLang modules.
# Multifile paths identify the file that emitted a requirement.  Provides and
# private-file requires are namespaced; the system SONAME list keeps ordinary
# runtime dependencies global while allowing new private SONAMEs to work.
CORE_SONAME = re.compile(
    r"^lib(?:torch|c10|c10d|kineto|shm|torch_cpu|torch_cuda|"
    r"torch_global_deps|torch_python|torchaudio|torchvision|triton|"
    r"llguidance|xgrammar|xgrammar_bindings|tvm_ffi|sglang|sgl_kernel|"
    r"aoti_custom_ops|backend_with_compiler|jitbackend_test|torchbind_test)"
    r"(?:[-_.].*)?\.so(?:\.[0-9]+)*$"
)
PRIVATE_SONAME = re.compile(
    r"^lib(?:torch|c10|c10d|kineto|shm|torch_cpu|torch_cuda|"
    r"torch_global_deps|torch_python|torchaudio|torchvision|triton|"
    r"llguidance|xgrammar|xgrammar_bindings|tvm_ffi|sglang|sgl_kernel|"
    r"aoti_custom_ops|backend_with_compiler|jitbackend_test|torchbind_test)"
    r"(?:[-_.].*)?\.so(?:\.[0-9]+)*$"
)

# A private ELF can introduce a new SONAME at any time.  Treat known system
# libraries as the exception rather than maintaining a closed private list.
SYSTEM_SONAME = re.compile(
    r"^(?:linux-vdso|ld-linux(?:-[^.]*)?|ld-musl(?:-[^.]*)?|lib(?:anl|"
    r"atomic|blas|bz2|c|crypt|dl|expat|ffi|gcc_s|gomp|lapack|lzma|m|"
    r"nsl|numa|omp|openblas(?:64)?|pthread|quadmath|resolv|rt|stdc\+\+|"
    r"util|uuid|z|zstd))(?:[-_.].*)?\.so(?:\.[0-9]+)*$"
)
SONAME = re.compile(r"^(?:lib|ld-)[^/]+\.so(?:\.[0-9]+)*$")


def _capability_name(capability: str) -> str:
    unwrapped = re.sub(r"^(?:sglang|sglang-extras)\((.*)\)$", r"\1", capability)
    return unwrapped.split("(", 1)[0]


def _private(capability: str) -> bool:
    name = _capability_name(capability)
    return bool(
        PRIVATE_SONAME.match(name)
        or SONAME.match(name) and not SYSTEM_SONAME.match(name)
    )


def _core(capability: str) -> bool:
    return bool(CORE_SONAME.match(_capability_name(capability)))


def _private_path(marker: str, profile: str | None = None) -> bool:
    """Return whether a multifile marker names a private SGLang file.

    RPM 6 prefixes multifile paths with the buildroot, so match the installed
    ``/usr/lib[64]`` portion rather than anchoring at the beginning.  A
    profile mismatch is rejected to keep the two file attributes isolated.
    """
    path = marker[1:].lstrip()
    match = re.search(r"(?:^|/)usr/lib(?:64)?/sglang/(core|extras)(?:/|$)", path)
    return bool(match and (profile is None or match.group(1) == profile))


def _namespace(capability: str, namespace: str) -> str:
    if capability.startswith(namespace + "("):
        return capability
    # A generator should emit raw capabilities, but canonicalize an already
    # namespaced private capability instead of producing nested namespaces.
    capability = re.sub(r"^(?:sglang|sglang-extras)\((.*)\)$", r"\1", capability)
    return f"{namespace}({capability})"


def _requires_namespace(capability: str, namespace: str) -> str:
    if _core(capability):
        return "sglang"
    return namespace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("core", "extras"), required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--generator", default="/usr/lib/rpm/elfdeps")
    args, passthrough = parser.parse_known_args()
    if not any(flag in passthrough for flag in ("--provides", "--requires")):
        parser.error("one of --provides or --requires is required")
    command = [args.generator, *passthrough]
    provides = "--provides" in passthrough or "-P" in passthrough
    multifile = "--multifile" in passthrough or "-m" in passthrough
    try:
        result = subprocess.run(
            command,
            check=False,
            input=sys.stdin.read(),
            text=True,
            stdout=subprocess.PIPE,
        )
    except OSError as exc:
        print(f"sglang-elfdeps: cannot execute {args.generator}: {exc}", file=sys.stderr)
        return 127
    private_file = False
    for line in result.stdout.splitlines():
        if multifile and line.startswith(";"):
            private_file = _private_path(line, args.profile)
            print(line)
            continue
        capability = line.strip()
        if capability and provides and private_file:
            print(_namespace(capability, _requires_namespace(
                capability, args.namespace)))
        elif (
            capability
            and not provides
            and (not multifile or private_file)
            and _private(capability)
        ):
            print(_namespace(capability, _requires_namespace(
                capability, args.namespace)))
        else:
            print(line)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

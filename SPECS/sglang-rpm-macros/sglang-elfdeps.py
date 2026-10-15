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
# System libraries remain ordinary ELF capabilities and are deliberately absent
# from this list.  The multifile provider path is authoritative for provides,
# so this list only needs to cover private libraries named by requires output.
CORE_SONAME = re.compile(
    r"^lib(?:torch|c10|c10d|kineto|shm|torch_cpu|torch_cuda|"
    r"torch_global_deps|torch_python|torchaudio|torchvision|triton|"
    r"llguidance|xgrammar|xgrammar_bindings|tvm_ffi|sglang|sgl_kernel|"
    r"aoti_custom_ops|backend_with_compiler|jitbackend_test|torchbind_test)"
    r"(?:[-_.].*)?\.so(?:\.[0-9]+)*"
)
PRIVATE_SONAME = re.compile(
    r"^lib(?:torch|c10|c10d|kineto|shm|torch_cpu|torch_cuda|"
    r"torch_global_deps|torch_python|torchaudio|torchvision|triton|"
    r"llguidance|xgrammar|xgrammar_bindings|tvm_ffi|sglang|sgl_kernel|"
    r"aoti_custom_ops|backend_with_compiler|jitbackend_test|torchbind_test)"
    r"(?:[-_.].*)?\.so(?:\.[0-9]+)*"
)


def _private(capability: str) -> bool:
    name = capability.split("(", 1)[0]
    return bool(PRIVATE_SONAME.match(name))


def _core(capability: str) -> bool:
    name = capability.split("(", 1)[0]
    return bool(CORE_SONAME.match(name))


def _private_path(marker: str) -> bool:
    """Return whether a multifile marker names a private SGLang file."""
    path = marker[1:].lstrip()
    return bool(re.search(r"(?:^|/)sglang/(?:core|extras)(?:/|$)", path))


def _namespace(capability: str, namespace: str) -> str:
    if capability.startswith(namespace + "("):
        return capability
    return f"{namespace}({capability})"


def _requires_namespace(capability: str, profile: str) -> str:
    if _core(capability):
        return "sglang"
    return "sglang" if profile == "core" else "sglang-extras"


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
            private_file = _private_path(line)
            print(line)
            continue
        capability = line.strip()
        if capability and provides and private_file:
            print(_namespace(capability, _requires_namespace(capability, args.profile)))
        elif capability and _private(capability):
            print(_namespace(capability, _requires_namespace(capability, args.profile)))
        else:
            print(line)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

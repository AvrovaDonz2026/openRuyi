#!/usr/bin/env bash
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-License-Identifier: MIT
#
# Run inside the riscv64 validation guest. Arguments are RPM files already
# staged in the guest. The transaction is only installed when --install is
# passed; metadata, dependency, and import checks always run.
set -Eeuo pipefail

install=0
if [[ ${1:-} == --install ]]; then install=1; shift; fi
(( $# > 0 )) || { echo "usage: $0 [--install] RPM..." >&2; exit 2; }
for rpm in "$@"; do [[ -f $rpm ]] || { echo "missing RPM: $rpm" >&2; exit 2; }; done

tmp_root=${TMPDIR:-/var/tmp}
tmp=$(mktemp -d "$tmp_root/openruyi-rpm-harness.XXXXXX")
trap 'rm -rf "$tmp"' EXIT

echo '== system =='
uname -a
rpm --version

system_snapshot() {
  env -i PATH=/usr/bin:/bin HOME=/root LANG=C LC_ALL=C \
    PYTHONNOUSERSITE=1 python3 -s - <<'PY'
import importlib
from pathlib import Path

for name in ("torch", "torchaudio", "torchvision", "tokenizers", "transformers", "sglang"):
    try:
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve() if getattr(module, "__file__", None) else "<none>"
        print(f"{name}\t{getattr(module, '__version__', '<none>')}\t{path}")
    except BaseException as exc:
        print(f"{name}\tERROR:{type(exc).__name__}")
PY
}

system_before=$(system_snapshot)
printf '%s\n' "$system_before" > "$tmp/system-before.txt"

echo '== candidate metadata =='
for rpm in "$@"; do
  echo "-- $rpm"
  rpm -qp --qf 'name=%{NAME} version=%{VERSION}-%{RELEASE} arch=%{ARCH}\n' "$rpm"
  echo 'provides:'
  rpm -qp --provides "$rpm" | LC_ALL=C sort
  echo 'requires:'
  rpm -qp --requires "$rpm" | LC_ALL=C sort
done

echo '== ShortCircuited metadata =='
if rpm -qp --requires "$@" | grep -Fq 'rpmlib(ShortCircuited)'; then
  echo 'ShortCircuited: PRESENT'
else
  echo 'ShortCircuited: ABSENT'
fi

echo '== transaction test =='
set +e
rpm -Uvh --nosignature --replacepkgs --test "$@"
test_rc=$?
set -e
echo "RPM_TEST_RC=$test_rc"

if (( install )); then
  echo '== install transaction =='
  rpm -Uvh --nosignature --replacepkgs "$@"
  echo '== verify installed packages =='
  for rpm in "$@"; do
    name=$(rpm -qp --qf '%{NAME}' "$rpm")
    rpm -V "$name"
  done
  system_after=$(system_snapshot)
  printf '%s\n' "$system_after" > "$tmp/system-after.txt"
  if [[ $system_after != "$system_before" ]]; then
    echo 'SYSTEM_BASELINE=CHANGED'
    diff -u "$tmp/system-before.txt" "$tmp/system-after.txt" || true
    exit 1
  fi
  echo 'SYSTEM_BASELINE=UNCHANGED'
else
  echo '== install skipped (pass --install to mutate guest) =='
fi

echo '== private Python import =='
private_site=
for candidate in /usr/lib/sglang/core/python*/site-packages \
                 /usr/lib64/sglang/core/python*/site-packages; do
  [[ -d $candidate ]] || continue
  resolved=$(readlink -f "$candidate")
  [[ -z $private_site || $private_site == "$resolved" ]] || {
    echo "multiple private Python trees: $private_site and $resolved" >&2
    exit 1
  }
  private_site=$resolved
done
if [[ -n $private_site ]]; then
  PYTHONNOUSERSITE=1 PYTHONPATH="$private_site" python3 -s - "$private_site" "$install" <<'PY'
import importlib
import importlib.metadata
import sys
from pathlib import Path

private = Path(sys.argv[1]).resolve()
strict = sys.argv[2] == "1"
names = ("torch", "torchaudio", "torchvision", "tokenizers", "transformers", "sglang")
required = {
    "transformers": ("transformers", "5.19.0"),
    "tokenizers": ("tokenizers", "0.23.2"),
    "huggingface_hub": ("huggingface-hub", "1.31.0"),
}

def check_private(name, module):
    path = getattr(module, "__file__", None)
    if path is None:
        raise RuntimeError(f"{name} has no module path")
    resolved = Path(path).resolve()
    if private != resolved and private not in resolved.parents:
        raise RuntimeError(f"{name} escaped private tree: {resolved}")
    return resolved

for name in names:
    try:
        module = importlib.import_module(name)
        path = check_private(name, module)
        if strict and name in required:
            distribution, expected = required[name]
            actual = importlib.metadata.version(distribution)
            if actual != expected:
                raise RuntimeError(
                    f"{name} version mismatch: expected {expected}, got {actual}"
                )
        print(f"IMPORT {name}: PASS path={path}")
    except BaseException as exc:
        print(f"IMPORT {name}: {type(exc).__name__}: {exc}")
        if strict and name in required:
            raise

if strict:
    module = importlib.import_module("huggingface_hub")
    path = check_private("huggingface_hub", module)
    actual = importlib.metadata.version("huggingface-hub")
    if actual != required["huggingface_hub"][1]:
        raise RuntimeError(
            f"huggingface_hub version mismatch: expected "
            f"{required['huggingface_hub'][1]}, got {actual}"
        )
    print(f"IMPORT huggingface_hub: PASS path={path} version={actual}")
else:
    print(f"private_site={private}")
PY
else
  echo 'PRIVATE_SITE=ABSENT'
  if (( install )); then
    echo 'private Python tree is required after --install' >&2
    exit 1
  fi
fi

echo "HARNESS_RESULT test_rc=$test_rc install=$install"
exit "$test_rc"

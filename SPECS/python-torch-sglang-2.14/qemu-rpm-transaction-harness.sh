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

candidate_names=()
for rpm in "$@"; do
  candidate_names+=("$(rpm -qp --qf '%{NAME}' "$rpm")")
done

contains_candidate() {
  local wanted=$1 name
  for name in "${candidate_names[@]}"; do
    [[ $name == "$wanted" ]] && return 0
  done
  return 1
}

metadata_failure=0
assert_metadata_line() {
  local rpm=$1 field=$2 expected=$3
  if ! rpm -qp "--$field" "$rpm" | grep -Fqx -- "$expected"; then
    echo "metadata mismatch: $(basename "$rpm") $field lacks: $expected" >&2
    metadata_failure=1
  fi
}

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

  name=$(rpm -qp --qf '%{NAME}' "$rpm")
  version=$(rpm -qp --qf '%{VERSION}' "$rpm")
  arch=$(rpm -qp --qf '%{ARCH}' "$rpm")
  [[ -n $name && -n $version && -n $arch ]] || {
    echo "incomplete RPM metadata: $rpm" >&2
    metadata_failure=1
  }
  [[ $arch == riscv64 ]] || {
    echo "unexpected RPM architecture for $rpm: $arch (expected riscv64)" >&2
    metadata_failure=1
  }
  case "$name" in
    python-torch-sglang-2.14)
      [[ $version == 2.14.0 ]] || { echo "unexpected Torch version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torch-cpu)) = 2.14.0'
      assert_metadata_line "$rpm" requires 'python3dist(typing-extensions) >= 4.10.0'
      ;;
    python-torch-sglang-2.14-rocm)
      [[ $version == 2.14.0 ]] || { echo "unexpected Torch version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torch-rocm)) = 2.14.0'
      ;;
    python-torchaudio-2.11)
      [[ $version == 2.11.0 ]] || { echo "unexpected TorchAudio version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torchaudio)) = 2.11.0'
      assert_metadata_line "$rpm" requires 'sglang(python3dist(torch-cpu)) = 2.14.0'
      ;;
    python-torchaudio-2.11-rocm)
      [[ $version == 2.11.0 ]] || { echo "unexpected TorchAudio version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torchaudio)) = 2.11.0'
      assert_metadata_line "$rpm" requires 'sglang(python3dist(torch-rocm)) = 2.14.0'
      ;;
    python-torchvision-0.29)
      [[ $version == 0.29.0 ]] || { echo "unexpected TorchVision version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torchvision)) = 0.29.0'
      assert_metadata_line "$rpm" requires 'sglang(python3dist(torch-cpu)) = 2.14.0'
      ;;
    python-torchvision-0.29-rocm)
      [[ $version == 0.29.0 ]] || { echo "unexpected TorchVision version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torchvision)) = 0.29.0'
      assert_metadata_line "$rpm" requires 'sglang(python3dist(torch-rocm)) = 2.14.0'
      ;;
    python-tokenizers-sglang-0.23)
      [[ $version == 0.23.2 ]] || { echo "unexpected tokenizers version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(tokenizers)) = 0.23.2'
      ;;
    python-transformers-sglang-5.19)
      [[ $version == 5.19.0 ]] || { echo "unexpected transformers version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(transformers)) = 5.19.0'
      ;;
    python-huggingface-hub-sglang-1.31)
      [[ $version == 1.31.0 ]] || { echo "unexpected huggingface-hub version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(huggingface_hub)) = 1.31.0'
      ;;
    python-sglang)
      [[ $version == 0.5.21 ]] || { echo "unexpected SGLang version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" requires 'sglang(python3dist(torch-cpu)) = 2.14.0'
      assert_metadata_line "$rpm" requires 'sglang(python3dist(transformers)) = 5.19.0'
      ;;
  esac
done

if (( metadata_failure )); then
  echo 'METADATA_RESULT=FAIL' >&2
  exit 1
fi
echo 'METADATA_RESULT=PASS'

echo '== ShortCircuited metadata =='
for rpm in "$@"; do
  if rpm -qp --requires "$rpm" | grep -Fq 'rpmlib(ShortCircuited)'; then
    echo "ShortCircuited: PRESENT in $rpm" >&2
    echo 'SHORTCIRCUITED_RESULT=FAIL' >&2
    exit 1
  fi
done
echo 'ShortCircuited: ABSENT'
echo 'SHORTCIRCUITED_RESULT=PASS'

echo '== transaction test =='
set +e
rpm -Uvh --nosignature --replacepkgs --test "$@"
test_rc=$?
set -e
echo "RPM_TEST_RC=$test_rc"
if (( test_rc != 0 )); then
  echo 'RPM_TRANSACTION_TEST=FAIL' >&2
  echo "HARNESS_RESULT test_rc=$test_rc install=$install"
  exit "$test_rc"
fi
echo 'RPM_TRANSACTION_TEST=PASS'

if (( install )); then
  echo '== install transaction =='
  rpm -Uvh --nosignature --replacepkgs "$@"
  echo '== verify installed packages =='
  for rpm in "$@"; do
    name=$(rpm -qp --qf '%{NAME}' "$rpm")
    rpm -V "$name"
  done
  echo 'INSTALL_VERIFY=PASS'
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
  echo 'INSTALL_RESULT=SKIPPED'
  echo 'PRIVATE_IMPORT=SKIPPED'
  echo 'TORCH_TENSOR_SMOKE=SKIPPED'
  echo 'GLOO_SMOKE=SKIPPED'
  echo 'SGLANG_SMOKE=SKIPPED'
  echo "HARNESS_RESULT test_rc=$test_rc install=$install"
  exit "$test_rc"
fi
echo 'INSTALL_RESULT=PASS'

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
  expected_modules=
  for name in "${candidate_names[@]}"; do
    case "$name" in
      python-torch-sglang-2.14|python-torch-sglang-2.14-rocm) expected_modules+="torch," ;;
      python-torchaudio-2.11|python-torchaudio-2.11-rocm) expected_modules+="torchaudio," ;;
      python-torchvision-0.29|python-torchvision-0.29-rocm) expected_modules+="torchvision," ;;
      python-tokenizers-sglang-0.23) expected_modules+="tokenizers," ;;
      python-transformers-sglang-5.19) expected_modules+="transformers," ;;
      python-huggingface-hub-sglang-1.31) expected_modules+="huggingface_hub," ;;
      python-sglang) expected_modules+="sglang," ;;
    esac
  done
  expected_modules=${expected_modules%,}
  PYTHONNOUSERSITE=1 PYTHONPATH="$private_site" SGLANG_EXPECTED_MODULES="$expected_modules" \
    python3 -s - "$private_site" <<'PY'
import importlib
import importlib.metadata
import os
import sys
from pathlib import Path

private = Path(sys.argv[1]).resolve()
names = tuple(name for name in os.environ.get("SGLANG_EXPECTED_MODULES", "").split(",") if name)
required = {
    "torch": ("torch", "2.14.0"),
    "torchaudio": ("torchaudio", "2.11.0"),
    "torchvision": ("torchvision", "0.29.0"),
    "tokenizers": ("tokenizers", "0.23.2"),
    "transformers": ("transformers", "5.19.0"),
    "huggingface_hub": ("huggingface-hub", "1.31.0"),
    "sglang": ("sglang-cpu", "0.5.21"),
}

def check_private(name, path):
    if path is None:
        raise RuntimeError(f"{name} has no module path")
    resolved = Path(path).resolve()
    if private != resolved and private not in resolved.parents:
        raise RuntimeError(f"{name} escaped private tree: {resolved}")
    return resolved

def check_module(name, module):
    path = check_private(name, getattr(module, "__file__", None))
    for root in getattr(module, "__path__", ()):
        check_private(f"{name}.__path__", root)
    distribution, expected = required[name]
    actual = importlib.metadata.version(distribution)
    if actual != expected:
        raise RuntimeError(f"{name} version mismatch: expected {expected}, got {actual}")
    location = Path(importlib.metadata.distribution(distribution).locate_file("")).resolve()
    check_private(f"{distribution} distribution", location)
    return path

for name in names:
    module = importlib.import_module(name)
    path = check_module(name, module)
    print(f"IMPORT {name}: PASS version={required[name][1]} path={path}")

for module_name, module in tuple(sys.modules.items()):
    if not module or not module_name.startswith(("torch", "torchaudio", "torchvision")):
        continue
    native = getattr(module, "__file__", None)
    if native and ".so" in native:
        check_private(f"{module_name} native", native)

for name in names:
    module = sys.modules[name]
    roots = [Path(module.__file__).resolve().parent]
    roots.extend(Path(root).resolve() for root in getattr(module, "__path__", ()))
    for root in roots:
        for native in root.rglob("*.so*"):
            if native.is_file():
                check_private(f"{name} native", native)

print(f"PRIVATE_IMPORT_RESULT=PASS private_site={private}")
PY
  echo 'PRIVATE_IMPORT=PASS'
else
  echo 'PRIVATE_SITE=ABSENT'
  echo 'PRIVATE_IMPORT=FAIL' >&2
  exit 1
fi

if contains_candidate python-torch-sglang-2.14 || contains_candidate python-torch-sglang-2.14-rocm; then
  echo '== Torch tensor smoke =='
  PYTHONNOUSERSITE=1 PYTHONPATH="$private_site" python3 -s - <<'PY'
import torch

x = torch.arange(16, dtype=torch.float32).reshape(4, 4)
expected = torch.tensor(
    [[56, 62, 68, 74], [152, 174, 196, 218],
     [248, 286, 324, 362], [344, 398, 452, 506]],
    dtype=torch.float32,
)
torch.testing.assert_close(x @ x, expected)
value = torch.tensor(3.0, requires_grad=True)
(value * value).backward()
assert value.grad.item() == 6.0
print("TORCH_TENSOR_SMOKE=PASS")
PY
else
  echo 'TORCH_TENSOR_SMOKE=SKIPPED (Torch RPM not supplied)'
fi

if contains_candidate python-torch-sglang-2.14; then
  echo '== Gloo smoke =='
  cat > "$tmp/gloo-smoke.py" <<'PY'
import datetime
import multiprocessing
import os
import shutil
import tempfile

WORLD_SIZE = 2

def worker(rank, rendezvous):
    import torch
    import torch.distributed as dist
    if not dist.is_available() or not dist.is_gloo_available():
        raise RuntimeError("torch.distributed Gloo is unavailable")
    dist.init_process_group(
        "gloo", init_method="file://" + rendezvous, rank=rank,
        world_size=WORLD_SIZE, timeout=datetime.timedelta(seconds=60),
    )
    try:
        value = torch.tensor([rank + 1], dtype=torch.float32)
        dist.all_reduce(value)
        assert value.item() == 3.0, value.item()
    finally:
        dist.destroy_process_group()

def main():
    import torch.distributed as dist
    if not dist.is_available() or not dist.is_gloo_available():
        raise RuntimeError("torch.distributed Gloo is unavailable")
    rendezvous_dir = tempfile.mkdtemp(prefix="openruyi-gloo-smoke-")
    processes = []
    try:
        rendezvous = os.path.join(rendezvous_dir, "store")
        context = multiprocessing.get_context("spawn")
        processes = [context.Process(target=worker, args=(rank, rendezvous)) for rank in range(WORLD_SIZE)]
        for process in processes:
            process.start()
        for process in processes:
            process.join(75)
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(5)
            if process.exitcode != 0:
                raise RuntimeError("Gloo rank failed with exit code %s" % process.exitcode)
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(5)
        shutil.rmtree(rendezvous_dir)
    print("GLOO_SMOKE=PASS")

if __name__ == "__main__":
    main()
PY
  PYTHONNOUSERSITE=1 PYTHONPATH="$private_site" python3 -s "$tmp/gloo-smoke.py"
else
  echo 'GLOO_SMOKE=SKIPPED (CPU Torch RPM not supplied)'
fi

if contains_candidate python-sglang; then
  echo '== SGLang smoke =='
  SGLANG_USE_CPU_ENGINE=1 PYTHONNOUSERSITE=1 PYTHONSAFEPATH=1 PYTHONPATH="$private_site" \
    python3 -s - <<'PY'
import subprocess

subprocess.run(["/usr/bin/sglang", "--help"], check=True, timeout=60,
               stdout=subprocess.DEVNULL)
PY
  echo 'SGLANG_SMOKE=PASS'
else
  echo 'SGLANG_SMOKE=SKIPPED (python-sglang RPM not supplied)'
fi

echo "HARNESS_RESULT test_rc=$test_rc install=$install"
exit "$test_rc"

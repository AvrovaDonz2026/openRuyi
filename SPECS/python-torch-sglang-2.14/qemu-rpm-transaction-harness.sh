#!/usr/bin/env bash
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-License-Identifier: MIT
#
# Run inside the riscv64 validation guest. Arguments are RPM files already
# staged in the guest. The transaction is only installed when --install is
# passed; metadata, dependency, signature, and import checks always run.
set -Eeuo pipefail

install=0
gpg_key=${RPM_GPG_KEY:-}
gpg_fingerprint=${RPM_GPG_FINGERPRINT:-}
coexistence_script=${COEXISTENCE_SCRIPT:-/usr/libexec/sglang/sglang-coexistence-test.py}
cpu_smoke_script=${CPU_SMOKE_SCRIPT:-/usr/libexec/sglang/sglang-cpu-engine-smoke.py}
offline_repo_source=${DNF_OFFLINE_REPO:-}
while (( $# > 0 )); do
  case $1 in
    --install) install=1 ;;
    --gpg-key) shift; [[ $# -gt 0 ]] || { echo '--gpg-key requires a file' >&2; exit 2; }; gpg_key=$1 ;;
    --gpg-fingerprint) shift; [[ $# -gt 0 ]] || { echo '--gpg-fingerprint requires a value' >&2; exit 2; }; gpg_fingerprint=$1 ;;
    --coexistence-script) shift; [[ $# -gt 0 ]] || { echo '--coexistence-script requires a file' >&2; exit 2; }; coexistence_script=$1 ;;
    --cpu-smoke-script) shift; [[ $# -gt 0 ]] || { echo '--cpu-smoke-script requires a file' >&2; exit 2; }; cpu_smoke_script=$1 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; exit 2 ;;
    *) break ;;
  esac
  shift
done
(( $# > 0 )) || { echo "usage: $0 [--install] [--gpg-key FILE] [--gpg-fingerprint FPR] RPM..." >&2; exit 2; }
case $coexistence_script in
  /*) ;;
  *) echo '--coexistence-script must be an absolute installed path' >&2; exit 2 ;;
esac
case $cpu_smoke_script in
  /*) ;;
  *) echo '--cpu-smoke-script must be an absolute installed path' >&2; exit 2 ;;
esac
for rpm in "$@"; do [[ -f $rpm ]] || { echo "missing RPM: $rpm" >&2; exit 2; }; done

candidate_names=()
candidate_paths=()
for rpm in "$@"; do
  path=$(basename -- "$rpm")
  if ((${#candidate_paths[@]} > 0)); then
    for existing in "${candidate_paths[@]}"; do
      [[ $existing != "$path" ]] && continue
      echo "duplicate candidate basename: $path" >&2
      exit 2
    done
  fi
  candidate_names+=("$(rpm -qp --qf '%{NAME}' "$rpm")")
  candidate_paths+=("$path")
done

for ((index = 0; index < ${#candidate_names[@]}; index++)); do
  for ((previous = 0; previous < index; previous++)); do
    if [[ ${candidate_names[index]} == "${candidate_names[previous]}" ]]; then
      echo "duplicate candidate package name: ${candidate_names[index]}" >&2
      exit 2
    fi
  done
done

contains_candidate() {
  local wanted=$1 name
  for name in "${candidate_names[@]}"; do
    [[ $name == "$wanted" ]] && return 0
  done
  return 1
}

# The SGLang CPU transaction is validated as one private runtime closure.  A
# partial closure would make the conditional smoke checks look successful while
# leaving dependency resolution to an unrelated system package.
if contains_candidate python-sglang || contains_candidate python-torchcodec; then
  contains_candidate python-torch-sglang-2.14 || {
    echo 'SGLang/TorchCodec transaction requires python-torch-sglang-2.14' >&2
    exit 2
  }
  contains_candidate python-sglang || {
    echo 'SGLang/TorchCodec transaction requires python-sglang' >&2
    exit 2
  }
  contains_candidate python-torchcodec || {
    echo 'SGLang/TorchCodec transaction requires python-torchcodec' >&2
    exit 2
  }
fi

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

rpm_snapshot() {
  rpm -qa --qf '%{NAME}\t%{EPOCHNUM}:%{VERSION}-%{RELEASE}\t%{ARCH}\n' | LC_ALL=C sort
}

rpm_before=$(rpm_snapshot)
printf '%s\n' "$rpm_before" > "$tmp/rpm-before.txt"

echo '== system =='
uname -a
rpm --version

system_snapshot() {
  env -i PATH=/usr/bin:/bin HOME=/root LANG=C LC_ALL=C \
    PYTHONNOUSERSITE=1 python3 -s - <<'PY'
import importlib
from pathlib import Path

for name in ("torch", "torchaudio", "torchvision", "tokenizers", "transformers", "sglang", "triton", "torchcodec"):
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

if [[ -z $gpg_key ]]; then
  for candidate in /etc/pki/rpm-gpg/RPM-GPG-KEY-openruyi \
                   /usr/share/openruyi-repos/RPM-GPG-KEY-openruyi; do
    if [[ -f $candidate ]]; then gpg_key=$candidate; break; fi
  done
fi

echo '== RPM signature verification =='
if (( install )) && [[ -z $gpg_fingerprint ]]; then
  echo 'signed installation requires --gpg-fingerprint' >&2
  exit 1
fi
if [[ -n $gpg_key ]]; then
  [[ -f $gpg_key ]] || { echo "missing RPM GPG key: $gpg_key" >&2; exit 1; }
  command -v gpg >/dev/null || { echo 'gpg is required for RPM key fingerprint verification' >&2; exit 1; }
  imported_fingerprint=$(gpg --batch --show-keys --with-colons "$gpg_key" |
    awk -F: '$1 == "fpr" { print toupper($10); exit }')
  [[ -n $imported_fingerprint ]] || { echo "cannot read fingerprint from $gpg_key" >&2; exit 1; }
  if [[ -n $gpg_fingerprint ]]; then
    expected_fingerprint=$(LC_ALL=C printf '%s' "$gpg_fingerprint" | LC_ALL=C tr '[:lower:]' '[:upper:]')
    [[ $imported_fingerprint == "$expected_fingerprint" ]] || {
      echo "RPM GPG fingerprint mismatch: $imported_fingerprint (expected $expected_fingerprint)" >&2
      exit 1
    }
  else
    expected_fingerprint=$imported_fingerprint
  fi
  rpm --import "$gpg_key"
  echo "RPM_GPG_FINGERPRINT=$expected_fingerprint"
  for rpm in "$@"; do rpm -K --verbose "$rpm"; done
  echo 'RPM_SIGNATURE_RESULT=PASS'
else
  echo 'RPM_SIGNATURE_RESULT=SKIPPED (provide --gpg-key and --gpg-fingerprint for signed validation)'
fi

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
  [[ $arch == riscv64 || $arch == noarch ]] || {
    echo "unexpected RPM architecture for $rpm: $arch (expected riscv64 or noarch)" >&2
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
      assert_metadata_line "$rpm" provides 'sglang(python3dist(huggingface-hub)) = 1.31'
      ;;
    python-sglang)
      [[ $version == 0.5.21 ]] || { echo "unexpected SGLang version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" requires 'sglang(python3dist(torch-cpu)) = 2.14.0'
      assert_metadata_line "$rpm" requires 'sglang(python3dist(transformers)) = 5.19.0'
      ;;
    python-triton-sglang-3.8)
      [[ $version == 3.8.0 ]] || { echo "unexpected Triton version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(triton)) = 3.8.0'
      ;;
    python-torchcodec)
      [[ $version == 0.12.0 ]] || { echo "unexpected TorchCodec version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torchcodec)) = 0.12.0'
      assert_metadata_line "$rpm" requires 'sglang(python3dist(torch-cpu)) = 2.14.0'
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

echo '== offline DNF repository check =='
repo_dir="$tmp/repo"
mkdir -p "$repo_dir"
if [[ -n $offline_repo_source ]]; then
  [[ -d $offline_repo_source ]] || {
    echo "DNF_OFFLINE_REPO is not a directory: $offline_repo_source" >&2
    exit 1
  }
  cp -a -- "$offline_repo_source"/. "$repo_dir/"
else
  cp -- "$@" "$repo_dir/"
fi
# Always stage the exact candidate files, even when the offline repository
# contains another build of the same package name.
for rpm in "$@"; do
  cp -- "$rpm" "$repo_dir/$(basename -- "$rpm")"
done
dnf_ready=0
dnf_args=(--disablerepo='*'
  --repofrompath=openruyi-qemu-local,"file://$repo_dir"
    --setopt=openruyi-qemu-local.gpgcheck=1
    --setopt=openruyi-qemu-local.repo_gpgcheck=0
    --setopt=install_weak_deps=False --setopt=metadata_expire=0)
if (( install )); then
  [[ -n $gpg_key && -n $gpg_fingerprint ]] || {
    echo 'signed installation requires --gpg-key and --gpg-fingerprint' >&2
    exit 1
  }
  command -v createrepo_c >/dev/null || {
    echo 'createrepo_c is required for --install' >&2
    exit 1
  }
  command -v dnf >/dev/null || {
    echo 'dnf is required for --install' >&2
    exit 1
  }
  createrepo_c --quiet "$repo_dir"
  dnf_ready=1
  dnf_preview_args=(--assumeyes --setopt=tsflags=test "${dnf_args[@]}")
  set +e
  dnf "${dnf_preview_args[@]}" install "${candidate_paths[@]/#/$repo_dir/}"
  dnf_rc=$?
  set -e
  echo "DNF_OFFLINE_RC=$dnf_rc"
  if (( dnf_rc != 0 )); then
    echo 'DNF_OFFLINE_RESULT=FAIL' >&2
    exit "$dnf_rc"
  fi
  echo 'DNF_OFFLINE_RESULT=PASS (RPM transaction test)'
elif [[ -z $gpg_key ]]; then
  echo 'DNF_OFFLINE_RESULT=SKIPPED (signed RPM key unavailable; scratch mode)'
elif ! command -v createrepo_c >/dev/null || ! command -v dnf >/dev/null; then
  echo 'DNF_OFFLINE_RESULT=SKIPPED (createrepo_c or dnf unavailable)'
else
  createrepo_c --quiet "$repo_dir"
  dnf_preview_args=(--assumeyes --setopt=tsflags=test "${dnf_args[@]}")
  set +e
  dnf "${dnf_preview_args[@]}" install "${candidate_paths[@]/#/$repo_dir/}"
  dnf_rc=$?
  set -e
  echo "DNF_OFFLINE_RC=$dnf_rc"
  if (( dnf_rc != 0 )); then
    echo 'DNF_OFFLINE_RESULT=FAIL' >&2
    exit "$dnf_rc"
  fi
  echo 'DNF_OFFLINE_RESULT=PASS (RPM transaction test)'
fi

rpm_signature_args=()
if [[ -z $gpg_key ]]; then
  if (( install )); then
    echo 'signed installation requires --gpg-key and --gpg-fingerprint' >&2
    exit 1
  fi
  rpm_signature_args+=(--nosignature)
  echo 'RPM_SIGNATURE_MODE=SCRATCH_NOSIGNATURE'
else
  echo 'RPM_SIGNATURE_MODE=SIGNED'
fi

coexistence_baseline="$tmp/coexistence-baseline.json"
coexistence_enabled=0
if contains_candidate python-sglang; then
  # A fresh guest does not have the validation helpers before the candidate
  # RPM is installed. Extract them from that RPM for the pre-install
  # baseline, then use the installed copies for post-install checks.
  validation_root="$tmp/validation"
  mkdir -p "$validation_root"
  installed_coexistence_script=$coexistence_script
  installed_cpu_smoke_script=$cpu_smoke_script
  if [[ ! -f $coexistence_script || ! -f $cpu_smoke_script ]]; then
    command -v rpm2cpio >/dev/null || {
      echo 'rpm2cpio is required to extract pre-install validation helpers' >&2
      exit 1
    }
    command -v cpio >/dev/null || {
      echo 'cpio is required to extract pre-install validation helpers' >&2
      exit 1
    }
    sglang_rpm=
    sglang_count=0
    for rpm in "$@"; do
      if [[ $(rpm -qp --qf '%{NAME}' "$rpm") == python-sglang ]]; then
        sglang_rpm=$rpm
        sglang_count=$((sglang_count + 1))
      fi
    done
    (( sglang_count == 1 )) || {
      echo "expected one python-sglang candidate, found $sglang_count" >&2
      exit 1
    }
    (cd "$validation_root" && rpm2cpio "$sglang_rpm" | cpio -idm --quiet)
    coexistence_script="$validation_root$coexistence_script"
    cpu_smoke_script="$validation_root$cpu_smoke_script"
  fi
  [[ -f $coexistence_script ]] || {
    echo "COEXISTENCE=FAIL (missing $coexistence_script)" >&2
    exit 1
  }
  [[ -f $cpu_smoke_script ]] || {
    echo "CPU_ENGINE_SMOKE=FAIL (missing $cpu_smoke_script)" >&2
    exit 1
  }
  python3 -s "$coexistence_script" --baseline-json "$coexistence_baseline" --snapshot
  coexistence_script=$installed_coexistence_script
  cpu_smoke_script=$installed_cpu_smoke_script
  coexistence_enabled=1
  echo 'COEXISTENCE_BASELINE=PASS'
fi

echo '== transaction test =='
if (( install )); then
  # The DNF preview above is the dependency transaction test.  A direct
  # rpm --test cannot resolve dependencies from the temporary repository.
  test_rc=0
  echo 'RPM_TRANSACTION_TEST=SKIPPED (DNF preview is authoritative)'
else
  set +e
  rpm -Uvh "${rpm_signature_args[@]}" --replacepkgs --test "$@"
  test_rc=$?
  set -e
  echo "RPM_TEST_RC=$test_rc"
  if (( test_rc != 0 )); then
    echo 'RPM_TRANSACTION_TEST=FAIL' >&2
    echo "HARNESS_RESULT test_rc=$test_rc install=$install"
    exit "$test_rc"
  fi
  echo 'RPM_TRANSACTION_TEST=PASS'
fi

if (( install )); then
  echo '== install transaction =='
  (( dnf_ready )) || { echo 'DNF transaction was not prepared' >&2; exit 1; }
  dnf --assumeyes "${dnf_args[@]}" install "${candidate_paths[@]/#/$repo_dir/}"
  echo 'DNF_INSTALL_RESULT=PASS'
  echo '== verify installed packages =='
  for rpm in "$@"; do
    name=$(rpm -qp --qf '%{NAME}' "$rpm")
    expected_nevra=$(rpm -qp --qf '%{NAME}-%{EPOCHNUM}:%{VERSION}-%{RELEASE}.%{ARCH}' "$rpm")
    installed_nevra=$(rpm -q --qf '%{NAME}-%{EPOCHNUM}:%{VERSION}-%{RELEASE}.%{ARCH}\n' "$name" |
      LC_ALL=C sort | tail -n 1)
    [[ $installed_nevra == "$expected_nevra" ]] || {
      echo "installed NEVRA mismatch for $name: $installed_nevra (expected $expected_nevra)" >&2
      exit 1
    }
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
  rpm_after=$(rpm_snapshot)
  printf '%s\n' "$rpm_after" > "$tmp/rpm-after.txt"
  removed_rpms=$(comm -23 "$tmp/rpm-before.txt" "$tmp/rpm-after.txt")
  if [[ -n $removed_rpms ]]; then
    echo 'RPM_BASELINE=REMOVED' >&2
    printf '%s\n' "$removed_rpms" >&2
    exit 1
  fi
  # Candidate packages are expected to be added or replaced.  Every other
  # installed NEVRA must remain identical so a private transaction cannot
  # silently upgrade or remove an existing system package.
  candidate_names_file="$tmp/candidate-names.txt"
  printf '%s\n' "${candidate_names[@]}" | LC_ALL=C sort -u > "$candidate_names_file"
  awk -F '\t' 'NR == FNR { names[$1] = 1; next } !names[$1]' \
    "$candidate_names_file" "$tmp/rpm-before.txt" | LC_ALL=C sort > "$tmp/rpm-before-system.txt"
  awk -F '\t' 'NR == FNR { names[$1] = 1; next } !names[$1]' \
    "$candidate_names_file" "$tmp/rpm-after.txt" | LC_ALL=C sort > "$tmp/rpm-after-system.txt"
  if ! cmp -s "$tmp/rpm-before-system.txt" "$tmp/rpm-after-system.txt"; then
    echo 'RPM_BASELINE=CHANGED (non-candidate package set)' >&2
    diff -u "$tmp/rpm-before-system.txt" "$tmp/rpm-after-system.txt" >&2 || true
    exit 1
  fi
  echo 'RPM_BASELINE=UNCHANGED'
else
  echo '== install skipped (pass --install to mutate guest) =='
  echo 'INSTALL_RESULT=SKIPPED'
  echo 'PRIVATE_IMPORT=SKIPPED'
  echo 'TORCH_TENSOR_SMOKE=SKIPPED'
  echo 'GLOO_SMOKE=SKIPPED'
  echo 'SGLANG_SMOKE=SKIPPED'
  echo 'COEXISTENCE=SKIPPED'
  echo 'CPU_ENGINE_SMOKE=SKIPPED'
  echo 'RPM_BASELINE=SKIPPED'
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
      python-triton-sglang-3.8) expected_modules+="triton," ;;
      python-torchcodec) expected_modules+="torchcodec," ;;
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
    "triton": ("triton", "3.8.0"),
    "torchcodec": ("torchcodec", "0.12.0"),
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
    if not module or not module_name.startswith(("torch", "torchaudio", "torchvision", "triton")):
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

if contains_candidate python-triton-sglang-3.8; then
  echo '== Triton smoke =='
  PYTHONNOUSERSITE=1 PYTHONPATH="$private_site" python3 -s - <<'PY'
import triton
import triton.compiler
import triton.language

assert triton.__version__ == "3.8.0", triton.__version__
assert triton.cdiv(7, 3) == 3
print("TRITON_SMOKE=PASS")
PY
else
  echo 'TRITON_SMOKE=SKIPPED (Triton RPM not supplied)'
fi

if contains_candidate python-torchcodec; then
  echo '== TorchCodec smoke =='
  PYTHONNOUSERSITE=1 PYTHONPATH="$private_site" python3 -s - <<'PY'
from torchcodec._core import get_ffmpeg_library_versions

versions = get_ffmpeg_library_versions()
assert versions.get("ffmpeg_version"), versions
print("TORCHCODEC_SMOKE=PASS")
PY
else
  echo 'TORCHCODEC_SMOKE=SKIPPED (TorchCodec RPM not supplied)'
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
  if (( coexistence_enabled )); then
    private_root=${private_site%/python*/site-packages}
    python3 -s "$coexistence_script" --baseline-json "$coexistence_baseline" \
      --private-root "$private_root"
    echo 'COEXISTENCE=PASS'
  fi
  PYTHONNOUSERSITE=1 PYTHONSAFEPATH=1 PYTHONPATH="$private_site" \
    python3 -s "$cpu_smoke_script"
  echo 'CPU_ENGINE_SMOKE=PASS'
else
  echo 'SGLANG_SMOKE=SKIPPED (python-sglang RPM not supplied)'
fi

echo "HARNESS_RESULT test_rc=$test_rc install=$install"
exit "$test_rc"

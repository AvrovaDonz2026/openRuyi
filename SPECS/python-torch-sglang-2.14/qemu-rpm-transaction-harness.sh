#!/usr/bin/env bash
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
# SPDX-License-Identifier: MIT
#
# Run inside the riscv64 validation guest. Arguments are RPM files already
# staged in the guest. This harness validates the CPU/private-runtime path;
# reserved CUDA and ROCm candidates are rejected before any transaction. No
# GPU runtime is claimed. The transaction is only installed when --install is passed.
# Without --install, this is an intentional metadata/transaction-check-only
# run and exits with EX_SKIP (77) after reporting the checks as skipped.
set -Eeuo pipefail

EX_SKIP=77

install=0
gpg_key=${RPM_GPG_KEY:-}
gpg_fingerprint=${RPM_GPG_FINGERPRINT:-}
coexistence_script=${COEXISTENCE_SCRIPT:-/usr/libexec/sglang/sglang-coexistence-test.py}
cpu_smoke_script=${CPU_SMOKE_SCRIPT:-/usr/libexec/sglang/sglang-cpu-engine-smoke.py}
kernel_smoke_script=${KERNEL_SMOKE_SCRIPT:-/usr/libexec/sglang/sglang-kernel-cpu-smoke.py}
kernel_smoke_timeout=${SGLANG_KERNEL_SMOKE_TIMEOUT:-300}
offline_repo_source=${DNF_OFFLINE_REPO:-}
while (( $# > 0 )); do
  case $1 in
    --install) install=1 ;;
    --gpg-key) shift; [[ $# -gt 0 ]] || { echo '--gpg-key requires a file' >&2; exit 2; }; gpg_key=$1 ;;
    --gpg-fingerprint) shift; [[ $# -gt 0 ]] || { echo '--gpg-fingerprint requires a value' >&2; exit 2; }; gpg_fingerprint=$1 ;;
    --coexistence-script) shift; [[ $# -gt 0 ]] || { echo '--coexistence-script requires a file' >&2; exit 2; }; coexistence_script=$1 ;;
    --cpu-smoke-script) shift; [[ $# -gt 0 ]] || { echo '--cpu-smoke-script requires a file' >&2; exit 2; }; cpu_smoke_script=$1 ;;
    --kernel-smoke-script) shift; [[ $# -gt 0 ]] || { echo '--kernel-smoke-script requires a file' >&2; exit 2; }; kernel_smoke_script=$1 ;;
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
case $kernel_smoke_script in
  /*) ;;
  *) echo '--kernel-smoke-script must be an absolute installed path' >&2; exit 2 ;;
esac
for rpm in "$@"; do [[ -f $rpm ]] || { echo "missing RPM: $rpm" >&2; exit 2; }; done

candidate_names=()
candidate_paths=()
candidate_files=()
for rpm in "$@"; do
  path=$(basename -- "$rpm")
  if ((${#candidate_paths[@]} > 0)); then
    for existing in "${candidate_paths[@]}"; do
      [[ $existing != "$path" ]] && continue
      echo "duplicate candidate basename: $path" >&2
      exit 2
    done
  fi
  candidate_names+=("$(rpm -qp --qf '%{NAME}' -- "$rpm")")
  candidate_paths+=("$path")
  candidate_files+=("$rpm")
done

for ((index = 0; index < ${#candidate_names[@]}; index++)); do
  for ((previous = 0; previous < index; previous++)); do
    if [[ ${candidate_names[index]} == "${candidate_names[previous]}" ]]; then
      echo "duplicate candidate package name: ${candidate_names[index]}" >&2
      exit 2
    fi
  done
done

# Accelerator packages are reserved flavors in the corresponding SPECs.
# Reject them here so a manually staged future candidate cannot be reported as
# a validated runtime by this CPU-focused harness.  Check both the normalized
# package name and the advertised capability: a renamed RPM must not bypass
# the guard.
reserved_flavor_failure=0
for ((index = 0; index < ${#candidate_names[@]}; index++)); do
  name=${candidate_names[index]}
  rpm=${candidate_files[index]}
  reserved_flavor=
  case "$name" in
    *-cuda) reserved_flavor=CUDA ;;
    *-rocm) reserved_flavor=ROCm ;;
  esac
  if [[ -z $reserved_flavor ]]; then
    while IFS= read -r capability; do
      case "$capability" in
        sglang\(python3dist\(*-cuda\)\)* ) reserved_flavor=CUDA; break ;;
        sglang\(python3dist\(*-rocm\)\)* ) reserved_flavor=ROCm; break ;;
      esac
    done < <(rpm -qp --provides -- "$rpm")
  fi
  if [[ -n $reserved_flavor ]]; then
    echo "reserved $reserved_flavor candidate is not testable: $name" >&2
    reserved_flavor_failure=1
  fi
done
if (( reserved_flavor_failure )); then
  echo 'RESERVED_FLAVOR_RESULT=FAIL' >&2
  exit 1
fi
echo 'RESERVED_FLAVOR_RESULT=PASS (no reserved accelerator candidates)'

# Private payload paths encode the Python ABI selected when the RPMs were
# built. Check it against the guest before dependency resolution or install so
# an incompatible rootfs fails without attempting the transaction.
candidate_private_python_abi=
for candidate_rpm in "${candidate_files[@]}"; do
  while IFS= read -r payload_path; do
    [[ $payload_path =~ ^/usr/lib(64)?/sglang/(core|extras)/python([0-9]+\.[0-9]+)/site-packages(/.*)?$ ]] || continue
    payload_python_abi=${BASH_REMATCH[3]}
    if [[ -n $candidate_private_python_abi && $candidate_private_python_abi != "$payload_python_abi" ]]; then
      echo "candidate RPMs use multiple private Python ABIs: $candidate_private_python_abi and $payload_python_abi" >&2
      exit 1
    fi
    candidate_private_python_abi=$payload_python_abi
  done < <(rpm -qp --qf '[%{FILENAMES}\n]' -- "$candidate_rpm")
done
if [[ -n $candidate_private_python_abi ]]; then
  echo '== private Python ABI preflight =='
  private_interpreter="/usr/bin/python$candidate_private_python_abi"
  [[ -x $private_interpreter ]] || {
    echo "guest lacks the versioned interpreter $private_interpreter required by the candidate payloads" >&2
    echo 'PRIVATE_PYTHON_ABI=FAIL' >&2
    exit 1
  }
  guest_python_abi=$(env -i PATH=/usr/bin:/bin "$private_interpreter" -I -c \
    'import sys; print("%d.%d" % sys.version_info[:2])')
  if [[ $guest_python_abi != "$candidate_private_python_abi" ]]; then
    echo "guest Python ABI mismatch: guest=$guest_python_abi candidates=$candidate_private_python_abi" >&2
    echo 'PRIVATE_PYTHON_ABI=FAIL' >&2
    exit 1
  fi
  python_abi_providers=$(rpm -q --whatprovides 'python(abi)' --qf '%{NAME}\n' 2>/dev/null || :)
  python_abi_provider_found=0
  while IFS= read -r python_abi_provider; do
    [[ -n $python_abi_provider ]] || continue
    if rpm -q --provides "$python_abi_provider" 2>/dev/null |
      grep -Fqx "python(abi) = $candidate_private_python_abi"; then
      python_abi_provider_found=1
      break
    fi
  done < <(printf '%s\n' "$python_abi_providers" | LC_ALL=C sort -u)
  if (( ! python_abi_provider_found )); then
    echo "guest RPM database lacks python(abi) = $candidate_private_python_abi" >&2
    echo 'PRIVATE_PYTHON_ABI=FAIL' >&2
    exit 1
  fi
  echo "PRIVATE_PYTHON_ABI=PASS ($candidate_private_python_abi)"
fi

contains_candidate() {
  local wanted=$1 name
  for name in "${candidate_names[@]}"; do
    [[ $name == "$wanted" ]] && return 0
  done
  return 1
}

# The SGLang CPU transaction is validated as one private runtime closure. A
# partial or augmented candidate set is not a closure: DNF could satisfy the
# missing pieces from an installed package or an unrelated repository. Keep the
# allowlist explicit so a newly named or accelerator package cannot reach the
# install/import/smoke stages by matching a broad prefix.
required_cpu_candidates=(
  python-torch-sglang-2.14
  python-torchaudio-2.11
  python-torchvision-0.29
  python-mistral-common-1.12
  python-click-sglang-8.4
  python-transformers-sglang-5.19
  python-tokenizers-sglang-0.23
  python-huggingface-hub-sglang-1.31
  python-xgrammar-0.2
  python-llguidance-1.7
  python-apache-tvm-ffi-0.1
  python-grpcio-sglang-1.84
  python-grpcio-health-checking-sglang-1.84
  python-grpcio-reflection-sglang-1.84
  python-smg-grpc-proto
  python-smg-grpc-servicer
  python-triton-sglang-3.8
  python-sglang-kernel-cpu
  python-sglang
  python-torchcodec-sglang-0.12
)
# These packages are valid optional providers used by the generated gRPC
# tooling/status modules. They are allowed when staged, but are not required
# by the SGLang CPU runtime dependency graph.
allowed_cpu_candidates=(
  "${required_cpu_candidates[@]}"
  python-grpcio-tools-sglang-1.84
  python-grpcio-status-sglang-1.84
)
private_runtime_candidate=0
for candidate_name in "${candidate_names[@]}"; do
  for required_candidate in "${required_cpu_candidates[@]}"; do
    [[ $candidate_name == "$required_candidate" ]] || continue
    private_runtime_candidate=1
    break 2
  done
done
if (( ! private_runtime_candidate )); then
  for candidate_rpm in "${candidate_files[@]}"; do
    while IFS= read -r capability; do
      if [[ $capability == sglang\(python3dist\(*\)\)* ]]; then
        private_runtime_candidate=1
        break 2
      fi
    done < <(rpm -qp --provides -- "$candidate_rpm")
  done
fi
cpu_closure_complete=0
if (( private_runtime_candidate )); then
  missing_cpu_candidates=()
  unexpected_cpu_candidates=()
  for required_candidate in "${required_cpu_candidates[@]}"; do
    contains_candidate "$required_candidate" || missing_cpu_candidates+=("$required_candidate")
  done
  for candidate_name in "${candidate_names[@]}"; do
    candidate_is_allowed=0
    for allowed_candidate in "${allowed_cpu_candidates[@]}"; do
      [[ $candidate_name == "$allowed_candidate" ]] || continue
      candidate_is_allowed=1
      break
    done
    (( candidate_is_allowed )) || unexpected_cpu_candidates+=("$candidate_name")
  done
  if ((${#missing_cpu_candidates[@]} > 0 || ${#unexpected_cpu_candidates[@]} > 0)); then
    if ((${#missing_cpu_candidates[@]} > 0)); then
      printf 'missing CPU SGLang RPM candidate: %s\n' "${missing_cpu_candidates[@]}" >&2
    fi
    if ((${#unexpected_cpu_candidates[@]} > 0)); then
      printf 'unexpected CPU SGLang RPM candidate: %s\n' "${unexpected_cpu_candidates[@]}" >&2
    fi
    echo 'CPU_SGLANG_CLOSURE=FAIL' >&2
    exit 2
  fi

  # No later stage may be reached unless the complete allowlisted set is present.
  cpu_closure_complete=1

  # Resolve the private Python capability graph from candidate RPM metadata
  # alone. DNF can see already-installed packages, so its transaction result
  # cannot establish that this candidate set contains the complete closure.
  candidate_private_provides=()
  candidate_private_requires=()
  for candidate_rpm in "${candidate_files[@]}"; do
    while IFS= read -r capability; do
      [[ $capability == sglang\(* ]] && candidate_private_provides+=("$capability")
    done < <(rpm -qp --provides -- "$candidate_rpm")
    while IFS= read -r capability; do
      [[ $capability == *sglang\(* ]] && candidate_private_requires+=("$capability")
    done < <(rpm -qp --requires -- "$candidate_rpm")
  done
  missing_private_capabilities=()
  unverified_private_capabilities=()
  rpm_vercmp() {
    local left=$1 right=$2 result
    # RPM version strings cannot contain Lua string delimiters or code syntax.
    [[ $left =~ ^[A-Za-z0-9._+~^:-]+$ && $right =~ ^[A-Za-z0-9._+~^:-]+$ ]] || return 2
    result=$(rpm --eval "%{lua:print(rpm.vercmp(\"$left\", \"$right\"))}") || return 2
    [[ $result =~ ^-?[0-9]+$ ]] || return 2
    printf '%s\n' "$result"
  }

  private_requirement_satisfied() {
    local requirement=$1 requirement_name operator required_version
    local provided_capability provided_name provided_version comparison
    local versioned=0
    if [[ $requirement =~ ^(sglang\([^[:space:]]+\))[[:space:]]+(=|\>=|\>|\<=|\<)[[:space:]]+([A-Za-z0-9._+~^:-]+)$ ]]; then
      requirement_name=${BASH_REMATCH[1]}
      operator=${BASH_REMATCH[2]}
      required_version=${BASH_REMATCH[3]}
      versioned=1
    elif [[ $requirement =~ ^sglang\([^[:space:]]+\)$ ]]; then
      requirement_name=$requirement
    else
      return 2
    fi

    for provided_capability in "${candidate_private_provides[@]}"; do
      if [[ $provided_capability =~ ^(sglang\([^[:space:]]+\))[[:space:]]+=[[:space:]]+([A-Za-z0-9._+~^:-]+)$ ]]; then
        provided_name=${BASH_REMATCH[1]}
        provided_version=${BASH_REMATCH[2]}
      elif [[ $provided_capability =~ ^sglang\([^[:space:]]+\)$ ]]; then
        provided_name=$provided_capability
        provided_version=
      else
        continue
      fi
      [[ $provided_name == "$requirement_name" ]] || continue
      if (( ! versioned )); then return 0; fi
      [[ -n $provided_version ]] || continue
      comparison=$(rpm_vercmp "$provided_version" "$required_version") || return 2
      case $operator in
        '=')  (( comparison == 0 )) && return 0 ;;
        '>=') (( comparison >= 0 )) && return 0 ;;
        '>')  (( comparison > 0 )) && return 0 ;;
        '<=') (( comparison <= 0 )) && return 0 ;;
        '<')  (( comparison < 0 )) && return 0 ;;
      esac
    done
    return 1
  }

  for required_capability in "${candidate_private_requires[@]}"; do
    [[ -n $required_capability ]] || continue
    if [[ $required_capability != *sglang\(* ]]; then continue; fi
    if private_requirement_satisfied "$required_capability"; then
      continue
    else
      result=$?
    fi
    if (( result == 2 )); then
      unverified_private_capabilities+=("$required_capability")
    else
      missing_private_capabilities+=("$required_capability")
    fi
  done
  if ((${#unverified_private_capabilities[@]} > 0)); then
    printf 'UNVERIFIED private requirement expression: %s\n' \
      "${unverified_private_capabilities[@]}" >&2
  fi
  if ((${#missing_private_capabilities[@]} > 0 || ${#unverified_private_capabilities[@]} > 0)); then
    if ((${#missing_private_capabilities[@]} > 0)); then
      printf 'missing candidate provider for private requirement: %s\n' \
        "${missing_private_capabilities[@]}" >&2
    fi
    echo 'CPU_SGLANG_CLOSURE=FAIL' >&2
    exit 2
  fi
  echo 'CPU_SGLANG_CLOSURE=PASS (all required candidates and private capability providers supplied)'
fi

metadata_failure=0
assert_metadata_line() {
  local rpm=$1 field=$2 expected=$3
  if ! rpm -qp "--$field" -- "$rpm" | grep -Fqx -- "$expected"; then
    echo "metadata mismatch: $(basename "$rpm") $field lacks: $expected" >&2
    metadata_failure=1
  fi
}

assert_metadata_line_any() {
  local rpm=$1 field=$2 line expected
  shift 2
  while IFS= read -r line; do
    for expected in "$@"; do
      [[ $line == "$expected" ]] && return 0
    done
  done < <(rpm -qp "--$field" -- "$rpm")
  echo "metadata mismatch: $(basename "$rpm") $field lacks one of: $*" >&2
  metadata_failure=1
}

assert_metadata_absent_prefix() {
  local rpm=$1 field=$2 forbidden_prefix=$3 line
  while IFS= read -r line; do
    [[ $line == "$forbidden_prefix"* ]] || continue
    echo "metadata mismatch: $(basename "$rpm") $field contains forbidden legacy capability prefix: $forbidden_prefix" >&2
    metadata_failure=1
    return 0
  done < <(rpm -qp "--$field" -- "$rpm")
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
    PYTHONNOUSERSITE=1 PYTHONSAFEPATH=1 python3 -s - <<'PY'
import importlib
import importlib.metadata
from pathlib import Path

shared_baseline = {
    "transformers": ("transformers", "5.12.1"),
    "tokenizers": ("tokenizers", "0.22.2"),
    "huggingface_hub": ("huggingface-hub", "1.16.0"),
    "timm": ("timm", "1.0.28"),
}
sglang_roots = (Path("/usr/lib/sglang").resolve(), Path("/usr/lib64/sglang").resolve())

def is_sglang_path(path):
    resolved = Path(path).resolve()
    return any(resolved == root or root in resolved.parents for root in sglang_roots)

for name in ("torch", "torchaudio", "torchvision", "tokenizers", "transformers", "timm", "sglang", "triton", "torchcodec"):
    try:
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve() if getattr(module, "__file__", None) else "<none>"
        if name in shared_baseline:
            distribution, expected = shared_baseline[name]
            actual = importlib.metadata.version(distribution)
            if actual != expected:
                raise RuntimeError(f"{name} system version mismatch: expected {expected}, got {actual}")
            module_paths = [getattr(module, "__file__", None), *getattr(module, "__path__", ())]
            distribution_path = importlib.metadata.distribution(distribution).locate_file("")
            if any(item and is_sglang_path(item) for item in [*module_paths, distribution_path]):
                raise RuntimeError(f"{name} system import resolved inside the SGLang tree")
        print(f"{name}\t{getattr(module, '__version__', '<none>')}\t{path}")
    except BaseException as exc:
        print(f"{name}\tERROR:{type(exc).__name__}")
        if name in shared_baseline:
            raise
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
if (( install )) && [[ -z $gpg_key || -z $gpg_fingerprint ]]; then
  echo 'signed installation requires --gpg-key and --gpg-fingerprint' >&2
  exit 1
fi
if [[ -n $gpg_key && -z $gpg_fingerprint ]]; then
  echo 'RPM signature validation requires an independently supplied --gpg-fingerprint' >&2
  exit 1
fi
if [[ -n $gpg_key ]]; then
  [[ -f $gpg_key ]] || { echo "missing RPM GPG key: $gpg_key" >&2; exit 1; }
  command -v gpg >/dev/null || { echo 'gpg is required for RPM key fingerprint verification' >&2; exit 1; }
  key_listing=$(gpg --batch --show-keys --with-colons "$gpg_key") || {
    echo "cannot read public key from $gpg_key" >&2
    exit 1
  }
  primary_key_count=$(printf '%s\n' "$key_listing" | awk -F: '$1 == "pub" { count++ } END { print count + 0 }')
  [[ $primary_key_count == 1 ]] || {
    echo "expected exactly one primary public key in $gpg_key; found $primary_key_count" >&2
    exit 1
  }
  imported_fingerprint=$(printf '%s\n' "$key_listing" |
    awk -F: '$1 == "pub" { in_primary = 1; next } $1 == "sub" { in_primary = 0 } in_primary && $1 == "fpr" { print toupper($10); exit }')
  [[ $imported_fingerprint =~ ^([A-F0-9]{40}|[A-F0-9]{64})$ ]] || {
    echo "cannot read a complete primary-key fingerprint from $gpg_key" >&2
    exit 1
  }
  expected_fingerprint=$(LC_ALL=C printf '%s' "$gpg_fingerprint" | LC_ALL=C tr '[:lower:]' '[:upper:]')
  [[ $expected_fingerprint =~ ^([A-F0-9]{40}|[A-F0-9]{64})$ ]] || {
    echo '--gpg-fingerprint must be a complete 40- or 64-hex-digit fingerprint' >&2
    exit 1
  }
  [[ $imported_fingerprint == "$expected_fingerprint" ]] || {
    echo "RPM GPG fingerprint mismatch: $imported_fingerprint (expected $expected_fingerprint)" >&2
    exit 1
  }
  signature_rpmdb="$tmp/signature-rpmdb"
  mkdir -p "$signature_rpmdb"
  rpm --dbpath "$signature_rpmdb" --initdb
  rpm --dbpath "$signature_rpmdb" --import "$gpg_key"
  echo "RPM_GPG_FINGERPRINT=$expected_fingerprint"
  for rpm in "$@"; do rpm --dbpath "$signature_rpmdb" -K --verbose -- "$rpm"; done
  echo 'RPM_SIGNATURE_RESULT=PASS'
else
  echo 'RPM_SIGNATURE_RESULT=SKIPPED (provide --gpg-key and --gpg-fingerprint for signed validation)'
fi

echo '== candidate metadata =='
for rpm in "$@"; do
  echo "-- $rpm"
  rpm -qp --qf 'name=%{NAME} version=%{VERSION}-%{RELEASE} arch=%{ARCH}\n' -- "$rpm"
  echo 'provides:'
  rpm -qp --provides -- "$rpm" | LC_ALL=C sort
  echo 'requires:'
  rpm -qp --requires -- "$rpm" | LC_ALL=C sort

  name=$(rpm -qp --qf '%{NAME}' -- "$rpm")
  version=$(rpm -qp --qf '%{VERSION}' -- "$rpm")
  arch=$(rpm -qp --qf '%{ARCH}' -- "$rpm")
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
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torch-cpu)) = 2.14'
      assert_metadata_line "$rpm" provides 'sglang(libc10.so()(64bit))'
      assert_metadata_line "$rpm" provides 'sglang(libtorch_cpu.so()(64bit))'
      assert_metadata_line "$rpm" requires 'python3dist(typing-extensions) >= 4.10.0'
      # The fixed private ELF generator must not leave the stale wheel3
      # libutf8 capabilities in either side of the Torch metadata contract.
      assert_metadata_absent_prefix "$rpm" provides 'sglang(libutf8_validity.so'
      assert_metadata_absent_prefix "$rpm" provides 'sglang(libutf8_range.so'
      assert_metadata_absent_prefix "$rpm" requires 'sglang(libutf8_validity.so'
      assert_metadata_absent_prefix "$rpm" requires 'sglang(libutf8_range.so'
      ;;
    python-torch-sglang-2.14-rocm)
      [[ $version == 2.14.0 ]] || { echo "unexpected Torch version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torch-rocm)) = 2.14.0'
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torch-rocm)) = 2.14'
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
    python-mistral-common-1.12)
      [[ $version == 1.12.0 ]] || { echo "unexpected Mistral Common version: $version" >&2; metadata_failure=1; }
      assert_metadata_line_any "$rpm" provides \
        'sglang(python3dist(mistral-common)) = 1.12' \
        'sglang(python3dist(mistral-common)) = 1.12.0'
      ;;
    python-click-sglang-8.4)
      [[ $version == 8.4.2 ]] || { echo "unexpected Click version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(click)) = 8.4.2'
      ;;
    python-transformers-sglang-5.19)
      [[ $version == 5.19.0 ]] || { echo "unexpected Transformers version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(transformers)) = 5.19'
      ;;
    python-tokenizers-sglang-0.23)
      [[ $version == 0.23.2 ]] || { echo "unexpected Tokenizers version: $version" >&2; metadata_failure=1; }
      assert_metadata_line_any "$rpm" provides \
        'sglang(python3dist(tokenizers)) = 0.23' \
        'sglang(python3dist(tokenizers)) = 0.23.2'
      ;;
    python-huggingface-hub-sglang-1.31)
      [[ $version == 1.31.0 ]] || { echo "unexpected Hugging Face Hub version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(huggingface-hub)) = 1.31.0'
      ;;
    python-xgrammar-0.2)
      [[ $version == 0.2.7 ]] || { echo "unexpected XGrammar version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(xgrammar)) = 0.2.7'
      ;;
    python-llguidance-1.7)
      [[ $version == 1.7.6 ]] || { echo "unexpected LLGuidance version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(llguidance)) = 1.7.6'
      ;;
    python-apache-tvm-ffi-0.1)
      [[ $version == 0.1.11 ]] || { echo "unexpected TVM FFI version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(apache-tvm-ffi)) = 0.1.11'
      ;;
    python-grpcio-sglang-1.84)
      [[ $version == 1.84.0 ]] || { echo "unexpected gRPC version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(grpcio)) = 1.84.0'
      ;;
    python-grpcio-tools-sglang-1.84)
      [[ $version == 1.84.0 ]] || { echo "unexpected grpcio-tools version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(grpcio-tools)) = 1.84.0'
      ;;
    python-grpcio-health-checking-sglang-1.84)
      [[ $version == 1.84.0 ]] || { echo "unexpected grpcio-health-checking version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(grpcio-health-checking)) = 1.84.0'
      ;;
    python-grpcio-reflection-sglang-1.84)
      [[ $version == 1.84.0 ]] || { echo "unexpected grpcio-reflection version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(grpcio-reflection)) = 1.84.0'
      ;;
    python-grpcio-status-sglang-1.84)
      [[ $version == 1.84.0 ]] || { echo "unexpected grpcio-status version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(grpcio-status)) = 1.84.0'
      ;;
    python-smg-grpc-proto)
      [[ $version == 0.4.22 ]] || { echo "unexpected SMG gRPC proto version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(smg-grpc-proto)) = 0.4.22'
      ;;
    python-smg-grpc-servicer)
      [[ $version == 0.9.1 ]] || { echo "unexpected SMG gRPC servicer version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(smg-grpc-servicer)) = 0.9.1'
      ;;
    python-sglang)
      [[ $version == 0.5.21 ]] || { echo "unexpected SGLang version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" requires 'sglang(python3dist(torch-cpu)) = 2.14.0'
      assert_metadata_line "$rpm" requires 'sglang(python3dist(transformers)) = 5.19'
      assert_metadata_line "$rpm" requires 'python3dist(timm) = 1.0.28'
      ;;
    python-sglang-kernel-cpu)
      [[ $version == 0.4.7 ]] || { echo "unexpected SGLang CPU kernel version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(sglang-kernel-cpu)) = 0.4.7'
      assert_metadata_line "$rpm" provides 'sglang(python3dist(sglang-kernel)) = 0.4.7'
      assert_metadata_line "$rpm" requires 'sglang(python3dist(torch-cpu)) = 2.14.0'
      ;;
    python-triton-sglang-3.8)
      [[ $version == 3.8.0 ]] || { echo "unexpected Triton version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(triton)) = 3.8.0'
      ;;
    python-torchcodec-sglang-0.12)
      [[ $version == 0.12.0 ]] || { echo "unexpected TorchCodec version: $version" >&2; metadata_failure=1; }
      assert_metadata_line "$rpm" provides 'sglang(python3dist(torchcodec)) = 0.12.0'
      assert_metadata_line "$rpm" requires 'sglang(python3dist(torch-cpu)) = 2.14.0'
      ;;
    *)
      echo "unknown candidate package for metadata validation: $name" >&2
      metadata_failure=1
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
  if rpm -qp --requires -- "$rpm" | grep -Fq 'rpmlib(ShortCircuited)'; then
    echo "ShortCircuited: PRESENT in $rpm" >&2
    echo 'SHORTCIRCUITED_RESULT=FAIL' >&2
    exit 1
  fi
done
echo 'ShortCircuited: ABSENT'
echo 'SHORTCIRCUITED_RESULT=PASS'

if (( ! cpu_closure_complete )); then
  echo 'CPU_SGLANG_CLOSURE=SKIPPED (candidate set is not a complete private CPU closure)' >&2
  echo 'HARNESS_RESULT=SKIPPED (no install/import/smoke without complete CPU closure)' >&2
  exit "$EX_SKIP"
fi

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
  # Candidate signatures were verified against the isolated key database
  # above. Keep the read-only dependency preview from importing keys into the
  # guest RPM database; the trusted key is imported immediately before install.
  dnf_preview_args=(--assumeyes --setopt=tsflags=test "${dnf_args[@]}" --setopt=openruyi-qemu-local.gpgcheck=0)
  set +e
  dnf "${dnf_preview_args[@]}" install "${candidate_paths[@]/#/$repo_dir/}"
  dnf_rc=$?
  set -e
  echo "DNF_OFFLINE_RC=$dnf_rc"
  if (( dnf_rc != 0 )); then
    echo 'DNF_OFFLINE_RESULT=FAIL' >&2
    exit "$dnf_rc"
  fi
  echo 'DNF_OFFLINE_RESULT=PASS (offline DNF transaction preview)'
elif [[ -z $gpg_key ]]; then
  echo 'DNF_OFFLINE_RESULT=SKIPPED (signed RPM key unavailable; scratch mode)'
elif ! command -v createrepo_c >/dev/null || ! command -v dnf >/dev/null; then
  echo 'DNF_OFFLINE_RESULT=SKIPPED (createrepo_c or dnf unavailable)'
else
  createrepo_c --quiet "$repo_dir"
  dnf_preview_args=(--assumeyes --setopt=tsflags=test "${dnf_args[@]}" --setopt=openruyi-qemu-local.gpgcheck=0)
  set +e
  dnf "${dnf_preview_args[@]}" install "${candidate_paths[@]/#/$repo_dir/}"
  dnf_rc=$?
  set -e
  echo "DNF_OFFLINE_RC=$dnf_rc"
  if (( dnf_rc != 0 )); then
    echo 'DNF_OFFLINE_RESULT=FAIL' >&2
    exit "$dnf_rc"
  fi
  echo 'DNF_OFFLINE_RESULT=PASS (offline DNF transaction preview)'
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
    if [[ $(rpm -qp --qf '%{NAME}' -- "$rpm") == python-sglang ]]; then
      sglang_rpm=$rpm
      sglang_count=$((sglang_count + 1))
    fi
  done
  (( sglang_count == 1 )) || {
    echo "expected one python-sglang candidate, found $sglang_count" >&2
    exit 1
  }
  rpm -qp --qf '[%{FILENAMES}\n]' -- "$sglang_rpm" | grep -Fqx -- "$coexistence_script" || {
    echo "candidate python-sglang does not own helper $coexistence_script" >&2
    exit 1
  }
  rpm -qp --qf '[%{FILENAMES}\n]' -- "$sglang_rpm" | grep -Fqx -- "$cpu_smoke_script" || {
    echo "candidate python-sglang does not own helper $cpu_smoke_script" >&2
    exit 1
  }
  (cd "$validation_root" && rpm2cpio "$sglang_rpm" | cpio -idm --quiet)
  preinstall_coexistence_script="$validation_root$coexistence_script"
  preinstall_cpu_smoke_script="$validation_root$cpu_smoke_script"
  [[ -f $preinstall_coexistence_script && -x $preinstall_coexistence_script ]] || {
    echo "COEXISTENCE=FAIL (missing candidate helper $preinstall_coexistence_script)" >&2
    exit 1
  }
  [[ -f $preinstall_cpu_smoke_script && -x $preinstall_cpu_smoke_script ]] || {
    echo "CPU_ENGINE_SMOKE=FAIL (missing candidate helper $preinstall_cpu_smoke_script)" >&2
    exit 1
  }
  python3 -s "$preinstall_coexistence_script" --baseline-json "$coexistence_baseline" --snapshot
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
  rpm -Uvh "${rpm_signature_args[@]}" --replacepkgs --test -- "$@"
  test_rc=$?
  set -e
  echo "RPM_TEST_RC=$test_rc"
  if (( test_rc != 0 )); then
    echo 'RPM_TRANSACTION_TEST=FAIL' >&2
    echo "HARNESS_RESULT=FAIL test_rc=$test_rc install=$install"
    exit "$test_rc"
  fi
  echo 'RPM_TRANSACTION_TEST=PASS'
fi

if (( install )); then
  echo '== install transaction =='
  (( dnf_ready )) || { echo 'DNF transaction was not prepared' >&2; exit 1; }
  # Import only after all pre-install checks have passed, immediately before
  # DNF performs the explicit mutating transaction.
  rpm --import "$gpg_key"
  dnf --assumeyes "${dnf_args[@]}" install "${candidate_paths[@]/#/$repo_dir/}"
  echo 'DNF_INSTALL_RESULT=PASS'
  echo '== verify installed packages =='
  for rpm in "$@"; do
    name=$(rpm -qp --qf '%{NAME}' -- "$rpm")
    expected_nevra=$(rpm -qp --qf '%{NAME}-%{EPOCHNUM}:%{VERSION}-%{RELEASE}.%{ARCH}' -- "$rpm")
    installed_nevra=$(rpm -q --qf '%{NAME}-%{EPOCHNUM}:%{VERSION}-%{RELEASE}.%{ARCH}\n' "$name" |
      LC_ALL=C sort)
    [[ $installed_nevra == "$expected_nevra" ]] || {
      echo "installed NEVRA mismatch for $name: $installed_nevra (expected $expected_nevra)" >&2
      exit 1
    }
    rpm -V "$name"
  done
  echo 'INSTALL_VERIFY=PASS'
  echo 'DNF_INSTALL_TRANSACTION_VERIFY=PASS (DNF completed and every candidate NEVRA is installed)'
  if contains_candidate python-sglang; then
    installed_helper_owner=$(rpm -qf --qf '%{NAME}\n' -- "$coexistence_script" 2>/dev/null) || {
      echo "installed coexistence helper is not RPM-owned: $coexistence_script" >&2
      exit 1
    }
    [[ $installed_helper_owner == python-sglang ]] || {
      echo "installed coexistence helper owner mismatch: $installed_helper_owner" >&2
      exit 1
    }
    installed_helper_owner=$(rpm -qf --qf '%{NAME}\n' -- "$cpu_smoke_script" 2>/dev/null) || {
      echo "installed CPU smoke helper is not RPM-owned: $cpu_smoke_script" >&2
      exit 1
    }
    [[ $installed_helper_owner == python-sglang ]] || {
      echo "installed CPU smoke helper owner mismatch: $installed_helper_owner" >&2
      exit 1
    }
  fi
  if contains_candidate python-sglang-kernel-cpu; then
    installed_helper_owner=$(rpm -qf --qf '%{NAME}\n' -- "$kernel_smoke_script" 2>/dev/null) || {
      echo "installed kernel smoke helper is not RPM-owned: $kernel_smoke_script" >&2
      exit 1
    }
    [[ $installed_helper_owner == python-sglang-kernel-cpu ]] || {
      echo "installed kernel smoke helper owner mismatch: $installed_helper_owner" >&2
      exit 1
    }
  fi
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
  # Candidate packages are expected to be added or replaced.  Every other
  # installed NEVRA must remain identical so a private transaction cannot
  # silently upgrade or remove an existing system package.
  candidate_names_file="$tmp/candidate-names.txt"
  printf '%s\n' "${candidate_names[@]}" | LC_ALL=C sort -u > "$candidate_names_file"
  awk -F '\t' 'NR == FNR { names[$1] = 1; next } !names[$1]' \
    "$candidate_names_file" "$tmp/rpm-before.txt" | LC_ALL=C sort > "$tmp/rpm-before-system.txt"
  awk -F '\t' 'NR == FNR { names[$1] = 1; next } !names[$1]' \
    "$candidate_names_file" "$tmp/rpm-after.txt" | LC_ALL=C sort > "$tmp/rpm-after-system.txt"
  removed_rpms=$(comm -23 "$tmp/rpm-before-system.txt" "$tmp/rpm-after-system.txt")
  if [[ -n $removed_rpms ]]; then
    echo 'RPM_BASELINE=REMOVED' >&2
    printf '%s\n' "$removed_rpms" >&2
    exit 1
  fi
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
  echo "HARNESS_RESULT=SKIPPED test_rc=$test_rc install=$install"
  exit "$EX_SKIP"
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
      python-click-sglang-8.4) expected_modules+="click," ;;
      python-mistral-common-1.12) expected_modules+="mistral_common," ;;
      python-xgrammar-0.2) expected_modules+="xgrammar," ;;
      python-llguidance-1.7) expected_modules+="llguidance," ;;
      python-apache-tvm-ffi-0.1) expected_modules+="tvm_ffi," ;;
      python-grpcio-sglang-1.84) expected_modules+="grpc," ;;
      python-grpcio-tools-sglang-1.84) expected_modules+="grpc_tools," ;;
      python-grpcio-health-checking-sglang-1.84) expected_modules+="grpc_health,grpc_health.v1.health_pb2," ;;
      python-grpcio-reflection-sglang-1.84) expected_modules+="grpc_reflection,grpc_reflection.v1alpha.reflection," ;;
      python-grpcio-status-sglang-1.84) expected_modules+="grpc_status,grpc_status.rpc_status," ;;
      python-smg-grpc-proto) expected_modules+="smg_grpc_proto,smg_grpc_proto.generated.common_pb2,smg_grpc_proto.generated.sglang_scheduler_pb2,smg_grpc_proto.generated.sglang_scheduler_pb2_grpc,smg_grpc_proto.generated.tokenspeed_scheduler_pb2,smg_grpc_proto.generated.vllm_engine_pb2_grpc," ;;
      python-smg-grpc-servicer) expected_modules+="smg_grpc_servicer," ;;
      python-sglang) expected_modules+="sglang," ;;
      python-transformers-sglang-5.19) expected_modules+="transformers," ;;
      python-tokenizers-sglang-0.23) expected_modules+="tokenizers," ;;
      python-huggingface-hub-sglang-1.31) expected_modules+="huggingface_hub," ;;
      python-sglang-kernel-cpu) expected_modules+="sgl_kernel," ;;
      python-triton-sglang-3.8) expected_modules+="triton," ;;
      python-torchcodec-sglang-0.12) expected_modules+="torchcodec," ;;
    esac
  done
  expected_modules=${expected_modules%,}
  [[ -n $expected_modules ]] || {
    echo "private site has no expected module mapping for candidate RPMs" >&2
    echo 'PRIVATE_IMPORT=FAIL' >&2
    exit 1
  }
  private_python=${SGLANG_PRIVATE_PYTHON:-}
  if [[ -z $private_python ]]; then
    if [[ -x /usr/bin/sglang-python ]]; then
      private_python=/usr/bin/sglang-python
    else
      private_python_version=${private_site%/site-packages}
      private_python_version=${private_python_version##*/}
      private_python=/usr/bin/$private_python_version
    fi
  fi
  if [[ $private_python != /* || ! -x $private_python ]]; then
    echo "private Python interpreter is unavailable: $private_python" >&2
    exit 1
  fi
  private_python_launcher=0
  [[ $private_python == /usr/bin/sglang-python ]] && private_python_launcher=1
  run_private_python() {
    if (( private_python_launcher )); then
      PYTHONNOUSERSITE=1 "$private_python" "$@"
    else
      env -u PYTHONHOME -u PYTHONPATH -u LD_LIBRARY_PATH -u LD_PRELOAD \
        PYTHONNOUSERSITE=1 PYTHONSAFEPATH=1 PYTHONPATH="$private_site" \
        "$private_python" -sP "$@"
    fi
  }
  SGLANG_EXPECTED_MODULES="$expected_modules" \
  SGLANG_CANDIDATE_NAMES="$(printf '%s\n' "${candidate_names[@]}")" \
  SGLANG_EXPECTED_PYTHON_VERSION="${private_site%/site-packages}" \
    run_private_python - "$private_site" <<'PY'
import importlib
import importlib.metadata
import os
import re
import subprocess
import sys
from pathlib import Path

private = Path(sys.argv[1]).resolve()
private_profile = private.parents[1]
sglang_root = private_profile.parent
expected_python = Path(os.environ["SGLANG_EXPECTED_PYTHON_VERSION"]).name.removeprefix("python")
actual_python = f"{sys.version_info.major}.{sys.version_info.minor}"
if actual_python != expected_python:
    raise RuntimeError(
        f"private interpreter ABI mismatch: expected Python {expected_python}, got {actual_python}"
    )
names = tuple(name for name in os.environ.get("SGLANG_EXPECTED_MODULES", "").split(",") if name)
candidate_names = frozenset(name for name in os.environ.get("SGLANG_CANDIDATE_NAMES", "").splitlines() if name)
required = {
    "torch": ("torch", "2.14.0"),
    "torchaudio": ("torchaudio", "2.11.0"),
    "torchvision": ("torchvision", "0.29.0"),
    "click": ("click", "8.4.2"),
    "transformers": ("transformers", "5.19.0"),
    "tokenizers": ("tokenizers", "0.23.2"),
    "huggingface_hub": ("huggingface-hub", "1.31.0"),
    "mistral_common": ("mistral-common", "1.12.0"),
    "xgrammar": ("xgrammar", "0.2.7"),
    "llguidance": ("llguidance", "1.7.6"),
    "tvm_ffi": ("apache-tvm-ffi", "0.1.11"),
    "grpc": ("grpcio", "1.84.0"),
    "grpc_tools": ("grpcio-tools", "1.84.0"),
    "grpc_health": ("grpcio-health-checking", "1.84.0"),
    "grpc_health.v1.health_pb2": ("grpcio-health-checking", "1.84.0"),
    "grpc_reflection": ("grpcio-reflection", "1.84.0"),
    "grpc_reflection.v1alpha.reflection": ("grpcio-reflection", "1.84.0"),
    "grpc_status": ("grpcio-status", "1.84.0"),
    "grpc_status.rpc_status": ("grpcio-status", "1.84.0"),
    "smg_grpc_proto": ("smg-grpc-proto", "0.4.22"),
    "smg_grpc_proto.generated.common_pb2": ("smg-grpc-proto", "0.4.22"),
    "smg_grpc_proto.generated.sglang_scheduler_pb2": ("smg-grpc-proto", "0.4.22"),
    "smg_grpc_proto.generated.sglang_scheduler_pb2_grpc": ("smg-grpc-proto", "0.4.22"),
    "smg_grpc_proto.generated.tokenspeed_scheduler_pb2": ("smg-grpc-proto", "0.4.22"),
    "smg_grpc_proto.generated.vllm_engine_pb2_grpc": ("smg-grpc-proto", "0.4.22"),
    "smg_grpc_servicer": ("smg-grpc-servicer", "0.9.1"),
    "sglang": ("sglang-cpu", "0.5.21"),
    "sgl_kernel": ("sglang-kernel-cpu", "0.4.7"),
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

shared = {
    "timm": ("timm", "1.0.28"),
}
for name, (distribution, expected_version) in shared.items():
    module = importlib.import_module(name)
    actual_version = importlib.metadata.version(distribution)
    if actual_version != expected_version:
        raise RuntimeError(
            f"{name} version mismatch: expected {expected_version}, got {actual_version}"
        )
    module_paths = [getattr(module, "__file__", None), *getattr(module, "__path__", ())]
    for module_path in module_paths:
        if module_path and (private in Path(module_path).resolve().parents or sglang_root in Path(module_path).resolve().parents):
            raise RuntimeError(f"shared module {name} loaded from private tree: {module_path}")
    distribution_path = Path(importlib.metadata.distribution(distribution).locate_file("")).resolve()
    if private in distribution_path.parents or sglang_root in distribution_path.parents:
        raise RuntimeError(f"shared distribution {distribution} is inside the SGLang tree")
    print(f"IMPORT_SHARED {name}: PASS version={actual_version} path={module_paths[0]}")

for module_name, module in tuple(sys.modules.items()):
    if not module or not module_name.startswith((
        "torch", "torchaudio", "torchvision", "triton", "sgl_kernel", "tvm_ffi",
        "xgrammar", "llguidance", "grpc", "smg_grpc_proto", "smg_grpc_servicer",
    )):
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

# Inspect the files that the dynamic loader actually mapped during import.
# Import paths alone miss transitive private libraries loaded by an extension;
# a mapped private object must remain inside this profile's RPM-owned tree and
# must have an ELF header. System libraries are intentionally outside this
# check and are resolved by normal RPM dependencies.
mapped_private_count = 0
for line in Path("/proc/self/maps").read_text().splitlines():
    fields = line.split()
    if len(fields) < 6:
        continue
    mapped = " ".join(fields[5:])
    if not mapped.startswith("/"):
        continue
    if mapped.endswith(" (deleted)"):
        mapped = mapped.removesuffix(" (deleted)")
    if not re.search(r"\.so(?:\.[0-9]+)*$", Path(mapped).name):
        continue
    resolved = Path(mapped).resolve()
    if sglang_root != resolved and sglang_root not in resolved.parents:
        continue
    mapped_private_count += 1
    owner_result = subprocess.run(
        ["rpm", "-qf", "--qf", "%{NAME}\\n", "--", str(resolved)],
        check=False, capture_output=True, text=True,
    )
    if owner_result.returncode != 0:
        raise RuntimeError(f"mapped private object is not RPM-owned: {resolved}")
    owners = frozenset(line for line in owner_result.stdout.splitlines() if line)
    if not owners or not owners.issubset(candidate_names):
        raise RuntimeError(
            f"mapped private object has unexpected RPM owner(s): {resolved}: {sorted(owners)}"
        )
    with resolved.open("rb") as stream:
        if stream.read(4) != b"\x7fELF":
            raise RuntimeError(f"mapped private object is not ELF: {resolved}")
    if private_profile != resolved and private_profile not in resolved.parents:
        raise RuntimeError(f"mapped private object escaped profile: {resolved}")

if mapped_private_count == 0:
    raise RuntimeError("no private ELF object was mapped during import")

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
  run_private_python - <<'PY'
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
  run_private_python "$tmp/gloo-smoke.py"
else
  echo 'GLOO_SMOKE=SKIPPED (CPU Torch RPM not supplied)'
fi

if contains_candidate python-triton-sglang-3.8; then
  echo '== Triton smoke =='
  run_private_python - <<'PY'
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

if contains_candidate python-torchcodec-sglang-0.12; then
  echo '== TorchCodec smoke =='
  run_private_python - <<'PY'
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
  SGLANG_USE_CPU_ENGINE=1 run_private_python - <<'PY'
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
  run_private_python "$cpu_smoke_script"
  echo 'CPU_ENGINE_SMOKE=PASS'
else
  echo 'SGLANG_SMOKE=SKIPPED (python-sglang RPM not supplied)'
fi

if contains_candidate python-sglang-kernel-cpu; then
  [[ -f $kernel_smoke_script ]] || {
    echo "CPU_KERNEL_SMOKE=FAIL (missing $kernel_smoke_script)" >&2
    exit 1
  }
  echo '== SGLang CPU kernel smoke =='
  SGLANG_KERNEL_SMOKE_TIMEOUT=$kernel_smoke_timeout \
    run_private_python "$kernel_smoke_script"
  echo 'CPU_KERNEL_SMOKE=PASS'
else
  echo 'CPU_KERNEL_SMOKE=SKIPPED (python-sglang-kernel-cpu RPM not supplied)'
fi

echo "HARNESS_RESULT=PASS test_rc=$test_rc install=$install"
exit "$test_rc"

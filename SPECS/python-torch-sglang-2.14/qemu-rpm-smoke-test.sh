#!/usr/bin/env bash
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-License-Identifier: MIT
#
# Install the CPU Torch stack in a riscv64 QEMU guest and exercise native ops.
# Usage: qemu-rpm-smoke-test.sh TORCH_RPM TORCHAUDIO_RPM TORCHVISION_RPM
set -Eeuo pipefail

[ "$#" -eq 3 ] || {
    echo "usage: $0 TORCH_RPM TORCHAUDIO_RPM TORCHVISION_RPM" >&2
    exit 2
}

: "${GUEST_SSH:=root@127.0.0.1}"
: "${GUEST_PORT:=22023}"
: "${GUEST_KEY:=/private/tmp/openruyi-sglang-validation/vm/id_ed25519}"
: "${KNOWN_HOSTS:=/private/tmp/openruyi-sglang-validation/vm/known_hosts}"

ssh_guest() {
    ssh -i "$GUEST_KEY" -o UserKnownHostsFile="$KNOWN_HOSTS" \
        -o StrictHostKeyChecking=no -o ConnectTimeout=10 -p "$GUEST_PORT" \
        "$GUEST_SSH" "$@"
}

remote_dir=/tmp/openruyi-torch-stack-smoke-$$

cleanup() {
    local status=$?
    trap - EXIT HUP INT TERM
    ssh_guest "rm -rf -- '$remote_dir'" || :
    exit "$status"
}

trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
ssh_guest "mkdir -p '$remote_dir'"

scp -i "$GUEST_KEY" -o UserKnownHostsFile="$KNOWN_HOSTS" \
    -o StrictHostKeyChecking=no -P "$GUEST_PORT" "$@" \
    "$GUEST_SSH:$remote_dir/"

ssh_guest bash -s -- "$remote_dir" <<'REMOTE'
set -Eeuo pipefail

remote_dir=$1

system_snapshot() {
    env -i PATH=/usr/bin:/bin HOME=/root LANG=C LC_ALL=C \
        PYTHONNOUSERSITE=1 python3 -s - <<'PY'
import importlib
from pathlib import Path

for name in ("torch", "torchaudio", "torchvision"):
    try:
        module = importlib.import_module(name)
    except BaseException as exc:
        print(f"{name}\tERROR:{type(exc).__name__}")
        continue
    path = getattr(module, "__file__", None)
    resolved = Path(path).resolve() if path else "<none>"
    print(f"{name}\t{getattr(module, '__version__', '<none>')}\t{resolved}")
PY
}

system_baseline=$(system_snapshot)
printf '%s\n' "$system_baseline" > "$remote_dir/system-baseline.txt"

expected_packages=$(printf '%s\n' \
    'python-torch-sglang-2.14 riscv64' \
    'python-torchaudio-2.11 riscv64' \
    'python-torchvision-0.29 riscv64' | LC_ALL=C sort)
actual_packages=$(rpm -qp --qf '%{NAME} %{ARCH}\n' "$remote_dir"/*.rpm | LC_ALL=C sort)
if [[ "$actual_packages" != "$expected_packages" ]]; then
    printf 'unexpected CPU compatibility RPM set:\n%s\n' "$actual_packages" >&2
    exit 1
fi

rpm -Uvh --replacepkgs --test "$remote_dir"/*.rpm
rpm -Uvh --replacepkgs "$remote_dir"/*.rpm

private_site=
for candidate in /usr/lib/sglang/core/python*/site-packages \
                 /usr/lib64/sglang/core/python*/site-packages; do
    [[ -d "$candidate" ]] || continue
    resolved_candidate=$(readlink -f "$candidate")
    [[ -z "$private_site" || "$private_site" == "$resolved_candidate" ]] || {
        echo "multiple SGLang private Python trees found" >&2
        exit 1
    }
    private_site=$resolved_candidate
done
[[ -n "$private_site" ]] || {
    echo "SGLang private CPU Python tree was not installed" >&2
    exit 1
}

private_python() {
    env -i PATH=/usr/bin:/bin HOME=/root LANG=C LC_ALL=C \
        PYTHONNOUSERSITE=1 SGLANG_PRIVATE_SITE="$private_site" \
        PYTHONPATH="$private_site" python3 -s "$@"
}

private_python - <<'PY'
import os
import sys
from pathlib import Path

import torch
import torchaudio
import torchvision

private = Path(os.environ["SGLANG_PRIVATE_SITE"]).resolve()

def assert_private(label, value):
    path = Path(value).resolve()
    assert path == private or private in path.parents, f"{label} escaped {private}: {path}"

assert torch.__version__.split('+', 1)[0] == '2.14.0', torch.__version__
assert torchaudio.__version__.split('+', 1)[0] == '2.11.0', torchaudio.__version__
assert torchvision.__version__.split('+', 1)[0] == '0.29.0', torchvision.__version__

for name, module in (("torch", torch), ("torchaudio", torchaudio), ("torchvision", torchvision)):
    assert_private(f"{name}.__file__", module.__file__)
    for root_name in getattr(module, "__path__", ()):
        root = Path(root_name).resolve()
        assert_private(f"{name}.__path__", root)
        for native in root.rglob("*"):
            if native.is_file() and ".so" in native.name:
                assert_private(f"{name} native", native)

for name, module in tuple(sys.modules.items()):
    if not module or not (name == "torch" or name.startswith(("torch.", "torchaudio.", "torchvision."))):
        continue
    native = getattr(module, "__file__", None)
    if native and ".so" in native:
        assert_private(f"{name} native", native)

x = torch.arange(16, dtype=torch.float32).reshape(4, 4)
expected = torch.tensor(
    [[56, 62, 68, 74], [152, 174, 196, 218],
     [248, 286, 324, 362], [344, 398, 452, 506]],
    dtype=torch.float32,
)
torch.testing.assert_close(x @ x, expected)
waveform = torch.tensor([[0.0, 1.0, 0.0, -1.0]])
assert torchaudio.functional.resample(waveform, 8000, 16000).shape[-1] == 8
boxes = torch.tensor([[0, 0, 10, 10], [1, 1, 11, 11]], dtype=torch.float32)
scores = torch.tensor([0.9, 0.8])
assert torchvision.ops.nms(boxes, scores, 0.5).tolist() == [0]
print(f"private CPU Torch tree: {private}")
print("QEMU RPM private CPU Torch smoke: PASS")
PY

system_after=$(system_snapshot)
if [[ "$system_after" != "$system_baseline" ]]; then
    echo "system Torch baseline changed after private RPM installation" >&2
    diff -u <(printf '%s\n' "$system_baseline") <(printf '%s\n' "$system_after") >&2 || true
    exit 1
fi

rpm -q python-torch-sglang-2.14 python-torchaudio-2.11 python-torchvision-0.29
echo "QEMU RPM system baseline: unchanged"
REMOTE

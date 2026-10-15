#!/bin/sh
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-License-Identifier: MIT
#
# Install the CPU Torch stack in a riscv64 QEMU guest and exercise native ops.
# Usage: qemu-rpm-smoke-test.sh TORCH_RPM TORCHAUDIO_RPM TORCHVISION_RPM
set -eu

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
ssh_guest "mkdir -p '$remote_dir'"
trap 'ssh_guest "rm -rf $remote_dir"' EXIT

scp -i "$GUEST_KEY" -o UserKnownHostsFile="$KNOWN_HOSTS" \
    -o StrictHostKeyChecking=no -P "$GUEST_PORT" "$@" \
    "$GUEST_SSH:$remote_dir/"

ssh_guest "set -eu
rpm -Uvh --replacepkgs '$remote_dir'/*.rpm
python3 - <<'PY'
import torch
import torchaudio
import torchvision

assert torch.__version__.split('+', 1)[0] == '2.14.0', torch.__version__
assert torchaudio.__version__.split('+', 1)[0] == '2.11.0', torchaudio.__version__
assert torchvision.__version__.split('+', 1)[0] == '0.29.0', torchvision.__version__

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
print('QEMU RPM install/import smoke: PASS')
PY
rpm -q python-torch python-torchaudio python-torchvision
"

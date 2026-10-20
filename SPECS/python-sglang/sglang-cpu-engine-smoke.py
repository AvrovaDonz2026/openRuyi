#!/usr/bin/python3
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0
"""Offline, post-install smoke test for the SGLang CPU engine on riscv64.

This exercises the CPU engine only. It does not validate CUDA or ROCm
availability, kernels, or device runtime behavior.
"""

import argparse
import json
import math
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request_json(url, payload=None, timeout=5):
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(url, data=data, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return response.status, json.loads(response.read()) if data else None


def make_fixture(root, timeout, python_command=None):
    vocab = {"<pad>": 0, "<bos>": 1, "<eos>": 2, "<unk>": 3}
    vocab.update({f"token{i}": i + 4 for i in range(28)})
    config = {
        "architectures": ["LlamaForCausalLM"],
        "model_type": "llama",
        "torch_dtype": "float32",
        "vocab_size": 32,
        "hidden_size": 32,
        "intermediate_size": 64,
        "num_hidden_layers": 1,
        "num_attention_heads": 4,
        "num_key_value_heads": 4,
        "max_position_embeddings": 128,
        "bos_token_id": vocab["<bos>"],
        "eos_token_id": vocab["<eos>"],
        "pad_token_id": 0,
    }
    (root / "config.json").write_text(json.dumps(config), encoding="utf-8")
    # Build a self-contained tokenizer with the installed tokenizers package.
    code = """
from pathlib import Path
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.decoders import WordPiece
import json, sys
root = Path(sys.argv[1])
vocab = {"<pad>": 0, "<bos>": 1, "<eos>": 2, "<unk>": 3}
vocab.update({f"token{i}": i + 4 for i in range(28)})
tok = Tokenizer(WordLevel(vocab, unk_token="<unk>"))
tok.pre_tokenizer = Whitespace()
tok.decoder = WordPiece(prefix="##")
tok.save(str(root / "tokenizer.json"))
(root / "tokenizer_config.json").write_text(json.dumps({
    "tokenizer_class": "PreTrainedTokenizerFast",
    "bos_token": "<bos>", "eos_token": "<eos>", "unk_token": "<unk>",
    "pad_token": "<pad>"
}), encoding="utf-8")
"""
    python_command = python_command or os.environ.get(
        "SGLANG_SMOKE_PYTHON", "/usr/bin/sglang-python"
    )
    subprocess.run(
        [python_command, "-c", code, str(root)],
        check=True,
        timeout=timeout,
    )


def terminate(process, timeout=5):
    if process is None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    if process.poll() is None:
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    if process.poll() is None:
        process.wait(timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=600.0)
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be a finite value greater than zero")
    started = time.monotonic()
    deadline = started + args.timeout
    port = free_port()
    process = None
    passed = False
    with tempfile.TemporaryDirectory(prefix="sglang-cpu-smoke-") as directory:
        model = Path(directory) / "model"
        model.mkdir()
        fixture_timeout = min(120.0, deadline - time.monotonic())
        if fixture_timeout <= 0:
            raise RuntimeError(f"smoke test exceeded its {args.timeout:g}s timeout")
        make_fixture(model, timeout=fixture_timeout)
        log_path = Path(directory) / "server.log"
        env = os.environ.copy()
        env.update({
            "SGLANG_USE_CPU_ENGINE": "1",
            "HF_HUB_OFFLINE": "1",
            "HF_DATASETS_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "HF_HUB_DISABLE_TELEMETRY": "1",
            "OMP_NUM_THREADS": "1",
            "TOKENIZERS_PARALLELISM": "false",
        })
        command = [
            os.environ.get("SGLANG_SMOKE_SERVER", "/usr/bin/sglang"),
            "serve", "--model-path", str(model),
            "--load-format", "dummy", "--device", "cpu",
            "--attention-backend", "torch_native", "--tp-size", "1",
            "--dtype", "float32", "--disable-overlap-schedule",
            "--max-total-tokens", "128",
            "--host", "127.0.0.1", "--port", str(port),
        ]
        with log_path.open("w", encoding="utf-8") as log:
            try:
                process = subprocess.Popen(
                    command, env=env, stdout=log, stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                base = f"http://127.0.0.1:{port}"
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        tail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:]
                        raise RuntimeError(
                            f"server exited with status {process.returncode}\n{tail}"
                        )
                    try:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            break
                        status, _ = request_json(
                            base + "/health", timeout=min(3.0, remaining)
                        )
                        if status == 200:
                            break
                    except (HTTPError, URLError, TimeoutError, OSError):
                        pass
                    time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))
                else:
                    raise RuntimeError(f"server did not become healthy within {args.timeout:g}s")

                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise RuntimeError(f"server did not become healthy within {args.timeout:g}s")
                status, response = request_json(
                    base + "/generate",
                    {"input_ids": [4, 5], "sampling_params": {
                        "temperature": 0.0, "max_new_tokens": 1}},
                    timeout=min(120.0, remaining),
                )
                if status != 200 or not isinstance(response, dict):
                    raise RuntimeError(f"unexpected /generate response: {status} {response!r}")
                output_ids = response.get("output_ids")
                if not output_ids or not isinstance(output_ids, list):
                    raise RuntimeError(f"/generate returned no token output: {response!r}")
                if process.poll() is not None:
                    tail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:]
                    raise RuntimeError(
                        f"server crashed after generation: {process.returncode}\n{tail}"
                    )
                passed = True
                print("sglang CPU engine offline smoke: PASS")
            finally:
                terminate(process)
                if not passed:
                    print("SGLang server log tail:", file=sys.stderr)
                    print(log_path.read_text(encoding="utf-8", errors="replace")[-4000:], file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"sglang CPU engine offline smoke: FAIL: {exc}") from exc

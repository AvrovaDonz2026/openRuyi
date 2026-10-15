<!--
SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
SPDX-License-Identifier: MulanPSL-2.0
-->

# SGLang CPU Dependency Audit

This audit compares the direct project dependencies in `python/pyproject_cpu.toml`
from the SGLang 0.5.21 source archive with package versions in this repository
on 2026-10-15. PEP 508 markers were evaluated for Linux, `riscv64`, and CPython
3.13. The audit also records the source archive's separate CPU AOT project.

## Direct CPU runtime dependencies

| Upstream requirement | Repository provider | Repository version | Result |
| --- | --- | ---: | --- |
| `aiohttp` | `python-aiohttp` | 3.14.1 | Satisfied |
| `anthropic>=0.20.0` | `python-anthropic` | 0.105.2 | Satisfied |
| `blobfile==3.0.0` | `python-blobfile` | 3.2.0 | Downstream bounded compatibility: `>=3.2.0,<4`; Azure connector checks passed |
| `build` | `python-build` | 1.3.0 | Satisfied |
| `compressed-tensors` | `python-compressed-tensors` | 0.18.0 | Satisfied |
| `datasets` | `python-datasets` | 5.0.1 | Satisfied |
| `easydict` | `python-easydict` | 1.13 | Satisfied |
| `einops` | `python-einops` | 0.8.2 | Satisfied |
| `fastapi` | `python-fastapi` | 0.136.1 | Satisfied |
| `gguf` | `python-gguf` | 0.19.0 | Satisfied |
| `intel-openmp; platform_machine == 'x86_64'` | — | — | Inactive on `riscv64` |
| `interegular` | `python-interegular` | 0.3.3 | Satisfied |
| `IPython` | `python-ipython` | 9.13.0 | Satisfied |
| `llguidance>=1.7.6,<2.0.0` | `python-llguidance` | 1.7.6 | Satisfied |
| `mistral_common>=1.11.5` | `python-mistral_common` | 1.12.0 | Satisfied |
| `modelscope` | `python-modelscope` | 1.40.2 | Satisfied |
| `msgspec` | `python-msgspec` | 0.19.0 | Satisfied |
| `ninja` | `python-ninja` | 1.13.2 | Satisfied |
| `numpy` | `python-numpy` | 2.5.4 | Satisfied |
| `openai==2.6.1` | `python-openai` | 2.40.0 | Downstream bounded compatibility: `>=2.40.0,<3`; backend request/retry checks passed |
| `openai-harmony==0.0.4` | `python-openai-harmony` | 0.0.8 | Downstream bounded compatibility: `>=0.0.8,<0.1` |
| `orjson` | `python-orjson` | 3.11.7 | Satisfied |
| `outlines` | `python-outlines` | 1.2.13 | Satisfied |
| `packaging` | `python-packaging` | 25.0 | Satisfied |
| `partial_json_parser` | `python-partial-json-parser` | 0.2.1.1~post7 | Satisfied |
| `pillow` | `python-pillow` | 12.0.0 | Satisfied |
| `prometheus-client>=0.20.0` | `python-prometheus-client` | 0.25.0 | Satisfied |
| `psutil` | `python-psutil` | 7.2.2 | Satisfied |
| `py-spy` | `python-py-spy` | 0.4.1 | Satisfied |
| `pybase64` | `python-pybase64` | 1.4.3 | Satisfied |
| `pydantic` | `python-pydantic` | 2.12.5 | Satisfied |
| `python-multipart` | `python-python-multipart` | 0.0.32 | Satisfied |
| `pytest` | `python-pytest` | 9.0.3 | Satisfied |
| `pyzmq>=25.1.2` | `python-pyzmq` | 27.1.0 | Satisfied |
| `regex` | `python-regex` | 2026.1.15 | Satisfied |
| `requests` | `python-requests` | 2.33.1 | Satisfied |
| `scipy` | `python-scipy` | 1.18.1 | Satisfied |
| `sentencepiece==0.2.1` | `python-sentencepiece` | 0.2.1 | Satisfied; upstream comment says 0.2.2 rejects null pieces in InternVL tokenizers |
| `setproctitle` | `python-setproctitle` | 1.1.10 | Satisfied |
| `smg-grpc-servicer>=0.9.0` | `python-smg-grpc-servicer` | 0.9.1 | Satisfied |
| `soundfile==0.13.1` | `python-soundfile` | 0.13.1 | Satisfied |
| `tabulate` | `python-tabulate` | 0.10.0 | Satisfied |
| `tiktoken` | `python-tiktoken` | 0.12.0 | Satisfied |
| `timm==1.0.16` | `python-timm` | 1.0.28 | Downstream bounded compatibility: `>=1.0.28,<2`; model registry check passed |
| `torch==2.14.0` | `python-torch` | 2.14.0 | Satisfied |
| `torchaudio==2.11.0` | `python-torchaudio` | 2.11.0 | Guest import/resampling pass after shared `libstdc++` relink in a scratch wheel environment |
| `torchcodec==0.12.0` with the upstream Linux architecture marker | `python-torchcodec` | 0.12.0 | Version query and constructor pass; frame path returns FFmpeg `AVERROR_PATCHWELCOME` |
| `torchvision==0.29.0` | `python-torchvision` | 0.29.0 | NMS passes in a scratch wheel environment |
| `tqdm` | `python-tqdm` | 4.67.3 | Satisfied |
| `transformers==5.12.1` | `python-transformers` | 5.16.0 | Downstream bounded compatibility: `>=5.16.0,<6`; import check is part of SGLang `%check` |
| `triton==3.8.0` | `python-triton` | 3.8.0 | Durable host-LLVM scratch artifact imports in QEMU (SHA-256 `77f0874e88507ad4bb7ffd4af9d3532641fd3ecb023d53a746b5619397bd89f7`); `triton.cdiv`, `triton.language`, and `triton.compiler` pass, but the driver probe reports `0 active drivers`; production RPM build and kernel execution remain unverified |
| `uvicorn` | `python-uvicorn` | 0.46.0 | Satisfied |
| `uvloop` | `python-uvloop` | 0.22.1 | Satisfied |
| `xxhash` | `python-xxhash` | 3.6.0 | Satisfied |
| `xgrammar==0.2.7` | `python-xgrammar` | 0.2.7 | Satisfied |
| `zstandard` | `python-zstandard` | 0.25.0 | Satisfied |

The current CPU SPEC rewrites the five incompatible exact pins before dependency
generation, using bounded downstream ranges tied to the repository versions.
The SPEC's API smoke checks exercise the packaged blobfile, OpenAI, Harmony,
timm, and Transformers imports plus representative call sites. These checks have
not established compatibility of SGLang's complete inference path. The framework
requirements for torch, torchaudio,
torchvision, triton, and `mistral-common` are also written explicitly in the
SPEC for both build and runtime dependencies. Runtime requirements must also
be available during the build because the SPEC imports them in `%check`.

## Build requirements

The source `build-system.requires` entries and corresponding repository
packages are:

| Upstream build requirement | Repository provider | Repository version | Result |
| --- | --- | ---: | --- |
| `setuptools>=61.0` | `python-setuptools` | 82.0.1 | Satisfied |
| `setuptools-scm>=8.0` | `python-setuptools-scm` | 10.0.5 | Satisfied |
| `wheel` | `python-wheel` | 0.48.0 | Satisfied |

The CPU SPEC also declares `pip`, `setuptools`, `setuptools-scm`, and `wheel`,
the Python development capability, and the RPM pyproject macros. Its RISC-V
conditional toolchain selects LLVM major version 22. The CPU SPEC declares the
exact torch, torchaudio, torchvision, and triton versions and the
`mistral-common` lower bound noted above. `%pyproject_buildrequires` reads
the CPU pyproject metadata to generate build and runtime requirements for the
build environment. Its `-R` option would skip runtime requirements and is not
used here. Generating requirements does not establish that they resolve.

## CPU AOT subproject

The same source archive contains `python/sglang/kernels/aot/pyproject_cpu.toml`,
which defines the separate `sglang-kernel-cpu` project at version 0.4.7. Its
runtime dependency list is empty. Its build requirements are
`scikit-build-core>=0.10`, `torch==2.14.0`, and `wheel`. The repository contains
`python-sglang-kernel-cpu` 0.4.7, with `python-scikit-build-core` 1.1.1,
`python-torch` 2.14.0, and `python-wheel` 0.48.0 satisfying its build
requirements, plus a torch runtime requirement. This AOT package is a separate
project; it is not a direct dependency listed by SGLang's CPU
`project.dependencies`. The main CPU RPM requires the AOT package because the
upstream CPU installation builds both projects. Host-LLVM cross-build and QEMU
checks were performed in scratch environments; they do not establish an OBS
RPM build or production package result. The isolated checks covered import,
RMSNorm, SiLU, and two-rank shared-memory operations after installing the AOT
artifact with Torch 2.14. The RPM digest check passed for that local artifact.

## Optional extras

These are declared as optional extras and are not part of the default CPU
runtime dependency set. The architecture markers below were also evaluated for
Linux `riscv64` and CPython 3.13.

| Extra | Upstream requirements | Repository comparison |
| --- | --- | --- |
| `diffusion` | `addict==2.4.0`, `av==16.1.0`, `cache-dit==1.3.0`, `cloudpickle==3.1.2`, `diffusers==0.37.0`, `imageio==2.36.0`, `imageio-ffmpeg==0.5.1`, `moviepy>=2.0.0`, `opencv-python-headless==4.10.0.84`, `PyYAML==6.0.1`, `remote-pdb==2.1.0`, `runai_model_streamer>=0.15.5`, `scikit-image==0.25.2`, `st_attn==0.0.7` (active), `trimesh>=4.0.0`, `vsa==0.0.4` (active), `xatlas` | Recipes exist for addict, cache-dit, moviepy, remote-pdb, st-attn, trimesh, vsa, xatlas, and the OpenCV headless flavor. RunAI Model Streamer and the strict upstream version constraints remain unresolved. |
| `tracing` | `opentelemetry-api`, `opentelemetry-exporter-otlp`, `opentelemetry-exporter-otlp-proto-grpc`, `opentelemetry-sdk` | All four repository packages exist at 1.42.1. |
| `test` | `accelerate`, `pymupdf`, `expecttest`, `jsonlines`, `matplotlib`, `pandas`, `peft>=0.18.0`, `sentence_transformers`, `sgl-eval==0.1.2` | `python-sgl-eval` 0.1.2 is packaged, but its Datasets/Pandas/Pillow bounds still need a solvable compatibility transaction. |
| `all` | No requirements | Empty. |
| `dev` | `sglang[test]` | Self-reference to the test extra; this is not an additional standalone package requirement. |

## Scope

This is a direct-dependency comparison against repository SPEC package names
and versions, not a claim that every transitive dependency is packaged or that
the complete dependency closure resolves. The generated requirements from an
RPM build remain necessary to verify the transitive closure in the target build
environment. Optional extras are reported separately because they are not
installed by the default CPU extra selection.

## Source changes

The upstream CPU build is selected with `pyproject_cpu.toml` and
`SGLANG_BUILD_RUST_EXTS=none`. The latter is an upstream build option.
The upstream setuptools-scm version override supplies the release version
without rewriting dynamic version metadata. PyTorch also uses upstream CMake
and environment options for CBLAS selection instead of a source patch.
Source changes in `%prep`, including dependency metadata substitutions, are
still downstream modifications.

| Change | Reason | Validation limit |
| --- | --- | --- |
| CPU AOT target selection | Upstream 0.5.21 has no RISC-V source selection and uses host-native ISA flags | Selected sources cross-compiled with LLVM; the production source RPM is unverified |
| CPU AOT shared-memory collectives | Upstream has no RISC-V SHM implementation | QEMU TP2 checks passed for FP32/FP16/BF16 across chunk-boundary and tail sizes; larger process counts remain unverified |
| Framework CPU runtime fallback | Upstream CPU detection and defaults cover x86 and ARM; some CPU imports require unavailable operators | Patch application and isolated imports do not establish complete engine support |
| Five dependency pin substitutions | The repository contains newer blobfile, OpenAI, Harmony, timm, and Transformers versions | Representative APIs passed; end-to-end compatibility remains unverified |

The three RISC-V patches cannot currently be removed without removing required
architecture support. CPU features that require unimplemented AOT operators
remain unavailable. No successful speculative-decoding, multi-rank, or complete
inference result is claimed.

## Target validation

The target environment is QEMU 11.1.1, `riscv-virtio`, Linux
7.1.2-533.1.or, OpenSBI 1.8.1, EDK2 2.7, Python 3.13.8, and RPM 6.0.1.
Host LLVM was used for the large native extensions; QEMU was used for target
installation and runtime checks.

| Component | Observed result | Artifact scope |
| --- | --- | --- |
| Torch 2.14 source | Import and CPU matrix multiplication passed | Scratch cross-built wheel; runtime reported `2.14.0a0`, so the release pin remains unverified |
| torchaudio 2.11.0 | Import and resampling passed with shared libstdc++ linkage | Scratch wheel |
| torchvision 0.29.0 | NMS passed | Scratch wheel |
| CPU AOT 0.4.7 | FP16/BF16 RMSNorm and SiLU passed against float32 references; TP2 FP32/FP16/BF16 SHM passed | Scratch artifact/RPM adapter with Torch `2.14.0a0`; the same script is included in `%check` |
| Triton 3.8.0 | Import, language/compiler imports, and `cdiv` passed | Scratch LLVM artifact; no active driver or kernel execution |
| Transformers 5.16.0 | Import, configuration/tokenizer loading, SGLang compatibility hooks, and image processor fixture passed | Scratch wheel |
| grpcio 1.84.0 | Health RPC and generated SMG stub imports passed | Scratch wheels |
| TVM-FFI 0.1.11 | Torch-loaded import and CPU device construction passed | Scratch dynamically linked artifact |
| TorchCodec 0.12.0 | Version query and constructor passed; frame decoding returned `AVERROR_PATCHWELCOME` | Scratch artifact; decoding is not verified |
| python-multipart 0.0.32 | Source build, `%check`, offline DNF install, and installed parser passed | Local source-built RPM; default rpmlint findings remain |
| GenSON 1.4.0 | Source RPM check ran 111 passing tests | Scratch RPM with QA findings |
| pybase64 and msgspec | Dependency-checked RPM install/import passed | Prebuilt-wheel RPM adapters |
| Addict, Proglog, MoviePy, Trimesh, xatlas, math verifier chain | Isolated functional checks passed | Scratch wheels |

These checks do not establish a complete offline OBS source build. Scratch
RPMs have outstanding rpmlint findings, including temporary metadata, development
file ownership, and unstripped files. The Torch adapter also required an RPATH
QA bypass; that bypass is not part of the production SPEC.

## Unresolved package closure

Recipes exist for the default CPU dependencies, but the target Base repository
cannot yet supply a complete transaction. Missing Python distribution providers include
`sglang-kernel-cpu`, `mistral-common`, `python-multipart`,
`smg-grpc-servicer`, `outlines`, and `modelscope`; their RPM recipe names are
listed in the dependency table above. Base provides older Torch
2.13.0, torchaudio 2.10.0, torchvision 0.28.0, Triton 3.7.1, and Transformers
5.12.1. Its Transformers constraint also conflicts with tokenizers 0.23.3.
The corresponding updated production RPMs and their transitive requirements
MUST be built and installed together before the closure can be accepted.

Optional dependency constraints also remain unresolved. `sgl-eval` requires
`datasets<5`, `pandas<3`, and `Pillow<12`; MoviePy requires `Pillow<12`.
Compatibility recipes for Datasets 4.8.5, Pandas 2.3.3, Pillow 11.3.0, and
fsspec 2026.2.0 exist, but their aliases alone do not solve conflicts with the
current unsuffixed providers. RunAI Model Streamer still needs its native
library, cloud SDK dependencies, and an offline RISC-V build toolchain.
The remote-pdb source test also has an unresolved Python 3.13 prompt mismatch.

A successful complete SGLang CPU RPM installation, server startup, and inference
request have not been demonstrated. CUDA and ROCm device execution are also
unverified. CUDA recipes requiring NVIDIA's toolkit currently cannot be built
for RISC-V with the available supported host toolchain.

## Offline CPU startup smoke plan

The smallest useful startup check uses a local Hugging Face-style model
directory. `model_path=dummy` is useful for unit fixtures, but the normal
`ModelConfig` path still needs a model configuration and therefore does not
exercise local configuration or tokenizer loading. Instead, create a temporary
directory containing only:

* `config.json` for a one-layer `LlamaForCausalLM` (for example, hidden size
  32, intermediate size 64, four attention heads, one key/value head,
  vocabulary size matching the tokenizer, and context length 64);
* a locally saved `tokenizer.json` plus `tokenizer_config.json` and
  `special_tokens_map.json`, generated with the packaged `tokenizers` library
  and a small WordLevel vocabulary; and
* no weight files. `--load-format dummy` makes SGLang initialize random model
  weights through `DummyModelLoader`, so this remains offline and deterministic
  with respect to the input files.

Once the complete target dependency closure is available in the guest, the
candidate command is:

```text
SGLANG_USE_CPU_ENGINE=1 python -m sglang.launch_server \
  --model-path /var/tmp/sglang-tiny \
  --tokenizer-path /var/tmp/sglang-tiny \
  --load-format dummy --device cpu --tensor-parallel-size 1 \
  --context-length 64 --max-total-tokens 64 \
  --max-running-requests 1 --port 30000
```

The smoke MUST first poll `GET /health`, then send one offline request to
`POST /v1/completions` with prompt `hello` and `max_tokens=1`, and finally
terminate the server while retaining its complete log. A successful HTTP
response would establish a target startup and one-token request path only; it
would not establish throughput, long-context behavior, speculative decoding,
GPU execution, or compatibility with arbitrary model architectures.

This smoke has not passed. It MUST run with real target dependencies and
without substitute operator or Triton stubs. A successful scratch run MUST be
followed by the same check against dependency-checked production RPMs.

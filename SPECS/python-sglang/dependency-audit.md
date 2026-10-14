<!--
SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
SPDX-License-Identifier: MulanPSL-2.0
-->

# SGLang CPU Dependency Audit

This audit compares the direct project dependencies in `python/pyproject_cpu.toml`
from the SGLang 0.5.21 source archive with package versions in this repository
on 2026-10-14. PEP 508 markers were evaluated for Linux, `riscv64`, and CPython
3.13. The audit also records the source archive's separate CPU AOT project.

## Direct CPU runtime dependencies

| Upstream requirement | Repository provider | Repository version | Result |
| --- | --- | ---: | --- |
| `aiohttp` | `python-aiohttp` | 3.14.1 | Satisfied |
| `anthropic>=0.20.0` | `python-anthropic` | 0.105.2 | Satisfied |
| `blobfile==3.0.0` | `python-blobfile` | 3.2.0 | Exact pin mismatch |
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
| `mistral_common>=1.11.5` | `python-mistral_common` | 1.11.5 | Satisfied |
| `modelscope` | `python-modelscope` | 1.40.2 | Satisfied |
| `msgspec` | `python-msgspec` | 0.19.0 | Satisfied |
| `ninja` | `python-ninja` | 1.13.2 | Satisfied |
| `numpy` | `python-numpy` | 2.5.4 | Satisfied |
| `openai==2.6.1` | `python-openai` | 2.40.0 | Exact pin mismatch |
| `openai-harmony==0.0.4` | `python-openai-harmony` | 0.0.8 | Exact pin mismatch |
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
| `timm==1.0.16` | `python-timm` | 1.0.28 | Exact pin mismatch |
| `torch==2.14.0` | `python-torch` | 2.14.0 | Satisfied |
| `torchaudio==2.11.0` | `python-torchaudio` | 2.11.0 | Satisfied |
| `torchcodec==0.12.0` with the upstream Linux architecture marker | `python-torchcodec` | 0.12.0 | Active and satisfied on `riscv64` |
| `torchvision==0.29.0` | `python-torchvision` | 0.29.0 | Satisfied |
| `tqdm` | `python-tqdm` | 4.67.3 | Satisfied |
| `transformers==5.12.1` | `python-transformers` | 5.16.0 | Exact pin mismatch |
| `triton==3.8.0` | `python-triton` | 3.8.0 | Satisfied |
| `uvicorn` | `python-uvicorn` | 0.46.0 | Satisfied |
| `uvloop` | `python-uvloop` | 0.22.1 | Satisfied |
| `xxhash` | `python-xxhash` | 3.6.0 | Satisfied |
| `xgrammar==0.2.7` | `python-xgrammar` | 0.2.7 | Satisfied |
| `zstandard` | `python-zstandard` | 0.25.0 | Satisfied |

The current CPU SPEC rewrites the `openai`, `openai-harmony`, and `timm`
constraints before dependency generation to accept the repository versions.
The SPEC's API smoke checks exercise those newer versions. These checks have
not established compatibility of SGLang's complete inference path.
The source metadata's `blobfile==3.0.0` and `transformers==5.12.1` pins also do
not match the repository's packaged versions; the current SPEC does not rewrite
those constraints. The framework requirements for torch, torchaudio,
torchvision, triton, and `mistral_common` are also written explicitly in the
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
`mistral_common` lower bound noted above. `%pyproject_buildrequires` reads
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
upstream CPU installation builds both projects. A recipe's presence does not
establish that its RISC-V build or runtime validation has passed.

## Optional extras

These are declared as optional extras and are not part of the default CPU
runtime dependency set. The architecture markers below were also evaluated for
Linux `riscv64` and CPython 3.13.

| Extra | Upstream requirements | Repository comparison |
| --- | --- | --- |
| `diffusion` | `addict==2.4.0`, `av==16.1.0`, `cache-dit==1.3.0`, `cloudpickle==3.1.2`, `diffusers==0.37.0`, `imageio==2.36.0`, `imageio-ffmpeg==0.5.1`, `moviepy>=2.0.0`, `opencv-python-headless==4.10.0.84`, `PyYAML==6.0.1`, `remote-pdb==2.1.0`, `runai_model_streamer>=0.15.5`, `scikit-image==0.25.2`, `st_attn==0.0.7` (active), `trimesh>=4.0.0`, `vsa==0.0.4` (active), `xatlas` | No repository SPEC found for `addict`, `cache-dit`, `moviepy`, `opencv-python-headless`, `remote-pdb`, `runai_model_streamer`, `st_attn`, `trimesh`, `vsa`, or `xatlas`. Repository versions also differ from exact pins for `av` (17.0.1), `diffusers` (0.38.0), `imageio` (2.37.3), `imageio-ffmpeg` (0.6.0), `PyYAML` (6.0.3), and `scikit-image` (0.26.0). `cloudpickle` 3.1.2 satisfies its pin. |
| `tracing` | `opentelemetry-api`, `opentelemetry-exporter-otlp`, `opentelemetry-exporter-otlp-proto-grpc`, `opentelemetry-sdk` | All four repository packages exist at 1.42.1. |
| `test` | `accelerate`, `pymupdf`, `expecttest`, `jsonlines`, `matplotlib`, `pandas`, `peft>=0.18.0`, `sentence_transformers`, `sgl-eval==0.1.2` | Repository packages satisfy all listed available requirements (`accelerate` 1.13.0, `pymupdf` 1.27.2, `expecttest` 0.3.0, `jsonlines` 4.0.0, `matplotlib` 3.11.0, `pandas` 3.0.1, `peft` 0.19.1, `sentence-transformers` 5.4.1); no SPEC was found for `sgl-eval`. |
| `all` | No requirements | Empty. |
| `dev` | `sglang[test]` | Self-reference to the test extra; this is not an additional standalone package requirement. |

## Scope

This is a direct-dependency comparison against repository SPEC package names
and versions, not a claim that every transitive dependency is packaged or that
the complete dependency closure resolves. The generated requirements from an
RPM build remain necessary to verify the transitive closure in the target build
environment. Optional extras are reported separately because they are not
installed by the default CPU extra selection.

## Validation status

The RISC-V CPU recipe includes downstream target-selection, shared-memory
collective, and runtime fallback patches. The patches apply to the pinned source
with zero fuzz and the Python changes pass syntax checks. LLVM compiled a RISC-V
shared-memory header probe; full AOT extension linking remains unverified.

The isolated target tests passed for Addict, Remote PDB, Proglog, MoviePy's
in-memory ColorClip path, Trimesh's unit-box geometry, xatlas's UV generation,
and the LaTeX/math verifier chain with ANTLR 4.9.3. These are wheel-level tests;
they do not establish production OBS RPM build equivalence. Standard target RPM
macro assembly and dependency-checked installation passed for pybase64 and
msgspec using local prebuilt-wheel adapters.

Optional sgl-eval retains datasets<5, pandas<3, and Pillow<12, which conflict
with the current repository providers. MoviePy also retains Pillow<12. These
bounds have not been relaxed. Full SGLang startup and inference with PyTorch
2.14.0, and CUDA/ROCm device execution, remain unverified.

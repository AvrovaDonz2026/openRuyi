<!--
SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
SPDX-License-Identifier: MulanPSL-2.0
-->

# SGLang 0.5.21 dependency isolation

The CPU recipe uses the upstream `python/pyproject_cpu.toml`. Existing
openRuyi packages remain the shared dependency providers when they satisfy its
requirements. The compatibility packages install under
`%{_libdir}/sglang/core/python%{python3_version}/site-packages`, rather than
replacing the distribution's Python modules or development files.

## Shared and private providers

| Dependency | Provider selection |
| --- | --- |
| Transformers 5.12.1 and tokenizers 0.22.2 | Existing distribution packages; the upstream Transformers pin is retained. |
| NumPy, SciPy, protobuf, compressed-tensors | Existing distribution recipes; SGLang does not require their proposed upgrades. |
| Datasets, fsspec, pandas, Pillow | Existing distribution packages for the core CPU environment. |
| Torch 2.14.0 | `python-sglang-torch-2.14`, including a private development SDK. |
| TorchAudio 2.11.0 and TorchVision 0.29.0 | Private compatibility packages linked against the private Torch SDK. |
| Triton 3.8.0, xgrammar 0.2.7, llguidance >=1.7.6 | Private compatibility packages. |
| Mistral common >=1.11.5 and TVM FFI | Private compatibility packages where the distribution version is insufficient. |
| scikit-build-core >=1.0 | Private build backend for Torch; the distribution's 0.12.2 backend remains available. |
| SGLang CPU kernels, TorchCodec and SMG/gRPC | Private modules sharing the selected private Torch/gRPC runtime. |
| ModelScope and py-spy | New shared packages; no differing existing version requires duplication. |

The optional Datasets 4, fsspec 2026.2, pandas 2 and Pillow 11 recipes use the
separate `extras` tree. They MUST NOT replace shared distribution providers.
They are not selected by the core CPU launcher. Optional diffusion dependencies,
including RunAI Model Streamer and its cloud SDK build closure, remain incomplete.

## Launch and dependency resolution

`sglang` and `sglang-python` select the private core tree, disable user site
packages and unsafe current-directory imports, and clear inherited Python and
ELF loader overrides. Shared modules remain accessible through the normal
system Python paths. Native compatibility modules use private library search
paths; global loader configuration is not changed.

Private Python distributions provide `sglang(python3dist(NAME))` capabilities;
optional private distributions use `sglang-extras(python3dist(NAME))`. Selected
internal requirements use the same namespaces. Python ABI and external system
libraries retain normal RPM requirements. Private ELF libraries MUST NOT
satisfy unrelated applications' global SONAME requirements.

The blobfile, OpenAI, Harmony and timm exact pins are replaced by bounded
requirements for the existing distribution versions. The recipe includes API
smoke checks for these substitutions. They do not establish complete inference
compatibility and remain explicit downstream changes for review.

## Required target validation

Before this stack is ready for mainline review, the final recipes MUST pass:

1. Offline source and binary RPM builds with complete BuildRequires.
2. RPM dependency and file ownership checks, including absence of global
   capabilities for private modules and native libraries.
3. Installation alongside the distribution packages without removals,
   replacements or payload modifications.
4. `sglang-coexistence-test.py` against a clean system snapshot, checking module
   versions and paths, native Torch library paths and distributed Gloo support.
5. SGLang CPU startup and a local inference test, followed by repeat checks of
   the original system modules and representative operations.
6. Applicable repository pre-commit checks and SRPM/binary RPM review checks.

Host LLVM 22 has produced a RISC-V executable that ran in QEMU. This validates
the basic cross toolchain, not the final Torch or SGLang RPMs. Full production
Torch 2.14 distributed support, SGLang CPU inference and the final coexistence
transaction have not yet passed. CUDA and ROCm runtime validation on RISC-V
also remains outstanding.

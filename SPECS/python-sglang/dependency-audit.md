<!--
SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
SPDX-License-Identifier: MulanPSL-2.0
-->

# SGLang 0.5.21 dependency isolation (audit 2026-10-19)

The v0.5.21 CPU metadata used by this recipe selects Transformers 5.19.0.
The private Transformers 5.19.0 compatibility package is selected alongside
Tokenizers 0.23.2, Hugging
Face Hub 1.31.0 and Click 8.4.2. This downstream choice is based on the
private compatibility package set and the declared `BuildRequires`/`Requires`;
the final OBS-signed RISC-V binary build, dependency transaction and runtime
compatibility remain to be verified.

The CPU recipe uses the upstream `python/pyproject_cpu.toml`. Existing
openRuyi packages remain the shared dependency providers when they satisfy its
requirements. The compatibility packages install under
`%{_libdir}/sglang/core/python%{python3_version}/site-packages`, rather than
replacing the distribution's Python modules or development files.

CPU is the only SGLang backend enabled by the current source tree. ROCm
branches remain in selected private Torch and TorchVision recipes as a
reserved flavor, but their `_multibuild` entries are deliberately absent. The
ROCm dependency closure, target build and device validation are
not complete, so no ROCm RPM is scheduled or claimed as built. The conditional
requirements continue to name `torch-rocm`; they MUST NOT fall back to the CPU
provider when the flavor is enabled in a future change.

The packaged CPU closure is currently limited to `riscv64`, where the private
Torch, TorchAudio, TorchVision, Triton and CPU-kernel recipes are scoped for
the target architecture. Their complete binary build and runtime validation
remain required before publication. The upstream
CPU metadata also mentions Linux ARM, but this repository does not yet provide
an ARM-compatible Triton RPM; publishing the SGLang RPM there would leave an
unsatisfied runtime dependency. x86_64 is likewise held back until the
repository supplies the upstream `intel-openmp` Python capability and validates
the complete transaction. The standalone `python-sglang-kernel-cpu` provider
uses the same architecture limit, so it cannot be scheduled independently on
an unsupported architecture.

The upstream CPU metadata requests `intel-openmp` on `x86_64`. This repository
has no `intel-openmp` recipe or provider; the RISC-V `%prep` path removes that
platform-marked requirement because the target uses the packaged LLVM OpenMP
runtime instead. The SGLang CPU and CPU-kernel recipes therefore explicitly
scope publication to RISC-V until an `intel-openmp` provider is added and the
x86_64 transaction is validated.

## Shared and private providers

| Dependency | Provider selection |
| --- | --- |
| Transformers 5.19.0 and Tokenizers 0.23.2 | Private compatibility packages selected by the current CPU metadata. |
| Hugging Face Hub >=1.31.0 and Click >=8.4.2 | Private 1.31.0 and 8.4.2 compatibility packages for the newer Transformers closure. |
| NumPy, SciPy, protobuf, compressed-tensors | Existing distribution recipes; SGLang does not require their proposed upgrades. |
| Datasets, fsspec, pandas, Pillow | Existing distribution packages for the core CPU environment. |
| Torch 2.14.0 | `python-torch-sglang-2.14`, including a private development SDK. |
| TorchAudio 2.11.0 and TorchVision 0.29.0 | Private compatibility packages linked against the private Torch SDK. |
| Triton 3.8.0, xgrammar 0.2.7, llguidance >=1.7.6 | Private compatibility packages. |
| Mistral common >=1.11.5 and TVM FFI | Private compatibility packages where the distribution version is insufficient. |
| scikit-build-core >=1.0 | Private build backend for Torch; the distribution's 0.12.2 backend remains available. |
| SGLang CPU kernels, TorchCodec and SMG/gRPC | Private modules sharing the selected private Torch/gRPC runtime. |
| ModelScope | Existing shared package; no differing version requires duplication. |

Tokenizers 0.23.2 uses the existing Rust PyO3, NumPy and async-runtime 0.29
crate series. A RISC-V QEMU build has completed offline Cargo resolution,
produced the `cp310-abi3-linux_riscv64` wheel, and passed the package import
and WordLevel encode/decode checks. In a separate RISC-V QEMU scratch RPMDB,
the same RPM installed with an explicit `--nosignature` validation override,
passed `rpm -V`, and passed the private-path import and WordLevel smoke while
leaving the existing system packages untouched. The resulting validation RPM
is unsigned scratch output, so the default signature check correctly rejects
it; the final OBS-signed transaction remains to be verified. The SGLang
pyproject wrappers export
`CARGO_NET_OFFLINE=true` for both build-requirements generation and wheel
construction, so this offline constraint is enforced by the package macros.
Hugging Face Hub's
`hf-xet>=1.5.2,<2` dependency applies only to its upstream x86/ARM platform
markers; the `python-hf-xet` recipe is aligned
to 1.5.2 for those platforms, although its target build remains unverified. It
is not required by the RISC-V CPU marker.

LLGuidance 1.7.6 requires the exact `derivre` 0.3.12 crate release. The
compatibility closure therefore keeps the existing 0.3.11 crate available and
adds a co-installable 0.3.12 provider, together with the required hashbrown
0.17.1 provider. The Rust crate transaction and LLGuidance target build remain
unverified.

The optional Datasets 4, fsspec 2026.2, pandas 2 and Pillow 11 recipes use the
separate `extras` tree. They MUST NOT replace shared distribution providers.
They are not selected by the core CPU launcher. Optional diffusion dependencies,
including RunAI Model Streamer and its cloud SDK build closure, remain incomplete.
The existing `opencv` package remains unchanged; the optional
`opencv-python-headless` requirement is therefore outside the current core
CPU closure and is not claimed as packaged here.

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

The blobfile, OpenAI, Harmony and timm requirements are bounded in `%prep`
for the existing distribution versions. The recipe includes API
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
   Its real `sglang --help` check enables Python's verbose import trace and
   verifies that the launcher imports `sglang` from the private core tree.
5. SGLang CPU startup and a local inference test, followed by repeat checks of
   the original system modules and representative operations.
6. Applicable repository pre-commit checks and SRPM/binary RPM review checks.

A scratch LLVM/RISC-V probe has produced an executable that ran in a QEMU
guest. This is toolchain evidence only, not a package build result. The current
QEMU RPM transaction harness checks the supplied Torch, TorchAudio, TorchVision,
TorchCodec, Triton and SGLang metadata, installs the candidate transaction,
checks private module versions and native paths, preserves the system RPM and
Python baselines, and exercises Torch distributed Gloo, TorchCodec/FFmpeg and
the SGLang CPU launcher when those candidate RPMs are supplied. It does not
constitute a real OBS-signed RISC-V binary build or prove complete inference
compatibility. Full production Torch 2.14 distributed support, SGLang CPU
inference and the final OBS-signed coexistence transaction remain unverified.

The CUDA flavor is unsupported on RISC-V: its SPEC is restricted to
`x86_64` and `aarch64`, and CUDA recipes requiring NVIDIA's toolkit cannot be
built for RISC-V with the supported toolchain. The repository currently does
not enable a CUDA multibuild because the private Torch provider has a CPU
variant but no CUDA variant; enabling it without that provider would leave the
CUDA Torch dependency unresolved. CUDA-only recipes are retained as
reserved, currently unbuildable sources with explicit architecture limits and
`torch-cuda` requirements. No CUDA runtime result is claimed here. ROCm device
execution is likewise outside this CPU audit and has not been validated on
RISC-V.

The pbuild CI configuration in `.github/build/_config` excludes
`python-sglang-kernel`, `python-sgl-deep-ep`, and `python-sgl-deep-gemm` with
`BuildFlags: excludebuild:PACKAGE` entries. `scripts/update-package` synchronizes
package sources, not this configuration. Before synchronizing the reserved
sources, the OBS project configuration MUST include matching exclusions; its
live configuration has not been verified. Recipe comments and architecture
limits alone do not disable builds. Without the exclusions, OBS can schedule
the standalone CUDA sources and fail dependency resolution because no
`torch-cuda` provider is published.

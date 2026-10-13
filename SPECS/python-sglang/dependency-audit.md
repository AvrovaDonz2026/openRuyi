<!--
SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
SPDX-License-Identifier: MulanPSL-2.0
-->

# SGLang Dependency Audit

Audit scope: SGLang 0.5.21 CPU flavor and its explicit `Requires` and
`BuildRequires` in `python-sglang.spec`, checked against repository SPECs on
2026-10-14. Existing worktree changes were included in the inspection.

## CPU runtime dependencies

| Requirement | Required version | Repository package | Result |
| --- | --- | --- | --- |
| `python3dist(torch)` | `= 2.14.0` | `python-torch` 2.14.0 | Satisfied |
| `python3dist(torchaudio)` | `= 2.11.0` | `python-torchaudio` 2.11.0 | Satisfied |
| `python3dist(torchvision)` | `= 0.29.0` | `python-torchvision` 0.29.0 | Satisfied |
| `python3dist(triton)` | `= 3.8.0` | `python-triton` 3.8.0 | Satisfied |
| `python3dist(mistral_common)` | `>= 1.11.5` | `python-mistral_common` 1.11.5 | Satisfied |

The `openai`, `openai-harmony`, and `timm` dependencies are declared in the
CPU project metadata, not as explicit SPEC requirements. The SPEC adjusts
their lower bounds to the versions used by the repository compatibility check;
the matching SPECs provide `python-openai` 2.40.0, `python-openai-harmony`
0.0.8, and `python-timm` 1.0.28.

## Build requirements

The explicit Python build tools (`pip`, `setuptools`, `setuptools-scm`, and
`wheel`), Python development capability, RPM Python macros, and pyproject RPM
macros are represented by repository packages. On RISC-V, the conditional
Clang/LLVM toolchain requirements select major version 22, also represented in
the repository. The CPU build also pins the four framework packages and
`mistral_common` listed above.

## Scope and findings

No missing or under-versioned package was found among the explicit CPU runtime
and build requirements. No new SPEC was warranted by this static audit.

The CPU dependency list is also read dynamically from `python/pyproject_cpu.toml`
inside the SGLang source archive by `%pyproject_buildrequires -R`. That file is
not present in the repository checkout, so this report cannot enumerate or
independently verify every generated/transitive requirement. The build service's
generated build requirements remain the authoritative check for that part of
the closure.

CUDA-specific extension packages present in the worktree (including
`sglang-kernel`, `sgl-deep-gemm`, and `sgl-deep-ep`) were not treated as CPU
runtime dependencies; their SPECs require CUDA tooling or NVIDIA runtime
libraries.

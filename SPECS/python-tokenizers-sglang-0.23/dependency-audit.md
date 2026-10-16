<!--
SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
SPDX-License-Identifier: MulanPSL-2.0
-->

# tokenizers 0.23.2 offline dependency audit

The 0.23.2 Python binding manifest pins PyO3, PyO3 FFI, and build support to
`=0.29`, and requires `pyo3-async-runtimes = "0.29"` plus `numpy = "0.29"`.
The repository provides those 0.29 packages, including the tokio-runtime and
abi3 feature metapackages, so the direct binding dependency closure is
available offline. The exact-equals constraints are retained in Cargo.toml;
the repository's 0.29.0 package satisfies `=0.29`.

The direct Rust dependencies otherwise match the repository's tokenizers-0.23
crate set, with `daachorse-3`, PyO3 0.29, ndarray 0.16, and numpy 0.29 noted
explicitly in the SPEC. The upstream `parity-aware-bpe` feature is enabled by
the binding default feature set and is provided by the existing tokenizers
0.23.2 Rust source package. This feature is empty in the upstream core
manifest, so it does not add `fancy-regex`, `smallvec`, or other crates;
`fancy-regex` is optional and `smallvec` is not a direct dependency. The
default feature set does require `onig`, `indicatif`, and `esaxx-rs/cpp`, all
listed in the SPEC.

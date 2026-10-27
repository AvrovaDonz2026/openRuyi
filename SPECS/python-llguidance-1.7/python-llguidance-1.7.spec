# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Kimmy <yucheng.or@isrc.iscas.ac.cn>
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname llguidance

%global compat_name python-llguidance-1.7
%ifarch riscv64
%global llvm_maj_ver 22
%global toolchain clang
%global llvm_bindir %{_libdir}/llvm%{llvm_maj_ver}/bin
%endif

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros >= 0.1-1000
%sglang_python_compat
Version:        1.7.6
Release:        %autorelease
Summary:        Low-level guidance Rust library bindings for Python
License:        MIT
URL:            https://github.com/microsoft/llguidance
#!RemoteAsset:  sha256:db7febbe412ed2015501904646750071d7e00e6df7f85c4b956ad4f206fd2df7
Source0:        https://files.pythonhosted.org/packages/source/l/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

# Drop optional/dev Rust dependencies used only for wasm, header-generation, and
# benchmark/test features that are not enabled for the Python extension build.
Patch2000:      2000-remove-unused-optional-rust-dependencies.patch

BuildOption(install):  -l llguidance
# Skip optional Hugging Face CLI integration: No module named 'huggingface_hub'.
BuildOption(check):  -e 'llguidance.cli'
# Skip optional Transformers tokenizer integration: No module named 'transformers'.
BuildOption(check):  -e 'llguidance.hf'
# Skip llama.cpp integration: No module named 'llama_cpp'.
BuildOption(check):  -e 'llguidance.llamacpp'
# Skip MLX integration: No module named 'mlx'.
BuildOption(check):  -e 'llguidance.mlx'
# Skip optional PyTorch integration: No module named 'torch'.
BuildOption(check):  -e 'llguidance.torch'

BuildRequires:  cargo
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(maturin)
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(pip)
BuildRequires:  rust >= 1.87
BuildRequires:  rust-rpm-macros
%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif
BuildRequires:  crate(anyhow-1/default) >= 1.0.95
BuildRequires:  crate(bytemuck-1/default) >= 1.21.0
BuildRequires:  crate(bytemuck-derive-1/default) >= 1.8.1
BuildRequires:  crate(derivre-0.3/ahash) >= 0.3.12
BuildRequires:  crate(derivre-0.3/compress) >= 0.3.12
# derivre 0.3.12 requires hashbrown 0.17.1; keep the offline build
# transaction from selecting the older distribution provider 0.17.0.
BuildRequires:  crate(hashbrown-0.17) >= 0.17.1
BuildRequires:  crate(indexmap-2/default) >= 2.7.1
BuildRequires:  crate(jsonschema-0.29/default) >= 0.29.0
BuildRequires:  crate(lazy-static-1/default) >= 1.5.0
BuildRequires:  crate(log-0.4/default) >= 0.4.25
BuildRequires:  crate(pyo3-0.28/default) >= 0.28.2
BuildRequires:  crate(pyo3-0.28/abi3-py39) >= 0.28.2
BuildRequires:  crate(pyo3-0.28/anyhow) >= 0.28.2
BuildRequires:  crate(pyo3-0.28/extension-module) >= 0.28.2
BuildRequires:  crate(rayon-1/default) >= 1.10.0
BuildRequires:  crate(referencing-0.29/default) >= 0.29.0
BuildRequires:  crate(regex-syntax-0.8/default) >= 0.8.5
BuildRequires:  crate(serde-1/default) >= 1.0.217
BuildRequires:  crate(serde-1/derive) >= 1.0.217
BuildRequires:  crate(serde-json-1/preserve-order) >= 1.0.138
BuildRequires:  crate(tiktoken-rs-0.7/default) >= 0.7.0
BuildRequires:  crate(tokenizers-0.21/fancy-regex) >= 0.21.2
BuildRequires:  crate(tokenizers-0.21/unstable-wasm) >= 0.21.2

%description
llguidance provides Python bindings for the low-level Guidance Rust library for
fast structured output generation and grammar-based token guidance.

%prep -a
%rust_setup_registry
rm -f Cargo.lock

%generate_buildrequires
%sglang_pyproject_buildrequires

%build -p
%ifarch riscv64
export PATH="%{llvm_bindir}:$PATH"
export CC="%{llvm_bindir}/clang"
export CXX="%{llvm_bindir}/clang++"
export AR="%{llvm_bindir}/llvm-ar"
export RANLIB="%{llvm_bindir}/llvm-ranlib"
export CFLAGS="%{build_cflags} --target=%{_target_platform}"
export CXXFLAGS="%{build_cxxflags} --target=%{_target_platform}"
export LDFLAGS="-fuse-ld=lld --target=%{_target_platform} %{build_ldflags}"
# Cargo invokes the target linker directly, so pass the cross target explicitly.
%if "%{openruyi_riscv_arch}" == "-march=rva23u64"
export CARGO_BUILD_TARGET="riscv64a23-unknown-linux-gnu"
export CARGO_TARGET_RISCV64A23_UNKNOWN_LINUX_GNU_LINKER="%{llvm_bindir}/clang"
export CARGO_TARGET_RISCV64A23_UNKNOWN_LINUX_GNU_RUSTFLAGS="${CARGO_TARGET_RISCV64A23_UNKNOWN_LINUX_GNU_RUSTFLAGS:-} -C link-arg=--target=%{_target_platform} -C link-arg=-fuse-ld=lld"
%else
export CARGO_BUILD_TARGET="riscv64gc-unknown-linux-gnu"
export CARGO_TARGET_RISCV64GC_UNKNOWN_LINUX_GNU_LINKER="%{llvm_bindir}/clang"
export CARGO_TARGET_RISCV64GC_UNKNOWN_LINUX_GNU_RUSTFLAGS="${CARGO_TARGET_RISCV64GC_UNKNOWN_LINUX_GNU_RUSTFLAGS:-} -C link-arg=--target=%{_target_platform} -C link-arg=-fuse-ld=lld"
%endif
%endif

%files -f %{pyproject_files}
%doc README.md CHANGELOG.md
%license LICENSE

%changelog
%{?autochangelog}

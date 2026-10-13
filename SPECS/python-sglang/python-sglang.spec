# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname sglang
%global flavor @BUILD_FLAVOR@%{nil}
%ifarch riscv64
%global llvm_maj_ver 22
%global toolchain clang
%endif

# The CPU flavor is the only flavor currently buildable in openRuyi.  The
# CUDA flavor keeps the upstream metadata for a future CUDA-enabled build host.
%if "%{flavor}" == "cuda"
%bcond cuda 1
%else
%bcond cuda 0
%endif

%if %{with cuda}
Name:           python-%{srcname}-cuda
%else
Name:           python-%{srcname}-cpu
%endif
Version:        0.5.21
Release:        %autorelease
Summary:        Fast serving framework for large language and vision-language models
License:        Apache-2.0
URL:            https://github.com/sgl-project/sglang
VCS:            git:https://github.com/sgl-project/sglang.git
#!RemoteAsset:  sha256:c44951b7871dac61262fc04e9fca628175758a97fa5f603c522b31dc31b94249
Source0:        https://github.com/sgl-project/sglang/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(prep):  -n %{srcname}-%{version}
BuildOption(install):  -l sglang

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(setuptools-scm)
BuildRequires:  python3dist(wheel)

%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif

%if %{with cuda}
# The CUDA flavor follows upstream's full CUDA metadata.  These requirements
# intentionally remain conditional until matching CUDA packages are available.
BuildRequires:  python3dist(setuptools-rust)
BuildRequires:  python3dist(torch)
%else
BuildRequires:  python3dist(torch) = 2.14.0
BuildRequires:  python3dist(torchaudio) = 2.11.0
BuildRequires:  python3dist(torchvision) = 0.29.0
BuildRequires:  python3dist(triton) = 3.8.0
%endif

%if %{without cuda}
Requires:       python3dist(torch) = 2.14.0
Requires:       python3dist(torchaudio) = 2.11.0
Requires:       python3dist(torchvision) = 0.29.0
Requires:       python3dist(triton) = 3.8.0
%endif

%description
SGLang is a fast serving framework for large language models and vision-language
models.  This package provides the openRuyi CPU or CUDA flavor selected by the
build flavor.

%prep -a
%if %{without cuda}
cp python/pyproject_cpu.toml python/pyproject.toml
%endif
grep -qF 'dynamic = ["version"]' python/pyproject.toml
sed -i 's/dynamic = \["version"\]/version = "%{version}"/' \
    python/pyproject.toml

%generate_buildrequires
cd python
%pyproject_buildrequires -R

%build -p
cd python
export SETUPTOOLS_SCM_PRETEND_VERSION='%{version}'
%if %{without cuda}
# The CPU metadata has no Rust build requirement.  Keep this explicit so a
# future setup.py change cannot silently pull GPU/Rust extensions into RISC-V.
export SGLANG_BUILD_RUST_EXTS=none
%endif
%ifarch riscv64
# Cross compilation uses the distribution LLVM toolchain.  The target sysroot
# and ABI flags are supplied by the openRuyi riscv64 build environment.
export CC=clang
export CXX=clang++
export LD=ld.lld
export AR=llvm-ar
export RANLIB=llvm-ranlib
export CFLAGS="%{build_cflags} --target=%{_target_platform}"
export CXXFLAGS="%{build_cxxflags} --target=%{_target_platform}"
export LDFLAGS="%{build_ldflags} -fuse-ld=lld"
%endif

%install -p
cd python

%check -a
cd python
%if %{with cuda}
%{python3} -c 'import importlib.metadata; import sglang; assert importlib.metadata.version("sglang") == "%{version}"; print(sglang.__version__)'
%else
%{python3} -c 'import importlib.metadata; import sglang; assert importlib.metadata.version("sglang-cpu") == "%{version}"; print(sglang.__version__)'
%endif

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/sglang

%changelog
%autochangelog

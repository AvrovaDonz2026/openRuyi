# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname sglang-kernel-cpu
%global toolchain clang
%global version_upstream 0.5.21
%ifarch riscv64
%global llvm_maj_ver 22
%endif

Name:           python-%{srcname}
Version:        0.4.7
Release:        %autorelease
Summary:        CPU kernel library for SGLang
License:        Apache-2.0
URL:            https://github.com/sgl-project/sglang/tree/main/python/sglang/kernels/aot
VCS:            git:https://github.com/sgl-project/sglang.git
#!RemoteAsset:  sha256:c44951b7871dac61262fc04e9fca628175758a97fa5f603c522b31dc31b94249
Source0:        https://github.com/sgl-project/sglang/archive/refs/tags/v%{version_upstream}.tar.gz#/sglang-%{version_upstream}.tar.gz
BuildSystem:    pyproject

BuildOption(prep):  -n sglang-%{version_upstream}/python/sglang/kernels/aot
BuildOption(install):  -l sgl_kernel

BuildRequires:  cmake >= 3.18
BuildRequires:  clang
BuildRequires:  libomp-devel
BuildRequires:  pkgconfig(numa)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(scikit-build-core) >= 0.10
BuildRequires:  python3dist(torch) = 2.14.0
BuildRequires:  python3dist(wheel)
BuildRequires:  python-torch-devel = 2.14.0

%ifarch riscv64
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif

Requires:       python3dist(torch) = 2.14.0

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
SGLang Kernel CPU provides the CPU AOT extension used by the SGLang inference
engine. It uses the upstream CPU build configuration from SGLang 0.5.21.

%prep -a
cp pyproject_cpu.toml pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%build -p
%ifarch riscv64
# Upstream shm.cpp rejects RISC-V; the CPU kernel still requires a target port.
export CC=clang
export CXX=clang++
export LD=ld.lld
export AR=llvm-ar
export RANLIB=llvm-ranlib
export CFLAGS="%{build_cflags} --target=%{_target_platform}"
export CXXFLAGS="%{build_cxxflags} --target=%{_target_platform}"
export LDFLAGS="%{build_ldflags} -fuse-ld=lld"
%endif

%check -a
%pyproject_check_import sgl_kernel

%files -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
%autochangelog

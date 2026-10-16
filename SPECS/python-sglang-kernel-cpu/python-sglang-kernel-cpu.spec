# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname sglang-kernel-cpu
%global toolchain clang
%global version_upstream 0.5.21
%ifarch riscv64
%global llvm_maj_ver 22
%endif

Name:           python-%{srcname}
BuildRequires:  sglang-rpm-macros
%sglang_python_compat core
Version:        0.4.7
Release:        %autorelease
Summary:        CPU kernel library for SGLang
License:        Apache-2.0
URL:            https://github.com/sgl-project/sglang/tree/v0.5.21/python/sglang/kernels/aot
VCS:            git:https://github.com/sgl-project/sglang.git
#!RemoteAsset:  sha256:c44951b7871dac61262fc04e9fca628175758a97fa5f603c522b31dc31b94249
Source0:        https://github.com/sgl-project/sglang/archive/refs/tags/v%{version_upstream}.tar.gz#/sglang-%{version_upstream}.tar.gz
Source1:        sglang-kernel-cpu-smoke.py
BuildSystem:    pyproject
Conflicts:      python-sglang-kernel

BuildOption(prep):  -n sglang-%{version_upstream}
BuildOption(install):  -l sgl_kernel

BuildRequires:  cmake >= 3.18
BuildRequires:  clang
BuildRequires:  file
BuildRequires:  patchelf
BuildRequires:  libomp-devel
BuildRequires:  pkgconfig(numa)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(scikit-build-core) >= 0.10
BuildRequires:  sglang(python3dist(torch-cpu)) = 2.14.0
BuildRequires:  python3dist(wheel)
BuildRequires:  python-torch-sglang-2.14-devel = 2.14.0

%ifarch riscv64
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif

Requires:       sglang(python3dist(torch-cpu)) = 2.14.0

%patchlist
# RISC-V source selection and explicit cross-target ISA handling.
2000-riscv64-cpu-target-selection.patch
# Portable scalar shared-memory collectives and acquire/release state hand-off.
2001-riscv64-port-cpu-shm-collectives.patch

%description
SGLang Kernel CPU provides the CPU AOT extension used by the SGLang inference
engine. It uses the upstream CPU build configuration from SGLang 0.5.21.

%prep -a
cd python/sglang/kernels/aot
cp pyproject_cpu.toml pyproject.toml

%generate_buildrequires
cd python/sglang/kernels/aot
%sglang_pyproject_buildrequires

%build -p
cd python/sglang/kernels/aot
%ifarch riscv64
export CC=clang
export CXX=clang++
export LD=ld.lld
export AR=llvm-ar
export RANLIB=llvm-ranlib
export CMAKE_ARGS="-DSGLANG_CPU_TARGET_ARCH=riscv64 -DSGLANG_CPU_MARCH=rv64gc"
export CFLAGS="%{build_cflags} --target=%{_target_platform}"
export CXXFLAGS="%{build_cxxflags} --target=%{_target_platform}"
export LDFLAGS="%{build_ldflags} -fuse-ld=lld"
%endif

%install -a
cd python/sglang/kernels/aot
%sglang_private_rpath

%check -a
export PYTHONPATH="%{buildroot}%{_sglang_private_sitearch}"
cd %{buildroot}
%sglang_pyproject_check_import sgl_kernel
%ifarch riscv64
# Check the built extension with the Torch build dependency.
# The smoke script validates registration, two-rank reduction, and
# synchronization with the native shared-memory implementation.
LOCAL_SIZE=1 MASTER_ADDR=127.0.0.1 MASTER_PORT=29599 \
  %{python3} %{SOURCE1}
%endif

%files -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
%autochangelog

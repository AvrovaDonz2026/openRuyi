# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname apache-tvm-ffi
%global pypi_name apache_tvm_ffi
%global compat_name python-apache-tvm-ffi-0.1
%ifarch riscv64
%global llvm_maj_ver 22
%endif

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros
%sglang_python_compat
Version:        0.1.11
Release:        %autorelease
Summary:        Open ABI and FFI for machine learning systems
License:        Apache-2.0
URL:            https://tvm.apache.org/ffi/
VCS:            git:https://github.com/apache/tvm-ffi.git
#!RemoteAsset:  sha256:153cd2c5a9717804cb0bcd9b2709f22a1e5f80ed05b5a490faf5949b136eedba
Source0:        https://files.pythonhosted.org/packages/source/a/%{srcname}/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l tvm_ffi
# An optional helper which imports PyTorch
BuildOption(check):  -e tvm_ffi.utils._build_optional_torch_c_dlpack
# Native shared libraries
BuildOption(check):  -e tvm_ffi.lib.libtvm_ffi
BuildOption(check):  -e tvm_ffi.lib.libtvm_ffi_testing

BuildRequires:  cmake
BuildRequires:  file
BuildRequires:  gcc-c++
BuildRequires:  ninja >= 1.11
BuildRequires:  patchelf
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(cython)
BuildRequires:  python3dist(scikit-build-core) >= 0.10
BuildRequires:  python3dist(setuptools-scm)
%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif

%description
Apache TVM FFI provides an open ABI and foreign-function interface for machine
learning systems, including Python and C++ bindings used by XGrammar.

%generate_buildrequires
%sglang_pyproject_buildrequires

%build -p
%ifarch riscv64
export CC=clang
export CXX=clang++
export LD=ld.lld
export AR=llvm-ar
export RANLIB=llvm-ranlib
export CFLAGS="%{build_cflags} --target=%{_target_platform}"
export CXXFLAGS="%{build_cxxflags} --target=%{_target_platform}"
export LDFLAGS="%{build_ldflags} -fuse-ld=lld"
%endif

%install -a
%sglang_private_rpath
%files -f %{pyproject_files}
%doc README.md
%license LICENSE NOTICE licenses/*
%{_sglang_private_libexec}/tvm-ffi-config
%{_sglang_private_libexec}/tvm-ffi-stubgen

%changelog
%autochangelog

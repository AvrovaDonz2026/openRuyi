# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname grpcio

Name:           python-grpcio-sglang-1.84
BuildRequires:  sglang-rpm-macros
%sglang_python_compat core
Version:        1.84.0
Release:        %autorelease
Summary:        Python bindings for gRPC
License:        Apache-2.0
URL:            https://grpc.io/
VCS:            git:https://github.com/grpc/grpc
#!RemoteAsset:  sha256:19aaf172fc2edbefccce3f6e92c5150975dbe56c45744e9e87cf72ebdf85bfbe
Source0:        https://files.pythonhosted.org/packages/source/g/%{srcname}/%{srcname}-%{version}.tar.gz
Patch0:         2000-relax-cython-build-requirement.patch
BuildSystem:    pyproject

BuildOption(install):  -l grpc

BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(cython)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)
%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = 22
BuildRequires:  compiler-rt(major) = 22
BuildRequires:  lld(major) = 22
BuildRequires:  llvm(major) = 22
%endif

%description
The gRPC Python package provides Python bindings for the gRPC remote procedure
call framework.

%generate_buildrequires
%sglang_pyproject_buildrequires

%build -p
%ifarch riscv64
export CC=clang
export CXX=clang++
export AR=llvm-ar
export RANLIB=llvm-ranlib
export CFLAGS="%{build_cflags}"
export CXXFLAGS="%{build_cxxflags}"
export LDFLAGS="%{build_ldflags} -fuse-ld=lld"
%endif

%files -f %{pyproject_files}
%license LICENSE

%changelog
%autochangelog

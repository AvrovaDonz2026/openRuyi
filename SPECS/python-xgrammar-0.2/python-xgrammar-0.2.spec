# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Li Guan <guanli.oerv@isrc.iscas.ac.cn>
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname xgrammar
%global compat_name python-xgrammar-0.2

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros
%sglang_python_compat
Version:        0.2.7
Release:        %autorelease
Summary:        Fast, Flexible and Portable Structured Generation
License:        Apache-2.0
URL:            https://github.com/mlc-ai/xgrammar
#!RemoteAsset:  sha256:7674afeee5e6eff9672627b62d5ab0aa2347ea51674f4d78a5c160029f92bc3e
Source0:        https://files.pythonhosted.org/packages/source/x/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l xgrammar
# No module named 'triton'
BuildOption(check):  -e xgrammar.kernels.apply_token_bitmask_inplace_triton
BuildOption(check):  -e xgrammar.kernels.apply_token_bitmask_inplace_cuda
# No module named 'mlx'
BuildOption(check):  -e xgrammar.kernels.apply_token_bitmask_mlx
BuildOption(check):  -e xgrammar.contrib.mlxlm
# Native shared library
BuildOption(check):  -e xgrammar.libxgrammar_bindings

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  cmake
BuildRequires:  file
BuildRequires:  ninja
BuildRequires:  patchelf
BuildRequires:  sglang(python3dist(apache-tvm-ffi)) >= 0.1.11
BuildRequires:  sglang(python3dist(torch)) >= 1.10

Requires:       sglang(python3dist(apache-tvm-ffi)) >= 0.1.11
Requires:       sglang(python3dist(torch)) >= 1.10

%description
Efficient, Flexible and Portable Structured Generation.

%prep -a
sed -i 's/-Werror//g' CMakeLists.txt

%generate_buildrequires
%sglang_pyproject_buildrequires

%install -a
%sglang_private_rpath
# tvm_ffi uses wheel RECORD metadata to locate the native binding library.
echo '%{srcname}/libxgrammar_bindings.so,,' > \
    %{buildroot}%{_sglang_private_sitearch}/%{srcname}-%{version}.dist-info/RECORD

%sglang_pyproject_save_files
%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_sglang_private_sitearch}/%{srcname}-%{version}.dist-info/RECORD

%changelog
%autochangelog

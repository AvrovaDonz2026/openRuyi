# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name torch_c_dlpack_ext

Name:           python-torch-c-dlpack-ext
Version:        0.1.5
Release:        %autorelease
Summary:        Ahead-of-time PyTorch DLPack conversion extension
License:        Apache-2.0
URL:            https://github.com/apache/tvm-ffi
VCS:            git:https://github.com/apache/tvm-ffi.git
#!RemoteAsset:  sha256:d06f0357d575d22a168cc77acb9020fc4bae30968ceb6718a055dcbe92bacabe
Source0:        https://files.pythonhosted.org/packages/source/t/torch-c-dlpack-ext/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(install):  -l torch_c_dlpack_ext

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(setuptools) >= 61
BuildRequires:  python3dist(torch)

Requires:       python3dist(torch)

%description
Torch C DLPack Extension is an ahead-of-time compiled PyTorch extension that
provides fast DLPack conversion through the DLPack v1.2 C exchange API.

%generate_buildrequires
%pyproject_buildrequires

%check -a
# Importing the extension requires a matching PyTorch ABI at runtime.
%pyproject_check_import torch_c_dlpack_ext

%files -f %{pyproject_files}
%license LICENSE

%changelog
%autochangelog

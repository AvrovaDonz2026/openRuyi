# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name flash_attn_4
%global upstream_version 4.0.0b34

Name:           python-flash-attn-4
Version:        4.0.0~b34
Release:        %autorelease
Summary:        CuTeDSL implementation of FlashAttention
License:        BSD-3-Clause
URL:            https://github.com/Dao-AILab/flash-attention
VCS:            git:https://github.com/Dao-AILab/flash-attention.git
#!RemoteAsset:  sha256:93118237c0d2e80b76bedd4e3c8b21a780d3119a42868ea26b974ae88d36b277
Source0:        https://files.pythonhosted.org/packages/77/4b/846fc5e941f4116185e268c6eb77c3d430736558239dd23bd941a6a293c1/%{pypi_name}-%{upstream_version}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(install):  flash_attn.cute +auto

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(setuptools) >= 75
BuildRequires:  python3dist(setuptools-scm) >= 8

Requires:       python3dist(apache-tvm-ffi) >= 0.1.11
Requires:       python3dist(einops)
Requires:       python3dist(nvidia-cutlass-dsl) >= 4.6.2
Requires:       python3dist(quack-kernels) >= 0.5.3
Requires:       python3dist(torch)
Requires:       python3dist(torch-c-dlpack-ext)
Requires:       python3dist(typing-extensions)

%description
FlashAttention-4 provides a CuTeDSL implementation of FlashAttention for
recent NVIDIA GPUs.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

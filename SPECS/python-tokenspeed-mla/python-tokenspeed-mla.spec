# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname tokenspeed
%global commit 5c3500254a82e85de573a4b121367921f0827625

Name:           python-tokenspeed-mla
Version:        0.1.8
Release:        %autorelease
Summary:        TokenSpeed MLA kernels for NVIDIA Blackwell GPUs
License:        MIT
URL:            https://github.com/lightseekorg/tokenspeed
VCS:            git:https://github.com/lightseekorg/tokenspeed.git
#!RemoteAsset:  sha256:5a9cb82ca52bba8c7fd1a79ceaff8a19d6e9cfe0faed60f739c98e333d12d38f
Source0:        https://github.com/lightseekorg/tokenspeed/archive/%{commit}.tar.gz#/%{srcname}-%{commit}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(prep):  -n %{srcname}-%{commit}/tokenspeed-mla
BuildOption(install):  -l tokenspeed_mla
BuildOption(install):  +auto

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools) >= 69.5.1
BuildRequires:  python3dist(wheel)

Requires:       python3dist(apache-tvm-ffi) >= 0.1.5
Requires:       python3dist(apache-tvm-ffi) <= 0.1.11
Requires:       python3dist(nvidia-cutlass-dsl)
Requires:       python3dist(tokenspeed-triton) >= 3.7.10.post20260531
Requires:       python3dist(torch)

%description
TokenSpeed MLA provides source-level CuTe DSL and Triton kernels for NVIDIA
Blackwell SM100 and SM103 inference. Kernels compile at runtime and no CUDA
compiler is required to install the Python package; execution requires a
compatible NVIDIA GPU and CUDA stack.

%generate_buildrequires
%pyproject_buildrequires

%check -a
# Runtime kernel tests require NVIDIA Blackwell hardware and are unavailable
# on the RISC-V build host.
%pyproject_check_import tokenspeed_mla

%files -f %{pyproject_files}
%license LICENSE
%doc THIRDPARTYNOTICES

%changelog
%autochangelog

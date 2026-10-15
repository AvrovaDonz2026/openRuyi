# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name quack_kernels

Name:           python-quack-kernels
Version:        0.6.5
Release:        %autorelease
Summary:        CUDA kernels for machine learning workloads
License:        Apache-2.0
URL:            https://github.com/Dao-AILab/quack
VCS:            git:https://github.com/Dao-AILab/quack.git
#!RemoteAsset:  sha256:dd9405a4a6fa35fc3a5a18fe35b46a14b0bf7e3ad9fe2451903e355047ac471d
Source0:        https://files.pythonhosted.org/packages/5f/18/6c2a20d00dff254f154fb3b951f4e5a0377a60122c17385e5f08d5f5b5e1/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject
# Upstream requires CUDA toolkit 12.9+ and NVIDIA H100, B200/B300, or RTX 50
# GPUs; no RISC-V CUDA toolkit target is supported by this CUDA-only package.
ExclusiveArch:  x86_64 aarch64

BuildOption(install):  quack +auto

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(setuptools)

Requires:       python3dist(apache-tvm-ffi) >= 0.1.6
Requires:       python3dist(einops)
Requires:       python3dist(nvidia-cutlass-dsl) >= 4.7
Requires:       python3dist(torch)
Requires:       python3dist(torch-c-dlpack-ext)

%description
Quack Kernels provides CUDA kernel implementations for machine learning
operations.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

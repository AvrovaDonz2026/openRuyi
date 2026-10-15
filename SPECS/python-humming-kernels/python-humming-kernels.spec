# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname humming-kernels
%global pypi_name humming_kernels

Name:           python-%{srcname}
Version:        0.1.16
Release:        %autorelease
Summary:        JIT-compiled GPU GEMM kernels for quantized inference
License:        Apache-2.0
URL:            https://github.com/vllm-project/humming
VCS:            git:https://github.com/vllm-project/humming.git
#!RemoteAsset:  sha256:a5356a63c4adf6c16c46f541749dec90fc2d49cf29ebc33ac05e23c744731809
Source0:        https://files.pythonhosted.org/packages/70/d2/e286acb9f594f998bbc2d99617966a4f01a603c699d829793a86a42c2440/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject
# Upstream requires NVCC and targets NVIDIA SM75+ GPUs; no RISC-V CUDA
# toolkit target is supported by this CUDA-only package.
ExclusiveArch:  x86_64 aarch64

BuildOption(install):  humming +auto

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(setuptools) >= 77.0.3
BuildRequires:  python3dist(setuptools-scm) >= 8
BuildRequires:  python3dist(wheel)

Requires:       python3dist(cuda-bindings)
Requires:       python3dist(jinja2)
Requires:       python3dist(numpy)
Requires:       python3dist(safetensors)
Requires:       python3dist(tabulate)
Requires:       python3dist(torch) >= 2.7
Requires:       python3dist(tqdm)
Requires:       python3dist(triton)

%description
Humming Kernels provides JIT-compiled GPU matrix multiplication kernels for
quantized inference.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

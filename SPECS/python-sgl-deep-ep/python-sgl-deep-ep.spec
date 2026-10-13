# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname DeepEP
%global pypi_name sgl-deep-ep

Name:           python-sgl-deep-ep
Version:        0.1.2
Release:        %autorelease
Summary:        CUDA expert parallel communication kernels for SGLang
License:        MIT
URL:            https://github.com/sgl-project/DeepEP
VCS:            git:https://github.com/sgl-project/DeepEP.git
#!RemoteAsset:  sha256:86057d9b7732146ebacadc925568e72f13319d7ecce7793ff9429c0e6c8fe12f
Source0:        https://github.com/sgl-project/DeepEP/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
#!RemoteAsset:  sha256:1f2ddcf7f913a82e10058d89a7501fa6afee387e9a662f42fa5eabcc39054e77
Source1:        https://github.com/fmtlib/fmt/archive/a4c7e17133ee9cb6a2f45545f6e974dd3c393efa.tar.gz#/fmt-a4c7e171.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(prep):  -n %{srcname}-%{version}

BuildRequires:  cuda-toolkit
BuildRequires:  gcc-c++
BuildRequires:  nccl-devel
BuildRequires:  nvshmem-devel
BuildRequires:  pkgconfig(python3)
BuildRequires:  pybind11-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(ninja)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(torch) = 2.14.0
BuildRequires:  python3dist(wheel)

Requires:       python3dist(torch) = 2.14.0
Requires:       nccl
Requires:       nvshmem

%description
SGL DeepEP is SGLang's CUDA expert parallel communication extension. It builds
the DeepEP extension for NVIDIA SM90-class GPUs and requires a CUDA toolkit,
NCCL, and NVSHMEM at build and runtime.

%prep -a
sed -i "s/name='deep_ep'/name='sgl-deep-ep'/; s/version=get_package_version()/version='0.1.2'/" setup.py
mkdir -p third-party/fmt
tar -xf %{SOURCE1} --strip-components=1 -C third-party/fmt

%generate_buildrequires
%pyproject_buildrequires

%build -p
export TORCH_CUDA_ARCH_LIST="9.0"
export EP_NUM_TOPK_IDX_BITS=32
%pyproject_wheel

%install -p
%pyproject_install

%check -a
# DeepEP tests require NVIDIA GPUs, NCCL communicators and NVSHMEM transports.
%pyproject_check_import deep_ep

%files -f %{pyproject_files}
%license LICENSE

%changelog
%autochangelog

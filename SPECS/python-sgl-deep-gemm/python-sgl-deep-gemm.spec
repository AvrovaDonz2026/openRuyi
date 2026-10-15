# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname DeepGEMM
%global pypi_name sgl-deep-gemm

Name:           python-sgl-deep-gemm
Version:        0.2.0
Release:        %autorelease
Summary:        CUDA FP8 GEMM kernels for SGLang
License:        Apache-2.0
URL:            https://github.com/sgl-project/DeepGEMM
VCS:            git:https://github.com/sgl-project/DeepGEMM.git
#!RemoteAsset:  sha256:77e9d6384e343e019d177e01ccf2d11d0c3be3083c27a74cd3f44e0e7d2887c5
Source0:        https://github.com/sgl-project/DeepGEMM/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
#!RemoteAsset:  sha256:2e5890306557bd87136e1d6914e4ee42536050b9116433848175520fd15991f2
Source1:        https://github.com/NVIDIA/cutlass/archive/f3fde58372d33e9a5650ba7b80fc48b3b49d40c8.tar.gz#/cutlass-f3fd583.tar.gz
#!RemoteAsset:  sha256:621bef0c728895dc0267bf8d5137c5174db862361e790b5591272a06ba139f0d
Source2:        https://github.com/deepseek-ai/DeepJIT/archive/e5bdee2bc4ca519eba00cfc5f0c6e950e6a96a16.tar.gz#/deepjit-e5bdee2.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(prep):  -n %{srcname}-%{version}
BuildOption(install):  -l deep_gemm
BuildOption(install):  +auto

BuildRequires:  cuda-toolkit
BuildRequires:  elfutils-libelf-devel
BuildRequires:  gcc-c++
BuildRequires:  ninja
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools) >= 77
BuildRequires:  python3dist(torch) = 2.14.0
BuildRequires:  python3dist(apache-tvm-ffi) = 0.1.11
BuildRequires:  python3dist(wheel)

Requires:       python3dist(torch) = 2.14.0
Requires:       python3dist(apache-tvm-ffi) = 0.1.11

%description
SGL DeepGEMM is SGLang's CUDA FP8 GEMM extension for Hopper and Blackwell
GPUs. The package includes the runtime JIT headers and builds its TVM-FFI CUDA
extension from the matching release source.

%prep -a
sed -i "s/name='deep_gemm'/name='sgl-deep-gemm'/; s/version=get_package_version()/version='0.2.0'/" setup.py
sed -i "/'bdist_wheel': CachedWheelsCommand,/d" setup.py
printf '%s\n' '[build-system]' 'requires = ["setuptools>=77.0.0", "wheel"]' 'build-backend = "setuptools.build_meta"' '' '[project]' 'name = "sgl-deep-gemm"' 'version = "0.2.0"' 'description = "SGLang fork of DeepGemm"' 'readme = "sgl_deep_gemm/README.md"' 'requires-python = ">=3.10"' 'license = {file = "sgl_deep_gemm/LICENSE"}' 'dependencies = ["apache-tvm-ffi==0.1.11"]' > pyproject.toml
mkdir -p third-party/cutlass third-party/deep_jit
tar -xf %{SOURCE1} --strip-components=1 -C third-party/cutlass
tar -xf %{SOURCE2} --strip-components=1 -C third-party/deep_jit

%generate_buildrequires
%pyproject_buildrequires

%build -p
export DG_USE_LOCAL_VERSION=0

%check -a
# Numerical and sanitizer tests require CUDA SM90/SM100 hardware.
%pyproject_check_import deep_gemm

%files -f %{pyproject_files}
%license LICENSE

%changelog
%autochangelog

# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname petit-kernel
%global toolchain clang
%global llvm_maj_ver 22

Name:           python-%{srcname}-rocm
Version:        0.0.2
Release:        %autorelease
Summary:        Optimized FP4 kernels for AMD GPUs
License:        BSD-3-Clause
URL:            https://github.com/causalflow-ai/petit-kernel
VCS:            git:https://github.com/causalflow-ai/petit-kernel.git
#!RemoteAsset:  sha256:a91fff2ebba78487d44865f2bb6a69270838403acc99114b0cf70e71c564fd92
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(prep):  -n %{srcname}-%{version}
BuildOption(install):  petit_kernel

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  cmake
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblaslt)
BuildRequires:  cmake(rocblas)
BuildRequires:  cmake(absl)
BuildRequires:  cmake(fmt)
BuildRequires:  cmake(gflags)
BuildRequires:  cmake(GTest)
BuildRequires:  cmake(RapidJSON)
BuildRequires:  cmake(spdlog)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  hipcc
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python-torch-rocm-devel >= 2.5.1
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools) >= 42
BuildRequires:  python3dist(wheel)
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%global __requires_exclude ^python3(\\.[0-9]+)?dist\\(torch\\)
Requires:       python-torch-rocm >= 2.5.1
Provides:       python3-%{srcname}-rocm = %{version}-%{release}
Provides:       python3-%{srcname}-rocm%{?_isa} = %{version}-%{release}

%patchlist
# Avoid network downloads by using the system CMake dependencies.
2000-Use-system-CMake-dependencies.patch

%description
Petit Kernel provides optimized FP16/BF16 x FP4 GPU kernels for AMD GPUs. It
enables inference frameworks such as SGLang to run NVFP4 quantized models on
AMD CDNA2 and CDNA3 accelerators.

%generate_buildrequires
%pyproject_buildrequires -R

%build -p
export ROCM_HOME=%{_prefix}
export ROCM_PATH="$(hipconfig -R)"
export HIP_PATH="$(hipconfig -p)"
export HIP_CLANG_PATH=%{rocmllvm_bindir}
export PATH=%{rocmllvm_bindir}:$PATH
export CC=%{rocmllvm_bindir}/clang
export CXX=%{rocmllvm_bindir}/clang++
export PYTORCH_ROCM_ARCH=%{rocm_gpu_list_default}
export CMAKE_ARGS="-DCMAKE_PREFIX_PATH=%{_prefix};$(%{python3} -c 'import torch; print(torch.utils.cmake_prefix_path)') -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++ -DCMAKE_HIP_ARCHITECTURES=%{rocm_gpu_list_default}"

%check -a
%pyproject_check_import

%files -f %{pyproject_files}
%doc README.md
%license LICENSE.txt

%changelog
%autochangelog

# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname cudnn-frontend
%global source_root cudnn-frontend-%{version}

Name:           python-nvidia-cudnn-frontend
Version:        1.30.0
Release:        %autorelease
Summary:        NVIDIA cuDNN Frontend Python and C++ graph API
License:        Apache-2.0 AND MIT
URL:            https://github.com/NVIDIA/cudnn-frontend
VCS:            git:https://github.com/NVIDIA/cudnn-frontend.git
#!RemoteAsset:  sha256:2e6a28661b91c0f43c2b24809750b480a93975bcf949c9715e540a7ab8575b31
Source0:        https://github.com/NVIDIA/cudnn-frontend/archive/refs/tags/v%{version}.tar.gz#/%{source_root}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(prep):  -n %{source_root}
BuildOption(install):  -l cudnn

BuildRequires:  cmake >= 3.18
BuildRequires:  cuda-toolkit
BuildRequires:  gcc-c++
BuildRequires:  ninja
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(apache-tvm-ffi) >= 0.1.11
BuildRequires:  python3dist(nvidia-cutlass-dsl) >= 4.6.2
BuildRequires:  python3dist(pybind11) >= 2.13
BuildRequires:  python3dist(pybind11) < 3
BuildRequires:  python3dist(setuptools) >= 64
BuildRequires:  python3dist(wheel)

Requires:       python3dist(apache-tvm-ffi) >= 0.1.11
Requires:       python3dist(nvidia-cutlass-dsl) >= 4.6.2

%description
cuDNN Frontend provides NVIDIA's Python and header-only C++ graph APIs for
cuDNN, including graph operations and optimized attention and GEMM kernels.

%generate_buildrequires
%pyproject_buildrequires

%build -p

%install -p

%files -f %{pyproject_files}
%doc README.md
%license LICENSE.txt LICENSE-MIT.txt NOTICE

%changelog
%autochangelog

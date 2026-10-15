# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname cuda-python
%global commit cuda-core-v1.2.1
%global source_root cuda-python-%{commit}

Name:           python-cuda-core
Version:        1.2.1
Release:        %autorelease
Summary:        Pythonic CUDA runtime and driver APIs
License:        Apache-2.0
URL:            https://github.com/NVIDIA/cuda-python
VCS:            git:https://github.com/NVIDIA/cuda-python.git
#!RemoteAsset:  sha256:7d5841068f9d0123658f45fd679bd81f92b6bd001776ca9e1b211938ab09bc22
Source0:        https://github.com/NVIDIA/cuda-python/archive/refs/tags/%{commit}.tar.gz#/%{source_root}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(prep):  -n %{source_root}/cuda_core
BuildOption(install):  -l cuda

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(cython) >= 3.2.5
BuildRequires:  python3dist(cython) < 3.3
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(setuptools) >= 80
BuildRequires:  python3dist(setuptools-scm) >= 8
BuildRequires:  python3dist(cuda-pathfinder) >= 1.5
BuildRequires:  python3dist(cuda-bindings) = 13.4.3
BuildRequires:  python3dist(wheel)

Requires:       python3dist(cuda-pathfinder) >= 1.4.2
Requires:       python3dist(numpy)

%description
cuda.core provides Pythonic access to CUDA runtime, driver, and JIT compiler
functionality.

%prep -a

%generate_buildrequires
%pyproject_buildrequires

%build -p

%install -p

%files -f %{pyproject_files}
%license LICENSE

%changelog
%autochangelog

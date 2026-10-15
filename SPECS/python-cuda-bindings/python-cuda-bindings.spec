# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname cuda-python
%global commit v13.4.3

Name:           python-cuda-bindings
Version:        13.4.3
Release:        %autorelease
Summary:        Low-level Python bindings for CUDA APIs
License:        Apache-2.0
URL:            https://github.com/NVIDIA/cuda-python
VCS:            git:https://github.com/NVIDIA/cuda-python.git
#!RemoteAsset:  sha256:6bab21767c717a0ebbef2b731c500f3653c58419fb7d80b91e32379c11c841ed
Source0:        https://github.com/NVIDIA/cuda-python/archive/refs/tags/%{commit}.tar.gz#/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(prep):  -n %{srcname}-%{version}/cuda_bindings
BuildOption(install):  -l cuda

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(cython) >= 3.2.5
BuildRequires:  python3dist(cython) < 3.3
BuildRequires:  python3dist(setuptools) >= 80
BuildRequires:  python3dist(setuptools-scm) >= 8
BuildRequires:  python3dist(wheel)
BuildRequires:  python3dist(cuda-pathfinder) >= 1.5

Requires:       python3dist(cuda-pathfinder) >= 1.4.2

%description
CUDA Bindings provides low-level Python bindings to the CUDA driver, runtime,
NVRTC, nvJitLink, NVVM, nvFatbin, cuFile, and NVML APIs.

%prep -a

%generate_buildrequires
%pyproject_buildrequires

%build -p

%install -p

%files -f %{pyproject_files}
%license LICENSE

%changelog
%autochangelog

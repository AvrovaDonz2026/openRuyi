# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname cuda-python
%global commit cuda-pathfinder-v1.8.3
%global source_root cuda-python-%{commit}

Name:           python-cuda-pathfinder
Version:        1.8.3
Release:        %autorelease
Summary:        CUDA component discovery utilities
License:        Apache-2.0
URL:            https://github.com/NVIDIA/cuda-python
VCS:            git:https://github.com/NVIDIA/cuda-python.git
#!RemoteAsset:  sha256:62c9b1e289b5ac9b962eedce368d568a25f6edf6b08100e0c117bf4e24eae1f4
Source0:        https://github.com/NVIDIA/cuda-python/archive/refs/tags/%{commit}.tar.gz#/%{source_root}.tar.gz
BuildSystem:    pyproject
BuildArch:      noarch

BuildOption(prep):  -n %{source_root}/cuda_pathfinder
BuildOption(install):  -l cuda

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(setuptools) >= 80
BuildRequires:  python3dist(setuptools-scm) >= 8
BuildRequires:  python3dist(wheel)

%description
CUDA Pathfinder locates CUDA components installed in a Python environment or
on the system.

%prep -a

%generate_buildrequires
%pyproject_buildrequires

%build -p

%install -p

%files -f %{pyproject_files}
%license LICENSE

%changelog
%autochangelog

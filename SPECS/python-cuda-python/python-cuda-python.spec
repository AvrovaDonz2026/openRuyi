# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname cuda-python
%global commit v13.4.1

Name:           python-%{srcname}
Version:        13.4.1
Release:        %autorelease
Summary:        Python interfaces to the CUDA platform
License:        Apache-2.0
URL:            https://github.com/NVIDIA/cuda-python
VCS:            git:https://github.com/NVIDIA/cuda-python.git
#!RemoteAsset:  sha256:873b52ec61980eae2cece989f8b136c7fdac3135182feca905c95592cd6a223a
Source0:        https://github.com/NVIDIA/cuda-python/archive/refs/tags/%{commit}.tar.gz#/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(prep):  -n %{srcname}-%{version}/cuda_python
BuildOption(install):  -M

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(setuptools) >= 80
BuildRequires:  python3dist(setuptools-scm) >= 8
BuildRequires:  python3dist(wheel)

Requires:       python3dist(cuda-bindings) >= 13.4.1
Requires:       python3dist(cuda-core) >= 1.2.0
Requires:       python3dist(cuda-pathfinder) >= 1.8.3

%description
CUDA Python provides Python interfaces to the CUDA platform, including the
low-level bindings and CUDA component discovery tools.

%prep -a

%generate_buildrequires
%pyproject_buildrequires

%build -p

%install -p

%files -f %{pyproject_files}
%license LICENSE

%changelog
%autochangelog

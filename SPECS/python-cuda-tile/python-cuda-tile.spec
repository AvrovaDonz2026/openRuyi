# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname cutile-python
%global commit 1.6.0

Name:           python-cuda-tile
Version:        1.6.0
Release:        %autorelease
Summary:        Python interface to NVIDIA CUDA Tile
License:        Apache-2.0
URL:            https://github.com/NVIDIA/cutile-python
VCS:            git:https://github.com/NVIDIA/cutile-python.git
#!RemoteAsset:  sha256:c4f42537bbcb6919840dff2dea425fd09fa96ee6869c2bac0fb66aae045cd06b
Source0:        https://github.com/NVIDIA/cutile-python/archive/refs/tags/v%{commit}.tar.gz#/%{srcname}-%{commit}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(prep):  -n %{srcname}-%{commit}
BuildOption(install):  -l cuda cutile_cache

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(setuptools) = 84.0.0
BuildRequires:  python3dist(wheel)

Requires:       python3dist(typing-extensions)

%description
CUDA Tile provides a Python interface for expressing and compiling GPU kernels
with NVIDIA CUDA Tile.

%prep -a

%generate_buildrequires
%pyproject_buildrequires

%build -p

%install -p

%files -f %{pyproject_files}
%license LICENSES/Apache-2.0.txt

%changelog
%autochangelog

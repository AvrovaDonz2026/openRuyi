# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname cache-dit

Name:           python-cache-dit
Version:        1.3.0
Release:        %autorelease
Summary:        Fast and efficient caching for diffusion transformers
License:        Apache-2.0
URL:            https://github.com/vipshop/cache-dit
VCS:            git:https://github.com/vipshop/cache-dit
#!RemoteAsset:  sha256:01a5ac7075420e7b94e85a57686dbe7afbf37d3926036e9f8ec377e13aeb954c
Source:         https://github.com/vipshop/cache-dit/archive/refs/tags/v%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l cache_dit

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools) >= 61
BuildRequires:  python3dist(setuptools-scm) >= 8
BuildRequires:  python3dist(wheel)

Requires:       python3dist(diffusers) >= 0.36
Requires:       python3dist(packaging)
Requires:       python3dist(pyyaml)
Requires:       python3dist(torch) >= 2.7.1
Requires:       python3dist(transformers) >= 4.55.2

Provides:       python3-cache-dit = %{version}-%{release}
%python_provide python3-cache-dit

%description
Cache-DiT provides caching methods to improve diffusion transformer
inference performance.

%prep -p
export SETUPTOOLS_SCM_PRETEND_VERSION='%{version}'

%generate_buildrequires
%pyproject_buildrequires

%build -p
export SETUPTOOLS_SCM_PRETEND_VERSION='%{version}'

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

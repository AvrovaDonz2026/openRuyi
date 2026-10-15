# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname proglog

Name:           python-%{srcname}
Version:        0.1.12
Release:        %autorelease
Summary:        Progress logging system for Python
License:        MIT
URL:            https://github.com/Edinburgh-Genome-Foundry/Proglog
VCS:            git:https://github.com/Edinburgh-Genome-Foundry/Proglog.git
#!RemoteAsset:  sha256:361ee074721c277b89b75c061336cb8c5f287c92b043efa562ccf7866cda931c
Source0:        https://files.pythonhosted.org/packages/source/p/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(tqdm)

Requires:       python3dist(tqdm)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Proglog provides a progress logging system for Python libraries.

%generate_buildrequires
%pyproject_buildrequires

%check -a
%pytest -q tests

%files -f %{pyproject_files}
%doc README.rst
%license LICENSE

%changelog
%autochangelog

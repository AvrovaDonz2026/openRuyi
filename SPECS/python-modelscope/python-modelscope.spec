# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname modelscope

Name:           python-modelscope
Version:        1.40.2
Release:        %autorelease
Summary:        Model-as-a-Service framework for machine learning
License:        Apache-2.0
URL:            https://pypi.org/project/modelscope/
VCS:            git:https://github.com/modelscope/modelscope
#!RemoteAsset:  sha256:7a642cef8c144c28c4ddcc37db5fd803f5481f0d78a7f26c2b9e0e2a225b528c
Source0:        https://files.pythonhosted.org/packages/source/m/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(filelock)
BuildRequires:  python3dist(modelscope-hub) >= 0.4.6
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(requests) >= 2.25
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(tqdm) >= 4.64.0
BuildRequires:  python3dist(urllib3) >= 1.26
BuildRequires:  python3dist(wheel)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

Requires:       python3dist(filelock)
Requires:       python3dist(modelscope-hub) >= 0.4.6
Requires:       python3dist(packaging)
Requires:       python3dist(requests) >= 2.25
Requires:       python3dist(tqdm) >= 4.64.0
Requires:       python3dist(urllib3) >= 1.26

%description
ModelScope provides unified interfaces for inference, training, and evaluation
of machine learning models across multiple domains.

%generate_buildrequires
%pyproject_buildrequires

%check
%pyproject_check_import modelscope

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

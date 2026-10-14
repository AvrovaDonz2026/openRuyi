# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname remote-pdb
%global pypi_name remote_pdb

Name:           python-%{srcname}
Version:        2.1.0
Release:        %autorelease
Summary:        Remote Python debugger over TCP sockets
License:        BSD-2-Clause
URL:            https://github.com/ionelmc/python-remote-pdb
#!RemoteAsset:  sha256:2d70c6f41e0eabf0165e8f1be58f82aa7a605aaeab8f2aefeb9ce246431091c1
Source0:        https://files.pythonhosted.org/packages/source/r/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{pypi_name}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(process-tests)
BuildRequires:  python3dist(psutil)
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(setuptools)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Remote PDB provides a Python debugger that can be accessed over TCP sockets.

%generate_buildrequires
%pyproject_buildrequires

%check -a
%pytest -q tests

%files -f %{pyproject_files}
%doc README.rst CHANGELOG.rst

%changelog
%autochangelog

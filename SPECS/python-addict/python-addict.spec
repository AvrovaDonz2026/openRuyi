# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname addict

Name:           python-%{srcname}
Version:        2.4.0
Release:        %autorelease
Summary:        Dictionary with attribute-style access
License:        MIT
URL:            https://github.com/mewwts/addict
#!RemoteAsset:  sha256:b3b2210e0e067a281f5646c8c5db92e99b7231ea8b0eb5f74dbdf9e259d4e494
Source0:        https://files.pythonhosted.org/packages/source/a/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(setuptools)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Addict provides a dictionary subclass whose items can be read and written
using either attribute or item syntax.

%generate_buildrequires
%pyproject_buildrequires

%check -a
%pytest -q test_addict.py

%files -f %{pyproject_files}
%doc README.md

%changelog
%autochangelog

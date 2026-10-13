# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname outlines

Name:           python-%{srcname}
Version:        1.2.13
Release:        %autorelease
Summary:        Probabilistic generative model programming
License:        Apache-2.0
URL:            https://github.com/dottxt-ai/outlines
#!RemoteAsset:  sha256:d48b6e92f15d32536a1b2bf73edc88ef78f21a331e5c4fb71f76535901a3abb1
Source0:        https://files.pythonhosted.org/packages/source/o/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Outlines provides tools for controlling language model generation with regular
expressions, JSON schemas, and context-free grammars.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

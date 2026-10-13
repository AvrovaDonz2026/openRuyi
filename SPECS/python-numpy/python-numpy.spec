# SPDX-FileCopyrightText: (C) 2025 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2025 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: yyjeqhc <jialin.oerv@isrc.iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname numpy

Name:           python-%{srcname}
Version:        2.5.4
Release:        %autorelease
Summary:        NumPy: array processing for numbers, strings, records, and objects
License:        BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0
URL:            https://github.com/numpy/numpy
#!RemoteAsset:  sha256:9a94cf751c9ad8ebaa835bcd3d40dacf8534ad086b88c38029b65123c7999d2a
Source:         https://files.pythonhosted.org/packages/source/n/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(build):  -Csetup-args=-Dblas=openblas
BuildOption(build):  -Csetup-args=-Dlapack=openblas
BuildOption(install):  -l %{srcname} -L

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  gcc-c++
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(wheel)
BuildRequires:  python3dist(meson-python) >= 0.18.0
BuildRequires:  python3dist(cython) >= 3.1.0
BuildRequires:  pkgconfig
BuildRequires:  openblas-devel
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(hypothesis)

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}
Provides:       python3-%{srcname}-f2py = %{version}-%{release}
Provides:       python3-%{srcname}-f2py%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}-f2py

%description
NumPy is the fundamental package for scientific computing with Python.
It contains among other things:
- a powerful N-dimensional array object
- sophisticated (broadcasting) functions
- tools for integrating C/C++ and Fortran code
- useful linear algebra, Fourier transform, and random number capabilities

%generate_buildrequires
%pyproject_buildrequires -R

%files -f %{pyproject_files}
%doc README.md THANKS.txt
%license LICENSE.txt
%{_bindir}/f2py
%{_bindir}/numpy-config

%changelog
%autochangelog

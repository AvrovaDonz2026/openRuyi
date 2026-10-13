# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: Suyun <ziyu.oerv@isrc.iscas.ac.cn>
# SPDX-FileContributor: yyjeqhc <jialin.oerv@isrc.iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname scipy

%global _pyproject_wheeldir %{_builddir}/%{name}-%{version}-%{release}/pyproject-wheeldir

Name:           python-%{srcname}
Version:        1.18.1
Release:        %autorelease
Summary:        Scientific Tools for Python
License:        BSD-3-Clause AND LGPL-2.0-or-later AND BSL-1.0
URL:            https://www.scipy.org
#!RemoteAsset:  sha256:52c4b7422442aba924d03ad4019852b08a92e64ea187b933135687bfe2747307
Source0:        https://files.pythonhosted.org/packages/source/s/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(build):  -Csetup-args=-Dblas=openblas
BuildOption(build):  -Csetup-args=-Dlapack=openblas
BuildOption(install):  -l %{srcname} -L
# We don't have python3dist(pooch)
BuildOption(check):  -e scipy.datasets.tests.test_data
# We have python3dist(hypothesis), but will it cause circular dependencies?
BuildOption(check):  -e scipy.integrate.tests.test_quadrature
BuildOption(check):  -e scipy.ndimage.tests.test_filters
BuildOption(check):  -e scipy.special.tests.test_support_alternative_backends
BuildOption(check):  -e scipy.stats.tests.test_continuous
BuildOption(check):  -e scipy.stats.tests.test_stats
# No module named 'marray'
BuildOption(check):  -e scipy.stats.tests.test_marray

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  gcc-fortran
BuildRequires:  python3dist(cython) >= 3.2.0
BuildRequires:  python3dist(meson-python) >= 0.15.0
BuildRequires:  python3dist(numpy) >= 2.0.0
BuildRequires:  python3dist(pybind11) >= 2.13.2
BuildRequires:  python3dist(pythran) >= 0.18.1
BuildRequires:  python3dist(pip)
BuildRequires:  pkgconfig(openblas64)
# For tests
BuildRequires:  python3dist(pytest)

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
SciPy is a collection of algorithms for scientific computing, including
optimization, integration, interpolation, signal processing, linear algebra,
and statistics.

%generate_buildrequires
%pyproject_buildrequires -R

%build -p
export FC=gfortran

%files -f %{pyproject_files}

%changelog
%autochangelog

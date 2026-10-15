# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname pandas

Name:           python-pandas-2
Version:        2.3.3
Release:        %autorelease
Summary:        Version 2 compatibility build of pandas
License:        BSD-3-Clause
URL:            https://pandas.pydata.org/
#!RemoteAsset:  sha256:e05e1af93b977f7eafa636d043f9f94c7ee3ac81af99c13508215942e64c993b
Source0:        https://files.pythonhosted.org/packages/source/p/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject
BuildRequires:  sglang-rpm-macros
%sglang_python_compat extras

BuildOption(install):  %{srcname}
BuildOption(check):  -e pandas.core.arrays.arrow.extension_types
BuildOption(check):  -e 'pandas.tests.*'

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  file
BuildRequires:  patchelf
BuildRequires:  clang
BuildRequires:  llvm
BuildRequires:  python3dist(cython) < 4.0.0a0
BuildRequires:  python3dist(meson) >= 1.2.1
BuildRequires:  python3dist(meson) < 2
BuildRequires:  python3dist(meson-python) >= 0.13.1
BuildRequires:  python3dist(numpy) >= 2.0
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(versioneer[toml])
BuildRequires:  python3dist(wheel)
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(hypothesis)
BuildRequires:  python3dist(jinja2)

%description
Version 2 of pandas, provided for applications whose declared dependency range
excludes the current upstream major release.

%generate_buildrequires
%sglang_pyproject_buildrequires -p

%build
export CC=clang
export CXX=clang++
%sglang_pyproject_build

%install -a
%sglang_private_rpath

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

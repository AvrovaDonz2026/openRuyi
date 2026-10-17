# SPDX-FileCopyrightText: (C) 2025 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2025 openRuyi Project Contributors
# SPDX-FileContributor: yyjeqhc <jialin.oerv@isrc.iscas.ac.cn>
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname scikit-build-core
%global pypi_name scikit_build_core
%global compat_name python-scikit-build-core-1
# skip the tests as some deps we don't have yet.
%bcond test 0

Name:           %{compat_name}
Version:        1.1.1
Release:        %autorelease
Summary:        Build backend for CMake based projects
License:        Apache-2.0 AND MIT
URL:            https://github.com/scikit-build/scikit-build-core
#!RemoteAsset:  sha256:e347a59193c878ac56a363e57506938652a6dd8c965790cb1cbc6bc7e8d5abad
Source:         https://files.pythonhosted.org/packages/source/s/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildRequires:  sglang-rpm-macros
%sglang_python_compat
BuildSystem:    pyproject

BuildOption(install):  -l scikit_build_core

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(hatchling)
BuildRequires:  python3dist(hatch-vcs)
%if %{with test}
BuildRequires:  cmake
BuildRequires:  ninja
BuildRequires:  gcc-c++
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(virtualenv)
BuildRequires:  python3dist(numpy)
%endif

%description
A next generation Python CMake adapter and Python API for plugins.

%prep -a
cp -p src/scikit_build_core/_vendor/pyproject_metadata/LICENSE LICENSE-pyproject-metadata

%generate_buildrequires
%sglang_pyproject_buildrequires

%if %{with test}
%check -a
%sglang_pyproject_check_import -e scikit_build_core
%endif

%files -f %{pyproject_files}
%doc README.md
%license LICENSE LICENSE-pyproject-metadata
%{_sglang_private_libexec}/scikit-build
%{_sglang_private_libexec}/scikit-build-core

%changelog
%autochangelog

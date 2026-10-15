# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname fsspec

Name:           python-%{srcname}-2026-2
Version:        2026.2.0
Release:        %autorelease
Summary:        File-system specification for Python
License:        BSD-3-Clause
URL:            https://filesystem-spec.readthedocs.io/
VCS:            git:https://github.com/fsspec/filesystem_spec
#!RemoteAsset:  sha256:6544e34b16869f5aacd5b90bdf1a71acb37792ea3ddf6125ee69a22a53fb8bff
Source0:        https://files.pythonhosted.org/packages/source/f/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  sglang-rpm-macros
%sglang_python_compat extras
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}
BuildOption(install):  +auto
BuildOption(check):  -e 'fsspec.tests.*'
BuildOption(check):  -e 'fsspec.implementations.*'
BuildOption(check):  -e fsspec.conftest
BuildOption(check):  -e fsspec.fuse
BuildOption(check):  -e fsspec.gui

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(hatch-vcs)
BuildRequires:  python3dist(hatchling) >= 1.27

%description
Fsspec provides a unified Python interface for local, remote, and embedded
filesystems. This package provides the 2026.2 compatibility release for
applications whose dependency range excludes newer fsspec releases.

%pyproject_extras_subpkg -n python-%{srcname}-2026-2 http

%generate_buildrequires
%sglang_pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

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

Provides:       python3-%{srcname}-2026-2 = %{version}-%{release}
Provides:       python3dist(%{srcname}) = %{version}
%python_provide python3-%{srcname}-2026-2
Conflicts:      python-fsspec

%description
Fsspec provides a unified Python interface for local, remote, and embedded
filesystems. This package provides the 2026.2 compatibility release for
applications whose dependency range excludes newer fsspec releases.

%pyproject_extras_subpkg -n python-%{srcname}-2026-2 abfs
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 adl
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 arrow
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 dask
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 dev
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 doc
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 dropbox
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 full
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 fuse
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 gcs
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 git
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 github
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 gs
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 gui
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 hdfs
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 http
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 libarchive
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 oci
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 s3
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 sftp
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 smb
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 ssh
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 test
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 test-downstream
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 test-full
%pyproject_extras_subpkg -n python-%{srcname}-2026-2 tqdm

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

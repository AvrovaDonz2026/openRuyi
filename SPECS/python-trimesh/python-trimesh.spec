# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname trimesh

Name:           python-%{srcname}
Version:        5.1.1
Release:        %autorelease
Summary:        Import, export, process, analyze and view triangular meshes
License:        MIT
URL:            https://github.com/mikedh/trimesh
VCS:            git:https://github.com/mikedh/trimesh
#!RemoteAsset:  sha256:56070be44cd97ac87544c9bd3da4b7a298c6f728e83183aeb1f3524d673d5fac
Source:         https://files.pythonhosted.org/packages/ab/bf/a7efaef127e0f1a228a03e5d00c04f5aeb2c25a60adb4d47003d4d0855bc/trimesh-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools) >= 61
BuildRequires:  python3dist(wheel)

Requires:       python3dist(numpy) >= 1.21

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Trimesh imports, exports, processes, analyzes, and views triangular meshes.

%generate_buildrequires
%pyproject_buildrequires

%check -a
PYTHONPATH=%{buildroot}%{python3_sitelib} %{python3} -c 'import trimesh; box = trimesh.creation.box(); assert box.is_watertight and box.volume == 1.0'

%files -f %{pyproject_files}
%doc README.md
%license LICENSE.md
%{_bindir}/trimesh

%changelog
%autochangelog

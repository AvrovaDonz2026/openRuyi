# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname moviepy

Name:           python-%{srcname}
Version:        2.2.1
Release:        %autorelease
Summary:        Video editing with Python
License:        MIT
URL:            https://github.com/Zulko/moviepy
VCS:            git:https://github.com/Zulko/moviepy.git
#!RemoteAsset:  sha256:c80cb56815ece94e5e3e2d361aa40070eeb30a09d23a24c4e684d03e16deacb1
Source0:        https://files.pythonhosted.org/packages/source/m/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(decorator) < 6
BuildRequires:  python3dist(imageio) < 3
BuildRequires:  python3dist(imageio-ffmpeg)
BuildRequires:  python3dist(numpy) >= 1.25
BuildRequires:  python3dist(pillow) >= 9.2
BuildRequires:  python3dist(pillow) < 12
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(proglog) <= 1
BuildRequires:  python3dist(python-dotenv) >= 0.10
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(setuptools) >= 42
BuildRequires:  python3dist(wheel)

Requires:       python3dist(decorator) < 6
Requires:       python3dist(imageio) < 3
Requires:       python3dist(imageio-ffmpeg)
Requires:       python3dist(numpy) >= 1.25
Requires:       python3dist(pillow) >= 9.2
Requires:       python3dist(pillow) < 12
Requires:       python3dist(proglog) <= 1
Requires:       python3dist(python-dotenv) >= 0.10

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
MoviePy provides Python tools for video editing, compositing, and processing.

%generate_buildrequires
%pyproject_buildrequires

%check -a
%pytest -q tests

%files -f %{pyproject_files}
%doc README.md
%license LICENCE.txt

%changelog
%autochangelog

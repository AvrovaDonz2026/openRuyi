# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
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
BuildRequires:  sglang-rpm-macros
%sglang_python_compat extras
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python-%{_sglang_private_python})
BuildRequires:  python%{_sglang_private_python}dist(decorator) < 6
BuildRequires:  python%{_sglang_private_python}dist(imageio) < 3
BuildRequires:  python%{_sglang_private_python}dist(imageio-ffmpeg)
BuildRequires:  python%{_sglang_private_python}dist(numpy) >= 1.25
BuildRequires:  sglang-extras(python%{_sglang_private_python}dist(pillow)) >= 9.2
BuildRequires:  sglang-extras(python%{_sglang_private_python}dist(pillow)) < 12
BuildRequires:  python%{_sglang_private_python}dist(pip)
BuildRequires:  python%{_sglang_private_python}dist(proglog) <= 1
BuildRequires:  python%{_sglang_private_python}dist(python-dotenv) >= 0.10
BuildRequires:  python%{_sglang_private_python}dist(pytest)
BuildRequires:  python%{_sglang_private_python}dist(setuptools) >= 42
BuildRequires:  python%{_sglang_private_python}dist(wheel)

Requires:       python%{_sglang_private_python}dist(decorator) < 6
Requires:       python%{_sglang_private_python}dist(imageio) < 3
Requires:       python%{_sglang_private_python}dist(imageio-ffmpeg)
Requires:       python%{_sglang_private_python}dist(numpy) >= 1.25
Requires:       sglang-extras(python%{_sglang_private_python}dist(pillow)) >= 9.2
Requires:       sglang-extras(python%{_sglang_private_python}dist(pillow)) < 12
Requires:       python%{_sglang_private_python}dist(proglog) <= 1
Requires:       python%{_sglang_private_python}dist(python-dotenv) >= 0.10

%description
MoviePy provides Python tools for video editing, compositing, and processing.

%generate_buildrequires
%sglang_pyproject_buildrequires

%check -a
%pytest -q tests

%files -f %{pyproject_files}
%doc README.md
%license LICENCE.txt

%changelog
%autochangelog

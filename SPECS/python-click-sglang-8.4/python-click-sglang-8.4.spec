# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname click
%global compat_name python-click-sglang-8.4

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros >= 0.1-1000
%sglang_python_compat core
Version:        8.4.2
Release:        %autorelease
Summary:        Composable command line interface toolkit
License:        BSD-3-Clause
URL:            https://palletsprojects.com/p/click/
VCS:            git:https://github.com/pallets/click
#!RemoteAsset:  sha256:9a6cea6e60b17ebe0a44c5cc636d94f09bd66142c1cd7d8b4cd731c4917a15f6
Source0:        https://files.pythonhosted.org/packages/source/c/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(flit-core) >= 3.11

%description
Click is a Python package for creating composable command line interfaces. This
package provides the SGLang-private 8.4 compatibility tree.

%generate_buildrequires
%sglang_pyproject_buildrequires

%check -a
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
%{python3} -s - <<'PY'
import click
from importlib.metadata import version

assert version("click") == "8.4.2"
assert click.style("compatibility-check", fg="green")
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE.txt

%changelog
%{?autochangelog}

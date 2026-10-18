# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name msgspec

Name:           python-%{pypi_name}
Version:        0.22.0
Release:        %autorelease
Summary:        Fast serialization and validation library
License:        BSD-3-Clause
URL:            https://jcristharif.com/msgspec/
#!RemoteAsset:  sha256:0a13624a4969159fe35d8c2a3d377b2b61bbd8585e327440d5e52725affcce38
Source0:        https://files.pythonhosted.org/packages/source/m/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  %{pypi_name}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3-devel
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools) >= 80
BuildRequires:  python3dist(setuptools-scm) >= 8
BuildRequires:  python3dist(wheel)

Provides:       python3-%{pypi_name} = %{version}-%{release}
Provides:       python3-%{pypi_name}%{?_isa} = %{version}-%{release}
%python_provide python3-%{pypi_name}

%description
A fast serialization and validation library, with builtin support for
JSON, MessagePack, YAML, and TOML.

%generate_buildrequires
%pyproject_buildrequires

%check -a
PYTHONPATH="%{buildroot}%{python3_sitearch}" \
%{python3} -s - <<'PY'
import importlib.metadata
import msgspec

assert importlib.metadata.version("msgspec") == "0.22.0"
assert msgspec.json.decode(msgspec.json.encode({"ok": True})) == {"ok": True}
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

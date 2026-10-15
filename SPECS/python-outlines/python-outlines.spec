# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname outlines

Name:           python-%{srcname}
Version:        1.2.13
Release:        %autorelease
Summary:        Probabilistic generative model programming
License:        Apache-2.0
URL:            https://github.com/dottxt-ai/outlines
#!RemoteAsset:  sha256:d48b6e92f15d32536a1b2bf73edc88ef78f21a331e5c4fb71f76535901a3abb1
Source0:        https://files.pythonhosted.org/packages/source/o/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(cloudpickle)
BuildRequires:  python3dist(diskcache)
BuildRequires:  python3dist(genson)
BuildRequires:  python3dist(jinja2)
BuildRequires:  python3dist(jsonpath-ng)
BuildRequires:  python3dist(jsonschema)
BuildRequires:  python3dist(outlines_core) = 0.2.14
BuildRequires:  python3dist(pillow)
BuildRequires:  python3dist(pydantic) >= 2
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(setuptools-scm) >= 6.2
BuildRequires:  python3dist(typing-extensions)
BuildRequires:  python3dist(wheel)

Requires:       python3dist(cloudpickle)
Requires:       python3dist(diskcache)
Requires:       python3dist(genson)
Requires:       python3dist(jinja2)
Requires:       python3dist(jsonpath-ng)
Requires:       python3dist(jsonschema)
Requires:       python3dist(outlines_core) = 0.2.14
Requires:       python3dist(pillow)
Requires:       python3dist(pydantic) >= 2
Requires:       python3dist(typing-extensions)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Outlines provides tools for controlling language model generation with regular
expressions, JSON schemas, and context-free grammars.

%generate_buildrequires
%pyproject_buildrequires

%check -a
export PYTHONPATH="%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}"
%{python3} - <<'PY'
import importlib.metadata

import outlines
from outlines import grammars, types

assert importlib.metadata.version("outlines") == "1.2.13"
assert types.digit.matches("7")
assert not types.digit.matches("x")
assert "start" in grammars.json
schema = types.json_schema('{"type": "string"}')
assert schema.schema == '{"type": "string"}'
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

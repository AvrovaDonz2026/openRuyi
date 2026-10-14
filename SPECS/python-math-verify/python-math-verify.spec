# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname math-verify
%global pypi_name math_verify

Name:           python-%{srcname}
Version:        0.9.0
Release:        %autorelease
Summary:        Library for verifying mathematical answers
License:        Apache-2.0
URL:            https://github.com/huggingface/Math-Verify
VCS:            git:https://github.com/huggingface/Math-Verify
#!RemoteAsset:  sha256:45ac6c61344ba056b9e99a660a4bc8d044ed408f730aed68c60435aa5eec4645
Source:         https://files.pythonhosted.org/packages/source/m/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l math_verify

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(latex2sympy2-extended) = 1.11.0
BuildRequires:  python3dist(setuptools)

%pyproject_extras_subpkg -n python-%{srcname} antlr4_9_3
%pyproject_extras_subpkg -n python-%{srcname} antlr4_11_0
%pyproject_extras_subpkg -n python-%{srcname} antlr4_13_2
BuildRequires:  python3dist(sympy) >= 1.13.1

Requires:       python3dist(latex2sympy2-extended) = 1.11.0
Requires:       python3dist(sympy) >= 1.13.1

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Math-Verify provides parsing and symbolic comparison helpers for verifying
mathematical answers.

%generate_buildrequires
%pyproject_buildrequires

%check -a
python3 - <<'PY'
from math_verify import parse, verify

assert verify(parse("$5$"), parse("5"))
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENCE

%changelog
%autochangelog

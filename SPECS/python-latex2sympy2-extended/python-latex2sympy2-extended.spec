# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname latex2sympy2-extended
%global pypi_name latex2sympy2_extended

Name:           python-%{srcname}
Version:        1.11.0
Release:        %autorelease
Summary:        Convert LaTeX math expressions to SymPy expressions
License:        MIT
URL:            https://github.com/hynky1999/latex2sympy2_extended
VCS:            git:https://github.com/hynky1999/latex2sympy2_extended
#!RemoteAsset:  sha256:9695657c81b50abba2636638638618db59f4663ed2a4a12d62cef74a40e28fec
Source:         https://files.pythonhosted.org/packages/source/l/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l latex2sympy2_extended -L

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(antlr4-python3-runtime) >= 4.9.3
BuildRequires:  python3dist(antlr4-python3-runtime) <= 4.13.2
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(sympy)
BuildRequires:  python3dist(wheel)

Requires:       python3dist(antlr4-python3-runtime) >= 4.9.3
Requires:       python3dist(antlr4-python3-runtime) <= 4.13.2
Requires:       python3dist(sympy)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
latex2sympy2_extended parses LaTeX mathematical expressions and converts
them into equivalent SymPy expressions.

%generate_buildrequires
%pyproject_buildrequires

%check -a
python3 - <<'PY'
from latex2sympy2_extended.latex2sympy2 import latex2sympy

assert str(latex2sympy("x^2")) == "x**2"
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE.txt

%changelog
%autochangelog

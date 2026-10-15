# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname sgl-eval
%global pypi_name sgl_eval

Name:           python-sgl-eval
Version:        0.1.2
Release:        %autorelease
Summary:        One-click accuracy evaluation harness for SGLang
License:        Apache-2.0
URL:            https://github.com/sgl-project/sgl-eval
VCS:            git:https://github.com/sgl-project/sgl-eval
#!RemoteAsset:  sha256:95d663d1896a0b7fe5eb0eb239d97eddeeca46f9cb057a8488aa43574974cf61
Source:         https://files.pythonhosted.org/packages/5f/5b/05497b34c3564836a71d2dc0a7b1604f1daab2126e0d0df68f6abde24c2b/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l sgl_eval

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools) >= 68
BuildRequires:  python3dist(wheel)

Requires:       python3dist(datasets) >= 2.14
Requires:       python3dist(datasets) < 5
Requires:       python3dist(editdistance) >= 0.6
Requires:       python3dist(editdistance) < 1
Requires:       python3dist(httpx) >= 0.24
Requires:       python3dist(httpx) < 1
Requires:       python3dist(latex2sympy2-extended) >= 1
Requires:       python3dist(latex2sympy2-extended) < 2
Requires:       python3dist(math-verify) >= 0.5
Requires:       python3dist(math-verify) < 1
Requires:       python3dist(math-verify[antlr4_9_3]) >= 0.5
Requires:       python3dist(numpy) >= 1.24
Requires:       python3dist(numpy) < 3
Requires:       python3dist(openai) >= 1
Requires:       python3dist(openai) < 3
Requires:       python3dist(pandas) >= 2
Requires:       python3dist(pandas) < 3
Requires:       python3dist(pillow) >= 10
Requires:       python3dist(pillow) < 12
Requires:       python3dist(pyyaml) >= 6
Requires:       python3dist(pyyaml) < 7
Requires:       python3dist(tqdm) >= 4.65
Requires:       python3dist(tqdm) < 5

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
SGL-Eval is an accuracy evaluation harness for SGLang with common language
model benchmarks and an OpenAI-compatible endpoint interface.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/sgl-eval

%changelog
%autochangelog

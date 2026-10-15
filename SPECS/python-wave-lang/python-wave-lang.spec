# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname wave
%global commit 1cdf9e30be9961b48e846441d942811de98b8971

Name:           python-wave-lang
Version:        3.8.2
Release:        %autorelease
Summary:        Python DSL and compiler for high performance machine learning
License:        Apache-2.0 WITH LLVM-exception
URL:            https://github.com/iree-org/wave
VCS:            git:https://github.com/iree-org/wave.git
#!RemoteAsset:  sha256:a1b8154e180577b4651b0df2558a69fb25e3f69bd07510f7ac600018bc64f56c
Source0:        https://github.com/iree-org/wave/archive/%{commit}.tar.gz#/%{srcname}-%{commit}.tar.gz
# Local manifest used by the Cargo registry and RPM crate dependency checks.
Source1:        Cargo.toml
BuildSystem:    pyproject

# Use the distribution CMake binary instead of the Python wheel wrapper.
# Downstream-only: openRuyi uses the system cmake package.
Patch2000:      2000-use-system-cmake.patch

BuildOption(prep):  -n %{srcname}-%{commit}
BuildOption(install):  -l wave_lang

BuildRequires:  cargo
BuildRequires:  cmake
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(iree-base-compiler) = 3.8.0
BuildRequires:  python3dist(iree-base-runtime) = 3.8.0
BuildRequires:  python3dist(nanobind) >= 2.9.2
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(setuptools-rust)
BuildRequires:  python3dist(torch)
BuildRequires:  python3dist(wheel)
BuildRequires:  rust
BuildRequires:  rust-rpm-macros
BuildRequires:  crate(pyo3-0.25/default) >= 0.25.1
BuildRequires:  crate(pyo3-0.25/extension-module) >= 0.25.1
BuildRequires:  crate(rayon-1/default) >= 1.5

Requires:       python3dist(iree-base-compiler) = 3.8.0
Requires:       python3dist(iree-base-runtime) = 3.8.0
Requires:       python3dist(jinja2) >= 3.1.6
Requires:       python3dist(ml-dtypes) >= 0.5.3
Requires:       python3dist(numpy)
Requires:       python3dist(torch)
Requires:       python3dist(typing-extensions)

Provides:       python3-wave-lang = %{version}-%{release}
%python_provide python3-wave-lang

%description
Wave is a Python domain-specific language for developing and optimizing machine
learning kernels. It provides Python APIs and native runtime components for
compiling and executing kernels with IREE.

%prep -a
cp %{SOURCE1} wave_lang/kernel/wave/scheduling/aplp/Cargo.toml
%rust_setup_registry

%generate_buildrequires
export WAVE_IS_STABLE_REL=1
%pyproject_buildrequires

%build -p
export WAVE_IS_STABLE_REL=1

%install -p

%check -a
%{python3} -c 'import importlib.metadata; assert importlib.metadata.version("wave-lang") == "%{version}"; import torch, iree.compiler, iree.runtime, wave_lang'

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

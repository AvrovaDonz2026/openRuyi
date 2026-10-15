# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname tilelang

Name:           python-%{srcname}
Version:        0.1.14
Release:        %autorelease
Summary:        Tile-level language for generating GPU and CPU kernels
License:        MIT
URL:            https://github.com/tile-ai/tilelang
VCS:            git:https://github.com/tile-ai/tilelang.git
#!RemoteAsset:  sha256:7ae0fba6c63dae80b3c9c5c11a70bb8d7165794994f290f36e2fe87bfb143cfc
Source0:        https://files.pythonhosted.org/packages/98/b6/b2a79ca220c63f0ec43ece86c0a37f92af9e22261b13951e58700b008a2b/tilelang-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  tilelang +auto

BuildRequires:  cmake >= 3.26.1
BuildRequires:  patchelf >= 0.17.2
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(cython) >= 3.1.0
BuildRequires:  python3dist(scikit-build-core)
BuildRequires:  python3dist(z3-solver) >= 4.13.0
BuildRequires:  python3dist(z3-solver) < 4.15.5

Requires:       python3dist(apache-tvm-ffi) >= 0.1.11
Requires:       python3dist(cloudpickle)
Requires:       python3dist(ml-dtypes)
Requires:       python3dist(numpy) >= 1.23.5
Requires:       python3dist(psutil)
Requires:       python3dist(torch)
Requires:       python3dist(torch-c-dlpack-ext)
Requires:       python3dist(tqdm) >= 4.62.3
Requires:       python3dist(typing-extensions) >= 4.10.0
Requires:       python3dist(z3-solver) >= 4.13.0
Requires:       python3dist(z3-solver) < 4.15.5

%description
TileLang is a tile-level programming language for generating high-performance
GPU and CPU kernels.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

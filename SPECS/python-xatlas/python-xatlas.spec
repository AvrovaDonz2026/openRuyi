# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname xatlas
%global toolchain clang
%ifarch riscv64
%global llvm_maj_ver 22
%endif

Name:           python-%{srcname}
Version:        0.0.11
Release:        %autorelease
Summary:        Python bindings for xatlas texture coordinate generation
License:        MIT AND BSD-3-Clause
URL:            https://github.com/mworchel/xatlas-python
VCS:            git:https://github.com/mworchel/xatlas-python.git
#!RemoteAsset:  sha256:72f0bc6c42c19252be87e947d9dfe251c8d6c6943fd43e3d173ddc6b1afad693
Source0:        https://files.pythonhosted.org/packages/source/x/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -L %{srcname}

BuildRequires:  cmake
BuildRequires:  clang
BuildRequires:  llvm
BuildRequires:  lld
BuildRequires:  ninja
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(scikit-build-core) >= 0.10

%ifarch riscv64
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
xatlas provides Python bindings for xatlas, a library that generates texture
coordinates for triangle meshes.

%prep -a
cp -p LICENSE LICENSE.xatlas-python
cp -p extern/xatlas/LICENSE LICENSE.xatlas
cp -p extern/pybind11/LICENSE LICENSE.pybind11

%generate_buildrequires
%pyproject_buildrequires

%check -a
export PYTHONPATH="%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}"
%{python3} - <<'PY'
import numpy as np
import xatlas

vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
faces = np.array([[0, 1, 2]], dtype=np.uint32)
vmapping, indices, uvs = xatlas.parametrize(vertices, faces)
assert vmapping.ndim == 1 and len(vmapping) >= 3
assert indices.ndim == 2 and indices.shape[1] == 3
assert uvs.shape == (len(vmapping), 2)
assert np.isfinite(uvs).all()
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE.xatlas-python LICENSE.xatlas LICENSE.pybind11

%changelog
%autochangelog

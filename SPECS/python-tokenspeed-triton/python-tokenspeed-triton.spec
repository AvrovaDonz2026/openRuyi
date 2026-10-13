# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname triton
%global commit 29820f3735823fe78793cf73b68826ef71928f0e

Name:           python-tokenspeed-triton
Version:        3.8.10.post20260920
Release:        %autorelease
Summary:        TokenSpeed vendor Triton compiler and runtime
License:        MIT AND (Apache-2.0 WITH LLVM-exception OR NCSA) AND BSD-3-Clause
URL:            https://github.com/lightseekorg/triton
VCS:            git:https://github.com/lightseekorg/triton.git
#!RemoteAsset:  sha256:e96e87d656c0cd20c7eb1c6d3ef791406a6dccc483b038e6c6baf69f1e8b4406
Source0:        https://github.com/lightseekorg/triton/archive/%{commit}.tar.gz#/%{srcname}-%{commit}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(install):  -l tokenspeed_triton
BuildOption(check):  -e 'tokenspeed_triton.profiler.*'

BuildRequires:  clang
BuildRequires:  cmake >= 3.20
BuildRequires:  cuda-toolkit
BuildRequires:  gcc-c++
BuildRequires:  llvm
BuildRequires:  lld
BuildRequires:  ninja
BuildRequires:  nlohmann-json
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(pybind11)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(nanobind)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

Requires:       python3dist(torch)

%description
TokenSpeed Triton is LightSeek's vendor Triton compiler and runtime for
custom deep-learning operations. It provides CUDA and AMD GPU code-generation
backends under the namespaced tokenspeed_triton Python module.

%prep -a
sed -i 's|name=os.environ.get("TRITON_WHEEL_NAME", "tokenspeed-triton")|name="tokenspeed-triton"|' setup.py
sed -i 's|TRITON_VERSION = "3.8.10" + get_triton_version_suffix()|TRITON_VERSION = "3.8.10.post20260920"|' setup.py

%generate_buildrequires
%pyproject_buildrequires

%build -p
export TRITON_WHEEL_NAME=tokenspeed-triton
export TRITON_OFFLINE_BUILD=1
export TRITON_BUILD_PROTON=OFF
export TRITON_BUILD_NVIDIA_BACKEND_PLUGIN=ON
export TRITON_CODEGEN_BACKENDS=nvidia
export TRITON_BUILD_TOOLS=OFF
%pyproject_wheel

%install -p
%pyproject_install

%check -a
# GPU code-generation tests require a CUDA device unavailable on build hosts.
%pyproject_check_import tokenspeed_triton

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

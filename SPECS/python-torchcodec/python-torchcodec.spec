# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname torchcodec
%ifarch riscv64
%global llvm_maj_ver 22
%global toolchain clang
%endif

Name:           python-%{srcname}
Version:        0.12.0
Release:        %autorelease
Summary:        PyTorch video decoding and encoding library
License:        BSD-3-Clause
URL:            https://github.com/meta-pytorch/torchcodec
VCS:            git:https://github.com/meta-pytorch/torchcodec.git
#!RemoteAsset:  sha256:f0cc21c1f99439cff30eb43080e9bc8e43c6b9505b4f327cb42ee132075bcec4
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  cmake
%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%else
BuildRequires:  gcc-c++
%endif
BuildRequires:  ffmpeg-devel
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(pybind11)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-torch-devel >= 2.11
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

Requires:       ffmpeg
Requires:       python-torch >= 2.11
Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
TorchCodec provides PyTorch bindings for decoding and encoding audio and video
with the system FFmpeg libraries.

%generate_buildrequires
%pyproject_buildrequires

%build -p
# The build links to the system FFmpeg package instead of downloading or
# bundling an FFmpeg build.  TorchCodec asks downstream distributors to make
# this licensing decision explicitly when producing a wheel.
export I_CONFIRM_THIS_IS_NOT_A_LICENSE_VIOLATION=1
export ENABLE_CUDA=0
export TORCHCODEC_DISABLE_COMPILE_WARNING_AS_ERROR=ON
%ifarch riscv64
export CC=clang
export CXX=clang++
export LD=ld.lld
export AR=llvm-ar
export RANLIB=llvm-ranlib
export CFLAGS="%{build_cflags} --target=%{_target_platform}"
export CXXFLAGS="%{build_cxxflags} --target=%{_target_platform}"
export LDFLAGS="%{build_ldflags} -fuse-ld=lld"
%endif

%check -a
PYTHONPATH="%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}" \
%{python3} - <<'PY'
from torchcodec._core import get_ffmpeg_library_versions

versions = get_ffmpeg_library_versions()
assert versions["ffmpeg_version"]
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

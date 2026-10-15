# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: Xuhai Chang <xuhai.oerv@isrc.iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname torchaudio
%ifarch riscv64
%global llvm_maj_ver 22
%global toolchain clang
%endif

Name:           python-%{srcname}
Version:        2.11.0
Release:        %autorelease
Summary:        Audio library for PyTorch
License:        BSD-2-Clause
URL:            https://github.com/pytorch/audio
# PyPI only provides prebuilt wheels for this release; build from GitHub source.
#!RemoteAsset:  sha256:599ec24e7e1eef476ef21f0178e33da00e2434f930ba42e9cc20bf4002220486
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(prep):  -n audio-%{version}
BuildOption(install):  %{srcname}
# libtorchaudio is a shared library loaded by torchaudio, not a Python module.
BuildOption(check):  -e %{srcname}.lib.libtorchaudio

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja
BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(pybind11)
BuildRequires:  pkgconfig(protobuf)
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(torch) = 2.14.0
BuildRequires:  python3dist(wheel)
# Could not find a package configuration file provided by "Torch"
BuildRequires:  python-torch-devel = 2.14.0
%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

Requires:       python3dist(torch) = 2.14.0

%description
TorchAudio is an audio package for PyTorch providing signal processing
functions, datasets, transforms, and I/O utilities.

%generate_buildrequires
%pyproject_buildrequires

%build -p
export BUILD_VERSION=%{version}
export USE_CUDA=0
export USE_ROCM=0
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
import torch
import torchaudio
from torchaudio.lib import _torchaudio

assert torchaudio.__version__ == "2.11.0"
waveform = torch.tensor([[0.0, 1.0, 0.0, -1.0]])
resampled = torchaudio.functional.resample(waveform, 8000, 16000)
assert resampled.shape[-1] == 8
assert _torchaudio is not None
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

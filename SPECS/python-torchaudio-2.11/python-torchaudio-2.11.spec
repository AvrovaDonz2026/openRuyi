# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-FileContributor: Xuhai Chang <xuhai.oerv@isrc.iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname torchaudio
%global compat_name python-torchaudio-2.11
# ROCm remains a source-level flavor for a future completed build.  No OBS
# multibuild entry is enabled while its dependency closure is unvalidated.
%global flavor @BUILD_FLAVOR@%{nil}
%if "%{flavor}" == "rocm"
%{error:ROCm SGLang TorchAudio flavor is reserved and is not supported by this SPEC}
%bcond rocm 1
%global torch_capability torch-rocm
%else
%bcond rocm 0
%global torch_capability torch-cpu
%endif
%ifarch riscv64
%global llvm_maj_ver 22
%global toolchain clang
%endif

%if %{with rocm}
Name:           %{compat_name}-rocm
%else
Name:           %{compat_name}
%endif
Version:        2.11.0
Release:        %autorelease
Summary:        Audio library for PyTorch
License:        BSD-2-Clause
URL:            https://github.com/pytorch/audio
# PyPI only provides prebuilt wheels for this release; build from GitHub source.
#!RemoteAsset:  sha256:599ec24e7e1eef476ef21f0178e33da00e2434f930ba42e9cc20bf4002220486
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz
BuildRequires:  sglang-rpm-macros
BuildRequires:  file
BuildRequires:  patchelf
%sglang_python_compat core
BuildSystem:    pyproject

BuildOption(prep):  -n audio-%{version}
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
BuildRequires:  sglang(python3dist(%{torch_capability})) = 2.14.0
BuildRequires:  python3dist(wheel)
# Could not find a package configuration file provided by "Torch"
%if %{with rocm}
BuildRequires:  python-torch-sglang-2.14-rocm-devel
%else
BuildRequires:  python-torch-sglang-2.14-devel
%endif
%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif

Requires:       sglang(python3dist(%{torch_capability})) = 2.14.0

%description
TorchAudio is an audio package for PyTorch providing signal processing
functions, datasets, transforms, and I/O utilities.

%generate_buildrequires
%sglang_pyproject_buildrequires

%build -p
export BUILD_VERSION=%{version}
export PYTHONPATH="%{_sglang_private_sitelib}${PYTHONPATH:+:$PYTHONPATH}"
export CMAKE_PREFIX_PATH="%{_sglang_private_sitelib}/torch/share/cmake${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"
%if %{with rocm}
export USE_CUDA=0
export USE_ROCM=1
%else
export USE_CUDA=0
export USE_ROCM=0
%endif
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

%install -a
%sglang_private_rpath

%check -a
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}" \
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

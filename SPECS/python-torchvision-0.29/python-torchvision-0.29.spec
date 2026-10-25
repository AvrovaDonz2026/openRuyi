# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname torchvision
%global compat_name python-torchvision-0.29
%global llvm_maj_ver 22
%ifarch riscv64
%global toolchain clang
%global llvm_bindir %{_libdir}/llvm%{llvm_maj_ver}/bin
%endif

# ROCm remains a source-level flavor for a future completed build.  No OBS
# multibuild entry is enabled while its dependency closure is unvalidated.
%global flavor @BUILD_FLAVOR@%{nil}
%if "%{flavor}" == "cuda"
%{error:CUDA SGLang TorchVision flavor is reserved and is not supported by this SPEC}
%bcond cuda 1
%else
%bcond cuda 0
%endif
%if "%{flavor}" == "rocm"
%{error:ROCm SGLang TorchVision flavor is reserved and is not supported by this SPEC}
%bcond rocm 1
%global torch_capability torch-rocm
%global toolchain clang
%else
%bcond rocm 0
%global torch_capability torch-cpu
%endif

%if %{with cuda}
%{error:CUDA SGLang TorchVision flavor is reserved and is not supported by this SPEC}
%endif
%if %{with rocm}
%{error:ROCm SGLang TorchVision flavor is reserved and is not supported by this SPEC}
%endif

%bcond test 0

%if %{with rocm}
Name:           %{compat_name}-rocm
%else
Name:           %{compat_name}
%endif
Version:        0.29.0
Release:        %autorelease
Summary:        Image and video datasets for torch deep learning
License:        BSD-3-Clause AND BSD-2-Clause AND MIT
URL:            https://github.com/pytorch/vision
#!RemoteAsset:  sha256:24be57d922927d8a2ac2e8f076f07c3447ddf8f1d25ddbb7b65578f36c9ab8e3
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
BuildRequires:  sglang-rpm-macros >= 0.1-1000
BuildRequires:  file
BuildRequires:  patchelf
%sglang_python_compat core
BuildSystem:    pyproject
%if %{without rocm}
# The private CPU TorchVision provider is currently validated only as part of
# the RISC-V SGLang closure.  Keep unsupported CPU transactions out of OBS
# until their dependency closure and target validation are complete.
ExclusiveArch:  riscv64
%else
# ROCm remains a reserved source flavor for the future completed build.
ExclusiveArch:  x86_64 aarch64
%endif

BuildOption(prep):  -n vision-%{version}
BuildOption(install):  -l torchvision
# torchvision.image*, image_stable, and io* are torch operator .so files, not
# Python extension modules. BuildOption(check) keeps one exclusion option, so
# the shared ``i*`` prefix covers all of these native modules in one glob.
BuildOption(check):  -e '%{srcname}.i*'
%ifarch riscv64
BuildOption(build):  -Ccmake.define.CMAKE_C_COMPILER=%{llvm_bindir}/clang
BuildOption(build):  -Ccmake.define.CMAKE_CXX_COMPILER=%{llvm_bindir}/clang++
BuildOption(build):  -Ccmake.define.CMAKE_C_COMPILER_TARGET:STRING=%{_target_platform}
BuildOption(build):  -Ccmake.define.CMAKE_CXX_COMPILER_TARGET:STRING=%{_target_platform}
%if "%{_host_cpu}" != "%{_target_cpu}"
BuildOption(build):  -Ccmake.define.CMAKE_SYSTEM_NAME=Linux
BuildOption(build):  -Ccmake.define.CMAKE_SYSTEM_PROCESSOR=riscv64
%endif
%endif

BuildRequires:  ninja
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(pybind11)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(numpy)
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(pillow)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(requests)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)
%if %{with test}
BuildRequires:  python3dist(pytest)
%endif
%if %{with rocm}
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hipblaslt)
BuildRequires:  cmake(hipsolver)
BuildRequires:  cmake(hipsparse)
BuildRequires:  cmake(rocm-core)
BuildRequires:  cmake(rocprim)
BuildRequires:  cmake(rocthrust)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  hipcc
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  sglang(python3dist(%{torch_capability})) = 2.14.0
BuildRequires:  python-torch-sglang-2.14-rocm-devel = 2.14.0
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
%else
BuildRequires:  gcc-c++
BuildRequires:  sglang(python3dist(%{torch_capability})) = 2.14.0
BuildRequires:  python-torch-sglang-2.14-devel = 2.14.0
%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif
%endif

Requires:       python3dist(numpy)
Requires:       python3dist(pillow)
Requires:       python3dist(requests)
Requires:       sglang(python3dist(%{torch_capability})) = 2.14.0

%patchlist
2001-Add-HIP-detect-logic.patch
2002-Use-flavor-specific-torch-build-dependency.patch

%description
The torchvision package consists of popular datasets, model architectures,
and common image transformations for computer vision.

%prep -a
# Need some debug info
sed -i -e 's@extra_compile_args["cxx"].append("-g0")@extra_compile_args["cxx"].append("-g")@' setup.py

%generate_buildrequires
%sglang_pyproject_buildrequires

%build -p
export BUILD_VERSION=%{version}
export PYTHONPATH="%{_sglang_private_sitelib}${PYTHONPATH:+:$PYTHONPATH}"
export CMAKE_PREFIX_PATH="%{_sglang_private_sitelib}/torch/share/cmake${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"
export TORCHVISION_USE_WEBP=1
%if %{without rocm}
%ifarch riscv64
export PATH="%{llvm_bindir}:$PATH"
export CC="%{llvm_bindir}/clang"
export CXX="%{llvm_bindir}/clang++"
export LD="%{llvm_bindir}/ld.lld"
export AR="%{llvm_bindir}/llvm-ar"
export RANLIB="%{llvm_bindir}/llvm-ranlib"
export CFLAGS="%{build_cflags} --target=%{_target_platform}"
export CXXFLAGS="%{build_cxxflags} --target=%{_target_platform}"
export LDFLAGS="-fuse-ld=lld --target=%{_target_platform} %{build_ldflags}"
%endif
%endif
%if %{with rocm}
export FORCE_CUDA=1
export ROCM_HOME=%{_prefix}
export HIP_CLANG_PATH=%{rocmllvm_bindir}
export PATH=%{rocmllvm_bindir}:$PATH
export PYTORCH_ROCM_ARCH=%{rocm_gpu_list_default}
%endif

%install -a
%sglang_private_rpath
# exec permission
find %{buildroot}%{_sglang_private_sitearch} -name '*.py' -print0 | while IFS= read -r -d '' f; do
    if [ ! -x "$f" ]; then
        sed -i '1{\@^#!/usr/bin@d}' "$f"
    fi
done

%check -a
%if %{with test}
%pytest
%else
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
%{python3} - <<'PY'
import torch
import torchvision

boxes = torch.tensor([[0, 0, 10, 10], [1, 1, 11, 11]], dtype=torch.float32)
scores = torch.tensor([0.9, 0.8])
assert torchvision.ops.nms(boxes, scores, 0.5).tolist() == [0]
PY
%endif

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

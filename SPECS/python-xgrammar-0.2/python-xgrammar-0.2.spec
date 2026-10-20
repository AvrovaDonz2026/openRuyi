# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Li Guan <guanli.oerv@isrc.iscas.ac.cn>
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname xgrammar
%global compat_name python-xgrammar-0.2
%ifarch riscv64
%global llvm_maj_ver 22
%global toolchain clang
%global llvm_bindir %{_libdir}/llvm%{llvm_maj_ver}/bin
%endif
# ROCm remains a source-level flavor for a future completed build.  No OBS
# multibuild entry is enabled while its dependency closure is unvalidated.
%global flavor @BUILD_FLAVOR@%{nil}
%if "%{flavor}" == "rocm"
%{error:ROCm SGLang XGrammar flavor is reserved and is not supported by this SPEC}
%bcond rocm 1
%global torch_capability torch-rocm
%else
%bcond rocm 0
%global torch_capability torch-cpu
%endif

# Keep the reserved ROCm flavor unbuildable when a caller enables the bcond
# directly instead of selecting BUILD_FLAVOR=rocm.
%if %{with rocm}
%{error:ROCm SGLang XGrammar flavor is reserved and is not supported by this SPEC}
%endif

%if "%{flavor}" == "rocm"
Name:           %{compat_name}-rocm
%else
Name:           %{compat_name}
%endif
BuildRequires:  sglang-rpm-macros
%sglang_python_compat
Version:        0.2.7
Release:        %autorelease
Summary:        Fast, Flexible and Portable Structured Generation
License:        Apache-2.0
URL:            https://github.com/mlc-ai/xgrammar
#!RemoteAsset:  sha256:7674afeee5e6eff9672627b62d5ab0aa2347ea51674f4d78a5c160029f92bc3e
Source0:        https://files.pythonhosted.org/packages/source/x/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject
# The default CPU flavor requires the private Torch provider, which is
# currently published only for the validated RISC-V closure. Keep the
# reserved ROCm architecture set explicit for a future completed flavor.
%if "%{flavor}" == "rocm"
ExclusiveArch:  x86_64 aarch64
%else
ExclusiveArch:  riscv64
%endif

BuildOption(install):  -l xgrammar
# No module named 'triton'
BuildOption(check):  -e xgrammar.kernels.apply_token_bitmask_inplace_triton
BuildOption(check):  -e xgrammar.kernels.apply_token_bitmask_inplace_cuda
# No module named 'mlx'
BuildOption(check):  -e xgrammar.kernels.apply_token_bitmask_mlx
BuildOption(check):  -e xgrammar.contrib.mlxlm
# Native shared library
BuildOption(check):  -e xgrammar.libxgrammar_bindings
%ifarch riscv64
BuildOption(build):  -Ccmake.define.CMAKE_C_COMPILER=%{llvm_bindir}/clang
BuildOption(build):  -Ccmake.define.CMAKE_CXX_COMPILER=%{llvm_bindir}/clang++
BuildOption(build):  -Ccmake.define.CMAKE_C_COMPILER_TARGET:STRING=%{_target_platform}
BuildOption(build):  -Ccmake.define.CMAKE_CXX_COMPILER_TARGET:STRING=%{_target_platform}
%endif

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  cmake
BuildRequires:  file
BuildRequires:  gcc-c++
BuildRequires:  ninja
BuildRequires:  patchelf
BuildRequires:  python3dist(scikit-build-core) >= 0.10
BuildRequires:  sglang(python3dist(apache-tvm-ffi)) >= 0.1.11
# The private native binding is built and tested with the SGLang Torch 2.14
# provider; keep this RPM edge exact while upstream Python metadata remains
# broad (torch>=1.10.0) for source compatibility.
BuildRequires:  sglang(python3dist(%{torch_capability})) = 2.14.0
%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif

Requires:       sglang(python3dist(apache-tvm-ffi)) >= 0.1.11
Requires:       sglang(python3dist(%{torch_capability})) = 2.14.0
%if "%{flavor}" == "rocm"
Conflicts:      %{compat_name}
%else
Conflicts:      %{compat_name}-rocm
%endif

%description
Efficient, Flexible and Portable Structured Generation.

%prep -a
sed -i 's/-Werror//g' CMakeLists.txt

%generate_buildrequires
%sglang_pyproject_buildrequires

%build -p
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

%install -a
%sglang_private_rpath
# tvm_ffi uses wheel RECORD metadata to locate the native binding library.
echo '%{srcname}/libxgrammar_bindings.so,,' > \
    %{buildroot}%{_sglang_private_sitearch}/%{srcname}-%{version}.dist-info/RECORD

%check -a
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
%{python3} - <<'PY'
import torch
import xgrammar
import xgrammar.libxgrammar_bindings as libxgrammar_bindings

assert xgrammar.__version__ == "%{version}"
assert libxgrammar_bindings.__name__ == "xgrammar.libxgrammar_bindings"
%if "%{flavor}" == "rocm"
assert torch.version.hip is not None
%else
assert torch.version.hip is None
%endif
PY

%sglang_pyproject_save_files
%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_sglang_private_sitearch}/%{srcname}-%{version}.dist-info/RECORD

%changelog
%autochangelog

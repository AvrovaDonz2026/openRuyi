# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname triton
%global compat_name python-triton-sglang-3.8

# CUDA and ROCm flavors are reserved until matching SGLang providers and
# validated target dependency closures are available.
%global flavor @BUILD_FLAVOR@%{nil}
%if "%{flavor}" == "cuda"
%{error:CUDA SGLang Triton flavor is reserved and is not supported by this SPEC}
%endif
%if "%{flavor}" == "rocm"
%{error:ROCm SGLang Triton flavor is reserved and is not supported by this SPEC}
%endif

# Triton pins an exact, in-development LLVM *commit*
%global llvm_commit 5f07f818b51b786b0a87b4e514882600ecba112f

%global bootstrap_llvm_maj_ver 22
%global bootstrap_llvm_bindir %{_libdir}/llvm%{bootstrap_llvm_maj_ver}/bin

# Build the bundled LLVM and the Triton extension with clang
%global toolchain clang
%global _lto_cflags %{nil}
%define _find_debuginfo_dwz_opts %{nil}

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros
BuildRequires:  file
BuildRequires:  patchelf
%sglang_python_compat
Version:        3.8.0
Release:        %autorelease
Summary:        Language and compiler for custom deep-learning primitives
# Triton itself is MIT.  The statically bundled LLVM/MLIR/LLD is
# "Apache-2.0 WITH LLVM-exception OR NCSA"; pybind11 headers are BSD-3-Clause
License:        MIT AND (Apache-2.0 WITH LLVM-exception OR NCSA) AND BSD-3-Clause
URL:            https://triton-lang.org/main/index.html
VCS:            git:https://github.com/triton-lang/triton.git
#!RemoteAsset:  sha256:451b07863426eb7804fc8fc59ca046a3e2e7312ded97124686a5a1d15fe9521f
Source0:        https://github.com/triton-lang/triton/releases/download/v%{version}/%{srcname}-%{version}.tar.gz
#!RemoteAsset:  git+https://github.com/llvm/llvm-project.git#%{llvm_commit}
#!CreateArchive
Source1:        llvm-project-%{llvm_commit}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 riscv64

BuildOption(install):  -l triton
BuildOption(check):  -e 'triton.instrumentation.*'
BuildOption(check):  -e 'triton.plugins.*'
BuildOption(check):  -e 'triton.runtime.interpreter'
BuildOption(check):  -e 'triton.tools.mxfp'

BuildRequires:  clang(major) = %{bootstrap_llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{bootstrap_llvm_maj_ver}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  libstdc++-devel
BuildRequires:  lld(major) = %{bootstrap_llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  nlohmann-json
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(pybind11)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(build)
BuildRequires:  python3dist(installer)
BuildRequires:  python3dist(pybind11)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

%patchlist
# Link RISC-V and X86 codegen libraries on the riscv64 host.
2001-Add-riscv64-host-codegen-libraries.patch
# Use system-provided build tools instead of vendored copies.
2002-use-system-build-tools.patch
# Build shared NVIDIA dialect libraries without the NVIDIA backend plugin.
2003-disable-nvidia-backend.patch

%description
Triton is a language and compiler for writing highly efficient custom
deep-learning primitives. It provides a Python programming interface and a
compiler stack that lowers Triton kernels through MLIR and LLVM backends for
GPU execution.

%prep -a
tar -xf %{SOURCE1}

%generate_buildrequires
%sglang_pyproject_buildrequires

%build -p
export PATH="%{bootstrap_llvm_bindir}:${PATH}"
export CC="%{bootstrap_llvm_bindir}/clang"
export CXX="%{bootstrap_llvm_bindir}/clang++"

llvm_src="$(pwd)/llvm-project-%{llvm_commit}"
llvm_install="$(pwd)/llvm-install"

mem_gb=$(awk '/MemTotal/ {print int($2/1024/1024)}' /proc/meminfo)
compile_jobs=$(nproc)
mem_jobs=$(( 1 + mem_gb / 2 ))
[ "$mem_jobs" -lt "$compile_jobs" ] && compile_jobs=$mem_jobs
[ "$compile_jobs" -lt 1 ] && compile_jobs=1
link_jobs=$(( 1 + mem_gb / 16 ))
[ "$link_jobs" -lt 1 ] && link_jobs=1

%ifarch x86_64
llvm_targets="X86;AMDGPU;NVPTX"
%elifarch riscv64
llvm_targets="RISCV;X86;AMDGPU;NVPTX"
%else
%{error:unsupported architecture for SGLang Triton}
%endif

cmake -S "$llvm_src/llvm" -B "$llvm_src/build" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$llvm_install" \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DLLVM_USE_LINKER=lld \
    -DLLVM_ENABLE_PROJECTS="mlir;lld" \
    -DLLVM_TARGETS_TO_BUILD="$llvm_targets" \
    -DLLVM_ENABLE_ASSERTIONS=OFF \
    -DBUILD_SHARED_LIBS=OFF \
    -DLLVM_BUILD_LLVM_DYLIB=OFF \
    -DLLVM_INSTALL_UTILS=ON \
    -DLLVM_ENABLE_ZSTD=ON \
    -DLLVM_INCLUDE_BENCHMARKS=OFF \
    -DLLVM_INCLUDE_EXAMPLES=OFF \
    -DLLVM_INCLUDE_TESTS=OFF \
    -DLLVM_PARALLEL_COMPILE_JOBS=$compile_jobs \
    -DLLVM_PARALLEL_LINK_JOBS=$link_jobs
cmake --build "$llvm_src/build" --target install -- -j$compile_jobs

export LLVM_SYSPATH="$llvm_install"
export PATH="$llvm_install/bin:$PATH"
export JSON_SYSPATH="%{_prefix}"
export PYBIND11_SYSPATH="%{_prefix}"
export PYBIND11_CMAKE_DIR="%{_datadir}/cmake/pybind11"
export MAX_JOBS=$compile_jobs
export TRITON_PARALLEL_LINK_JOBS=$link_jobs
export TRITON_BUILD_WITH_CLANG_LLD=ON
%ifarch riscv64
export TRITON_BUILD_PROTON=OFF
export TRITON_BUILD_NVIDIA_BACKEND_PLUGIN=OFF
export TRITON_CODEGEN_BACKENDS=amd
%elifarch x86_64
export TRITON_BUILD_PROTON=ON
export TRITON_BUILD_NVIDIA_BACKEND_PLUGIN=ON
export TRITON_CODEGEN_BACKENDS="nvidia;amd"
%else
%{error:unsupported architecture for SGLang Triton}
%endif
export TRITON_OFFLINE_BUILD=1
export TRITON_BUILD_TOOLS=OFF

%install -a
%sglang_private_rpath

%check -a
export PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}"
cd %{buildroot}
%{python3} - <<'PY'
import triton
import triton.compiler
import triton.language

assert triton.__version__ == "%{version}"
assert triton.cdiv(7, 3) == 3
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%license llvm-project-%{llvm_commit}/llvm/LICENSE.TXT
%license third_party/f2reduce/LICENCE.txt

%changelog
%autochangelog

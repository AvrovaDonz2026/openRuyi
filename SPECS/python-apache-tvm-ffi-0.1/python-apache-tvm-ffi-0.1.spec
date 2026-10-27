# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname apache-tvm-ffi
%global pypi_name apache_tvm_ffi
%global compat_name python-apache-tvm-ffi-0.1
%ifarch riscv64
%global llvm_maj_ver 22
%global llvm_bindir %{_libdir}/llvm%{llvm_maj_ver}/bin
%endif

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros >= 0.1-1000
%sglang_python_compat
Version:        0.1.11
Release:        %autorelease
Summary:        Open ABI and FFI for machine learning systems
License:        Apache-2.0
Provides:       sglang(python3dist(apache-tvm-ffi)) = %{version}
URL:            https://tvm.apache.org/ffi/
VCS:            git:https://github.com/apache/tvm-ffi.git
#!RemoteAsset:  sha256:153cd2c5a9717804cb0bcd9b2709f22a1e5f80ed05b5a490faf5949b136eedba
Source0:        https://files.pythonhosted.org/packages/source/a/%{srcname}/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l tvm_ffi -L
# An optional helper which imports PyTorch
BuildOption(check):  -e 'tvm_ffi.*'
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

BuildRequires:  cmake
BuildRequires:  file
BuildRequires:  gcc-c++
BuildRequires:  ninja >= 1.11
BuildRequires:  patchelf
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(cython)
BuildRequires:  python3dist(scikit-build-core) >= 0.10
BuildRequires:  python3dist(setuptools-scm)
%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif

%description
Apache TVM FFI provides an open ABI and foreign-function interface for machine
learning systems, including Python and C++ bindings used by XGrammar.

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

%check -a
# The build option accepts one exclusion glob; check runtime submodules explicitly.
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
%{python3} -sP /usr/lib/rpm/openruyi/import_all_modules.py \
    -f "%{_builddir}/%{name}-%{version}-%{release}.%{_target_cpu}-pyproject-modules" \
    -e tvm_ffi.lib.libtvm_ffi \
    -e tvm_ffi.lib.libtvm_ffi_testing \
    -e 'tvm_ffi.testing*' \
    -e tvm_ffi.utils._build_optional_torch_c_dlpack

PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
%{python3} - <<'PY'
import tvm_ffi

assert tvm_ffi.__version__ == "0.1.11"
assert tvm_ffi.LIB is not None

name = "openruyi.package_check.echo"
tvm_ffi.register_global_func(name, lambda value: value)
try:
    assert tvm_ffi.get_global_func(name)(37) == 37
finally:
    tvm_ffi.remove_global_func(name)
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE NOTICE licenses/*
%{_sglang_private_libexec}/tvm-ffi-config
%{_sglang_private_libexec}/tvm-ffi-stubgen

%changelog
%{?autochangelog}

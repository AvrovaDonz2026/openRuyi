# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname iree
%global cpuinfo_commit 3c8b1533ac03dd6531ab6e7b9245d488f13a82a5
%global flatcc_commit 9362cd00f0007d8cbee7bff86e90fb4b6b227ff3
%global vulkan_headers_commit df60f0316899460eeaaefa06d2dd7e4e300c1604
%global nanobind_commit cc860b2b771a0003ce70415fc56ea18f61b0a153
%global robin_map_commit 4ec1bf19c6a96125ea22062f38c2cf5b958e448e
%global benchmark_commit 99bdb2127d1fa1cff444bbefb814e105c7d20c45

Name:           python-iree-base-compiler
Version:        3.8.0
Release:        %autorelease
Summary:        IREE compiler Python API and native compiler
License:        Apache-2.0 WITH LLVM-exception
URL:            https://iree.dev/
VCS:            git:https://github.com/iree-org/iree.git
#!RemoteAsset:  sha256:81be830e331c1840fd09eecec2bed62a61c81ef9d5a2733a81f730aeb3ca591c
Source0:        https://github.com/iree-org/iree/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
#!RemoteAsset:  sha256:87fc79472eb30b734cbe700dfe3edc0bdb96c33e3ce44e48ab327bbd8783f07f
Source1:        https://codeload.github.com/pytorch/cpuinfo/tar.gz/%{cpuinfo_commit}#/cpuinfo-%{cpuinfo_commit}.tar.gz
#!RemoteAsset:  sha256:f77f842e996f5bbfa25305a7b38b40d1325fb44154f2bf9880c58356ece92c62
Source2:        https://codeload.github.com/dvidelabs/flatcc/tar.gz/%{flatcc_commit}#/flatcc-%{flatcc_commit}.tar.gz
#!RemoteAsset:  sha256:70de3ec1eec289552052dfb886a49a4578b65d84fd536da3254731c8165cb3e6
Source3:        https://codeload.github.com/KhronosGroup/Vulkan-Headers/tar.gz/%{vulkan_headers_commit}#/Vulkan-Headers-%{vulkan_headers_commit}.tar.gz
#!RemoteAsset:  sha256:3a9fef5199fc1a6d8513ca81c2d10cd811be4806d744059f0c6e847401e0f7f5
Source4:        https://codeload.github.com/wjakob/nanobind/tar.gz/%{nanobind_commit}#/nanobind-%{nanobind_commit}.tar.gz
#!RemoteAsset:  sha256:4968947bd2e908854481519ec422823af4161a286ff1e16943293b753e80cb3f
Source5:        https://codeload.github.com/Tessil/robin-map/tar.gz/%{robin_map_commit}#/robin-map-%{robin_map_commit}.tar.gz
#!RemoteAsset:  sha256:90885324d98c85dbbabafc4ab997fc41988006f34f994d742d7aa902b000e9ab
Source6:        https://codeload.github.com/google/benchmark/tar.gz/%{benchmark_commit}#/benchmark-%{benchmark_commit}.tar.gz
Patch0:         2000-Use-packaged-nanobind-source.patch
BuildSystem:    pyproject

BuildOption(prep):  -n %{srcname}-%{version}
BuildOption(install):  -l iree_compiler

BuildRequires:  cmake
BuildRequires:  clang22-devel
BuildRequires:  gcc-c++
BuildRequires:  lld22-devel
BuildRequires:  mlir22-devel
BuildRequires:  llvm22-devel
BuildRequires:  ninja
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(numpy) >= 2.0
BuildRequires:  python3dist(packaging)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(sympy)
BuildRequires:  python3dist(wheel)

Requires:       python3dist(numpy)
Requires:       python3dist(packaging)
Provides:       python3-iree-base-compiler = %{version}-%{release}
%python_provide python3-iree-base-compiler

%description
IREE's compiler Python API and native compiler lower ML programs through MLIR
to deployable IREE modules and executable artifacts.

%prep -a
mkdir -p third_party/llvm-project third_party/cpuinfo third_party/flatcc third_party/vulkan_headers third_party/benchmark nanobind-source
tar -xf %{SOURCE1} --strip-components=1 -C third_party/cpuinfo
tar -xf %{SOURCE2} --strip-components=1 -C third_party/flatcc
tar -xf %{SOURCE3} --strip-components=1 -C third_party/vulkan_headers
tar -xf %{SOURCE4} --strip-components=1 -C nanobind-source
mkdir -p nanobind-source/ext/robin_map
tar -xf %{SOURCE5} --strip-components=1 -C nanobind-source/ext/robin_map
tar -xf %{SOURCE6} --strip-components=1 -C third_party/benchmark
printf '{"package-version":"%{version}"}\n' > compiler/version_local.json

%generate_buildrequires
cd compiler
%pyproject_buildrequires

%build -p
export IREE_NANOBIND_SOURCE_DIR="%{_builddir}/%{srcname}-%{version}/nanobind-source"
export IREE_BUILD_BUNDLED_LLVM=OFF
export CMAKE_PREFIX_PATH="%{_prefix}/%{_lib}/llvm22${CMAKE_PREFIX_PATH:+:${CMAKE_PREFIX_PATH}}"
export IREE_ENABLE_CPUINFO=ON
export IREE_TARGET_BACKEND_ROCM=OFF
export IREE_TARGET_BACKEND_CUDA=OFF

%install -p
cd compiler
install -Dpm 0644 ../LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE
install -Dpm 0644 ../README.md %{buildroot}%{_docdir}/%{name}/README.md

%check -a
%{python3} -c 'import importlib.metadata; assert importlib.metadata.version("iree-base-compiler") == "%{version}"; import iree.compiler'

%files -f %{pyproject_files}
%license %{_licensedir}/%{name}/LICENSE
%doc %{_docdir}/%{name}/README.md

%changelog
%autochangelog

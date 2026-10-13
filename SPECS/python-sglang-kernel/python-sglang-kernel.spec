# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname sglang
%global kernel_version 0.4.7

Name:           python-sglang-kernel
Version:        %{kernel_version}
Release:        %autorelease
Summary:        CUDA kernel library for SGLang
License:        Apache-2.0
URL:            https://github.com/sgl-project/sglang/tree/v0.5.21/python/sglang/kernels/aot
VCS:            git:https://github.com/sgl-project/sglang.git
#!RemoteAsset:  sha256:c44951b7871dac61262fc04e9fca628175758a97fa5f603c522b31dc31b94249
Source0:        https://github.com/sgl-project/sglang/archive/refs/tags/v0.5.21.tar.gz#/%{srcname}-0.5.21.tar.gz
#!RemoteAsset:  sha256:09237099a70f80bff1dc8bb80c843a674bb4fdcb46e43cc6993e711c5ca89bb5
Source1:        https://github.com/NVIDIA/cutlass/archive/57e3cfb47a2d9e0d46eb6335c3dc411498efa198.tar.gz#/cutlass-57e3cfb.tar.gz
#!RemoteAsset:  sha256:c314292789d28c3c3b420e75a7b2d1706f685f7fb63289128d46aeaea2c6be71
Source2:        https://github.com/fmtlib/fmt/archive/553ec11ec06fbe0beebfbb45f9dc3c9eabd83d28.tar.gz#/fmt-553ec11.tar.gz
#!RemoteAsset:  sha256:7d998625d1035ac496d06a81117727647169422ee67b8889609f06fd5367c491
Source3:        https://github.com/triton-lang/triton/archive/refs/tags/v3.7.1.tar.gz#/triton-v3.7.1.tar.gz
#!RemoteAsset:  sha256:931dfd118f4b6de8c7d98702153c7c03840139170af21a07607693bd9749744d
Source4:        https://github.com/flashinfer-ai/flashinfer/archive/bc29697ba20b7e6bdb728ded98f04788e16ee021.tar.gz#/flashinfer-bc29697.tar.gz
#!RemoteAsset:  sha256:418b5681584dc3efff496a1cab5ffd58d2728d89dcfe0ea16e6985d6ef35c68c
Source5:        https://github.com/sgl-project/sgl-attn/archive/f89bc2306632d1ec5f97b014dded4254f5b4a907.tar.gz#/sgl-attn-f89bc230.tar.gz
#!RemoteAsset:  sha256:ab2af4657683a1bbaa707a2781a5e2c2792eba574ff36905f1832598e67fea79
Source6:        https://github.com/sgl-project/FlashMLA/archive/3e18517fb055a6c9608eef5a1f1347fb1a047bbd.tar.gz#/flashmla-3e18517.tar.gz
#!RemoteAsset:  sha256:9f6c53320a85b4a570975e557918cde65168cd311f081920446c238437347dc6
Source7:        https://github.com/NVIDIA/cutlass/archive/147f5673d0c1c3dcf66f78d677fd647e4a020219.tar.gz#/cutlass-147f567.tar.gz
BuildSystem:    pyproject

BuildOption(prep):  -n %{srcname}-0.5.21/python/sglang/kernels/aot

BuildRequires:  cuda-toolkit
BuildRequires:  cmake >= 3.31
BuildRequires:  gcc-c++
BuildRequires:  ninja
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(scikit-build-core) >= 0.10
BuildRequires:  python3dist(torch) = 2.14.0
BuildRequires:  python3dist(wheel)

Requires:       python3dist(torch) = 2.14.0

%description
SGLang Kernel provides optimized CUDA compute primitives used by the SGLang
inference engine. This source package builds the AOT extension, including SM90
and newer kernels where supported by the selected CUDA toolkit, from SGLang 0.5.21.
The RISC-V build host has no supported CUDA toolkit, so this package cannot be
compiled for RISC-V in the current build environment.

%prep -a
sed -i \
  -e 's|URL      https://${GITHUB_ARTIFACTORY}/sgl-project/FlashMLA/archive/3e18517fb055a6c9608eef5a1f1347fb1a047bbd.tar.gz|SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/third-party/flashmla|' \
  -e '/URL_HASH SHA256=ab2af4657683a1bbaa707a2781a5e2c2792eba574ff36905f1832598e67fea79/d' \
  -e 's|URL      https://${GITHUB_ARTIFACTORY}/NVIDIA/cutlass/archive/147f5673d0c1c3dcf66f78d677fd647e4a020219.tar.gz|SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/third-party/flashmla/csrc/cutlass|' \
  -e '/URL_HASH SHA256=9f6c53320a85b4a570975e557918cde65168cd311f081920446c238437347dc6/d' \
  cmake/flashmla.cmake
sed -i \
  -e 's|URL      https://${GITHUB_ARTIFACTORY}/NVIDIA/cutlass/archive/57e3cfb47a2d9e0d46eb6335c3dc411498efa198.tar.gz|SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/third-party/cutlass|' \
  -e '/URL_HASH SHA256=09237099a70f80bff1dc8bb80c843a674bb4fdcb46e43cc6993e711c5ca89bb5/d' \
  -e 's|URL      https://${GITHUB_ARTIFACTORY}/fmtlib/fmt/archive/553ec11ec06fbe0beebfbb45f9dc3c9eabd83d28.tar.gz|SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/third-party/fmt|' \
  -e '/URL_HASH SHA256=c314292789d28c3c3b420e75a7b2d1706f685f7fb63289128d46aeaea2c6be71/d' \
  -e 's|URL      https://${GITHUB_ARTIFACTORY}/triton-lang/triton/archive/v3.7.1.tar.gz|SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/third-party/triton|' \
  -e '/URL_HASH SHA256=7d998625d1035ac496d06a81117727647169422ee67b8889609f06fd5367c491/d' \
  -e 's|URL      https://${GITHUB_ARTIFACTORY}/flashinfer-ai/flashinfer/archive/bc29697ba20b7e6bdb728ded98f04788e16ee021.tar.gz|SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/third-party/flashinfer|' \
  -e '/URL_HASH SHA256=931dfd118f4b6de8c7d98702153c7c03840139170af21a07607693bd9749744d/d' \
  -e 's|URL      https://${GITHUB_ARTIFACTORY}/sgl-project/sgl-attn/archive/f89bc2306632d1ec5f97b014dded4254f5b4a907.tar.gz|SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/third-party/flash-attention|' \
  -e '/URL_HASH SHA256=418b5681584dc3efff496a1cab5ffd58d2728d89dcfe0ea16e6985d6ef35c68c/d' CMakeLists.txt
mkdir -p third-party/cutlass third-party/fmt third-party/triton \
    third-party/flashinfer third-party/flash-attention third-party/flashmla/csrc/cutlass
tar -xf %{SOURCE1} --strip-components=1 -C third-party/cutlass
tar -xf %{SOURCE2} --strip-components=1 -C third-party/fmt
tar -xf %{SOURCE3} --strip-components=1 -C third-party/triton
tar -xf %{SOURCE4} --strip-components=1 -C third-party/flashinfer
tar -xf %{SOURCE5} --strip-components=1 -C third-party/flash-attention
tar -xf %{SOURCE6} --strip-components=1 -C third-party/flashmla
tar -xf %{SOURCE7} --strip-components=1 -C third-party/flashmla/csrc/cutlass

%generate_buildrequires
%pyproject_buildrequires

%build -p
%pyproject_wheel

%install -p
%pyproject_install

%check -a
%pyproject_check_import sgl_kernel

%files -f %{pyproject_files}
%license LICENSE
%doc THIRDPARTYNOTICES.txt

%changelog
%autochangelog

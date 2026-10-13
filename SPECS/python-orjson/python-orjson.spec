# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: purofle <yuguo.or@isrc.iscas.ac.cn>
# SPDX-FileContributor: yyjeqhc <jialin.oerv@isrc.iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname orjson

Name:           python-%{srcname}
Version:        3.11.7
Release:        %autorelease
Summary:        Fast, correct Python JSON library supporting dataclasses, datetimes, and numpy
License:        MPL-2.0 AND (Apache-2.0 OR MIT)
URL:            https://github.com/ijl/orjson
#!RemoteAsset:  sha256:9b1a67243945819ce55d24a30b59d6a168e86220452d2c96f4d1f093e71c0c49
Source0:        https://files.pythonhosted.org/packages/source/o/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(parso)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  rust-rpm-macros
BuildRequires:  crate(associative-cache-2/default) >= 2.0.0
BuildRequires:  crate(bytes-1/default) >= 1.0.0
BuildRequires:  crate(bytecount-0.6/runtime-dispatch-simd) >= 0.6.7
BuildRequires:  crate(cc-1/default) >= 1.0.0
BuildRequires:  crate(encoding-rs-0.8/default) >= 0.8.0
BuildRequires:  crate(half-2/default) >= 2.0.0
BuildRequires:  crate(itoa-1/default) >= 1.0.0
BuildRequires:  crate(itoap-1/simd) >= 1.0.0
BuildRequires:  crate(itoap-1/std) >= 1.0.0
BuildRequires:  crate(jiff-0.2/default) >= 0.2.0
BuildRequires:  crate(once-cell-1/alloc) >= 1.0.0
BuildRequires:  crate(once-cell-1/race) >= 1.0.0
BuildRequires:  crate(pyo3-ffi-0.28) >= 0.28.0
BuildRequires:  crate(pyo3-build-config-0.28/default) >= 0.28.0
BuildRequires:  crate(serde-1/default) >= 1.0.0
BuildRequires:  crate(serde-json-1/std) >= 1.0.0
BuildRequires:  crate(simdutf8-0.1/aarch64-neon) >= 0.1.0
BuildRequires:  crate(simdutf8-0.1/public-imp) >= 0.1.0
BuildRequires:  crate(simdutf8-0.1/std) >= 0.1.0
BuildRequires:  crate(smallvec-1/union) >= 1.11.0
BuildRequires:  crate(smallvec-1/write) >= 1.11.0
BuildRequires:  crate(uuid-1/default) >= 1.0.0
BuildRequires:  crate(xxhash-rust-0.8/xxh3) >= 0.8.0
BuildRequires:  crate(zmij-1/default) >= 1.0.0
BuildRequires:  crate(version-check-0.9/default) >= 0.9.0

%prep -a
%rust_setup_registry
rm -f Cargo.lock

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
orjson is a fast, correct JSON library for Python. It benchmarks as
the fastest Python library for JSON and is more correct than the standard
json library or other third-party libraries. It serializes dataclass,
datetime, numpy, and UUID instances natively.

%build -p
%ifarch riscv64
# Work around rustc SIGSEGV while compiling pyo3 under release optimization.
export RUST_MIN_STACK=33554432
export CARGO_BUILD_JOBS=1
export CARGO_PROFILE_RELEASE_OPT_LEVEL=1
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=256
%endif

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE-APACHE LICENSE-MIT LICENSE-MPL-2.0

%changelog
%autochangelog

# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name pyo3-async-runtimes
%global full_version 0.29.0
%global pkgname pyo3-async-runtimes-0.29

Name:           rust-pyo3-async-runtimes-0.29
Version:        0.29.0
Release:        %autorelease
Summary:        Rust crate "pyo3-async-runtimes"
License:        Apache-2.0
URL:            https://github.com/PyO3/pyo3-async-runtimes
#!RemoteAsset:  sha256:b3ef68daa7316a3fac65e5e18b2203f010346de1c1c53456811a2624673ab046
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Requires:       crate(futures-channel-0.3/default) >= 0.3.0
Requires:       crate(futures-util-0.3/default) >= 0.3.0
Requires:       crate(once-cell-1/default) >= 1.14.0
Requires:       crate(pin-project-lite-0.2/default) >= 0.2.0
Requires:       crate(pyo3-0.29/default) >= 0.29.0
Provides:       crate(%{pkgname}) = %{version}
Provides:       crate(%{pkgname}/default) = %{version}

%description
Source code for takopackized Rust crate "pyo3-async-runtimes"

%package     -n %{name}+tokio
Summary:        PyO3 bridges from Rust runtimes to Python's Asyncio library - feature "tokio"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(tokio-1/default) >= 1.13.0
Requires:       crate(tokio-1/rt) >= 1.13.0
Requires:       crate(tokio-1/rt-multi-thread) >= 1.13.0
Requires:       crate(tokio-1/time) >= 1.13.0
Provides:       crate(%{pkgname}/tokio) = %{version}
Provides:       crate(%{pkgname}/tokio-runtime) = %{version}

%description -n %{name}+tokio
This metapackage enables feature "tokio" for the Rust pyo3-async-runtimes crate.

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

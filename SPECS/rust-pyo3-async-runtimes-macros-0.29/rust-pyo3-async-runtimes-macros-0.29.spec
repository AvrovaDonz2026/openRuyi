# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name pyo3-async-runtimes-macros
%global full_version 0.29.0
%global pkgname pyo3-async-runtimes-macros-0.29

Name:           rust-pyo3-async-runtimes-macros-0.29
Version:        0.29.0
Release:        %autorelease
Summary:        Rust crate "pyo3-async-runtimes-macros"
License:        Apache-2.0
URL:            https://github.com/PyO3/pyo3-async-runtimes
#!RemoteAsset:  sha256:faf75ff3922e6830adcaa30f3a359ce861326f6161f16a13d97adb40ba6a744a
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Requires:       crate(proc-macro2-1/default) >= 1.0.0
Requires:       crate(quote-1/default) >= 1.0.0
Requires:       crate(syn-2/default) >= 2.0.0
Requires:       crate(syn-2/full) >= 2.0.0
Provides:       crate(%{pkgname}) = %{version}
Provides:       crate(%{pkgname}/default) = %{version}

%description
Source code for takopackized Rust crate "pyo3-async-runtimes-macros"

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

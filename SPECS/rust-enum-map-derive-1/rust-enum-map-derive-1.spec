# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name enum-map-derive
%global full_version 1.0.1
%global pkgname enum-map-derive-1

Name:           rust-enum-map-derive-1
Version:        1.0.1
Release:        %autorelease
Summary:        Rust crate "enum-map-derive"
License:        MIT OR Apache-2.0
URL:            https://codeberg.org/sugar700/enum-map
#!RemoteAsset:  sha256:7127272f64b3e098f7d81f350d672081b879bff896d219c42370dc858b1af9ff
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Requires:       crate(proc-macro2-1/default) >= 1.0.107
Requires:       crate(quote-1/default) >= 1.0.47
Requires:       crate(syn-3/derive) >= 3.0.2
Requires:       crate(syn-3/parsing) >= 3.0.2
Requires:       crate(syn-3/printing) >= 3.0.2
Requires:       crate(syn-3/proc-macro) >= 3.0.2

Provides:       crate(%{pkgname}) = %{version}
Provides:       crate(%{pkgname}/default) = %{version}

%description
Source code for takopackized Rust crate "enum-map-derive"

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

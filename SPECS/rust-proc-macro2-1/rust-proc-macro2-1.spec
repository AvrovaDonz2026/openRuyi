# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name proc-macro2
%global full_version 1.0.107
%global pkgname proc-macro2-1

Name:           rust-proc-macro2-1
Version:        1.0.107
Release:        %autorelease
Summary:        Rust crate "proc-macro2"
License:        MIT OR Apache-2.0
URL:            https://github.com/dtolnay/proc-macro2
#!RemoteAsset:  sha256:985e7ec9bb745e6ce6535b544d84d6cd6f7ad8bd711c398938ae983b91a766d9
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Requires:       crate(unicode-ident-1/default) >= 1.0.0

Provides:       crate(%{pkgname}) = %{version}
Provides:       crate(%{pkgname}/default) = %{version}
Provides:       crate(%{pkgname}/nightly) = %{version}
Provides:       crate(%{pkgname}/proc-macro) = %{version}
Provides:       crate(%{pkgname}/span-locations) = %{version}

%description
Source code for takopackized Rust crate "proc-macro2"

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

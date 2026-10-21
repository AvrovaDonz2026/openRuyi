# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name webpki-roots
%global full_version 1.0.10
%global pkgname webpki-roots-1

Name:           rust-webpki-roots-1
Version:        1.0.10
Release:        %autorelease
Summary:        Rust crate "webpki-roots"
License:        CDLA-Permissive-2.0
URL:            https://github.com/rustls/webpki-roots
#!RemoteAsset:  sha256:1c1c8e20c8a38fc7d65abfe74eb7280e4aa667e8eec8bc84996d2874810748d9
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Requires:       crate(rustls-pki-types-1) >= 1.8.0

Provides:       crate(%{pkgname}) = %{version}
Provides:       crate(%{pkgname}/default) = %{version}

%description
Source code for takopackized Rust crate "webpki-roots"

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

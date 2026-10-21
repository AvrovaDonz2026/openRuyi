# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name webpki-root-certs
%global full_version 1.0.10
%global pkgname webpki-root-certs-1

Name:           rust-webpki-root-certs-1
Version:        1.0.10
Release:        %autorelease
Summary:        Rust crate "webpki-root-certs"
License:        CDLA-Permissive-2.0
URL:            https://github.com/rustls/webpki-roots
#!RemoteAsset:  sha256:58ec80e73fd8baf57bf0d9615554c75348bda990d6d5bbeab964dd068319fecb
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Requires:       crate(rustls-pki-types-1) >= 1.8.0

Provides:       crate(%{pkgname}) = %{version}
Provides:       crate(%{pkgname}/default) = %{version}

%description
Source code for takopackized Rust crate "webpki-root-certs"

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

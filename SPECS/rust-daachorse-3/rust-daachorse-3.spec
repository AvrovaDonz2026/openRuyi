# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name daachorse
%global full_version 3.0.0
%global pkgname daachorse-3

Name:           rust-daachorse-3
Version:        3.0.0
Release:        %autorelease
Summary:        Rust crate "daachorse"
License:        MIT OR Apache-2.0
URL:            https://github.com/daac-tools/daachorse
#!RemoteAsset:  sha256:9d87f75bbe32ee10609201e09e818537df81c3acb436be2b78f47cc85d139475
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Provides:       crate(%{pkgname}) = %{version}

%description
Source code for takopackized Rust crate "daachorse"

%package     -n %{name}+alloc
Summary:        Double-Array Aho-Corasick - feature "alloc"
Requires:       crate(%{pkgname}) = %{version}
Provides:       crate(%{pkgname}/alloc) = %{version}

%description -n %{name}+alloc
This metapackage enables feature "alloc" for the Rust daachorse crate.

%package     -n %{name}+default
Summary:        Double-Array Aho-Corasick - feature "default"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(%{pkgname}/alloc) = %{version}
Provides:       crate(%{pkgname}/default) = %{version}

%description -n %{name}+default
This metapackage enables feature "default" for the Rust daachorse crate.

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

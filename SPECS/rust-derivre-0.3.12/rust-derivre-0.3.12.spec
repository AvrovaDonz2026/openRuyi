# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name derivre
%global full_version 0.3.12
%global pkgname derivre-0.3

Name:           rust-derivre-0.3.12
Version:        0.3.12
Release:        %autorelease
Summary:        Rust crate "derivre"
License:        MIT
URL:            https://github.com/microsoft/derivre
#!RemoteAsset:  sha256:a892ec3953f4ca893e8d2086ed03d4b58e19c77ffb864a574b332d7d40c175f3
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Requires:       crate(anyhow-1/default) >= 1.0.95
Requires:       crate(bytemuck-1/default) >= 1.21.0
Requires:       crate(bytemuck-derive-1/default) >= 1.8.1
Requires:       crate(hashbrown-0.17) >= 0.17.1
Requires:       crate(regex-syntax-0.8/default) >= 0.8.5
Requires:       crate(strum-0.28/default) >= 0.28.0
Requires:       crate(strum-0.28/derive) >= 0.28.0
Provides:       crate(%{pkgname}) = %{version}
Provides:       crate(%{pkgname}/compress) = %{version}

%description
Source code for takopackized Rust crate "derivre"

%package     -n %{name}+ahash
Summary:        Derivative-based regular expression engine - feature "ahash"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(ahash-0.8/default) >= 0.8.11
Provides:       crate(%{pkgname}/ahash) = %{version}

%description -n %{name}+ahash
This metapackage enables feature "ahash" for the Rust derivre crate, by pulling in any additional dependencies needed by that feature.

%package     -n %{name}+default
Summary:        Derivative-based regular expression engine - feature "default"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(%{pkgname}/ahash) = %{version}
Requires:       crate(%{pkgname}/compress) = %{version}
Provides:       crate(%{pkgname}/default) = %{version}

%description -n %{name}+default
This metapackage enables feature "default" for the Rust derivre crate, by pulling in any additional dependencies needed by that feature.

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

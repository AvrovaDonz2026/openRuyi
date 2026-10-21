# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name enum-map
%global full_version 3.1.0
%global pkgname enum-map-3

Name:           rust-enum-map-3
Version:        3.1.0
Release:        %autorelease
Summary:        Rust crate "enum-map"
License:        MIT OR Apache-2.0
URL:            https://codeberg.org/sugar700/enum-map
#!RemoteAsset:  sha256:d4532960034c15ba2f55e9eee631040ecc473c32e6c4b200828c759840f13a06
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Provides:       crate(%{pkgname}) = %{version}

%description
Source code for takopackized Rust crate "enum-map"

%package     -n %{name}+arbitrary
Summary:        Map with C-like enum keys represented internally as an array - feature "arbitrary"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(arbitrary-1/default) >= 1.4.2
Provides:       crate(%{pkgname}/arbitrary) = %{version}

%description -n %{name}+arbitrary
This metapackage enables feature "arbitrary" for the Rust enum-map crate, by pulling in any additional dependencies needed by that feature.

%package     -n %{name}+bytemuck
Summary:        Map with C-like enum keys represented internally as an array - feature "bytemuck"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(bytemuck-1/default) >= 1.25.2
Provides:       crate(%{pkgname}/bytemuck) = %{version}

%description -n %{name}+bytemuck
This metapackage enables feature "bytemuck" for the Rust enum-map crate, by pulling in any additional dependencies needed by that feature.

%package     -n %{name}+derive
Summary:        Map with C-like enum keys represented internally as an array - feature "derive" and 1 more
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(enum-map-derive-1/default) >= 1.0.0
Provides:       crate(%{pkgname}/default) = %{version}
Provides:       crate(%{pkgname}/derive) = %{version}

%description -n %{name}+derive
This metapackage enables feature "derive" for the Rust enum-map crate, by pulling in any additional dependencies needed by that feature.

Additionally, this package also provides the "default" feature.

%package     -n %{name}+serde
Summary:        Map with C-like enum keys represented internally as an array - feature "serde"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(serde-1) >= 1.0.229
Provides:       crate(%{pkgname}/serde) = %{version}

%description -n %{name}+serde
This metapackage enables feature "serde" for the Rust enum-map crate, by pulling in any additional dependencies needed by that feature.

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

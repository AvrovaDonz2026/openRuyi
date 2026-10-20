# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name rand_distr
%global full_version 0.4.3
%global pkgname rand-distr-0.4

Name:           rust-rand-distr-0.4
Version:        0.4.3
Release:        %autorelease
Summary:        Rust crate "rand_distr"
License:        MIT OR Apache-2.0
URL:            https://rust-random.github.io/book
#!RemoteAsset:  sha256:32cb0b9bc82b0a0876c2dd994a7e7a2683d3e7390ca40e6886785ef0c7e3ee31
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Requires:       crate(num-traits-0.2/libm) >= 0.2.0
Requires:       crate(rand-0.8/default) >= 0.8.0
Provides:       crate(%{pkgname}) = %{version}

%description
Source code for takopackized Rust crate "rand_distr"

%package     -n %{name}+alloc
Summary:        Sampling from random number distributions - feature "alloc"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(rand-0.8/alloc) >= 0.8.0
Provides:       crate(%{pkgname}/alloc) = %{version}

%description -n %{name}+alloc
This metapackage enables feature "alloc" for the Rust rand_distr crate.

%package     -n %{name}+default
Summary:        Sampling from random number distributions - feature "default"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(%{pkgname}/std) = %{version}
Provides:       crate(%{pkgname}/default) = %{version}

%description -n %{name}+default
This metapackage enables feature "default" for the Rust rand_distr crate.

%package     -n %{name}+std
Summary:        Sampling from random number distributions - feature "std"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(%{pkgname}/alloc) = %{version}
Requires:       crate(rand-0.8/std) >= 0.8.0
Provides:       crate(%{pkgname}/std) = %{version}

%description -n %{name}+std
This metapackage enables feature "std" for the Rust rand_distr crate.

%package     -n %{name}+serde1
Summary:        Sampling from random number distributions - feature "serde1"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(rand-0.8/serde1) >= 0.8.0
Requires:       crate(serde-1/derive) >= 1.0.103
Provides:       crate(%{pkgname}/serde1) = %{version}

%description -n %{name}+serde1
This metapackage enables feature "serde1" for the Rust rand_distr crate.

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

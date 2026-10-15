# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
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

%package     -n %{name}+async-channel
Summary:        PyO3 bridges from Rust runtimes to Python's Asyncio library - feature "async-channel"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(async-channel-2/default) >= 2.3.0
Requires:       crate(futures-channel-0.3/sink) >= 0.3.0
Requires:       crate(futures-util-0.3/sink) >= 0.3.0
Provides:       crate(%{pkgname}/async-channel) = %{version}
Provides:       crate(%{pkgname}/unstable-streams) = %{version}

%description -n %{name}+async-channel
This metapackage enables the async-channel and unstable-streams features for the Rust pyo3-async-runtimes crate.

%package     -n %{name}+async-std
Summary:        PyO3 bridges from Rust runtimes to Python's Asyncio library - feature "async-std-runtime"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(async-std-1/default) >= 1.12.0
Requires:       crate(async-std-1/unstable) >= 1.12.0
Provides:       crate(%{pkgname}/async-std-runtime) = %{version}
Provides:       crate(%{pkgname}/async-std) = %{version}

%description -n %{name}+async-std
This metapackage enables the async-std-runtime feature for the Rust pyo3-async-runtimes crate.

%package     -n %{name}+clap
Summary:        PyO3 bridges from Rust runtimes to Python's Asyncio library - feature "clap"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(clap-4/default) >= 4.5.0
Provides:       crate(%{pkgname}/clap) = %{version}

%description -n %{name}+clap
This metapackage enables the clap feature for the Rust pyo3-async-runtimes crate.

%package     -n %{name}+inventory
Summary:        PyO3 bridges from Rust runtimes to Python's Asyncio library - feature "inventory"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(inventory-0.3/default) >= 0.3.0
Provides:       crate(%{pkgname}/inventory) = %{version}

%description -n %{name}+inventory
This metapackage enables the inventory feature for the Rust pyo3-async-runtimes crate.

%package     -n %{name}+pyo3-async-runtimes-macros
Summary:        PyO3 bridges from Rust runtimes to Python's Asyncio library - procedural macros
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(pyo3-async-runtimes-macros-0.29/default) >= 0.29.0
Provides:       crate(%{pkgname}/attributes) = %{version}
Provides:       crate(%{pkgname}/pyo3-async-runtimes-macros) = %{version}

%description -n %{name}+pyo3-async-runtimes-macros
This metapackage enables the procedural macro support for the Rust pyo3-async-runtimes crate.

%package     -n %{name}+testing
Summary:        PyO3 bridges from Rust runtimes to Python's Asyncio library - feature "testing"
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(%{pkgname}/clap) = %{version}
Requires:       crate(%{pkgname}/inventory) = %{version}
Provides:       crate(%{pkgname}/testing) = %{version}

%description -n %{name}+testing
This metapackage enables the testing feature for the Rust pyo3-async-runtimes crate.

%files -n %{name}+async-channel

%files -n %{name}+async-std

%files -n %{name}+clap

%files -n %{name}+inventory

%files -n %{name}+pyo3-async-runtimes-macros

%files -n %{name}+testing

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

%files -n %{name}+tokio

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global crate_name tokenizers
%global full_version 0.23.2
%global pkgname tokenizers-0.23

Name:           rust-tokenizers-0.23
Version:        0.23.2
Release:        %autorelease
Summary:        Rust crate "tokenizers"
License:        Apache-2.0
URL:            https://github.com/huggingface/tokenizers
#!RemoteAsset:  sha256:7afbf6e88718afcc138bad01d6ccc3051dbbc3b2ce9793d8b8a3aeb610969cfc
Source:         https://static.crates.io/crates/%{crate_name}/%{full_version}/download#/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    rustcrates

BuildRequires:  rust-rpm-macros

Requires:       crate(ahash-0.8/default) >= 0.8.11
Requires:       crate(ahash-0.8/serde) >= 0.8.11
Requires:       crate(compact-str-0.9/default) >= 0.9.0
Requires:       crate(compact-str-0.9/serde) >= 0.9.0
Requires:       crate(daachorse-3/default) >= 3.0.0
Requires:       crate(dary-heap-0.3/default) >= 0.3.6
Requires:       crate(dary-heap-0.3/serde) >= 0.3.6
Requires:       crate(derive-builder-0.20/default) >= 0.20.0
Requires:       crate(esaxx-rs-0.1) >= 0.1.10
Requires:       crate(getrandom-0.3/default) >= 0.3.0
Requires:       crate(itertools-0.14/default) >= 0.14.0
Requires:       crate(log-0.4/default) >= 0.4.0
Requires:       crate(macro-rules-attribute-0.2/default) >= 0.2.0
Requires:       crate(monostate-0.1/default) >= 0.1.12
Requires:       crate(paste-1/default) >= 1.0.14
Requires:       crate(rand-0.9/default) >= 0.9.0
Requires:       crate(rayon-1/default) >= 1.10.0
Requires:       crate(rayon-cond-0.4/default) >= 0.4.0
Requires:       crate(regex-1/default) >= 1.10.0
Requires:       crate(regex-syntax-0.8/default) >= 0.8.0
Requires:       crate(serde-1/default) >= 1.0.0
Requires:       crate(serde-1/derive) >= 1.0.0
Requires:       crate(serde-json-1/default) >= 1.0.0
Requires:       crate(spm-precompiled-0.1/default) >= 0.1.3
Requires:       crate(thiserror-2/default) >= 2.0.0
Requires:       crate(unicode-normalization-alignments-0.1/default) >= 0.1.0
Requires:       crate(unicode-segmentation-1/default) >= 1.11.0
Requires:       crate(unicode-categories-0.1/default) >= 0.1.0
Provides:       crate(%{pkgname}) = %{version}

%description
Source code for takopackized Rust crate "tokenizers"

%package     -n %{name}+default
Summary:        Tokenizers implementation with default features
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(%{pkgname}/esaxx-fast) = %{version}
Requires:       crate(%{pkgname}/onig) = %{version}
Requires:       crate(%{pkgname}/progressbar) = %{version}
Provides:       crate(%{pkgname}/default) = %{version}

%description -n %{name}+default
This metapackage enables the default features for the Rust tokenizers crate.

%package     -n %{name}+esaxx-fast
Summary:        Tokenizers feature for fast suffix array construction
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(esaxx-rs-0.1/cpp) >= 0.1.10
Provides:       crate(%{pkgname}/esaxx-fast) = %{version}

%description -n %{name}+esaxx-fast
This metapackage enables the esaxx_fast feature for the Rust tokenizers crate.

%package     -n %{name}+fancy-regex
Summary:        Tokenizers feature for fancy regular expressions
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(fancy-regex-0.17/default) >= 0.17.0
Provides:       crate(%{pkgname}/fancy-regex) = %{version}

%description -n %{name}+fancy-regex
This metapackage enables the fancy-regex feature for the Rust tokenizers crate.

%package     -n %{name}+hf-hub
Summary:        Tokenizers feature for Hugging Face Hub access
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(hf-hub-0.4/ureq) >= 0.4.1
Provides:       crate(%{pkgname}/hf-hub) = %{version}
Provides:       crate(%{pkgname}/http) = %{version}

%description -n %{name}+hf-hub
This metapackage enables the http feature for the Rust tokenizers crate.

%package     -n %{name}+indicatif
Summary:        Tokenizers feature for progress reporting
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(indicatif-0.18/default) >= 0.18.0
Provides:       crate(%{pkgname}/indicatif) = %{version}
Provides:       crate(%{pkgname}/progressbar) = %{version}

%description -n %{name}+indicatif
This metapackage enables progress reporting for the Rust tokenizers crate.

%package     -n %{name}+onig
Summary:        Tokenizers feature for Oniguruma regular expressions
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(onig-6) >= 6.5.1
Provides:       crate(%{pkgname}/onig) = %{version}

%description -n %{name}+onig
This metapackage enables the onig feature for the Rust tokenizers crate.

%package     -n %{name}+rustls-tls
Summary:        Tokenizers feature for Rustls TLS
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(hf-hub-0.4/rustls-tls) >= 0.4.1
Requires:       crate(hf-hub-0.4/ureq) >= 0.4.1
Provides:       crate(%{pkgname}/rustls-tls) = %{version}

%description -n %{name}+rustls-tls
This metapackage enables Rustls TLS support for the Rust tokenizers crate.

%package     -n %{name}+unstable-wasm
Summary:        Tokenizers feature for unstable WebAssembly support
Requires:       crate(%{pkgname}) = %{version}
Requires:       crate(%{pkgname}/fancy-regex) = %{version}
Requires:       crate(getrandom-0.3/wasm-js) >= 0.3.0
Provides:       crate(%{pkgname}/unstable-wasm) = %{version}

%description -n %{name}+unstable-wasm
This metapackage enables the unstable_wasm feature for the Rust tokenizers crate.

%files
%{_datadir}/cargo/registry/%{crate_name}-%{version}/

%changelog
%autochangelog

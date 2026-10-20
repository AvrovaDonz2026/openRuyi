# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name nvidia_cutlass_dsl

Name:           python-nvidia-cutlass-dsl
Version:        4.8.0
Release:        %autorelease
Summary:        NVIDIA CUTLASS Python DSL
License:        LicenseRef-NVIDIA-CUTLASS
URL:            https://github.com/NVIDIA/cutlass
#!RemoteAsset:  sha256:24f996e0e5fa88c8b417f4893e615af135bdfdfdbdbed7e239faf36a88df711b
Source0:        https://files.pythonhosted.org/packages/e4/f4/e96f452f7975dd2fd4d2a4af88c63205431dad7efbe63aff6e3a4b1ada17/%{pypi_name}-%{version}-py3-none-any.whl
BuildArch:      noarch
ExclusiveArch:  x86_64 aarch64

BuildRequires:  python-rpm-macros
BuildRequires:  unzip

Requires:       python-nvidia-cutlass-dsl-libs-base = %{version}
Requires:       python-nvidia-cutlass-dsl-libs-cu12 = %{version}

%description
CuTe DSL is the Python interface to NVIDIA CUTLASS for writing high-performance
CUDA kernels using the CuTe programming model.

%prep -a

%build -p

%install -p
mkdir -p %{buildroot}%{python3_sitelib}
unzip -q %{SOURCE0} -d %{buildroot}%{python3_sitelib}
rm -f %{buildroot}%{python3_sitelib}/nvidia_cutlass_dsl-*.dist-info/RECORD

%files
%{python3_sitelib}/cutlass/
%{python3_sitelib}/nvidia_cutlass_dsl-*.dist-info/
%exclude %{python3_sitelib}/nvidia_cutlass_dsl-*.dist-info/licenses/*
%license %{python3_sitelib}/nvidia_cutlass_dsl-*.dist-info/licenses/*

%changelog
%autochangelog

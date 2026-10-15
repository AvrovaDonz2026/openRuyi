# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name nvidia_mathdx

Name:           python-nvidia-mathdx
Version:        25.6.0
Release:        %autorelease
Summary:        NVIDIA MathDX device-side mathematical libraries
License:        LicenseRef-NVIDIA-Math-Libraries-SDK
URL:            https://developer.nvidia.com/mathdx
#!RemoteAsset:  sha256:22e6ad5d0d005f836be5cbd14e836cf2e9ea42c82deb602707246ce8198eaa96
Source0:        https://files.pythonhosted.org/packages/20/1a/a418b8c1adc58abd87fd69414c19883af5c1b10514e3dbfcc27cde831b13/%{pypi_name}-%{version}-py3-none-any.whl
BuildArch:      noarch
ExclusiveArch:  x86_64 aarch64

BuildRequires:  python-rpm-macros
BuildRequires:  unzip

Provides:       python3dist(nvidia-mathdx) = %{version}
%python_provide python3-nvidia-mathdx

%description
NVIDIA MathDX provides device-side API extensions for mathematical
calculations inside CUDA kernels, including FFT, solver, sparse, random
number generation, and compression operations.

%prep -a

%build -p

%install -p
mkdir -p %{buildroot}%{python3_sitelib}
unzip -q %{SOURCE0} -d %{buildroot}%{python3_sitelib}
rm -f %{buildroot}%{python3_sitelib}/nvidia_mathdx-*.dist-info/RECORD

%files
%{python3_sitelib}/nvidia/mathdx/
%{python3_sitelib}/nvidia_mathdx-*.dist-info/
%exclude %{python3_sitelib}/nvidia_mathdx-*.dist-info/licenses/*
%license %{python3_sitelib}/nvidia_mathdx-*.dist-info/licenses/*

%changelog
%autochangelog

# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name nvidia_cutlass_dsl_libs_base

Name:           python-nvidia-cutlass-dsl-libs-base
Version:        4.8.0
Release:        %autorelease
Summary:        NVIDIA CUTLASS DSL base libraries
License:        LicenseRef-NVIDIA-CUTLASS
URL:            https://github.com/NVIDIA/cutlass
ExclusiveArch:  x86_64 aarch64

%ifarch x86_64
#!RemoteAsset:  sha256:5e36773748f5a8061afe999264f1c3dccc5ff18ec9548a9c769d8e72632c8b00
Source0:        https://files.pythonhosted.org/packages/9e/ac/81f4d08ca7f15f42cd1abac37b909ed0ecac1a56375bb88cc2ff03254360/%{pypi_name}-%{version}-cp313-cp313-manylinux_2_28_x86_64.whl
%else
#!RemoteAsset:  sha256:4d26dd2848b2fa03954151cfd6da92b79e2f4175d87f4d661eedc77c36b7a054
Source0:        https://files.pythonhosted.org/packages/ba/03/cb09bad2c3ff82e3f42272b82e2953d12160f9457b5244427c313117374d/%{pypi_name}-%{version}-cp313-cp313-manylinux_2_28_aarch64.whl
%endif

BuildRequires:  python-rpm-macros
BuildRequires:  unzip

Provides:       python3dist(nvidia-cutlass-dsl-libs-base) = %{version}
%python_provide python3-nvidia-cutlass-dsl-libs-base

%description
Binary base libraries used by the NVIDIA CUTLASS Python DSL.

%prep -a

%build -p

%install -p
mkdir -p %{buildroot}%{python3_sitearch}
unzip -q %{SOURCE0} -d %{buildroot}%{python3_sitearch}
rm -f %{buildroot}%{python3_sitearch}/%{pypi_name}-*.dist-info/RECORD

%files
%{python3_sitearch}/cutlass/
%{python3_sitearch}/%{pypi_name}-*.dist-info/
%exclude %{python3_sitearch}/%{pypi_name}-*.dist-info/licenses/*
%license %{python3_sitearch}/%{pypi_name}-*.dist-info/licenses/*

%changelog
%autochangelog

# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name nvidia_cutlass_dsl_libs_cu12

Name:           python-nvidia-cutlass-dsl-libs-cu12
Version:        4.8.0
Release:        %autorelease
Summary:        NVIDIA CUTLASS DSL CUDA 12 libraries
License:        LicenseRef-NVIDIA-CUTLASS
URL:            https://github.com/NVIDIA/cutlass
ExclusiveArch:  x86_64 aarch64

%ifarch x86_64
#!RemoteAsset:  sha256:a06ea6a42c921ec66b190f14849e152a95a45f28819214488b9b0aa34168da33
Source0:        https://files.pythonhosted.org/packages/6e/6f/0a6f2988575a3f7b78c88a67fb4fffcf32e1eee31f1c5c76db0f1674f127/%{pypi_name}-%{version}-cp313-cp313-manylinux_2_28_x86_64.whl
%else
#!RemoteAsset:  sha256:08af2b89f33081df69b64be1cad133f9f767274b33669882cbee6a5fa35c5fcc
Source0:        https://files.pythonhosted.org/packages/9c/0c/b81c27b5f0304ad3ad4c8d195aff70e5270ea57b90837871a89150d5fd8e/%{pypi_name}-%{version}-cp313-cp313-manylinux_2_28_aarch64.whl
%endif

BuildRequires:  python-rpm-macros
BuildRequires:  unzip

Provides:       python3dist(nvidia-cutlass-dsl-libs-cu12) = %{version}
%python_provide python3-nvidia-cutlass-dsl-libs-cu12

%description
Binary CUDA 12 libraries used by the NVIDIA CUTLASS Python DSL.

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

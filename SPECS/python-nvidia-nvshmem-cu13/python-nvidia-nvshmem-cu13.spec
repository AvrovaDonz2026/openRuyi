# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name nvidia_nvshmem_cu13

Name:           python-nvidia-nvshmem-cu13
Version:        3.8.0
Release:        %autorelease
Summary:        NVIDIA NVSHMEM CUDA 13 runtime libraries
License:        Apache-2.0
URL:            https://github.com/NVIDIA/nvshmem
VCS:            git:https://github.com/NVIDIA/nvshmem.git
ExclusiveArch:  x86_64 aarch64

%ifarch x86_64
#!RemoteAsset:  sha256:81a4d1f666543e6d34df6d2ff940c7da1435e34e186aab6f3c2b48861b64ef38
Source0:        https://files.pythonhosted.org/packages/74/5d/674525ba89232e9f7ae71f393ee97a7855e82728099ebda4c377901300e2/%{pypi_name}-%{version}-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
%else
#!RemoteAsset:  sha256:8120175024f52a64323cfc5d645e95ac7345f1ee243a998d140ce19163285294
Source0:        https://files.pythonhosted.org/packages/49/a3/a17ee2e50d4cdf0a18716d8ded8be8248430f768c87f6807d431681645c2/%{pypi_name}-%{version}-py3-none-manylinux2014_aarch64.manylinux_2_17_aarch64.whl
%endif

BuildRequires:  python-rpm-macros
BuildRequires:  unzip

Provides:       python3dist(nvidia-nvshmem-cu13) = %{version}
%python_provide python3-nvidia-nvshmem-cu13

%description
NVIDIA NVSHMEM runtime libraries for CUDA 13 GPU clusters.

%prep -a

%build -p

%install -p
mkdir -p %{buildroot}%{python3_sitearch}
unzip -q %{SOURCE0} -d %{buildroot}%{python3_sitearch}
rm -f %{buildroot}%{python3_sitearch}/%{pypi_name}-*.dist-info/RECORD

%files
%{python3_sitearch}/nvidia/
%{python3_sitearch}/%{pypi_name}-*.dist-info/
%exclude %{python3_sitearch}/%{pypi_name}-*.dist-info/licenses/*
%license %{python3_sitearch}/%{pypi_name}-*.dist-info/licenses/*

%changelog
%autochangelog

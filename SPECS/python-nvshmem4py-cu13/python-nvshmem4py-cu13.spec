# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name nvshmem4py_cu13

Name:           python-nvshmem4py-cu13
Version:        0.4.0
Release:        %autorelease
Summary:        Python bindings for NVSHMEM with CUDA 13
License:        Apache-2.0
URL:            https://github.com/NVIDIA/nvshmem
VCS:            git:https://github.com/NVIDIA/nvshmem.git
ExclusiveArch:  x86_64 aarch64

%ifarch x86_64
#!RemoteAsset:  sha256:401459b3a6d0dd2b5cc787a65385e4d76478fbdd8174e5d85d93ed97e76279c8
Source0:        https://files.pythonhosted.org/packages/fe/b1/0363a1d614c49c7ca52de80684e72598c441418a00833ab110b03348cfd0/%{pypi_name}-%{version}-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_34_x86_64.whl
%else
#!RemoteAsset:  sha256:8261d47e49dc67bc023a0143d1566b0f909dd4a02e281d2b52b770ae99401e7e
Source0:        https://files.pythonhosted.org/packages/4c/43/b6c47b00b37c7c9169beba517c94c22727daf7a93e07c4a2a284eb7728e3/%{pypi_name}-%{version}-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_34_aarch64.whl
%endif

BuildRequires:  python-rpm-macros
BuildRequires:  unzip

Provides:       python3dist(nvshmem4py-cu13) = %{version}
%python_provide python3-nvshmem4py-cu13

Requires:       python3dist(cuda-python) >= 13.0
Requires:       python3dist(cuda-python) < 14.0
Requires:       python3dist(cuda-core) >= 0.5.0
Requires:       python3dist(cuda-pathfinder) >= 1.2.3
Requires:       python3dist(nvidia-nvshmem-cu13)
Requires:       python3dist(numpy)

%description
NVSHMEM4Py provides Python bindings for NVIDIA NVSHMEM, including host,
device, and on-stream interfaces with interoperability for CUDA Python,
Numba, PyTorch, CuPy, and CuTe DSL.

%prep -a

%build -p

%install -p
mkdir -p %{buildroot}%{python3_sitearch}
unzip -q %{SOURCE0} -d %{buildroot}%{python3_sitearch}
rm -f %{buildroot}%{python3_sitearch}/%{pypi_name}-*.dist-info/RECORD

%files
%{python3_sitearch}/nvshmem/
%{python3_sitearch}/%{pypi_name}-*.dist-info/
%exclude %{python3_sitearch}/%{pypi_name}-*.dist-info/licenses/*
%license %{python3_sitearch}/%{pypi_name}-*.dist-info/licenses/*

%changelog
%autochangelog

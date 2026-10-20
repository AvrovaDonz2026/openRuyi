# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name flashinfer_python

Name:           python-flashinfer-python
Version:        0.7.1
Release:        %autorelease
Summary:        Kernel library for large language model serving
License:        Apache-2.0
URL:            https://github.com/flashinfer-ai/flashinfer
VCS:            git:https://github.com/flashinfer-ai/flashinfer.git
#!RemoteAsset:  sha256:960ae60c06419579598406d0daa2f09da30488a9a812dde151218515aedcbd08
Source0:        https://files.pythonhosted.org/packages/source/f/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(install):  -l flashinfer

BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(apache-tvm-ffi) >= 0.1.11
BuildRequires:  python3dist(apache-tvm-ffi) < 0.2
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(packaging) >= 24
BuildRequires:  python3dist(setuptools) >= 77
BuildRequires:  python3dist(wheel)

Requires:       python3dist(apache-tvm-ffi) >= 0.1.11
Requires:       python3dist(apache-tvm-ffi) < 0.2
Requires:       python3dist(click)
Requires:       python3dist(cuda-python) >= 12.0
Requires:       python3dist(cuda-tile) >= 1.4.0
Requires:       python3dist(einops)
Requires:       python3dist(nccl-extensions) >= 0.1.0
Requires:       python3dist(nccl4py) >= 0.4.1
Requires:       python3dist(ninja)
Requires:       python3dist(numpy)
Requires:       python3dist(nvidia-cudnn-frontend) >= 1.30.0
Requires:       python3dist(nvidia-cutlass-dsl) >= 4.6.2a0
Requires:       python3dist(nvidia-ml-py)
Requires:       python3dist(packaging) >= 24.2
Requires:       python3dist(requests)
Requires:       python3dist(tabulate)
Requires:       python3dist(torch)
Requires:       python3dist(tqdm)

%description
FlashInfer is a kernel library for large language model serving. It provides
specialized GPU kernels and Python APIs used by CUDA-enabled inference
frameworks.

%prep -a

%generate_buildrequires
%pyproject_buildrequires

%build -p

%install -p

%check -a
%{python3} -c 'import importlib.metadata; assert importlib.metadata.version("flashinfer-python") == "%{version}"'

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

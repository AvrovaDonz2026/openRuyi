# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname smg_grpc_servicer
%global pypi_name smg-grpc-servicer

Name:           python-smg-grpc-servicer
Version:        0.9.1
Release:        %autorelease
Summary:        SMG gRPC servicer implementations for LLM inference engines
License:        Apache-2.0
URL:            https://pypi.org/project/%{pypi_name}/
VCS:            git:https://github.com/smg-project/smg.git
#!RemoteAsset:  sha256:1e3e18fe7db76bd4f320876366d14ba4cd2b5c0aea46c08c3457708cd6d95dbf
Source0:        https://files.pythonhosted.org/packages/source/s/%{pypi_name}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(grpcio) >= 1.81.1
BuildRequires:  python3dist(grpcio-health-checking) >= 1.81.1
BuildRequires:  python3dist(grpcio-reflection) >= 1.81.1
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools) >= 77
BuildRequires:  python3dist(smg-grpc-proto) >= 0.4.18

Requires:       python3dist(grpcio) >= 1.81.1
Requires:       python3dist(grpcio-health-checking) >= 1.81.1
Requires:       python3dist(grpcio-reflection) >= 1.81.1
Requires:       python3dist(smg-grpc-proto) >= 0.4.18

Provides:       python3-%{pypi_name} = %{version}-%{release}
%python_provide python3-%{pypi_name}

%description
This package provides gRPC servicer implementations for LLM inference engines,
including vLLM, MLX, TokenSpeed, and SGLang.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

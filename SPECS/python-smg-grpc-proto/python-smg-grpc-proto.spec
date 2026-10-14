# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname smg_grpc_proto
%global pypi_name smg-grpc-proto

Name:           python-smg-grpc-proto
Version:        0.4.22
Release:        %autorelease
Summary:        Protocol Buffer definitions for SMG gRPC services
License:        Apache-2.0
URL:            https://pypi.org/project/%{pypi_name}/
VCS:            git:https://github.com/smg-project/smg.git
#!RemoteAsset:  sha256:0d69e782cabd4b76480461767351c2acddb887e2fed54bd1e7e4d1d4a52a5bd2
Source0:        https://files.pythonhosted.org/packages/source/s/%{pypi_name}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(grpcio) >= 1.81.1
BuildRequires:  python3dist(grpcio-tools) >= 1.81.1
BuildRequires:  python3dist(protobuf) >= 5.26.0

Requires:       python3dist(grpcio) >= 1.81.1
Requires:       python3dist(protobuf) >= 5.26.0

Provides:       python3-%{pypi_name} = %{version}-%{release}
%python_provide python3-%{pypi_name}

%description
Protocol Buffer definitions and pre-compiled Python gRPC stubs for SMG
(Shepherd Model Gateway) services.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

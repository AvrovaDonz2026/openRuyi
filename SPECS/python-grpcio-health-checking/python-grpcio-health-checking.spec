# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname grpcio-health-checking
%global pypi_name grpcio_health_checking

Name:           python-%{srcname}
Version:        1.84.0
Release:        %autorelease
Summary:        Health checking service for gRPC
License:        Apache-2.0
URL:            https://grpc.io/
VCS:            git:https://github.com/grpc/grpc
#!RemoteAsset:  sha256:c69ea3775a5f90cd094f294859dfd0150a560f7101a8936bf7b4e08b7186a14e
Source0:        https://files.pythonhosted.org/packages/source/g/%{srcname}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l grpc_health

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(grpcio) >= %{version}
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(protobuf) >= 7.35.1
BuildRequires:  python3dist(protobuf) < 8.0.0
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

Requires:       python3dist(grpcio) >= %{version}
Requires:       python3dist(protobuf) >= 7.35.1
Requires:       python3dist(protobuf) < 8.0.0
Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
This package provides the standard health checking service for gRPC.

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

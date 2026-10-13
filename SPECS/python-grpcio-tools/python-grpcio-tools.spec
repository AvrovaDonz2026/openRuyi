# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Suyun <ziyu.oerv@isrc.iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname grpcio-tools
%global pypi_name grpcio_tools

Name:           python-%{srcname}
Version:        1.84.0
Release:        %autorelease
Summary:        Protobuf code generator for gRPC
License:        Apache-2.0
URL:            https://grpc.io/
VCS:            git:https://github.com/grpc/grpc.git
#!RemoteAsset:  sha256:210ac5ac9803569490ec33574b7e995bc087815b00d9b777e0134cab5ed9a379
Source0:        https://files.pythonhosted.org/packages/source/g/%{srcname}/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l grpc_tools -L

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(grpcio) >= %{version}
BuildRequires:  python3dist(protobuf) >= 7.35.1

Requires:       python3dist(grpcio) >= %{version}
Requires:       python3dist(protobuf) >= 7.35.1

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
grpcio-tools provides the Protobuf compiler plugin for generating
gRPC Python code from service definitions.

%prep -a
sed -i 's/"Cython.*",/"Cython",/' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.rst
%{_bindir}/python-grpc-tools-protoc

%changelog
%autochangelog

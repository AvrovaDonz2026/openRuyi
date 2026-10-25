# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-FileContributor: Suyun <ziyu.oerv@isrc.iscas.ac.cn>
#
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname grpcio-tools
%global pypi_name grpcio_tools

Name:           python-grpcio-tools-sglang-1.84
BuildRequires:  sglang-rpm-macros >= 0.1-1000
%sglang_python_compat core
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
BuildRequires:  sglang(python3dist(grpcio)) >= %{version}
BuildRequires:  python3dist(protobuf) >= 7.35.1
BuildRequires:  python3dist(protobuf) < 8.0.0

Requires:       sglang(python3dist(grpcio)) >= %{version}
Requires:       python3dist(protobuf) >= 7.35.1
Requires:       python3dist(protobuf) < 8.0.0

%description
grpcio-tools provides the Protobuf compiler plugin for generating
gRPC Python code from service definitions.

%prep -a
sed -i 's/"Cython.*",/"Cython",/' pyproject.toml

%generate_buildrequires
%sglang_pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.rst
%{_sglang_private_libexec}/python-grpc-tools-protoc

%changelog
%autochangelog

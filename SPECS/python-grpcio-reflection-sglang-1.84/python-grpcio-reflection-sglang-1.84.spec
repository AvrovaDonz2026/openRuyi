# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-FileContributor: Li Guan <guanli.oerv@isrc.iscas.ac.cn>
#
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname grpcio-reflection
%global pypi_name grpcio_reflection

Name:           python-grpcio-reflection-sglang-1.84
BuildRequires:  sglang-rpm-macros >= 0.1-1000
%sglang_python_compat core
Version:        1.84.0
Release:        %autorelease
Summary:        Standard Protobuf Reflection Service for gRPC
License:        Apache-2.0
URL:            https://grpc.io/
VCS:            git:https://github.com/grpc/grpc
#!RemoteAsset:  sha256:06bf3d7d8cef9afbcc721ee52191652b4483831774255e174404b0e0551741bc
Source0:        https://files.pythonhosted.org/packages/source/g/%{srcname}/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l grpc_reflection

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  sglang(python3dist(grpcio)) >= %{version}
BuildRequires:  python3dist(protobuf) >= 7.35.1
BuildRequires:  python3dist(protobuf) < 8.0.0

Requires:       sglang(python3dist(grpcio)) >= %{version}
Requires:       python3dist(protobuf) >= 7.35.1
Requires:       python3dist(protobuf) < 8.0.0

%description
Standard Protobuf Reflection Service for gRPC.

%generate_buildrequires
%sglang_pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.rst
%license LICENSE

%changelog
%{?autochangelog}

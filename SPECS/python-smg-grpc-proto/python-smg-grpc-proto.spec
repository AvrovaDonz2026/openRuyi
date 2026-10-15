# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
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
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools) >= 77
BuildRequires:  python3dist(grpcio) >= 1.84.0
BuildRequires:  python3dist(grpcio-tools) >= 1.84.0
BuildRequires:  python3dist(protobuf) >= 7.35.1
BuildRequires:  python3dist(protobuf) < 8.0.0

Requires:       python3dist(grpcio) >= 1.84.0
Requires:       python3dist(protobuf) >= 7.35.1
Requires:       python3dist(protobuf) < 8.0.0

Provides:       python3-%{pypi_name} = %{version}-%{release}
%python_provide python3-%{pypi_name}

%description
Protocol Buffer definitions and pre-compiled Python gRPC stubs for SMG
(Shepherd Model Gateway) services.

%prep -a
# The repository carries grpcio-tools 1.84, which supports these generated
# stubs; the upstream cap below 1.82 is obsolete for the packaged protobuf 7
# stack.  Adjust only the build metadata and keep the generated sources intact.
sed -i 's/grpcio-tools>=1.81.1,<1.82/grpcio-tools>=1.84.0/' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%check -a
PYTHONPATH="%{buildroot}%{python3_sitelib}" %{python3} - <<'PY'
import importlib
import importlib.metadata

assert importlib.metadata.version("smg-grpc-proto") == "%{version}"
for name in (
    "common_pb2",
    "sglang_scheduler_pb2",
    "sglang_scheduler_pb2_grpc",
    "tokenspeed_scheduler_pb2",
    "vllm_engine_pb2_grpc",
):
    importlib.import_module(f"smg_grpc_proto.generated.{name}")
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-FileContributor: zhangjinqiang <jinqiang.oerv@isrc.iscas.ac.cn>
#
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname grpcio-status
%global pypi_name grpcio_status

Name:           python-grpcio-status-sglang-1.84
BuildRequires:  sglang-rpm-macros >= 0.1-1000
%sglang_python_compat core
Version:        1.84.0
Release:        %autorelease
Summary:        Status proto mapping for gRPC
License:        Apache-2.0
URL:            https://grpc.io/
VCS:            git:https://github.com/grpc/grpc.git
#!RemoteAsset:  sha256:5caf28ba7184b81f618b5f7f094859fd2541bf429d2189bbbcd715c9c2cdcee2
Source0:        https://files.pythonhosted.org/packages/source/g/%{srcname}/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l grpc_status

BuildRequires:  pkgconfig(python-%{_sglang_private_python})
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python%{_sglang_private_python}dist(googleapis-common-protos) >= 1.5.5
BuildRequires:  sglang(python%{_sglang_private_python}dist(grpcio)) >= %{version}
BuildRequires:  python%{_sglang_private_python}dist(pip)
BuildRequires:  python%{_sglang_private_python}dist(protobuf) >= 6.33.5
BuildRequires:  python%{_sglang_private_python}dist(protobuf) < 8.0.0
BuildRequires:  python%{_sglang_private_python}dist(setuptools)
BuildRequires:  python%{_sglang_private_python}dist(wheel)

Requires:       python%{_sglang_private_python}dist(googleapis-common-protos) >= 1.5.5
Requires:       sglang(python%{_sglang_private_python}dist(grpcio)) >= %{version}
Requires:       python%{_sglang_private_python}dist(protobuf) >= 6.33.5
Requires:       python%{_sglang_private_python}dist(protobuf) < 8.0.0

%description
grpcio-status provides a mapping between rich Protobuf status messages and
gRPC status codes.

%generate_buildrequires
%sglang_pyproject_buildrequires

%check -a
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}" %{python3} - <<'PY'
import importlib
import importlib.metadata

assert importlib.metadata.version("grpcio-status") == "%{version}"
importlib.import_module("grpc_status")
importlib.import_module("grpc_status.rpc_status")
PY

%files -f %{pyproject_files}
%doc README.rst

%changelog
%{?autochangelog}

# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname huggingface-hub
%global pypi_name huggingface_hub
%global compat_name python-huggingface-hub-sglang-1.31

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros
%sglang_python_compat core
Version:        1.31.0
Release:        %autorelease
Summary:        Client library for the Hugging Face Hub
License:        Apache-2.0
URL:            https://pypi.org/project/huggingface-hub/
VCS:            git:https://github.com/huggingface/huggingface_hub
#!RemoteAsset:  sha256:f8e9e710a210613fa5d0f26bba6da05ef4aef9fba5a0f23f508f5ac4d08b6f90
Source0:        https://files.pythonhosted.org/packages/source/h/%{srcname}/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject

# pythondistdeps normalizes the automatic capability to ``1.31`` by removing
# trailing zero components. Keep an exact-version capability for consumers
# whose RPM requirement is written as >= 1.31.0.
Provides:       sglang(python3dist(huggingface-hub)) = 1.31.0
Provides:       sglang(python3.14dist(huggingface-hub)) = 1.31.0

BuildOption(install):  -l huggingface_hub +auto
# The default import scan traverses optional OAuth, MCP, and provider modules;
# the focused smoke test below exercises the local API without network access.
BuildOption(check):  -e 'huggingface_hub.*'

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)

%description
Hugging Face Hub client library to download and publish models, datasets, and
spaces from Python. This package provides the SGLang-private 1.31 compatibility
tree.

%generate_buildrequires
%sglang_pyproject_buildrequires

%check -a
HF_HUB_OFFLINE=1 \
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
%{python3} -s - <<'PY'
import importlib.metadata

from huggingface_hub import HfApi, hf_hub_url

assert importlib.metadata.version("huggingface-hub") == "1.31.0"
api = HfApi()
assert api.endpoint.startswith("https://")
assert hf_hub_url("openruyi/compatibility-check", "config.json").endswith("/config.json")
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

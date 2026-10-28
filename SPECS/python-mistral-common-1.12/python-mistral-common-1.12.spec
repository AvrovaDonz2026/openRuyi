# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Li Guan <guanli.oerv@isrc.iscas.ac.cn>
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname mistral_common
%global compat_name python-mistral-common-1.12

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros >= 0.1-1000
%sglang_python_compat
Version:        1.12.0
Release:        %autorelease
Summary:        Mistral-common is a library of common utilities for Mistral AI
License:        Apache-2.0
URL:            https://github.com/mistralai/mistral-common
#!RemoteAsset:  sha256:d0f150926733cf422d4750ca19b47568df1f714557c9054a432b866f1f30bf52
Source0:        https://files.pythonhosted.org/packages/source/m/%{srcname}/%{srcname}-%{version}.tar.gz
#!RemoteAsset:  sha256:5ed6f79e77734b5a60740dd821af5ecac9a6f33709c860eea4e20fcb6cca7fcc
Source1:        https://raw.githubusercontent.com/mistralai/mistral-common/refs/tags/v1.12.0/LICENSE
BuildSystem:    pyproject
# The private SGLang CPU dependency closure is currently validated on RISC-V.
ExclusiveArch:  riscv64

BuildOption(install):  -l mistral_common

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python-%{_sglang_private_python})
BuildRequires:  python%{_sglang_private_python}dist(build)
BuildRequires:  sglang(python%{_sglang_private_python}dist(click)) >= 8.4.2
BuildRequires:  python%{_sglang_private_python}dist(fastapi)
BuildRequires:  python%{_sglang_private_python}dist(jsonschema) >= 4.21.1
BuildRequires:  python%{_sglang_private_python}dist(numpy) >= 1.25
BuildRequires:  python%{_sglang_private_python}dist(pillow) >= 10.3
BuildRequires:  python%{_sglang_private_python}dist(pip)
%if %{python3_version_nodots} >= 314
BuildRequires:  python%{_sglang_private_python}dist(pydantic) >= 2.12
BuildRequires:  python%{_sglang_private_python}dist(tiktoken) >= 0.12
%else
BuildRequires:  python%{_sglang_private_python}dist(pydantic) >= 2.7
BuildRequires:  python%{_sglang_private_python}dist(tiktoken) >= 0.7
%endif
BuildRequires:  python%{_sglang_private_python}dist(pydantic) < 3
BuildRequires:  python%{_sglang_private_python}dist(pydantic-settings)
BuildRequires:  python%{_sglang_private_python}dist(pydantic-extra-types) >= 2.10.5
BuildRequires:  python%{_sglang_private_python}dist(pycountry)
BuildRequires:  python%{_sglang_private_python}dist(requests) >= 2
BuildRequires:  python%{_sglang_private_python}dist(setuptools) >= 42
BuildRequires:  python%{_sglang_private_python}dist(typing-extensions) >= 4.11
BuildRequires:  python%{_sglang_private_python}dist(wheel)
BuildRequires:  python%{_sglang_private_python}dist(uvicorn)

Requires:       python%{_sglang_private_python}dist(jsonschema) >= 4.21.1
Requires:       python%{_sglang_private_python}dist(numpy) >= 1.25
Requires:       python%{_sglang_private_python}dist(pillow) >= 10.3
%if %{python3_version_nodots} >= 314
Requires:       python%{_sglang_private_python}dist(pydantic) >= 2.12
Requires:       python%{_sglang_private_python}dist(tiktoken) >= 0.12
%else
Requires:       python%{_sglang_private_python}dist(pydantic) >= 2.7
Requires:       python%{_sglang_private_python}dist(tiktoken) >= 0.7
%endif
Requires:       python%{_sglang_private_python}dist(pydantic) < 3
Requires:       python%{_sglang_private_python}dist(pydantic-extra-types) >= 2.10.5
Requires:       python%{_sglang_private_python}dist(pycountry)
Requires:       python%{_sglang_private_python}dist(requests) >= 2
Requires:       python%{_sglang_private_python}dist(typing-extensions) >= 4.11
Requires:       sglang(python%{_sglang_private_python}dist(click)) >= 8.4.2
Requires:       python%{_sglang_private_python}dist(fastapi)
Requires:       python%{_sglang_private_python}dist(pydantic-settings)
Requires:       python%{_sglang_private_python}dist(uvicorn)

%description
mistral-common is a set of tools to help you work with Mistral AI models.

%prep -a
cp %{SOURCE1} LICENSE

%generate_buildrequires
%sglang_pyproject_buildrequires

%check -a
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
%{python3} -s - <<'PY'
import importlib.metadata
import mistral_common

assert importlib.metadata.version("mistral-common") == "1.12.0"
assert mistral_common
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_sglang_private_libexec}/mistral_common

%changelog
%{?autochangelog}

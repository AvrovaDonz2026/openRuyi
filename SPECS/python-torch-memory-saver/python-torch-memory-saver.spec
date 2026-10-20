# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global pypi_name torch_memory_saver

Name:           python-torch-memory-saver
Version:        0.0.10
Release:        %autorelease
Summary:        Memory management helpers for PyTorch GPU applications
License:        MIT
URL:            https://github.com/fzyzcjy/torch_memory_saver
#!RemoteAsset:  sha256:480fe8e35e5b8cb5005d816d21e5382a1dc970c47d405dd36d8c5a21844dc427
Source0:        https://files.pythonhosted.org/packages/82/54/88f020fd9bd55303931ca51ee297a4a156208a6ce868e3f473b4fb13272d/%{pypi_name}-%{version}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64 aarch64

BuildOption(install):  -l torch_memory_saver

BuildRequires:  pkgconfig(python3)
BuildRequires:  gcc-c++
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)
BuildRequires:  python3dist(torch)

Requires:       python3dist(torch)

%description
Torch Memory Saver provides memory management helpers for PyTorch applications
that use accelerator memory.

%prep -a
sed -i 's/wheel-stub/setuptools/; s/wheel_stub.buildapi/setuptools.build_meta/' \
    pyproject.toml

%generate_buildrequires
%pyproject_buildrequires -R

%build -p
export TMS_PLATFORM=cuda
export TMS_CUDA_MAJOR=13

%install -p

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

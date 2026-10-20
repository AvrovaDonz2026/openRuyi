# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname timm
%global compat_name python-timm-sglang-1.0

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros
%sglang_python_compat core
Version:        1.0.28
Release:        %autorelease
Summary:        SGLang-private PyTorch image models and utilities
License:        Apache-2.0
URL:            https://github.com/huggingface/pytorch-image-models
VCS:            git:https://github.com/huggingface/pytorch-image-models.git
#!RemoteAsset:  sha256:3789d313fdd5541a327b60180d70dbb4bdec73db8ff0655e413db3c3d134a9a4
Source0:        https://files.pythonhosted.org/packages/source/t/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject
# The private CPU Torch and TorchVision providers used by this compatibility
# package are currently published only for the validated RISC-V closure.
ExclusiveArch:  riscv64

BuildOption(install):  -l %{srcname}
BuildOption(check):  -e timm.data.readers.reader_tfds
BuildOption(check):  -e timm.data.tf_preprocessing

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(datasets)
BuildRequires:  sglang(python3dist(huggingface-hub)) >= 1.31.0
BuildRequires:  python3dist(pdm-backend)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(pyyaml)
BuildRequires:  python3dist(safetensors)
BuildRequires:  sglang(python3dist(torch-cpu)) = 2.14.0
BuildRequires:  sglang(python3dist(torchvision)) = 0.29.0

Requires:       sglang(python3dist(huggingface-hub)) >= 1.31.0
Requires:       sglang(python3dist(torch-cpu)) = 2.14.0
Requires:       sglang(python3dist(torchvision)) = 0.29.0

%description
PyTorch Image Models provides model architectures, layers, and utilities for
PyTorch. This package provides the SGLang-private compatibility tree so its
Torch requirements resolve to the SGLang CPU provider.

%generate_buildrequires
%sglang_pyproject_buildrequires

%check -a
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
%{python3} -s - <<'PY'
import importlib.metadata
import timm

assert importlib.metadata.version("timm") == "1.0.28"
assert timm.is_model("vit_so400m_patch14_siglip_384.webli")
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE

%changelog
%autochangelog

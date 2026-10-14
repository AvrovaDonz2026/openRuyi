# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname vsa
%global fastvideo_version 0.1.7

Name:           python-%{srcname}
Version:        0.0.4
Release:        %autorelease
Summary:        Video sparse attention CUDA kernel used in FastVideo
License:        Apache-2.0
URL:            https://github.com/hao-ai-lab/FastVideo/tree/v0.1.7/csrc/attn/video_sparse_attn
VCS:            git:https://github.com/hao-ai-lab/FastVideo.git
#!RemoteAsset:  git+https://github.com/hao-ai-lab/FastVideo.git#v%{fastvideo_version}
#!CreateArchive
Source0:        FastVideo-%{fastvideo_version}.tar.gz
BuildSystem:    pyproject
ExclusiveArch:  x86_64

BuildOption(prep):  -n FastVideo-%{fastvideo_version}/csrc/attn/video_sparse_attn
BuildOption(install):  vsa
BuildOption(install):  +auto

BuildRequires:  cuda-toolkit
BuildRequires:  gcc-c++
BuildRequires:  ninja
BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(torch) >= 2.5.0
BuildRequires:  python3dist(wheel)
BuildRequires:  python-torch-devel >= 2.5.0

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}

Requires:       python3dist(torch) >= 2.5.0

%description
Video Sparse Attention provides the CUDA kernel used by FastVideo and SGLang
Diffusion's optional video sparse attention backend.

%generate_buildrequires
%pyproject_buildrequires

%install -p
install -D -m 0644 ../../../LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

%check -a
%pyproject_check_import vsa

%files -f %{pyproject_files}
%license %{_licensedir}/%{name}/LICENSE

%changelog
%autochangelog

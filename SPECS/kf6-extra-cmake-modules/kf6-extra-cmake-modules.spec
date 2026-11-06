# SPDX-FileCopyrightText: (C) 2025, 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2025, 2026 openRuyi Project Contributors
# SPDX-FileContributor: jingyupu <pujingyu@iscas.ac.cn>
# SPDX-FileContributor: misaka00251 <liuxin@iscas.ac.cn>
# SPDX-FileContributor: yyjeqhc <jialin.oerv@isrc.iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

Name:           kf6-extra-cmake-modules
Version:        6.31.0
Release:        %autorelease
Summary:        CMake modules
License:        BSD-3-Clause
URL:            https://www.kde.org
VCS:            git:https://invent.kde.org/frameworks/extra-cmake-modules
#!RemoteAsset:  sha256:9faba5ab696c2341cccb1ccd231787b96b65f12491c1e8da94a13fb3d0c2499b
Source0:        https://invent.kde.org/frameworks/extra-cmake-modules/-/archive/v%{version}/extra-cmake-modules-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    cmake

BuildOption(conf):  -DQT_MAJOR_VERSION=6

BuildRequires:  cmake
BuildRequires:  kf6-rpm-macros
BuildRequires:  gcc-c++
BuildRequires:  qt6-qtbase
# BuildRequires:  python-sphinx

Requires:       gcc-c++
Requires:       cmake
Requires:       kf6-rpm-macros

Provides:       extra-cmake-modules = %{version}

# TODO: Fix tests.
%check

%description
Extra modules and scripts for CMake.

%files
%license LICENSES/*
%{_datadir}/ECM/

%changelog
%autochangelog

# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

Name:           sglang-rpm-macros
Version:        0.1
Release:        %autorelease
Summary:        RPM macros and dependency generators for private SGLang trees
License:        MulanPSL-2.0
URL:            https://github.com/openRuyi-Project/openRuyi
Source0:        macros.sglang
Source1:        sglang_private_paths.py
Source2:        sglangdistdeps.py
Source3:        sglang-elfdeps.py
Source4:        sglang_core_python.attr
Source5:        sglang_extras_python.attr
Source6:        sglang_core_elf.attr
Source7:        sglang_extras_elf.attr
Source8:        test_sglang_deps.py
Source9:        check_sglang_rpm_closure.py
BuildArch:      noarch

BuildRequires:  pkgconfig(python3)
BuildRequires:  rpm-build
Requires:       python3-rpm-generators
Requires:       pyproject-rpm-macros
Requires:       patchelf

%description
This package provides opt-in RPM macros and dependency generators for SGLang
private core and extras Python trees.  Selected Python distributions and their
private native SONAMEs use an explicit RPM namespace; Python ABI and system
library dependencies remain generated normally.

%prep

%build

%install
install -Dpm0644 %{SOURCE0} %{buildroot}%{_rpmmacrodir}/macros.sglang
install -Dpm0755 %{SOURCE1} %{buildroot}%{_rpmconfigdir}/openruyi/sglang_private_paths.py
install -Dpm0755 %{SOURCE2} %{buildroot}%{_rpmconfigdir}/sglangdistdeps.py
install -Dpm0755 %{SOURCE3} %{buildroot}%{_rpmconfigdir}/sglang-elfdeps.py
install -Dpm0755 %{SOURCE9} %{buildroot}%{_rpmconfigdir}/openruyi/check_sglang_rpm_closure.py
install -Dpm0644 %{SOURCE4} %{buildroot}%{_fileattrsdir}/sglang_core_python.attr
install -Dpm0644 %{SOURCE5} %{buildroot}%{_fileattrsdir}/sglang_extras_python.attr
install -Dpm0644 %{SOURCE6} %{buildroot}%{_fileattrsdir}/sglang_core_elf.attr
install -Dpm0644 %{SOURCE7} %{buildroot}%{_fileattrsdir}/sglang_extras_elf.attr

%check
%{__python3} -m py_compile %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE9}
%{__python3} %{SOURCE8}

%files
%{_rpmmacrodir}/macros.sglang
%{_rpmconfigdir}/openruyi/sglang_private_paths.py
%{_rpmconfigdir}/sglangdistdeps.py
%{_rpmconfigdir}/sglang-elfdeps.py
%{_rpmconfigdir}/openruyi/check_sglang_rpm_closure.py
%{_fileattrsdir}/sglang_core_python.attr
%{_fileattrsdir}/sglang_extras_python.attr
%{_fileattrsdir}/sglang_core_elf.attr
%{_fileattrsdir}/sglang_extras_elf.attr

%changelog
%autochangelog

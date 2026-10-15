# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname pillow

Name:           python-pillow-11
Version:        11.3.0
Release:        %autorelease
Summary:        Version 11 compatibility build of Pillow
License:        MIT-CMU
URL:            http://python-pillow.github.io/
#!RemoteAsset:  sha256:3828ee7586cd0b2091b6209e5ad53e20d0649bbe87164a459d0676e035e8f523
Source0:        https://files.pythonhosted.org/packages/source/p/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject
BuildRequires:  sglang-rpm-macros
%sglang_python_compat extras

BuildOption(install):  -l PIL

BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(lcms2)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libtiff-4)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  file
BuildRequires:  patchelf
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(pybind11)
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

%description
Version 11 of Pillow, provided for applications whose declared dependency
range excludes the current upstream major release.

%package devel
Summary:        Development headers for the Pillow 11 compatibility build
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
This package provides the Imaging headers for developing applications that
use the Pillow 11 compatibility build.

%generate_buildrequires
%sglang_pyproject_buildrequires

%install -a
install -d %{buildroot}%{_sglang_private_root}/include/Imaging
install -m 644 src/libImaging/*.h %{buildroot}%{_sglang_private_root}/include/Imaging
%sglang_private_rpath

%check
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}" %{python3} - <<'PY'
import io

from PIL import Image, __version__, features

assert __version__ == "%{version}", __version__

image = Image.new("RGB", (16, 12), (32, 100, 180))
for format_name in ("PNG", "JPEG", "WEBP"):
    stream = io.BytesIO()
    image.save(stream, format=format_name)
    stream.seek(0)
    decoded = Image.open(stream)
    decoded.load()
    assert decoded.size == image.size
    assert decoded.mode == image.mode

assert features.check("jpg")
assert features.check("webp")
assert features.check("zlib")
PY

%files -f %{pyproject_files}
%doc README.md CHANGES.rst
%license docs/COPYING

%files devel
%license docs/COPYING
%{_sglang_private_root}/include/Imaging/

%changelog
%autochangelog

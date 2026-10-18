# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global upstream_name sglang
# Keep the CUDA conditionals for a future provider-backed flavor.  This source
# package intentionally has no multibuild entry until a CUDA Torch provider is
# available; the default build must resolve to the CPU dependency closure.
%global flavor @BUILD_FLAVOR@%{nil}
%if "%{flavor}" == "cuda"
%{error:CUDA SGLang flavor is reserved and is not supported by this SPEC}
%endif
%if "%{flavor}" == "rocm"
%{error:ROCm SGLang flavor is reserved and is not supported by this SPEC}
%endif
%ifarch riscv64
%global llvm_maj_ver 22
%global toolchain clang
%endif

# Select the upstream platform metadata for each build flavor.
%if "%{flavor}" == "cuda"
%bcond cuda 1
%else
%bcond cuda 0
%endif

# Keep the ROCm flavor unbuildable even when a caller enables it directly
# instead of selecting BUILD_FLAVOR=rocm.
%if "%{flavor}" == "rocm"
%bcond rocm 1
%else
%bcond rocm 0
%endif

# Keep the reserved CUDA flavor unbuildable even when a caller overrides the
# bcond directly instead of selecting BUILD_FLAVOR=cuda.
%if %{with cuda}
%{error:CUDA SGLang flavor is reserved and is not supported by this SPEC}
%endif
%if %{with rocm}
%{error:ROCm SGLang flavor is reserved and is not supported by this SPEC}
%endif

%if %{with cuda}
%global srcname sglang
Name:           python-sglang-cuda
%else
%global srcname sglang-cpu
Name:           python-sglang
%endif

%sglang_python_compat core
Version:        0.5.21
Release:        %autorelease
Summary:        Fast serving framework for large language and vision-language models
License:        Apache-2.0
URL:            https://github.com/sgl-project/sglang
VCS:            git:https://github.com/sgl-project/sglang.git
#!RemoteAsset:  sha256:c44951b7871dac61262fc04e9fca628175758a97fa5f603c522b31dc31b94249
Source0:        https://github.com/sgl-project/sglang/archive/refs/tags/v%{version}.tar.gz#/%{upstream_name}-%{version}.tar.gz
Source1:        sglang-launcher
Source2:        sglang-python-launcher
Source3:        sglang-extras-python
Source4:        sglang-cpu-engine-smoke.py
BuildSystem:    pyproject
%if %{without cuda}
# The CPU closure currently relies on the private Triton provider, which is
# built only for these targets.  Keep unsupported architectures out of the
# repository rather than publishing an RPM with an unsatisfied dependency.
ExclusiveArch:  x86_64 riscv64
%else
# CUDA toolkit currently provides Linux host support for these architectures.
ExclusiveArch:  x86_64 aarch64
%endif

BuildOption(prep):  -n %{upstream_name}-%{version}
BuildOption(install):  -l sglang

BuildRequires:  pkgconfig(python3)
BuildRequires:  file
BuildRequires:  patchelf
BuildRequires:  sglang-rpm-macros
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(setuptools-scm)
BuildRequires:  python3dist(wheel)

%ifarch riscv64
BuildRequires:  clang
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
%endif

%if %{with cuda}
# The CUDA flavor is intentionally dormant until a CUDA Torch provider is
# added.
Conflicts:      python-sglang
BuildRequires:  python3dist(setuptools-rust)
BuildRequires:  sglang(python3dist(torch-cuda)) = 2.14.0
Requires:       sglang(python3dist(torch-cuda)) = 2.14.0
%else
Conflicts:      python-sglang-cuda
BuildRequires:  sglang(python3dist(torch-cpu)) = 2.14.0
BuildRequires:  sglang(python3dist(torchaudio)) = 2.11.0
BuildRequires:  sglang(python3dist(torchvision)) = 0.29.0
BuildRequires:  sglang(python3dist(triton)) = 3.8.0
BuildRequires:  sglang(python3dist(sglang-kernel-cpu)) = 0.4.7
BuildRequires:  sglang(python3dist(mistral-common)) >= 1.11.5
BuildRequires:  sglang(python3dist(transformers)) = 5.19.0
BuildRequires:  sglang(python3dist(timm)) = 1.0.28
%ifnarch aarch64 armv7hl
# pyproject_cpu.toml excludes torchcodec on Linux ARM (aarch64, arm64, armv7l).
BuildRequires:  sglang(python3dist(torchcodec)) = 0.12.0
%endif
%endif

%if %{without cuda}
Requires:       sglang(python3dist(torch-cpu)) = 2.14.0
Requires:       sglang(python3dist(torchaudio)) = 2.11.0
Requires:       sglang(python3dist(torchvision)) = 0.29.0
Requires:       sglang(python3dist(triton)) = 3.8.0
# The upstream CPU installation also builds the separate AOT kernel project.
Requires:       sglang(python3dist(sglang-kernel-cpu)) = 0.4.7
# SGLang's CPU metadata imports Mistral tokenizer utilities at runtime.
Requires:       sglang(python3dist(mistral-common)) >= 1.11.5
Requires:       sglang(python3dist(transformers)) = 5.19.0
Requires:       sglang(python3dist(timm)) = 1.0.28
%ifnarch aarch64 armv7hl
Requires:       sglang(python3dist(torchcodec)) = 0.12.0
%endif
%endif

%patchlist
# RISC-V torch-native runtime fallback and capability-gated unsupported AOT operators.
2002-riscv64-cpu-runtime-fallback.patch

%description
SGLang is a fast serving framework for large language models and vision-language
models.
%if %{with cuda}
This package provides the CUDA backend.
%else
This package provides the CPU backend.
%endif

%prep -a
cp README.md LICENSE python/
%if %{without cuda}
cp python/pyproject_cpu.toml python/pyproject.toml
sed -i \
    -e 's/"blobfile==3.0.0"/"blobfile>=3.2.0,<4"/' \
    -e 's/"openai==2.6.1"/"openai>=2.40.0,<3"/' \
    -e 's/"openai-harmony==0.0.4"/"openai-harmony>=0.0.8,<0.1"/' \
    -e 's/"transformers==5.12.1"/"transformers==5.19.0"/' \
    -e 's/"timm==1.0.16"/"timm>=1.0.28,<2"/' \
    python/pyproject.toml
%ifarch riscv64
sed -i '/intel-openmp.*platform_machine.*x86_64/d' python/pyproject.toml
%endif
%endif

%generate_buildrequires
cd python
export SETUPTOOLS_SCM_PRETEND_VERSION='%{version}'
%if %{without cuda}
export SGLANG_BUILD_RUST_EXTS=none
%endif
%sglang_pyproject_buildrequires

%build -p
cd python
export SETUPTOOLS_SCM_PRETEND_VERSION='%{version}'
%if %{without cuda}
# The CPU metadata has no Rust build requirement.  Keep this explicit so a
# future setup.py change cannot silently pull GPU/Rust extensions into RISC-V.
export SGLANG_BUILD_RUST_EXTS=none
%endif
%ifarch riscv64
# Select LLVM for native extensions. Cross-build sysroots are supplied externally.
export CC=clang
export CXX=clang++
export LD=ld.lld
export AR=llvm-ar
export RANLIB=llvm-ranlib
export CFLAGS="%{build_cflags} --target=%{_target_platform}"
export CXXFLAGS="%{build_cxxflags} --target=%{_target_platform}"
export LDFLAGS="%{build_ldflags} -fuse-ld=lld"
%endif

%install -p
cd python

%install -a
%sglang_private_rpath

install -Dpm0755 %{SOURCE1} %{buildroot}%{_bindir}/sglang
install -Dpm0755 %{SOURCE2} %{buildroot}%{_bindir}/sglang-python
install -Dpm0755 %{SOURCE3} %{buildroot}%{_bindir}/sglang-extras-python
%if %{without cuda}
install -Dpm0755 %{SOURCE4} %{buildroot}%{_libexecdir}/sglang/sglang-cpu-engine-smoke.py
%endif
sed -i \
  -e 's|@PRIVATE_SITELIB@|%{_sglang_private_sitelib}|g' \
  -e 's|@PRIVATE_LIBEXEC@|%{_sglang_private_libexec}|g' \
  %{buildroot}%{_bindir}/sglang %{buildroot}%{_bindir}/sglang-python
sed -i \
  -e 's|@EXTRAS_SITELIB@|%{_libdir}/sglang/extras/python%{python3_version}/site-packages|g' \
  -e 's|@CORE_SITELIB@|%{_libdir}/sglang/core/python%{python3_version}/site-packages|g' \
  %{buildroot}%{_bindir}/sglang-extras-python

%check -a
cd %{buildroot}
%if %{with cuda}
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" %{python3} -s -c 'import importlib.metadata; import sglang; assert importlib.metadata.version("sglang") == "%{version}"; print(sglang.__version__)'
%else
export SGLANG_USE_CPU_ENGINE=1
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" %{python3} -s -c 'import importlib.metadata; import sglang; assert importlib.metadata.version("sglang-cpu") == "%{version}"; print(sglang.__version__)'
%endif
%if %{without cuda}
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" %{python3} -s - <<'PY'
import importlib.metadata
import blobfile
import openai
import timm
from openai.types.responses import ResponseOutputMessage, ResponseOutputText
from openai_harmony import Message, Role, StreamableParser
from packaging.version import Version

assert Version(importlib.metadata.version("openai")) >= Version("2.40.0")
assert Version(importlib.metadata.version("openai-harmony")) >= Version("0.0.8")
assert Version(importlib.metadata.version("timm")) >= Version("1.0.28")
assert Version(importlib.metadata.version("blobfile")) >= Version("3.2.0")

client = openai.OpenAI(api_key="compatibility-check", base_url="http://localhost")
assert client.base_url.host == "localhost"
message = Message.from_role_and_content(Role.USER, "compatibility check")
assert message.author.role == Role.USER
assert Message.from_role_and_content(Role.ASSISTANT, "ok").with_channel("final")
assert StreamableParser
output = ResponseOutputMessage(
    id="msg_compatibility",
    content=[ResponseOutputText(text="ok", annotations=[], type="output_text", logprobs=None)],
    role="assistant", status="completed", type="message", phase="final_answer",
)
assert output.content[0].text == "ok"
assert timm.is_model("vit_so400m_patch14_siglip_384.webli")
assert blobfile.exists(".")
PY
%endif

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/sglang
%{_bindir}/sglang-python
%{_bindir}/sglang-extras-python
%if %{without cuda}
%{_libexecdir}/sglang/sglang-cpu-engine-smoke.py
%endif

%changelog
%autochangelog

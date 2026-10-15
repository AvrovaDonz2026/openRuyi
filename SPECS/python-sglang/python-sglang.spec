# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global upstream_name sglang
%global flavor @BUILD_FLAVOR@%{nil}
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

%if %{with cuda}
%global srcname sglang
Name:           python-sglang-cuda
%else
%global srcname sglang-cpu
Name:           python-sglang
%endif
Version:        0.5.21
Release:        %autorelease
Summary:        Fast serving framework for large language and vision-language models
License:        Apache-2.0
URL:            https://github.com/sgl-project/sglang
VCS:            git:https://github.com/sgl-project/sglang.git
#!RemoteAsset:  sha256:c44951b7871dac61262fc04e9fca628175758a97fa5f603c522b31dc31b94249
Source0:        https://github.com/sgl-project/sglang/archive/refs/tags/v%{version}.tar.gz#/%{upstream_name}-%{version}.tar.gz
BuildSystem:    pyproject
%if %{with cuda}
# CUDA toolkit currently provides Linux host support for these architectures.
ExclusiveArch:  x86_64 aarch64
%endif

BuildOption(prep):  -n %{upstream_name}-%{version}
BuildOption(install):  -l sglang

BuildRequires:  pkgconfig(python3)
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
# The CUDA flavor retains the upstream CUDA dependency versions.
BuildRequires:  python3dist(setuptools-rust)
BuildRequires:  python3dist(torch)
%else
BuildRequires:  python3dist(torch) = 2.14.0
BuildRequires:  python3dist(torchaudio) = 2.11.0
BuildRequires:  python3dist(torchvision) = 0.29.0
BuildRequires:  python3dist(triton) = 3.8.0
BuildRequires:  python3dist(sglang-kernel-cpu) = 0.4.7
BuildRequires:  python3dist(mistral-common) >= 1.11.5
%endif

%if %{without cuda}
Requires:       python3dist(torch) = 2.14.0
Requires:       python3dist(torchaudio) = 2.11.0
Requires:       python3dist(torchvision) = 0.29.0
Requires:       python3dist(triton) = 3.8.0
# The upstream CPU installation also builds the separate AOT kernel project.
Requires:       python3dist(sglang-kernel-cpu) = 0.4.7
# SGLang's CPU metadata imports Mistral tokenizer utilities at runtime.
Requires:       python3dist(mistral-common) >= 1.11.5
%endif

Provides:       python3-%{srcname} = %{version}-%{release}
Provides:       python3-%{srcname}%{?_isa} = %{version}-%{release}
%python_provide python3-%{srcname}
%if %{with cuda}
Conflicts:      python-sglang
%else
Conflicts:      python-sglang-cuda
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
# Match the packaged dependency versions and check the exercised API surfaces.
# Full inference compatibility with these versions still requires validation.
sed -i \
    -e 's/"blobfile==3.0.0"/"blobfile>=3.2.0,<4"/' \
    -e 's/"openai==2.6.1"/"openai>=2.40.0,<3"/' \
    -e 's/"openai-harmony==0.0.4"/"openai-harmony>=0.0.8,<0.1"/' \
    -e 's/"timm==1.0.16"/"timm>=1.0.28,<2"/' \
    -e 's/"transformers==5.12.1"/"transformers>=5.16.0,<6"/' \
    python/pyproject.toml
%endif
grep -qF 'dynamic = ["version"]' python/pyproject.toml
sed -i 's/dynamic = \["version"\]/version = "%{version}"/' \
    python/pyproject.toml

%generate_buildrequires
cd python
%if %{without cuda}
export SGLANG_BUILD_RUST_EXTS=none
%endif
%pyproject_buildrequires

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

%check -a
export PYTHONPATH="%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}"
cd %{buildroot}
%if %{with cuda}
%{python3} -c 'import importlib.metadata; import sglang; assert importlib.metadata.version("sglang") == "%{version}"; print(sglang.__version__)'
%else
export SGLANG_USE_CPU_ENGINE=1
%{python3} -c 'import importlib.metadata; import sglang; assert importlib.metadata.version("sglang-cpu") == "%{version}"; print(sglang.__version__)'
%endif
%if %{without cuda}
%{python3} - <<'PY'
import importlib.metadata
import blobfile
import openai
import timm
import transformers
from openai.types.responses import ResponseOutputMessage, ResponseOutputText
from openai_harmony import Message, Role, StreamableParser
from packaging.version import Version

assert Version(importlib.metadata.version("openai")) >= Version("2.40.0")
assert Version(importlib.metadata.version("openai-harmony")) >= Version("0.0.8")
assert Version(importlib.metadata.version("timm")) >= Version("1.0.28")
assert Version(importlib.metadata.version("blobfile")) >= Version("3.2.0")
assert Version(importlib.metadata.version("transformers")) >= Version("5.16.0")

client = openai.OpenAI(api_key="compatibility-check", base_url="http://localhost")
assert client.base_url.host == "localhost"
message = Message.from_role_and_content(Role.USER, "compatibility check")
assert message.author.role == Role.USER
assert Message.from_role_and_content(Role.ASSISTANT, "ok").with_channel("final")
assert StreamableParser
output = ResponseOutputMessage(
    id="msg_compatibility",
    content=[
        ResponseOutputText(
            text="ok", annotations=[], type="output_text", logprobs=None
        )
    ],
    role="assistant",
    status="completed",
    type="message",
    phase="final_answer",
)
assert output.content[0].text == "ok"
assert timm.is_model("vit_so400m_patch14_siglip_384.webli")
assert blobfile.exists(".")
assert transformers.__version__
PY
%endif

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/sglang

%changelog
%autochangelog

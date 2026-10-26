# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global upstream_name sglang
# The base distribution ships Transformers 5.12.1, while v0.5.21 requires
# 5.19.0. Keep Transformers in the private compatibility tree. The base
# timm 1.0.28 package is newer than the upstream 1.0.16 pin and is shared.
%global transformers_compat_version 5.19.0
# pythondistdeps normalizes the trailing .0 in the RPM capability to 5.19.
%global transformers_compat_rpm_version 5.19
%global xgrammar_compat_version 0.2.7
%global llguidance_compat_min_version 1.7.6
%global sglang_shared_dists timm
# Reuse the distro's timm 1.0.28 instead of the tag's 1.0.16 pin.
%global timm_system_version 1.0.28
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
%global llvm_bindir %{_libdir}/llvm%{llvm_maj_ver}/bin
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
Source5:        sglang-coexistence-test.py
BuildSystem:    pyproject
%if %{without cuda}
# The CPU closure currently relies on private providers that are validated
# only on RISC-V.  The upstream x86_64 metadata also requests
# python3dist(intel-openmp), which is not provided by this repository.
# Keep x86_64 out until a real provider and target validation are available.
ExclusiveArch:  riscv64
%else
# CUDA toolkit currently provides Linux host support for these architectures.
ExclusiveArch:  x86_64 aarch64
%endif

BuildOption(prep):  -n %{upstream_name}-%{version}
BuildOption(install):  -l sglang

BuildRequires:  pkgconfig(python3)
BuildRequires:  file
BuildRequires:  patchelf
BuildRequires:  sglang-rpm-macros >= 0.1-1000
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(setuptools-scm)
BuildRequires:  python3dist(wheel)

# The private site-packages tree and launcher are tied to this exact Python ABI.
Requires:       python(abi) = %{_sglang_private_python}
Requires:       %{_sglang_private_interpreter}

%ifarch riscv64
# Keep CMake's compiler driver and target triple aligned with the LLVM 22
# toolchain used for the RISC-V package build.
BuildOption(build):  -Ccmake.define.CMAKE_C_COMPILER=%{llvm_bindir}/clang
BuildOption(build):  -Ccmake.define.CMAKE_CXX_COMPILER=%{llvm_bindir}/clang++
BuildOption(build):  -Ccmake.define.CMAKE_C_COMPILER_TARGET:STRING=%{_target_platform}
BuildOption(build):  -Ccmake.define.CMAKE_CXX_COMPILER_TARGET:STRING=%{_target_platform}
%if "%{_host_cpu}" != "%{_target_cpu}"
BuildOption(build):  -Ccmake.define.CMAKE_SYSTEM_NAME=Linux
BuildOption(build):  -Ccmake.define.CMAKE_SYSTEM_PROCESSOR=riscv64
%endif
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
Provides:       sglang(python3dist(%{srcname})) = %{version}
BuildRequires:  python3dist(setuptools-rust)
BuildRequires:  sglang(python3dist(torch-cuda)) = 2.14.0
Requires:       sglang(python3dist(torch-cuda)) = 2.14.0
%else
Provides:       sglang(python3dist(%{srcname})) = %{version}
BuildRequires:  sglang(python3dist(torch-cpu)) = 2.14.0
BuildRequires:  sglang(python3dist(torchaudio)) = 2.11.0
BuildRequires:  sglang(python3dist(torchvision)) = 0.29.0
BuildRequires:  sglang(python3dist(triton)) = 3.8.0
BuildRequires:  sglang(python3dist(sglang-kernel-cpu)) = 0.4.7
BuildRequires:  sglang(python3dist(mistral-common)) >= 1.11.5
BuildRequires:  sglang(python3dist(transformers)) = %{transformers_compat_rpm_version}
BuildRequires:  sglang(python3dist(xgrammar)) = %{xgrammar_compat_version}
BuildRequires:  sglang(python3dist(llguidance)) >= %{llguidance_compat_min_version}
BuildRequires:  sglang(python3dist(llguidance)) < 2
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
Requires:       sglang(python3dist(transformers)) = %{transformers_compat_rpm_version}
Requires:       sglang(python3dist(xgrammar)) = %{xgrammar_compat_version}
Requires:       sglang(python3dist(llguidance)) >= %{llguidance_compat_min_version}
Requires:       sglang(python3dist(llguidance)) < 2
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
# The source archive has no Git metadata.  Use a static project version for
# setuptools' wheel metadata so offline builds do not fall back to 0.0.0.
sed -i -e 's/^dynamic = \["version"\]/version = "%{version}"/' \
    python/pyproject.toml
sed -i \
    -e 's/"blobfile==3.0.0"/"blobfile>=3.2.0,<4"/' \
    -e 's/"openai==2.6.1"/"openai>=2.40.0,<3"/' \
    -e 's/"openai-harmony==0.0.4"/"openai-harmony>=0.0.8,<0.1"/' \
    -e 's/"transformers==[^"]*"/"transformers==%{transformers_compat_version}"/' \
    -e 's/"timm==[^"]*"/"timm==%{timm_system_version}"/' \
    python/pyproject.toml
%ifarch riscv64
sed -i '/intel-openmp.*platform_machine.*x86_64/d' python/pyproject.toml
%endif
%endif

%generate_buildrequires
cd python
export SETUPTOOLS_SCM_PRETEND_VERSION='%{version}'
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SGLANG_CPU='%{version}'
%if %{without cuda}
export SGLANG_BUILD_RUST_EXTS=none
%endif
%sglang_pyproject_buildrequires

%build -p
cd python
export SETUPTOOLS_SCM_PRETEND_VERSION='%{version}'
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SGLANG_CPU='%{version}'
%if %{without cuda}
# The CPU metadata has no Rust build requirement.  Keep this explicit so a
# future setup.py change cannot silently pull GPU/Rust extensions into RISC-V.
export SGLANG_BUILD_RUST_EXTS=none
%endif
%ifarch riscv64
# Select LLVM for native extensions. Cross-build sysroots are supplied externally.
export PATH="%{llvm_bindir}:$PATH"
export CC="%{llvm_bindir}/clang"
export CXX="%{llvm_bindir}/clang++"
export LD="%{llvm_bindir}/ld.lld"
export AR="%{llvm_bindir}/llvm-ar"
export RANLIB="%{llvm_bindir}/llvm-ranlib"
export CFLAGS="%{build_cflags} --target=%{_target_platform}"
export CXXFLAGS="%{build_cxxflags} --target=%{_target_platform}"
export LDFLAGS="-fuse-ld=lld --target=%{_target_platform} %{build_ldflags}"
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
install -Dpm0755 %{SOURCE5} %{buildroot}%{_libexecdir}/sglang/sglang-coexistence-test.py
%endif
sed -i \
  -e 's|@PRIVATE_SITELIB@|%{_sglang_private_sitelib}|g' \
  -e 's|@PRIVATE_LIBEXEC@|%{_sglang_private_libexec}|g' \
  -e 's|@PYTHON3@|%{_sglang_private_interpreter}|g' \
  %{buildroot}%{_bindir}/sglang %{buildroot}%{_bindir}/sglang-python
sed -i \
  -e 's|@EXTRAS_SITELIB@|%{_libdir}/sglang/extras/python%{_sglang_private_python}/site-packages|g' \
  -e 's|@CORE_SITELIB@|%{_libdir}/sglang/core/python%{_sglang_private_python}/site-packages|g' \
  -e 's|@PYTHON3@|%{_sglang_private_interpreter}|g' \
  %{buildroot}%{_bindir}/sglang-extras-python

%check -a
for launcher in %{SOURCE1} %{SOURCE2} \
  "%{buildroot}%{_bindir}/sglang" \
  "%{buildroot}%{_bindir}/sglang-python"; do
  bash -n "$launcher"
done
cd %{buildroot}
%if %{with cuda}
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" %{_sglang_private_interpreter} -s -c 'import importlib.metadata; import sglang; assert importlib.metadata.version("sglang") == "%{version}"; print(sglang.__version__)'
%else
export SGLANG_USE_CPU_ENGINE=1
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" %{_sglang_private_interpreter} -s -c 'import importlib.metadata; import sglang; assert importlib.metadata.version("sglang-cpu") == "%{version}"; print(sglang.__version__)'
%endif
%if %{without cuda}
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" %{_sglang_private_interpreter} -s - <<'PY'
import importlib.metadata
import blobfile
import openai
import timm
from openai.types.responses import ResponseOutputMessage, ResponseOutputText
from openai_harmony import Message, Role, StreamableParser
from packaging.version import Version

assert Version(importlib.metadata.version("openai")) >= Version("2.40.0")
assert Version(importlib.metadata.version("openai-harmony")) >= Version("0.0.8")
assert Version(importlib.metadata.version("timm")) == Version("%{timm_system_version}")
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
# The public wrapper resolves its final installed path; use the private entrypoint in buildroot.
PYTHONNOUSERSITE=1 PYTHONSAFEPATH=1 \
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
SGLANG_SMOKE_PYTHON="%{_sglang_private_interpreter}" \
SGLANG_SMOKE_SERVER="%{buildroot}%{_sglang_private_libexec}/sglang" \
%{_sglang_private_interpreter} -s "%{buildroot}%{_libexecdir}/sglang/sglang-cpu-engine-smoke.py"
%endif

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/sglang
%{_bindir}/sglang-python
%{_bindir}/sglang-extras-python
# The wheel's console entry point is relocated into the private libexec tree
# and is invoked by the public wrapper above.
%{_libexecdir}/sglang/sglang
%if %{without cuda}
%{_libexecdir}/sglang/sglang-cpu-engine-smoke.py
%{_libexecdir}/sglang/sglang-coexistence-test.py
%endif

%changelog
%autochangelog

# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname tokenizers
%global compat_name python-tokenizers-sglang-0.23

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros
%sglang_python_compat core
Version:        0.23.2
Release:        %autorelease
Summary:        Fast tokenization implementation for the SGLang private runtime
License:        Apache-2.0
URL:            https://pypi.org/project/tokenizers/
VCS:            git:https://github.com/huggingface/tokenizers
#!RemoteAsset:  sha256:7f0f085686b9de0d0079e6f874ae053600db64c5d13049e0bbc0119926d25aac
Source0:        https://files.pythonhosted.org/packages/18/1e/bc6587c5ab643b2e17776cace9070a2ae73549c86bffac9934a600bf3c31/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

# Tokenizers 0.23.2 does not publish PEP 639 License-File metadata.  Keep
# automatic file collection, but handle the source license explicitly below.
BuildOption(install):  -l %{srcname} -L
# The default import scan also probes optional model and network helpers.
BuildOption(check):  -e 'tokenizers.*'

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(maturin)
BuildRequires:  gcc-c++
BuildRequires:  rust
BuildRequires:  rust-rpm-macros
BuildRequires:  crate(ahash-0.8/default)
BuildRequires:  crate(ahash-0.8/serde)
BuildRequires:  crate(compact-str-0.9/default)
BuildRequires:  crate(compact-str-0.9/serde)
BuildRequires:  crate(daachorse-3/default)
BuildRequires:  crate(dary-heap-0.3/default)
BuildRequires:  crate(dary-heap-0.3/serde)
BuildRequires:  crate(derive-builder-0.20/default)
BuildRequires:  crate(env-logger-0.11/default)
BuildRequires:  crate(esaxx-rs-0.1/cpp)
BuildRequires:  crate(getrandom-0.3/default)
BuildRequires:  crate(indicatif-0.18/default)
BuildRequires:  crate(itertools-0.14/default)
BuildRequires:  crate(libc-0.2/default)
BuildRequires:  crate(log-0.4/default)
BuildRequires:  crate(macro-rules-attribute-0.2/default)
BuildRequires:  crate(monostate-0.1/default)
BuildRequires:  crate(ndarray-0.16/default)
BuildRequires:  crate(numpy-0.29/default)
BuildRequires:  crate(once-cell-1/default)
BuildRequires:  crate(paste-1/default)
BuildRequires:  crate(pyo3-0.29/abi3)
BuildRequires:  crate(pyo3-0.29/abi3-py310)
BuildRequires:  crate(pyo3-0.29/experimental-inspect)
BuildRequires:  crate(pyo3-0.29/extension-module)
BuildRequires:  crate(pyo3-0.29/py-clone)
BuildRequires:  crate(pyo3-async-runtimes-0.29/tokio-runtime)
BuildRequires:  crate(pyo3-build-config-0.29/default)
BuildRequires:  crate(pyo3-build-config-0.29/resolve-config)
BuildRequires:  crate(pyo3-ffi-0.29/abi3)
BuildRequires:  crate(pyo3-ffi-0.29/extension-module)
BuildRequires:  crate(rand-0.9/default)
BuildRequires:  crate(rayon-1/default)
BuildRequires:  crate(rayon-cond-0.4/default)
BuildRequires:  crate(regex-1/default)
BuildRequires:  crate(regex-syntax-0.8/default)
BuildRequires:  crate(serde-1/default)
BuildRequires:  crate(serde-1/derive)
BuildRequires:  crate(serde-1/rc)
BuildRequires:  crate(serde-json-1/default)
BuildRequires:  crate(spm-precompiled-0.1/default)
BuildRequires:  crate(thiserror-2/default)
BuildRequires:  crate(tokio-1/default)
BuildRequires:  crate(tokio-1/macros)
BuildRequires:  crate(tokio-1/rt)
BuildRequires:  crate(tokio-1/rt-multi-thread)
BuildRequires:  crate(tokio-1/signal)
BuildRequires:  crate(unicode-categories-0.1/default)
BuildRequires:  crate(unicode-normalization-alignments-0.1/default)
BuildRequires:  crate(unicode-segmentation-1/default)
BuildRequires:  crate(onig-6/default)

%description
Tokenizers provides fast and production-ready tokenization implementations for
modern natural language processing workloads. This package provides the
SGLang-private 0.23 compatibility tree.

%prep -a
%rust_setup_registry
rm -f bindings/python/Cargo.lock

%generate_buildrequires
%sglang_pyproject_buildrequires

%check -a
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
%{python3} -s - <<'PY'
import importlib.metadata
from tokenizers import Tokenizer
from tokenizers.models import WordLevel

assert importlib.metadata.version("tokenizers") == "0.23.2"
tokenizer = Tokenizer(WordLevel({"hello": 0, "[UNK]": 1}, unk_token="[UNK]"))
encoded = tokenizer.encode("hello")
assert encoded.tokens == ["hello"]
assert tokenizer.decode(encoded.ids) == "hello"
PY

%files -f %{pyproject_files}
%doc tokenizers/README.md
%license tokenizers/LICENSE

%changelog
%autochangelog

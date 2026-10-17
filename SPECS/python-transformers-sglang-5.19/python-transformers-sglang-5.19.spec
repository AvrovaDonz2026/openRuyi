# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname transformers
%global compat_name python-transformers-sglang-5.19

Name:           %{compat_name}
BuildRequires:  sglang-rpm-macros
%sglang_python_compat core
Version:        5.19.0
Release:        %autorelease
Summary:        Model-definition framework for state-of-the-art machine learning
License:        Apache-2.0
URL:            https://pypi.org/project/transformers/
VCS:            git:https://github.com/huggingface/transformers
#!RemoteAsset:  sha256:87f38dd25e4521151b97e94520ac457f44a0ae8a8358a5b112daff6c64a822d6
Source0:        https://files.pythonhosted.org/packages/source/t/%{srcname}/%{srcname}-%{version}.tar.gz
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}
# The default import scan eagerly imports optional model backends and their
# unavailable runtime dependencies; the focused smoke test below covers the
# installed package without requiring those extras.
BuildOption(check):  -e 'transformers.*'

BuildRequires:  pkgconfig(python3)
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)

%description
Transformers provides model definitions for state-of-the-art machine learning
across text, vision, audio, video, and multimodal tasks for inference and
training. This package provides the SGLang-private 5.19 compatibility tree.

%generate_buildrequires
%sglang_pyproject_buildrequires

%check -a
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
cat > "$tmpdir/config.json" <<'JSON'
{"model_type":"bert","hidden_size":16,"num_attention_heads":2,"num_hidden_layers":1,"vocab_size":4}
JSON
cat > "$tmpdir/tokenizer_config.json" <<'JSON'
{"tokenizer_class":"BertTokenizer","model_max_length":128,"do_lower_case":true}
JSON
printf '[UNK]\n[CLS]\n[SEP]\nhello\n' > "$tmpdir/vocab.txt"
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
PYTHONPATH="%{buildroot}%{_sglang_private_sitelib}:%{_sglang_private_pythonpath}" \
%{python3} -s - "$tmpdir" <<'PY'
import importlib.metadata
import json
import sys

from transformers import AutoConfig

root = sys.argv[1]
assert importlib.metadata.version("transformers") == "5.19.0"
config = AutoConfig.from_pretrained(root, local_files_only=True)
assert config.model_type == "bert"
with open(root + "/tokenizer_config.json", encoding="utf-8") as stream:
    tokenizer_config = json.load(stream)
assert tokenizer_config["tokenizer_class"] == "BertTokenizer"
assert tokenizer_config["model_max_length"] == 128
PY

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_sglang_private_libexec}/transformers

%changelog
%autochangelog

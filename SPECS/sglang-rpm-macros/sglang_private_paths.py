#!/usr/bin/python3
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
# SPDX-License-Identifier: MulanPSL-2.0
"""Rewrite pyproject-rpm-macros bookkeeping after private-tree relocation."""
import argparse
import json
from pathlib import Path


def rewrite_python_shebangs(root, interpreter):
    """Bind private entry points to the interpreter selected for the tree."""
    root = Path(root)
    if not root.is_dir():
        return
    interpreter = str(interpreter)
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        data = path.read_bytes()
        first, separator, remainder = data.partition(b"\n")
        if not first.startswith(b"#!"):
            continue
        command = first[2:].decode("utf-8", "surrogateescape").strip().split()
        if not command:
            continue
        executable = Path(command[0]).name
        arguments = command[1:]
        if executable == "env" and len(command) > 1:
            executable = Path(command[1]).name
            arguments = command[2:]
        if executable != "python" and executable != "python3" and not executable.startswith("python3."):
            continue
        suffix = " " + " ".join(arguments) if arguments else ""
        path.write_bytes(
            f"#!{interpreter}{suffix}".encode()
            + (b"\n" if separator else b"")
            + remainder
        )


def replace_text(path, old_site, new_site, old_bin, new_bin):
    if path and path.is_file():
        path.write_text(path.read_text().replace(old_site, new_site).replace(old_bin, new_bin))

def main():
    p = argparse.ArgumentParser()
    for name in ("record", "ghost", "files", "modules"):
        p.add_argument("--" + name, type=Path)
    p.add_argument("--from-site", required=True)
    p.add_argument("--to-site", required=True)
    p.add_argument("--from-sitearch")
    p.add_argument("--to-sitearch")
    p.add_argument("--from-bin", required=True)
    p.add_argument("--to-bin", required=True)
    p.add_argument("--interpreter", required=True)
    a = p.parse_args()
    for value in (a.ghost, a.files, a.modules):
        replace_text(value, a.from_site, a.to_site, a.from_bin, a.to_bin)
        if a.from_sitearch and a.to_sitearch:
            replace_text(value, a.from_sitearch, a.to_sitearch, a.from_bin, a.to_bin)
    rewrite_python_shebangs(a.to_site, a.interpreter)
    rewrite_python_shebangs(a.to_bin, a.interpreter)
    if a.record and a.record.is_file():
        data = json.loads(a.record.read_text())
        def rewrite(value):
            if isinstance(value, str):
                value = value.replace(a.from_site, a.to_site).replace(a.from_bin, a.to_bin)
                if a.from_sitearch and a.to_sitearch:
                    value = value.replace(a.from_sitearch, a.to_sitearch)
                return value
            if isinstance(value, list):
                return [rewrite(item) for item in value]
            if isinstance(value, dict):
                return {rewrite(k): rewrite(v) for k, v in value.items()}
            return value
        a.record.write_text(json.dumps(rewrite(data)))

if __name__ == "__main__":
    main()

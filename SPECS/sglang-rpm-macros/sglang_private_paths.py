#!/usr/bin/python3
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-License-Identifier: MulanPSL-2.0
"""Rewrite pyproject-rpm-macros bookkeeping after private-tree relocation."""
import argparse
import json
from pathlib import Path

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
    a = p.parse_args()
    for value in (a.ghost, a.files, a.modules):
        replace_text(value, a.from_site, a.to_site, a.from_bin, a.to_bin)
        if a.from_sitearch and a.to_sitearch:
            replace_text(value, a.from_sitearch, a.to_sitearch, a.from_bin, a.to_bin)
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

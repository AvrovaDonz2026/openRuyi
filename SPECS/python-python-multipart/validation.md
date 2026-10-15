<!--
SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
SPDX-FileContributor: A.Donz <avrova.minix@donz.si>

SPDX-License-Identifier: MulanPSL-2.0
-->

# python-multipart 0.0.32 validation

The recipe is present at `SPECS/python-python-multipart/python-python-multipart.spec`.
Its PyPI source is `python_multipart-0.0.32.tar.gz`; the RemoteAsset SHA256 is
`be54b7f3fa167bb83e4fcd936b887b708f4e57fe75911c02aebf53efaf8d938e`.

The SPEC includes an installation smoke check that imports `multipart` and
constructs a parser for a minimal `multipart/form-data` body. The check runs
after installation so it verifies the packaged import path.

Offline validation status on 2026-10-15:

* `python3 scripts/pre-commit-hooks/check_source_with_remoteasset.py SPECS/python-python-multipart/python-python-multipart.spec` passed.
* `rpmspec --parse` could not parse the repository's custom `BuildSystem: pyproject`
  directive with the host RPM 4.20 parser; this is a host-tool limitation.
* The source archive was not present in the local offline cache, so a source RPM
  could not be assembled without downloading the upstream archive.
* `qemu-riscv64` is not installed on the host, and no target RPM is cached;
  RISC-V RPM installation and guest import therefore remain unverified here.

The source hash was checked against the PyPI 0.0.32 release metadata. No source
checksum was changed.

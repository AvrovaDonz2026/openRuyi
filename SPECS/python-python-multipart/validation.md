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

Target source-build validation passed on 2026-10-15:

* The unmodified SPEC built a source RPM and binary RPM from the declared
  archive, including its import and parser `%check`.
* Local `rpmbuild` invocation defined `autorelease=1.local` and an empty
  `autochangelog`, because the guest lacks the Git-based automatic release
  preprocessing. The committed SPEC retains the required automatic macros.
* DNF installed the binary RPM with every repository disabled and downloaded
  zero bytes. The installed module parsed a multipart form field correctly.
* The source, SPDX, and other applicable pre-commit checks passed.

| Artifact | SHA-256 |
| --- | --- |
| `python-python-multipart-0.0.32-1.local.noarch.rpm` | `67d0412d4d42a9f5b212672c3a72ee509983c4ed4d33714b1883eb01d553f484` |
| `python-python-multipart-0.0.32-1.local.src.rpm` | `1f18ba33d336847a439ec384c1964d29a5ad89098376209917fbd60b03228095` |

The QEMU target uses Python 3.13.8, RPM 6.0.1, and Linux
7.1.2-533.1.or with QEMU 11.1.1. No source checksum was changed.

This is a local target source build, not an OBS acceptance result. The guest's
rpmlint 2.8.0 default configuration reported 9 errors and 9 warnings, including
missing signing/packager/changelog metadata, Group-tag expectations that conflict
with repository policy, and unexpanded automatic macros when rereading the
source SPEC. Clean production QA remains pending.

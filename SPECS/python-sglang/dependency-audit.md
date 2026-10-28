<!--
SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
SPDX-License-Identifier: MulanPSL-2.0
-->

# SGLang 0.5.21 dependency isolation (audit 2026-10-25)

## Current status (2026-10-25)

The retained wheel3 capability-rebuild report is identified as
`torch-elfcap-rebuild-20261023/REPORT.md` (a local staging artifact, not a
repository file). It
identifies runtime NEVRA
`python-torch-sglang-2.14-2.14.0-999.or.wheel3.riscv64` at
the artifact named
`python-torch-sglang-2.14-2.14.0-999.or.wheel3.riscv64.rpm`,
SHA256 `2890f52f6f1e86e636810bc53d50a8184d0397b515fce343b31d0b096925f4a2`;
the matching devel NEVRA is
`python-torch-sglang-2.14-devel-2.14.0-999.or.wheel3.riscv64`, SHA256
`c412a2bf94b29a5b4594d0285b2f9698e3efb098056dd5172f58e3f0153a8d70`. This
report says the build used cached `sglang-rpm-macros-0.1-999.or`. A later
header query confirms that this candidate still requires both
`libutf8_validity.so.33.2.0()(64bit)` and
`sglang(libutf8_validity.so.33.2.0()(64bit))`; it therefore does not validate
the fixed private ELF dependency generator. This candidate MUST NOT be
described as rebuilt with the fixed macros.
The report confirms namespaced private ELF capabilities, including
`sglang(libtorch_cpu.so()(64bit))` and
`sglang(libtorch_python.so()(64bit))`.

This wheel3 pair is distinct from the wheel1 pair referenced by the closure
audit: runtime NEVRA
`python-torch-sglang-2.14-2.14.0-999.or.wheel1.riscv64`, SHA256
`893a0806ffad2e725ae125d6c93f68a8a08eb69b4f59d0686f067dd3b4b68f5a`, from
the artifact set `torch-wheel-fixed-rpm-luna`. The
closure-audit artifact names that wheel1 pair as a reusable provisional
candidate; its hash MUST NOT be substituted for the wheel3 hash above. A
separate wheel3 candidate described in a previous status summary as built with
source macros `0.1-1000` is not available for local verification. The macro
recipe itself was rebuilt on 2026-10-24 as
`sglang-rpm-macros-0.1-1000.or.noarch`; this validates the macro package and
its minimum-version edge only, not a rebuilt Torch wheel3 RPM. The previously
summarized `torch-elfcap-rebuild-current/REPORT.md` is also absent from the
accessible artifact tree. Its exact artifact NEVRA, source and validation
therefore remain unconfirmed; those summary hashes are not treated as verified
values or conflated with either retained pair above.

The RISC-V Torchaudio 2.11.0 build, recorded under artifact set
`torchaudio-sglang-luna-20261023`, produced SRPM
`python-torchaudio-2.11-2.11.0-999.or.src.rpm` (SHA256
`b829c1069afcff9a9d4ca8a697b2be9c10557630cc3b740555479ebf839e34f1`) and RPM
`python-torchaudio-2.11-2.11.0-999.or.riscv64.rpm` (SHA256
`61c040a5fde4d13a6ecc4a57b43d711d1cd391add5c03a9efd1cd0a5c04c367b`).
The build log records `%check` importing Torchaudio modules and completing
successfully. Its build input was the wheel1 Torch runtime/devel pair. This
does not validate co-installation with the wheel3 candidates or a complete
SGLang transaction.

These are unsigned local staging artifacts, not production Torch or OBS-
signed packages. No complete transaction preflight has passed with the
current provider set. TorchVision, Triton, the SGLang CPU kernel, timm, and the
main SGLang package still lack validated current RISC-V RPMs; XGrammar,
LLGuidance and TorchCodec are also not complete. These remain release
blockers; neither wheel-derived candidate MUST be read as a completed SGLang
transaction. The pre-fix candidate-set preflight log is retained as
`wheel3-transaction-preflight-20261023.log` (a local staging artifact, not a
repository file).

## RISC-V QEMU boot and RPM candidate check (2026-10-24)

The official openRuyi Creek 2026.06 RVA23 Zero kernel and initramfs were
downloaded and matched the release SHA256 values:

- Kernel `openRuyi-2026.06-zero.kernel`: SHA256
  `cedc52f549d3ef63374ea31a7b63f63028d5ebb3c14cbede6b4e0a1ae9b49544`.
- Initramfs `openRuyi-2026.06-zero.cpio.gz`: SHA256
  `2543628f6a9d39b897bf2e520004388148334259a19662d5919cd9e8d85e8d08`.

QEMU 11.1.1 booted the release with `-cpu rva23s64`; the guest reported
OpenRuyi kernel `7.1.2-533.1.or` and `riscv64`. Its Zero rootfs contains only
the BusyBox RPM applet and no `python3`, so it cannot validate RPM dependency
transactions, private Python imports, coexistence, or inference. No package was
installed in this guest.

The wheel3 Torch runtime and devel RPMs were mounted read-only into the guest.
The BusyBox RPM query listed their metadata and private payload paths; their
guest-side SHA256 values matched the candidate hashes recorded above. This
checks file readability and basic RPM header parsing only. It does not replace
the full RPM transaction harness, and the runtime candidate's confirmed
`libutf8_validity` Requires remain an unresolved metadata defect.

An isolated QEMU 11.1.1 attempt with the OpenRuyi 2026.06 `Server-cloud` QCOW2
reached OpenSBI and the RISC-V UEFI firmware, but GRUB stopped with repeated
XFS inode read errors before entering the operating system. The base QCOW2 was
kept read-only and the temporary overlay was removed after the attempt. This
image therefore provides no additional RPM, Python, coexistence, or inference
evidence.

## Official 2026.09 Server-cloud guest and ABI check (2026-10-24)

The official openRuyi Creek 2026.09 RVA23 Server-cloud image and UEFI
firmware were downloaded and checksum-verified:

- QCOW2 SHA256 `2045e94d448ec12dbd3d7613c68005e8fdbe0748faf837f6e212af475dc8bc47`.
- `RISCV_VIRT_CODE.fd` SHA256
  `4dc955ecb8fa727e3989e8f40c1b846bffc38cd2830601a97eaa620807480c01`.
- `RISCV_VIRT_VARS.fd` SHA256
  `ea8094e953b1215444bd001ee1cf22818f1f7f8abcb158e62180cbaa6c1f70af`.

`qemu-img check` reported no image errors. QEMU 11.1.1 booted the image with
`-cpu rva23s64` and RISC-V EDK2 firmware 2.7; the guest reported kernel
`7.2.6-1.0_555.1.or`, `riscv64`, Python 3.13.8 and RPM 6.0.1. The guest
reached its serial login despite a failed `systemd-repart.service`; its 2.2
GiB root filesystem had 365 MiB free. RPM candidates were exposed through
read-only 9p mounts.

The guest RPM database successfully queried the wheel3 Torch runtime and
Tokenizers candidates, then `rpm -Uvh --test --nosignature` rejected them. Both
require `python(abi) = 3.14`, which the guest does not provide; the Torch RPM
also requires the unresolved private capability
`sglang(libutf8_validity.so.33.2.0()(64bit))` and numerous native providers.
Post-test `rpm -q` confirmed neither package was installed. This is a
non-mutating rejection of stale candidates, not a validation of the current
SPEC-built packages. The guest therefore provides a verified current boot and
RPM ABI baseline, but no complete dependency transaction, private import,
coexistence, or inference evidence.

The current dependency-macro tests were also run inside this QEMU guest: all 32
tests passed, and `bash -n` accepted the transaction harness. With the staged
`python-tokenizers-sglang-0.23-0.23.2-999.or.riscv64.rpm`, the harness reported
`RESERVED_FLAVOR_RESULT=PASS`, then rejected the private Python 3.14 payload
against guest Python 3.13.8 with `PRIVATE_PYTHON_ABI=FAIL` and exit status 1,
before RPM transaction or installation. This validates the ABI rejection guard
only; it does not validate a compatible candidate, the complete closure,
imports, coexistence, or inference. The guest was shut down cleanly afterward,
and its temporary COW overlay and variable-store copy were removed; the base
QCOW2 was not modified.

The 2026.09 guest was subsequently reached over the forwarded SSH port
`127.0.0.1:12055` with its `openruyi` account; root password login was rejected.
The guest reported 286 installed RPMs, Python 3.13.8, RPM 6.0.1, and 355 MiB
free before repository metadata refresh. No Torch, TorchAudio, TorchVision, or
SGLang module was installed, and no candidate RPM directory was mounted. A
read-only query of the enabled `Base` repository found no SGLang compatibility
closure candidates. Its public providers were Torch 2.13.0,
TorchAudio 2.11.0, TorchVision 0.28.0, Tokenizers 0.22.2, Transformers 5.12.1,
and Triton 3.7.1, below the private versions selected by this branch. No
package transaction was attempted because the candidate set was absent and
incomplete. This confirms the repository gap; it does not validate installation,
coexistence, private imports, or CPU inference.

## QEMU user-mode CPU checks and RPM preflight (2026-10-24)

A separate local OpenRuyi `riscv64` buildroot contains Python 3.14.7 and the
wheel1 Torch 2.14.0 runtime/devel RPMs. Its installed SGLang RPM macros are
`0.1-999.or`; this is a staged package buildroot, not a clean system snapshot.
From the Debian 13 `aarch64` Lima build host, QEMU user-mode 10.0.13 ran the
target Python interpreter as `riscv64`. Importing Torch 2.14.0, a 4x4 CPU
matrix multiplication, and a single-rank Gloo `all_reduce` passed. Torch
emitted a warning because NumPy is absent from this buildroot. These checks do
not exercise SGLang or model inference, and they do not establish an RPM
installation transaction.

The Torchaudio 2.11.0 candidate RPM was checked with the target root's RPM
6.0.1 using `rpm -Uvh --test --nosignature`. The transaction preflight failed
because `sglang(libtorch_cpu.so()(64bit))` is required but not provided. The
installed wheel1 Torch RPM advertises the unnamespaced
`libtorch_cpu.so()(64bit)` capability and does not advertise the corresponding
`sglang(...)` capability. No package was installed by this `--test` run. This
confirms that this Torch/Torchaudio candidate pair is not a valid private RPM
transaction; rebuilding with the corrected private ELF dependency generator
and rerunning the complete transaction are still required.

The upstream [v0.5.21 CPU metadata](https://github.com/sgl-project/sglang/blob/v0.5.21/python/pyproject_cpu.toml)
pins Transformers 5.19.0 and timm 1.0.16. The base repository provides
Transformers 5.12.1 and timm 1.0.28. The SGLang SPEC therefore keeps
Transformers 5.19.0, together with Tokenizers 0.23.2 and Hub 1.31.0, in the
private compatibility tree, while reusing the newer global timm 1.0.28 package
after adjusting the timm metadata pin. Click 8.4.2 remains a private provider
for the compatibility closure. The final OBS-signed RISC-V binary build,
dependency transaction and runtime compatibility remain to be verified.

## Public RISC-V provider metadata snapshot (checked 2026-10-19)

The repository metadata snapshot checked on 2026-10-19 listed Torch 2.13,
TorchAudio 2.11, TorchVision 0.28, Triton 3.7, LLGuidance 1.7.5, derivre
0.3.11, and hashbrown 0.17.0. This snapshot was not refreshed on 2026-10-24.
The SGLang CPU closure names private providers at Torch 2.14.0, TorchAudio
2.11.0, TorchVision 0.29.0, Triton 3.8.0, LLGuidance 1.7.6, derivre 0.3.12,
hashbrown 0.17.1, Transformers 5.19.0, Tokenizers 0.23.2, Hub 1.31.0,
Click 8.4.2, Mistral Common 1.12.0, SGLang CPU kernels 0.4.7, and TorchCodec
0.12.0. Timm 1.0.28 uses the existing global provider. The dated comparison is
evidence that the branch required OBS builds and transaction validation at that
time; it is not a replacement plan for the public providers or evidence of
current public-repository versions.

## Local OpenRuyi build evidence (2026-10-19)

In a disposable Debian 13 aarch64 Lima guest, `obs-build` used this
repository's `_config`, the OpenRuyi `riscv64` repository, and the `--arch
riscv64` target. The local run used `--nosignature` only because the public
repository signing key is not available in the guest; it does not claim an
OBS-signed result.

The `rust-hashbrown-0.17` recipe completed and produced version 0.17.1
noarch RPMs. Its source archive matched the declared RemoteAsset checksum
`ed5909b6e89a2db4456e54cd5f673791d7eca6732202bbf2a9cc504fe2f9b84a`. The
`sglang-rpm-macros` recipe also completed in the same target configuration;
all 28 dependency-generator tests passed and the resulting RPM provided
`rpm_macro(sglang_python_compat)` and the private SGLang dependency
capabilities.

The Click 8.4.2 recipe completed in the guest and produced
`python-click-sglang-8.4-8.4.2-999.or.riscv64.rpm` (SHA256
`5e9743fd7751be5c1463a50231a79f2df01201ce3785eec3f8e0c6fe94792cb5`). Its
RPM metadata provides both `sglang(python3dist(click)) = 8.4.2` and the
Python 3.14 capability used by the private Hub package.

A rerun of the current Click SPEC used a disposable copy of the seeded
Python 3.14.7 RISC-V buildroot, the current `sglang-rpm-macros` 0.1-1000 RPM,
and cached `flit-core` 3.12.0. QEMU-user executed the target Python and the
dynamic BuildRequires step accepted flit-core, but the build stopped before
the wheel build and `%check`: `python3dist(pip) >= 19` was not installed, and
the seeded root did not expand `%autorelease`. No final binary RPM was
produced. This is an incomplete build-environment result; it does not supersede
or validate the historical release 999 artifact above. The disposable
buildroot was removed after the attempt.

An earlier offline Hugging Face Hub 1.31.0 build with a Click candidate
produced a RISC-V RPM with SHA256
`d70b20ac764525e65f54f41828a6ea53df7eaa229b616190ff874a3369a66818`,
provides both the generator-normalized
`sglang(python3dist(huggingface-hub)) = 1.31` and the explicit exact-version
capability `= 1.31.0`, and requires the private Click range `>= 8.4.2, < 9`
together with the shared filelock, fsspec, PyYAML, tqdm, typing-extensions and
HTTPX providers. This earlier candidate is superseded by the current-SPEC
build and QEMU-user chroot validation recorded below.

The Tokenizers 0.23.2 recipe then completed a full OpenRuyi RISC-V build with
the Rust feature RPMs, Click and Hub candidates. Maturin produced a
`cp310-abi3-linux_riscv64` wheel; the RPM SHA256 is
`67b063d6d88af53720b0a5a28f948d2749ecd6df75456075d858d61f56e81b19`.
`rpm -K --nosignature` reported `digests OK`, the native extension was an
`ELF 64-bit ... UCB RISC-V ... double-float ABI` shared object, and a RISC-V
chroot import/encode test returned version `0.23.2` and IDs `[0, 1]` for a
WordLevel tokenizer. The build log is identified as
`tokenizers-build-final.log` and the extracted RPM metadata as
`tokenizers/rpm-metadata.txt` (local staging artifacts, not repository files).
These are unsigned local validation artifacts; OBS signing, the full Torch
closure, and the final co-install/inference transaction remain outstanding.

The Transformers 5.19.0 recipe completed in the same RISC-V guest with the
private Hub and Tokenizers candidates. The resulting RPM has SHA256
`e4b8c8f27d75aeacb5911f9aa6f90dfa3b1a9f7440c9be26a9d7729e0193b236`.
Its `%check` imported all Transformers modules and passed an offline BERT
`AutoConfig` smoke test. RPM smoke validation reported `digests OK`, and the
private installation path contained `transformers/__init__.py`; the package
provided `sglang(python3dist(transformers)) = 5.19` and
`sglang(python3.14dist(transformers)) = 5.19`. Its metadata requires the
private Hub range `>= 1.31, < 3` and Tokenizers `>= 0.23.1, < 0.24`, along
with the listed shared providers. The verification record is identified as
`transformers-verification.txt` (a local staging artifact, not a repository
file); this remains an
unsigned local artifact and does not establish an OBS-signed package or a
complete SGLang/Torch transaction.

The private `python-scikit-build-core-1` provider required by the Torch 2.14
recipe also completed in the RISC-V guest. The 1.1.1 RPM provides
`sglang(python3dist(scikit-build-core)) = 1.1.1`; its source matched the
declared checksum
`e347a59193c878ac56a363e57506938652a6dd8c965790cb1cbc6bc7e8d5abad`, all
installed modules passed `%check`, and a QEMU `rpm -qp` query confirmed the
`riscv64` package. The artifact is unsigned local validation output.

After adding that provider, the Torch 2.14 build resolved and installed its
full 227-package build environment. The build did not produce a Torch RPM:
the declared 760 MiB PyTorch release archive was still downloading when the
guest transfer was interrupted by the available network throughput. Torch,
TorchVision, TorchAudio, Triton, TorchCodec, the CPU kernel, timm, Mistral
Common, and the final SGLang transaction therefore remain unverified.

The CPU recipe uses the upstream `python/pyproject_cpu.toml`. Existing
openRuyi packages remain the shared dependency providers when they satisfy its
requirements. The compatibility packages install under
`%{_libdir}/sglang/core/python%{python3_version}/site-packages`, rather than
replacing the distribution's Python modules or development files.

CPU is the only SGLang backend enabled by the current source tree. ROCm
branches remain in selected private Torch and TorchVision recipes as a
reserved flavor, but their `_multibuild` entries are deliberately absent. The
ROCm dependency closure, target build and device validation are
not complete, so no ROCm RPM is scheduled or claimed as built. The conditional
requirements continue to name `torch-rocm`; they MUST NOT fall back to the CPU
provider when the flavor is enabled in a future change.

The packaged CPU closure is currently limited to `riscv64`, where the private
Torch, TorchAudio, TorchVision, Triton and CPU-kernel recipes are scoped for
the target architecture. Their complete binary build and runtime validation
remain required before publication. The upstream
CPU metadata also mentions Linux ARM, but this repository does not yet provide
an ARM-compatible Triton RPM; publishing the SGLang RPM there would leave an
unsatisfied runtime dependency. x86_64 is likewise held back until the
repository supplies the upstream `intel-openmp` Python capability and validates
the complete transaction. The standalone `python-sglang-kernel-cpu` provider
uses the same architecture limit, so it cannot be scheduled independently on
an unsupported architecture.

## Static hardening (2026-10-24)

The private RPM macros now exclude both installed and RPM 6 buildroot paths
from the global ELF dependency generator, and normalize nested SGLang Python
capabilities. The dependency-generator regression suite passes 32 tests. The
Torch recipe now requires `sglang-rpm-macros >= 0.1-1000`; the retained Torch
wheel3 candidate used `0.1-999` and remains invalid evidence for the corrected
ELF metadata.

The `sglang-rpm-macros` source recipe before the Release adjustment below was
rebuilt offline in the Debian 13 aarch64 Lima guest with an OpenRuyi
`riscv64` build root. The build
completed with exit code 0, all 32 `%check` tests passed, and
`rpm -K --nosignature` reported `digests OK`. The resulting RPM is
`sglang-rpm-macros-0.1-999.or.noarch`, SHA256
`b7d2d86ebe0b1df60908bc252b2d96089aadd64f9f1f299b5a6c27514abc1346`;
the artifact and log are in
`/private/tmp/openruyi-build/sglang-macros-noarch-repro-20261024-1845/`.
This package did not satisfy the consumer minimum
`sglang-rpm-macros >= 0.1-1000`. In that guest, RPM 6.0.1 defines its default
release macro as the non-parametric `999%{?dist}`; attempting
`%autorelease -b 1000` leaves the release at 999. The macro SPEC therefore
sets the next monotonic release as `1000%{?dist}` while retaining the
distribution suffix macro. This SPEC records a justified exception to the
preferred `%autorelease` convention.

The adjusted 0.1 source recipe was rebuilt offline in the same Debian 13
aarch64 Lima/OpenRuyi `riscv64` environment without a release override. It
completed with exit code 0, passed all 32 `%check` tests, and emitted no RPM
comment expansion warnings. Its manual `Release: 1000%{?dist}` workaround is
superseded because the repository pre-commit policy requires `%autorelease`.
The current source recipe advances to version 0.1.1 and restores `%autorelease`
so it remains newer than the consumer minimum without overriding the release
macro. It was rebuilt offline on 2026-10-25 in the Debian 13 `aarch64`
Lima/OpenRuyi `riscv64` buildroot. The RPM is
`sglang-rpm-macros-0.1.1-999.or.noarch`, SHA256
`d42e00eeea43ca41b577e9fd5e4ac943ac6f6a07084b0060915b80b0e1824d69`; its
SRPM SHA256 is
`3acfad7a698c9331b61e72bd87ab75b215f42c60dee13245d44f89b445611220`.
All 32 `%check` tests passed and `rpm -K --nosignature` reported `digests OK`.
RPM's `labelCompare` confirmed `0.1.1-999` is newer than the consumer minimum
`0.1-1000`. The unsigned RPMs and build log are retained under
`/private/tmp/openruyi-build/sglang-macros-version011-final-20261025/`.
The temporary buildroot was removed, leaving 4.4 GiB free in the guest. The
earlier RPM is
`sglang-rpm-macros-0.1-1000.or.noarch`, SHA256
`7b3b51fd6777780b497256460933a15f6813209fa865c5f06484b695ad56bec5`;
`rpm -K --nosignature` reported `digests OK`. A separate consumer probe with
`Requires: sglang-rpm-macros >= 0.1-1000` passed `rpm --test` against a private
RPM database seeded with this RPM; the guest system RPM database was not
modified. Final build artifacts and logs are retained under
`/private/tmp/openruyi-build/sglang-macros-release1000-final-20261024/`.
That historical 0.1-1000 candidate and its edge were validated separately; the
current 0.1.1 recipe and its version edge are now also validated. The full
SGLang dependency transaction remains unresolved.

The CPU transaction harness now requires the complete allowlisted candidate
set before it can reach DNF, installation, private imports, or smoke tests. It
checks ownership of the packaged test helpers and the RPM ownership and paths
of private ELF objects actually mapped by the import process. Optional gRPC
tools and status packages may be supplied, but do not satisfy required runtime
edges. The harness has not run against a complete target RPM transaction.
Its pre-install Python ABI guard was exercised separately in a live 2026.09
guest as recorded below.

The XGrammar TVM FFI edge now has a version 0.1.11 private compatibility
provider recipe, and LLGuidance declares the missing offline Cargo leaves. The
Triton CPU recipe conditionally links each GPU LLVM library group only when
its matching NVIDIA or AMD codegen backend is enabled. The ordered 2001-2004
patch stack applies to the cached Triton 3.8.0 source tree; a focused source
assertion confirms that the RISC-V and X86 host libraries remain present while
the GPU groups are backend-conditional. Static review also found that a
cross-build placed target LLVM binaries first on `PATH`, although Triton 3.8.0
resolves its extension compiler as `clang` and `clang++` by name. The recipe
now keeps the host LLVM toolchain first for x86_64-to-riscv64 builds, and
explicitly selects the host `mlir-tblgen` for the bundled LLVM cross configure.
These source-level checks do not validate host-tool compatibility, CMake
configuration, linking, or an RPM build; none of those were run. Cross-only
CMake target settings are present in the eight RISC-V CPU recipes that
configure CMake.
These are source-level packaging changes; they do not establish successful
RISC-V builds or runtime imports.

On 2026-10-24, `git diff --check`, Python syntax checks, shell syntax checks,
the Rust Cargo/spec consistency hook, and all 32 dependency-generator tests
passed. Full `pre-commit` could not fetch its GitHub hooks because DNS access
was unavailable. The available Zero guest lacks Python and a usable RPM
transaction environment; the 2026.06 Server-cloud QCOW2 failed during GRUB/XFS
boot. The 2026.09 guest boots, but its Python 3.13 ABI rejects the available
Python 3.14 candidates. Consequently no current complete RISC-V RPM install,
coexistence, private import, or inference-engine result is claimed.

BARNACLE: PINNED-SPDX-HOOK-REJECTS-ATTRIBUTION-TEXT. On 2026-10-25, the
configured SPDX header hook rejected the requested
`SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>` line
because its allowlist does not recognize that declaration. The REUSE header
check passed. All remaining configured pre-commit hooks passed after restoring
`%autorelease`; the attribution line is retained in the new compatibility
SPECs as requested. The hook needs maintainer review before the full configured
pre-commit suite can pass.

The harness ABI rejection was reproduced in QEMU 11.1.1 using the official
2026.09 Server-cloud image, RVA23 CPU model, and EDK2 2.7 firmware. The guest
reported kernel `7.2.6-1.0_555.1.or`, Python 3.13.8, and RPM 6.0.1. The
repository and candidate RPM directory were shared read-only through virtio-9p
from a disposable COW overlay; host TCP port forwarding was unavailable, so
the test used the serial console. Running the harness with
`python-tokenizers-sglang-0.23-0.23.2-999.or.riscv64.rpm` returned exit code 1
with `guest Python ABI mismatch: guest=3.13 candidates=3.14` and
`PRIVATE_PYTHON_ABI=FAIL`. The candidate was rejected before DNF or
installation, and a subsequent RPM query confirmed it was not installed.
This validates the ABI rejection gate only; the current Python 3.14 RPM
transaction, private imports, coexistence checks, and SGLang CPU inference
remain unverified.

The upstream CPU metadata requests `intel-openmp` on `x86_64`. This repository
has no `intel-openmp` recipe or provider; the RISC-V `%prep` path removes that
platform-marked requirement because the target uses the packaged LLVM OpenMP
runtime instead. The SGLang CPU and CPU-kernel recipes therefore explicitly
scope publication to RISC-V until an `intel-openmp` provider is added and the
x86_64 transaction is validated.

## Offline Click and TVM FFI builds (2026-10-25)

Click 8.4.2 and Apache TVM FFI 0.1.11 were built offline in the OpenRuyi
`riscv64` RPM buildroot on the Debian 13 `aarch64` Lima host. The buildroot
used Python 3.14.7 and the RVA23 flags. TVM FFI's C/C++ compilation used
LLVM 22 Clang with `--target=riscv64-openruyi-linux`; target `rpmbuild` and
Python checks ran under QEMU user-mode `qemu-riscv64`. This is LLVM-targeted
compilation inside the emulated RISC-V build environment, not a host-native
cross-build or a booted RISC-V system test.

The Click RPM is
`python-click-sglang-8.4-8.4.2-999.or.riscv64`, SHA256
`63a19a04249d536930a16dd5f54fba713663363040065f82ae25b41b78662370`;
its SRPM SHA256 is
`60eba3bcdb54b5719b8a80d0dc6e8c815249607a225889440525a67d990e9e34`.
The package's `rpmbuild` completed `%check`, including the recipe assertion
and imports of all Click modules. The enclosing `obs-build` command returned
1 because a trailing `rpmautospec-rpm-macros` argument was parsed as another
build target; this does not change the completed Click `rpmbuild` result.
`rpm -K --nosignature` reported `digests OK`. The RPM requires
`python(abi) = 3.14` and installs under
`/usr/lib64/sglang/core/python3.14/site-packages`.

The TVM FFI RPM is
`python-apache-tvm-ffi-0.1-0.1.11-999.or.riscv64`, SHA256
`7d0154dada4e38d07707863d380c1cc5b1d980c30c0cc411f1bbce58c8ea62c9`;
its SRPM SHA256 is
`7cb2d10c2e710d7ccdb62ef5be61339c4e7dc01fc430f6b9d34271876bf09981`.
The build exited 0, and `%check` imported all packaged modules, verified
version 0.1.11 and the native library load, then registered, invoked, and
removed a global FFI callback. `rpm -K --nosignature` reported `digests OK`.
The RPM provides `sglang(python3dist(apache-tvm-ffi)) = 0.1.11` and private
TVM FFI ELF capabilities; it requires `python(abi) = 3.14` and
`typing-extensions >= 4.5`. Its Python payload is under
`/usr/lib64/sglang/core/python3.14/site-packages`.

Both packages are unsigned local candidates. Their RPMs, SRPMs, logs, and
build reports are retained under
`/private/tmp/openruyi-build/click-offline-20261025-0050/` and
`/private/tmp/openruyi-build/tvmffi-0.1.11-offline-20261025-0055/`.
The dedicated OBS build roots were removed after the jobs finished; the Lima
guest then had 4.4 GiB free. Neither candidate was installed in the official
2026.09 QEMU release guest, whose Python 3.13.8 does not satisfy their Python
3.14 ABI. The complete candidate transaction, coexistence check, private
imports in an installed system, and SGLang CPU inference remain unverified.

A wheel-derived Torch 2.14 macro probe was attempted with the fixed
`sglang-rpm-macros-0.1-1000` package, solely to check whether the private
`libutf8_validity.so.33.2.0` requirement is removed. Initial attempts failed
during root extraction and dependency initialization. A later retry selected
116 packages, installed the staged macro RPM, rewrote the RPATHs of the Torch
ELF objects, and reached `%check`, but its reduced probe SPEC omitted
`BuildRequires: cmake(fmt)`, which is present in the full Torch SPEC. The
probe buildroot consequently lacked `libfmt.so.12`, and the import smoke failed
with `ImportError: libfmt.so.12`. This does not validate the full Torch recipe.
No Torch RPM was produced, so the private ELF requirement behavior remains
unverified. The wheel, macro RPM, logs, and report are retained under
`/private/tmp/openruyi-build/torch-macro-probe-20261025/stage/`.

The probe also exposed duplicate `$ORIGIN` entries in the shared private-RPATH
macro. The macro now deduplicates preserved and required entries; the focused
shell check, all 33 dependency-generator tests, and `git diff --check` pass.
This change has not yet been rebuilt in the guest. On 2026-10-25 the configured
Lima instance reported `Broken`, and its SSH control socket was inaccessible,
so no guest rebuild or QEMU transaction could be run.

The private-install macro now also rewrites Python entry-point shebangs after
relocating files into the SGLang tree. New builds therefore bind console
scripts to `%{_sglang_private_interpreter}` instead of leaving a generic
`/usr/bin/python3` dependency. Existing Click, Hub, and TVM FFI RPMs listed
above predate this change and MUST be rebuilt before their metadata can be
used as evidence of Python ABI isolation.

## Hugging Face Hub RISC-V validation (2026-10-24)

The current `python-huggingface-hub-sglang-1.31` SPEC (SHA256
`423443300902c005bf72cef6fbb70c39a7ef9148ffdd41ad89d55e59a01dee39`) and the
source archive (SHA256
`f8e9e710a210613fa5d0f26bba6da05ef4aef9fba5a0f23f508f5ac4d08b6f90`) built
offline in a disposable OpenRuyi RISC-V RPM buildroot. The build used Python
3.14.7, RPM 6.0.1 and the `rva23u64` target flags. The Lima build VM is Debian
13 `aarch64` on kernel `6.12.113+deb13-cloud-arm64`, with QEMU user-mode
`qemu-riscv64` 10.0.13 executing target binaries. This pure-Python wheel build
produced no native ELF objects; `initvm.aarch64` was unavailable, so this was
not an LLVM cross-build or a booted RISC-V system test. The final build log is
`hub-offline-current-20261024/obs-build-final.log` (a local staging artifact).

The successful binary RPM is
`python-huggingface-hub-sglang-1.31-1.31.0-999.or.riscv64.rpm`, SHA256
`58570334276b4064c33be72e598576243b1d5e5df4d3bade608bbdd782d5507a`; its
SRPM SHA256 is
`f5459708c3212310374ce2950cbe64e3e74e9f8d3c7bbe993544d4a6cb8067dd`.
`rpm -K --nosignature` in the guest reported `digests OK` for both unsigned
local artifacts; they are not OBS-signed packages. The RPM provides normalized
and exact `sglang(python3dist(huggingface-hub))` versions and declares the
private Click 8.4.2 range plus Python 3.14 and the shared runtime requirements.

Inside the disposable RISC-V chroot, `rpm -Uvh --replacepkgs --test` passed,
then the final RPM was installed with `--replacepkgs`. `rpm -V` passed for the
Hub RPM, private Click 8.4.2, and system Click 8.3.3. Default Python continued
to import system Click 8.3.3 from `/usr/lib/python3.14/site-packages`; RPM
file ownership identifies `python-click-8.3.3-5.13.or.noarch`. With the
SGLang-private site-packages path selected, Python imported Hub 1.31.0 and
Click 8.4.2 from `/usr/lib64/sglang/core/python3.14/site-packages`. The
offline API smoke constructed `HfApi`, generated a Hub URL, and passed with
`HF_HUB_OFFLINE=1`. No base Hub RPM was available in the local candidate
repository, so coexistence with a system Hub version was not tested.

This validates the current Hub and Click candidates only. The full SGLang CPU
RPM closure, system-wide baseline comparison, complete original-dependency
coexistence, SGLang startup, native Torch imports and CPU inference remain
unverified; this result does not satisfy the complete transaction and
inference gates below.

## Shared and private providers

| Dependency | Provider selection |
| --- | --- |
| timm 1.0.28 | Existing system package; the SGLang SPEC aligns the upstream 1.0.16 pin to the current base version. |
| Transformers 5.19.0, Tokenizers 0.23.2 and Hub 1.31.0 | Private compatibility packages selected by the v0.5.21 CPU runtime closure. |
| Click 8.4.2 | Private compatibility provider required by Hub and Mistral Common. |
| NumPy, SciPy, protobuf, compressed-tensors | Existing distribution recipes; SGLang does not require their proposed upgrades. |
| Datasets, fsspec, pandas, Pillow | Existing distribution packages for the core CPU environment. |
| Torch 2.14.0 | `python-torch-sglang-2.14`, including a private development SDK. |
| TorchAudio 2.11.0 and TorchVision 0.29.0 | Private compatibility packages linked against the private Torch SDK. |
| Triton 3.8.0, xgrammar 0.2.7, llguidance >=1.7.6 | Private compatibility packages. |
| Mistral common >=1.11.5 and TVM FFI | Private compatibility packages where the distribution version is insufficient. |
| scikit-build-core >=1.0 | Private build backend for Torch; the distribution's 0.12.2 backend remains available. |
| SGLang CPU kernels, TorchCodec and SMG/gRPC | Private modules sharing the selected private Torch/gRPC runtime. |
| ModelScope | Existing shared package; no differing version requires duplication. |

The SGLang SPEC now declares the direct private `xgrammar` 0.2.7 and
`llguidance` 1.7.6-or-later, below-2.0 edges explicitly in both build and
runtime requirements. These versions follow the current CPU metadata used for
this downstream compatibility profile; the original v0.5.21 release metadata
must still be identified separately when preparing the mainline review.

Tokenizers 0.23.2 uses the existing Rust PyO3, NumPy and async-runtime 0.29
crate series. Historical validation notes report a RISC-V QEMU run that
completed offline Cargo resolution, produced the
`cp310-abi3-linux_riscv64` wheel, and passed package import and WordLevel
encode/decode checks. The notes also report a separate RISC-V QEMU scratch
RPMDB run in which an unsigned RPM installed with an explicit `--nosignature`
override, passed `rpm -V`, and passed private-path import and WordLevel smoke
checks while leaving the existing system packages untouched. Those logs and
the scratch RPM are not current repository artifacts; they do not prove a
reproducible package build, a signed RPM, or a successful SGLang inference
run. The SGLang pyproject wrappers export
`CARGO_NET_OFFLINE=true` for both build-requirements generation and wheel
construction, so this offline constraint is enforced by the package macros.
Hugging Face Hub's
`hf-xet>=1.5.2,<2` dependency applies only to its upstream x86/ARM platform
markers; the `python-hf-xet` recipe is aligned
to 1.5.2 for those platforms, although its target build remains unverified. It
is not required by the RISC-V CPU marker.

LLGuidance 1.7.6 requires the exact `derivre` 0.3.12 crate release. The
compatibility closure therefore keeps the existing 0.3.11 crate available and
adds a co-installable 0.3.12 provider, together with the required hashbrown
0.17.1 provider. The Rust crate transaction and LLGuidance target build remain
unverified.

The optional Datasets 4, fsspec 2026.2, pandas 2 and Pillow 11 recipes use the
separate `extras` tree. They MUST NOT replace shared distribution providers.
They are not selected by the core CPU launcher. Optional diffusion dependencies,
including RunAI Model Streamer and its cloud SDK build closure, remain incomplete.
The existing `opencv` package remains unchanged; the optional
`opencv-python-headless` requirement is therefore outside the current core
CPU closure and is not claimed as packaged here.

## Launch and dependency resolution

`sglang` and `sglang-python` select the private core tree, disable user site
packages and unsafe current-directory imports, and clear inherited Python and
ELF loader overrides. They invoke the versioned interpreter matching the
private tree (for example, `/usr/bin/python3.14`) and the package explicitly
requires both that interpreter path and `python(abi)` version. Transformers,
Tokenizers and Hugging Face Hub are loaded from the private compatibility tree;
timm and the other selected base modules remain accessible through the normal
system Python paths. The coexistence check reads the ABI from the private
launcher itself, so its test runner may use a different system Python version.
Torch and native compatibility modules use the private core tree and private
library search paths; global loader configuration is not changed.

Private Python distributions provide `sglang(python3dist(NAME))` capabilities;
optional private distributions use `sglang-extras(python3dist(NAME))`. Selected
internal requirements use the same namespaces. Python ABI and external system
libraries retain normal RPM requirements. Private ELF libraries MUST NOT
satisfy unrelated applications' global SONAME requirements.

## Python ABI coexistence boundary (2026-10-25)

The official 2026.09 RVA23 guest reports Python 3.13.8. Current SGLang
candidate RPMs use Python 3.14 paths and the local `riscv64` buildroot uses
Python 3.14.7. The checked-in `SPECS/python/python.spec` currently builds the
main `python3` package for Python 3.14; it owns the generic `/usr/bin/python3`
entrypoint and provides `python(abi) = 3.14`. Installing that package into the
3.13 release guest would replace the default interpreter package, so it is not
evidence of a coexisting compatibility runtime.

The repository Python RPM policy permits multiple Python 3 versions but only
one main `python3` package may own generic names and entrypoints. An alternate
interpreter stack MUST use versioned package names and paths such as
`python3.14`, `/usr/bin/python3.14`, and `python3.14-*`; its RPM ownership and
dependencies must not replace the existing Python 3.13 system packages. The
local RISC-V RPM inventory contains no installable Python 3.14 interpreter or
runtime RPM. A cached repository metadata snapshot lists generic `python3`
3.14.9 packages, which cannot establish safe side-by-side installation.

The `python314` multibuild flavor now keeps the interpreter and library package
names versioned. CPython's non-debug Linux install also stages the stable-ABI
`libpython3.so`; the broad library file list would otherwise package that
generic path alongside the system interpreter. The alternate flavor now
excludes it while retaining `libpython3.14.so`. Local `rpmspec` expansion
confirmed the exclusion in `python3.14-libs`; actual RPM file ownership and
co-installation with the 2026.09 Python 3.13 packages remain unverified.

The SGLang recipe now locks its launcher to the versioned interpreter and
declares the matching ABI and executable requirements. This prevents a generic
`/usr/bin/python3` switch from silently selecting an interpreter that cannot
load the private tree. It does not create the alternate Python 3.14 provider.
The `python314` multibuild recipe exists, but no corresponding installable RPM
has been produced. The 2026.09 guest therefore continues to reject the current
candidates before transaction resolution until a versioned Python 3.14 runtime
is built and staged in the test guest. Full RPM installation, private import,
system coexistence, and CPU inference remain unverified.

The blobfile, OpenAI, Harmony and timm requirements are bounded in `%prep`
for the existing distribution versions. The recipe includes API
smoke checks for these substitutions. They do not establish complete inference
compatibility and remain explicit downstream changes for review.

## Required target validation

Before this stack is ready for mainline review, the final recipes MUST pass:

1. Offline source and binary RPM builds with complete BuildRequires.
2. RPM dependency and file ownership checks, including absence of global
   capabilities for private modules and native libraries.
3. Installation alongside the distribution packages without removals,
   replacements or payload modifications.
4. `sglang-coexistence-test.py` against a clean system snapshot, checking module
   versions and paths, native Torch library paths and distributed Gloo support.
   Its real `sglang --help` check enables Python's verbose import trace and
   verifies that the launcher imports `sglang` from the private core tree.
5. SGLang CPU startup and a local inference test, followed by repeat checks of
   the original system modules and representative operations.
6. Applicable repository pre-commit checks and SRPM/binary RPM review checks.

Historical validation notes also report a scratch LLVM/RISC-V probe producing
an executable that ran in a QEMU guest; no such executable or run log is
present as a current repository artifact. This is toolchain evidence only, not
a package build result. The current QEMU RPM transaction harness checks the
supplied Torch, TorchAudio, TorchVision,
TorchCodec, Triton and SGLang metadata, installs the candidate transaction,
checks private module versions and native paths, preserves the system RPM and
Python baselines, and exercises Torch distributed Gloo, TorchCodec/FFmpeg and
the SGLang CPU launcher when those candidate RPMs are supplied. It does not
constitute a real OBS-signed RISC-V binary build or prove complete inference
compatibility. Full production Torch 2.14 distributed support, SGLang CPU
inference, and the final OBS-signed coexistence transaction remain unverified;
no inference result is claimed by this audit.

The CUDA flavor is unsupported on RISC-V: its SPEC is restricted to
`x86_64` and `aarch64`, and CUDA recipes requiring NVIDIA's toolkit cannot be
built for RISC-V with the supported toolchain. The repository currently does
not enable a CUDA multibuild because the private Torch provider has a CPU
variant but no CUDA variant; enabling it without that provider would leave the
CUDA Torch dependency unresolved. CUDA-only recipes are retained as
reserved, currently unbuildable sources with explicit architecture limits and
`torch-cuda` requirements. No CUDA runtime result is claimed here. ROCm device
execution is likewise outside this CPU audit and has not been validated on
RISC-V.

The local pbuild CI configuration in `.github/build/_config` currently has no
SGLang-specific build exclusions. `scripts/update-package` synchronizes
package sources, not this configuration. The live OBS project configuration
MUST exclude `python-sglang-kernel`, `python-sgl-deep-ep`, and
`python-sgl-deep-gemm` until their CUDA dependency closure is buildable; its
current state has not been verified. Recipe comments and architecture limits
alone do not disable builds. Without matching OBS exclusions, the build service
can schedule the reserved CUDA sources and fail dependency resolution because
no `torch-cuda` provider is published.

## Fresh official guest preflight (2026-10-25)

A fresh OpenRuyi Creek 2026.09 Server-cloud image was booted with QEMU 11.1.1,
the `rva23s64` CPU model, and EDK2 2.7 firmware. The base QCOW2 and firmware
were kept unchanged; the guest used a disposable 16 GiB copy-on-write overlay
and an independent VARS copy. The guest reported `riscv64`, kernel
`7.2.6-1.0_555.1.or`, Python 3.13.8, RPM 6.0.1, and 14 GiB free on `/` after
automatic XFS growth. Host staging was mounted read-only through virtio-9p.

The current offline Click 8.4.2 candidate
`python-click-sglang-8.4-8.4.2-999.or.riscv64.rpm` was passed to the current
transaction harness. It returned `PRIVATE_PYTHON_ABI=FAIL` because the guest
does not have `/usr/bin/python3.14`. A separate non-installing
`rpm -Uvh --test --nosignature` reported the unsatisfied `python(abi) = 3.14`
requirement. The candidate was not installed. Afterwards, `rpm -V python3
python3-libs` passed, Python 3.13.8 imported its system `ssl` and `sqlite3`
modules, and `dnf --version` reported 5.4.2.0. This confirms the guard rejects
the incompatible candidate without changing the base Python packages; it does
not validate a compatible transaction, private imports, coexistence of the
full dependency closure, or SGLang inference.

The same guest performed a second read-only header and transaction check over
the staged Click, Hub, TVM FFI, and Torch 2.14 wheel3 candidates. All payloads
were readable `riscv64` RPMs. `rpm -Uvh --test --nosignature` returned status 5
without changing the RPM database: the Python 3.14 ABI and its versioned
Python-distribution requirements were unavailable, and Torch additionally
requested its native Abseil/OpenMP/BLAS/ONNX providers plus the unresolved
`sglang(libutf8_validity.so.33.2.0()(64bit))` capability. No candidate was
installed; the system Python 3.13 baseline remained untouched. This is a
non-mutating rejection of an incomplete candidate set, not a complete SGLang
transaction or inference result.

The separate Debian 13 aarch64 Lima build host is reachable and provides
`/usr/bin/obs-build`, `/usr/bin/clang-22`, `/usr/bin/llvm-config-22`, and
`/usr/bin/ld.lld-22`; Clang 22 registers the RISCV backend. An initial
toolchain probe checked only for unversioned command names and incorrectly
reported LLVM missing. Debian cross libc, Linux headers, libgcc, and libstdc++
sysroot packages were installed for a temporary smoke test (24.4 MiB download,
148 MiB installed). That sysroot uses glibc 2.41, while the OpenRuyi QEMU guest
uses glibc 2.44, so it is not an acceptable OpenRuyi package-build sysroot.
The 15 temporary Debian cross packages and their downloaded `.deb` archives
were purged after the smoke test; the Lima guest returned to 6 GiB free.

Clang 22 compiled a `-march=rva23u64 -mabi=lp64d` RISC-V ELF and the OpenRuyi
QEMU guest ran it successfully. A disposable RPM probe was then built on the
Lima host as
`llvm-riscv64-cross-smoke-0.0.1-1.riscv64.rpm` (SHA256
`a4659069a7f1dcf6d2dcd33e0b6add9386cfbc3092e2bdd07805008ed3d993db`). The
probe used a per-command RPM `buildarch_compat` override and LLVM's
RISC-V-aware strip/objdump tools; it does not change the repository or the
guest's global RPM configuration. Its transaction preflight and installation
passed in the 2026.09 QEMU guest, `rpm -V` passed, and the installed binary
reported `machine=riscv64` and kernel `7.2.6-1.0_555.1.or`. The probe RPM was
removed afterward. Python 3.13 and its RPM payload still verified, `ssl` and
`sqlite3` imported, and DNF remained at 5.4.2.0.

This validates the basic host LLVM-to-RISC-V ELF/RPM/QEMU path only. It does
not build an SGLang package or establish a production RPM build environment.
A matching OpenRuyi target sysroot, package-specific cross-build checks, and
the complete private runtime closure are still required.

## Lima build-host status recheck (2026-10-25)

The configured `lima-openruyi-riscv` SSH endpoint on port 49896 is a Debian 13
`aarch64` host, not the `rva23s64` OpenRuyi runtime guest. It has RPM 4.20.1,
Python 3.13.5, `obs-build`, LLVM 22, and `qemu-riscv64`; it has no Python 3.14
interpreter, RISC-V cross GCC, or installed RISC-V sysroot. The only matching
include directory found was `/usr/include/riscv64-linux-gnu`. It is therefore
not a ready package buildroot or a substitute for the target RPM transaction
and runtime tests.

The host root filesystem had 2.5 GiB free of 40 GiB, and `/var/tmp` occupied
31 GiB. No `obs-build` or `rpmbuild` process was present during the check. Two
`qemu-riscv64` Python 3.14 multiprocessing children remained under an active
SSH login scope after systemd recorded OOM-killed processes at 06:18; both
children had PPID 1, were sleeping on pipe reads, and had accumulated no CPU
time during a 4.5-hour interval. They were not treated as a completed Python
runtime build or as a usable interactive RVA23 guest. No process was signaled
and no remote temporary files were removed during this inspection.

The local forwarded listener at port 49896 belongs to this AArch64 Lima host.
No RVA23 SSH endpoint was identified. Full dependency construction and target
validation remain pending access to the user's running RVA23 guest or another
usable OpenRuyi RISC-V build environment.

## Python 3.14 alternate flavor build gate (2026-10-25)

The `python314` multibuild flavor now passes
`TESTOPTS="-j1 -u-network,-urlfetch ..."` to CPython's fast-CI test target.
The source test runner derives its default worker count from the available CPU
count plus two when no positive `-j` value is supplied; the explicit `-j1`
therefore bounds the QEMU test worker fan-out without dropping the selected
test cases. This is a resource-control correction, not a completed build
result.

The alternate flavor now declares `python3-bootstrap` as its build interpreter
provider instead of requiring `python3.14`, which is the runtime package being
built and is absent from the verified Python 3.13 guest. The existing
`bootstrap` multibuild flavor is intended to provide the versioned interpreter
needed by `regen-all`; OBS dependency ordering and the resulting bootstrap RPM
have not yet been validated in the target build environment.

The earlier expanded SPEC retained `TESTOPTS="-j2 ..."`. A previous remote
probe report for `/var/tmp/sglang-python314-probe-retry-root/.build.log`
recorded an uncapped `make -O -j4 ... test`, SIGKILLed CPython test workers,
and `rpmbuild` failure in `%check`, alongside systemd OOM kills. That remote
log is not available in the current local staging tree for re-reading. The
process listing also recorded two orphaned `qemu-riscv64` Python children, but
the saved local evidence does not tie those specific PIDs to the failed
`%check`. The next RISC-V build MUST use the current `-j1` source and retain
its complete `%check` log.

Separate local probes also failed before `%check`: a remote build report said
its `%prep` source directory lacked the declared
`0001-change-user-install-location.patch`; the patch exists in the repository,
so that result indicates incomplete source staging. The local Homebrew
`rpmspec` probe separately rejected its generated changelog because it did not
start with `*`; this does not establish a target OBS changelog failure. These
are build-environment/staging defects; no Python 3.14 RPM or SRPM was
produced, and no alternate interpreter has been installed in the official
guest. The private ABI transaction, coexistence, import, and inference gates
remain open.

On 2026-10-25 the local source checks passed `git diff --check`, Bash syntax
validation for the transaction harness, and all 33 dependency-macro unit
tests. Homebrew `rpmspec` cannot parse the unmodified OpenRuyi spec directly
because it lacks the `autotools` BuildSystem definition; a local expansion
with OpenRuyi-only tags removed selected `python3.14-*` packages and the
`python3-bootstrap` build provider. This is static expansion only, not a
target build or RPM validation.

## QEMU session 14861 ABI and base-package guard (2026-10-25)

The disposable OpenRuyi 2026.09 Server-cloud guest was rechecked through its
serial QEMU session `14861`. QEMU 11.1.1 booted `rva23s64`; the guest reported
`riscv64`, kernel `7.2.6-1.0_555.1.or`, Python 3.13.8, RPM 6.0.1, and DNF
5.4.2.0. The shared 9p mount exposed only the currently staged candidates:
Torch 2.14 wheel3 runtime/devel, Click, Hub, TVM FFI, and the SGLang macro
probes; it did not contain a complete CPU SGLang closure.

The current transaction harness was copied to the shared staging directory
and run against the two Torch wheel3 RPMs. It returned status 1 before DNF or
RPM installation with `PRIVATE_PYTHON_ABI=FAIL` because the guest has no
`/usr/bin/python3.14`. The same read-only check confirmed both candidates are
`riscv64`; the runtime advertises `python(abi) = 3.14` and the legacy
`sglang(libutf8_validity.so.33.2.0()(64bit))` requirement. The expected
incompatible-candidate rejection therefore passed, while the candidate itself
remains unsuitable for the current guest and is not a validated provider.

Before and after the check, `python3-3.13.8-10.25.or.riscv64` and
`python3-libs-3.13.8-10.25.or.riscv64` remained installed; `rpm -V
python3 python3-libs` produced no output, `/usr/bin/python3` and
`libpython3.13.so.1.0` retained their original RPM ownership, and no package
was installed. The guest had approximately 341 MiB free on `/`. This run
validates the ABI rejection and base-package preservation guards only. It
does not establish a complete dependency transaction, private imports,
coexistence, SGLang startup, or CPU inference.

The same session ran `rpm -Uvh --test --nosignature` over the Torch runtime and
devel pair without changing the RPM database. It returned status 2 and listed
missing Abseil SONAMEs, cpuinfo, NUMA, OpenMP, ONNX, OpenBLAS, protobuf/utf8,
SLEEF, the Python 3.14 ABI and Python distribution capabilities, in addition to
the stale private `libutf8_validity` capability. This is the expected rejection
of an incomplete native and Python provider set. The command was never retried
with `--nodeps` and no package was installed.

## QEMU session 70306 source and RPM header verification (2026-10-25)

A fresh disposable QEMU 11.1.1 session used the same 16 GiB overlay and an
explicit read-only virtio-9p mount of the staging directory. The guest again
reported `riscv64`, kernel `7.2.6-1.0_555.1.or`, Python 3.13.8, and RPM 6.0.1.
The exact SGLang v0.5.21 archive was readable at
`/mnt/host/qemu-staging-20261025/sglang-0.5.21-upstream.tar.gz`; its guest-side
SHA256 was
`c44951b7871dac61262fc04e9fca628175758a97fa5f603c522b31dc31b94249`, matching
the SPEC RemoteAsset checksum. The archive had the expected
`sglang-0.5.21/` top level and both CPU `pyproject_cpu.toml` files.

The seven staged candidates (Torch runtime/devel, Tokenizers, Click, Hub, TVM
FFI, and the SGLang macro RPM) passed `rpm -K --nosignature`; their NEVRA and
`riscv64`/`noarch` headers were queryable. No candidate was installed. The
guest has only the base Python 3.13 runtime, and its configured repository
`boat.openruyi.cn` was not resolvable. The guest also lacks `rpmbuild`,
`obs-build`, LLVM/Clang/LLD, CMake, Ninja, Rust, Cargo, and the `patch` utility.
Consequently the three downstream patch dry-runs returned command-not-found,
and no package build, dependency transaction, private import, coexistence,
SGLang startup, or inference result is claimed from this session.

## Local buildroot dependency follow-up (2026-10-25)

The separate Lima `openruyi-riscv` instance is a Debian 13 `aarch64` build
host, not a booted RISC-V system. Its seeded OpenRuyi `riscv64` buildroot is
`/var/tmp/openruyi-sglang-kernel-cpu-root-seeded-20261023`. The buildroot
initially lacked `concurrentqueue-devel`, which stopped the SGLang CPU-kernel
wheel during Torch CMake configuration at `find_package(concurrentqueue)`.

The OpenRuyi `riscv64` repository metadata lists
`concurrentqueue-devel-1.0.5-5.8.or.riscv64` with
`cmake(concurrentqueue) = 1.0.0`; the published RPM SHA256
`f90b8c75bcdc0db3e62f004713ff5e3eeebcb85c197953ccedf7c679f720585d` matched
the downloaded file. Target RPM `-Uvh --test` and installation succeeded
under `qemu-riscv64` in the disposable buildroot. RPM readback resolved the
capability and listed the packaged headers and CMake config. The target CMake
package lookup reported `concurrentqueue found.` A minimal C++ queue program
was compiled with the buildroot's Clang 22 for `rv64gc`, then run under
`qemu-riscv64` with exit status 0. The temporary RPM and test executable were
removed after the checks; the provider remains installed in the disposable
buildroot for subsequent builds.

RPM emitted `NOKEY` for the repository package signature because the signing
key is not imported into this buildroot. The downloaded RPM digest was checked
against the repository primary metadata, but cryptographic signature
verification remains outstanding. These checks validate this existing base
provider only; they are not a complete SGLang dependency transaction.

The Debian `aarch64` guest host has host-native Clang/LLD 22.1.8 and
`qemu-riscv64` 10.0.13. A temporary RISC-V sysroot assembled from the seeded
root supplied Torch 2.14 headers and libraries. Host LLVM compiled all 24 CPU
kernel objects with `riscv64-openruyi-linux` and `-march=rva23u64`; the final
link used `ld.lld` and produced an ELF64 RISC-V `common_ops.abi3.so`.

The exact v0.5.21 archive was staged with SHA-256
`c44951b7871dac61262fc04e9fca628175758a97fa5f603c522b31dc31b94249`, matching
the SPEC RemoteAsset. A normal target `rpmbuild -bb` (without
`--short-circuit`) produced:

```text
python-sglang-kernel-cpu-0.4.7-1000.or.riscv64.rpm
SHA256 e79556000b80fb70a4fff70a4edb6bbfaf42d63f720648556b29b69261021259
```

The RPM contains the complete upstream `sgl_kernel` Python package, the
RISC-V extension, the smoke launcher, README, and license. Its metadata
contains the private Torch ELF requirements (`sglang(libc10.so...)`,
`sglang(libtorch.so...)`, and `sglang(libtorch_cpu.so...)`) and no
`rpmlib(ShortCircuited)` marker. The preserved artifact and ten-line smoke log
are under `/private/tmp/openruyi-build/sglang-rpms-20261025/`; the sysroot,
source tree, build tree, and staging payload were removed after validation.

The seeded root's strict `rpm -Uvh --test` correctly rejected the kernel RPM
because its installed Torch wheel1 predates the tracked Torch recipe changes
that add the matching private `sglang(libc10/libtorch...)` Provides. This is a
real transaction blocker, not a reason to use `--nodeps`; the Torch runtime
must be rebuilt or replaced by the normal OpenRuyi provider transaction before
publishing the SGLang package.

For runtime validation only, the kernel RPM was installed with `--nodeps` in
the disposable root. Under `qemu-riscv64`, Python 3.14 imported the complete
`sgl_kernel` package, registered `rmsnorm_cpu`, `silu_and_mul_cpu`,
`initialize`, and `shm_allreduce`, and passed the TP=2 shared-memory smoke over
float32/float16/bfloat16 and boundary sizes. The package was then erased; the
original Torch RPMs remained installed and `import torch` still reported
2.14.0. No complete SGLang runtime transaction, engine startup, or model
inference is claimed until the rebuilt Torch provider and remaining dependency
closure are available.

## Full-system QEMU CPU-path checks (2026-10-26)

A disposable standalone copy of the guest disk was booted with QEMU 11.1.1
system emulation. The guest reported `riscv64`, kernel
`7.1.2-533.1.or`, RPM 6.0.1, and Python 3.14.7. QEMU used `-cpu max`; this
was not an explicitly named `rva23s64` CPU profile, so this run is RISC-V
execution evidence but does not certify the minimum RVA23 profile.

The guest had seven SGLang candidates installed: Torch 2.14.0, Tokenizers
0.23.2, Click 8.4.2, Hugging Face Hub 1.31.0, TVM-FFI 0.1.11, the CPU
`sgl_kernel` RPM, and `sglang-rpm-macros`. `rpm -V` passed for all seven.
Under `/usr/lib64/sglang/core/python3.14/site-packages`, private imports of
Torch, Tokenizers, Click, Hugging Face Hub, and TVM-FFI passed. A Torch CPU
2x2 matrix multiplication returned the expected `[[19, 22], [43, 50]]`.

The updated CPU-kernel smoke helper was transferred to the guest and its
SHA-256 matched the source file. With a shared 300-second rank deadline, the
installed RISC-V extension passed its TP=2 shared-memory smoke for float32,
float16, and bfloat16 across small, chunk-boundary, and non-divisible sizes.

Coexistence checks passed for the existing `python3`, `python3-libs`, NumPy,
SciPy, Requests, Packaging, PyYAML, and typing-extensions RPM payloads. Their
isolated system-Python imports resolved under `/usr/lib*/python3.14/site-packages`
with the installed versions unchanged; `tokenizers`, `huggingface_hub`,
`transformers`, and `timm` were absent from the system import path.

The complete CPU candidate set is still incomplete. Fourteen required RPMs
were absent: TorchAudio, TorchVision, Mistral Common, Transformers, XGrammar,
LLGuidance, grpcio, grpcio health checking, grpcio reflection, SMG gRPC proto,
SMG gRPC servicer, Triton, SGLang, and TorchCodec. `python-sglang` and the
`sglang` CLI were absent, so a complete RPM transaction, SGLang engine startup,
and model inference remain unverified. The passed kernel smoke is not an
SGLang inference result.

## Authenticated guest follow-up (2026-10-26)

The running standalone guest was reached as `openruyi` over forwarded SSH port
`12056`. It remains an OpenRuyi `riscv64` system with kernel `7.1.2-533.1.or`,
Python 3.14.7, RPM 6.0.1, and about 17 GiB free on its 20 GiB root filesystem.
The QEMU process still uses `-cpu max`, not an explicitly named `rva23s64`
profile. No RPM was installed or erased during this follow-up.

The guest's 306-package RPM database was queried read-only through a temporary
user-owned copy of its RPM database. The private profile imported Torch 2.14.0,
Tokenizers 0.23.2, Hugging Face Hub 1.31.0, Click 8.4.2, and TVM-FFI 0.1.11
with Python 3.14.7. The same interpreter without the private profile could not
import Torch, Tokenizers, Hugging Face Hub, or Transformers, confirming those
modules are not exposed on the system Python path. The coexistence baseline
probe passed and resolved NumPy 2.4.6 and SciPy 1.17.1 from
`/usr/lib64/python3.14/site-packages`; optional private modules and absent
shared dependencies such as `datasets` were recorded as absent.

The `openruyi` account has no passwordless `sudo` access, and the documented
default root password was rejected. Consequently, this follow-up did not run a
guest RPM transaction or modify the installed package set. `python-sglang`,
its `sglang` launcher, the remaining required providers, engine startup, and
`/generate` inference remain unverified. Temporary validation files were
removed after the read-only checks.

## Candidate payload and transaction follow-up (2026-10-26)

The private Transformers 5.19.0 RPM was rehashed after its build completed:

```text
python-transformers-sglang-5.19-5.19.0-999.or.riscv64.rpm
SHA256 215f7ef34a760ad2f3e778de7f7ae75e36f6d75cbe9692905669b787a1634b6f
```

`rpm -K --nosignature` reported `digests OK`. Its metadata provides
`sglang(python3.14dist(transformers)) = 5.19` and requires the private
Transformers 5.19-compatible Tokenizers and Hugging Face Hub capabilities.
The RPM payload, together with the candidate Safetensors 0.8.0 and Regex
2026.1.15 payloads, imported successfully under Python 3.14 in the RISC-V
guest; an offline `AutoConfig.for_model("bert")` smoke returned
`model_type == "bert"`.

A strict `rpm -Uvh --test` using a user-owned copy of the guest RPM database
rejected the candidate set only for the missing Base provider
`python3.14dist(typer)`. The system RPM database remained unchanged, and the
transaction log is retained at
`/home/openruyi/validation-reports/transformers-transaction-20261026/transaction.log`.
The Base repository metadata lists `python-typer-0.25.1-4.1.or.noarch`, but
the guest and host could not download it during this offline validation.

The updated coexistence baseline snapshot ran on the guest with Python 3.14
and 304 installed RPMs; it resolved the existing NumPy, SciPy, and FSSpec
system modules while preserving the absence of the private Torch, Tokenizers,
Hugging Face Hub, Transformers, and Timm modules from the system path. The
existing seven-package private CPU profile still passes `rpm -V`, the Torch
matrix smoke, and the 300-second CPU-kernel shared-memory smoke. These checks
do not establish a complete SGLang RPM transaction or inference result until
Typer and the remaining CPU closure are available.

## Isolated SGLang transaction follow-up (2026-10-27)

The final `python-sglang-0.5.21-1001.riscv64.rpm` was checked against the
user-owned transaction staging area
`/home/openruyi/closure-transaction-20261026/rpms` in the QEMU guest. The
audited package SHA-256 is
`edd4f7fc92fa429e0f120c71e5ede6d3bf144b19306f3263c2005ea2627392c8`.
The earlier staged package was discarded from the candidate set because it
carried `rpmlib(ShortCircuited)`; the audited package has no such capability.
The staging set contained 233 RPMs. The authoritative no-write check was:

```text
rpm --dbpath /home/openruyi/closure-transaction-20261026/rpmdb --test -Uvh \
  --nosignature /home/openruyi/closure-transaction-20261026/rpms/*.rpm \
  /home/openruyi/rpmbuild-sglang/RPMS/riscv64/python-sglang-0.5.21-1001.riscv64.rpm
```

It returned `234`. The transaction log is
`/home/openruyi/closure-transaction-20261026/logs/transaction-all-with-audited-sglang-20261027.log`;
its SHA-256 is
`680a6e9155a0f5098ac57bca1d5c11251c277f10927480be3f9e4abc548d30b3`.
The isolated RPM database still contains 306 packages and its package/index
database timestamps did not change. No package was installed into the guest's
base RPM database.

The successful supplemental artifacts staged for this check were Blobfile
3.2.0, EasyDict 1.13, ModelScope Hub 0.4.6, ModelScope 1.40.2, and OpenAI
2.40.0. The existing Torchaudio artifact still exposes only the short private
capability `2.11`; the SGLang package also requires the exact `2.11.0`
capability, so that artifact is not a valid final provider until rebuilt from
the updated SPEC. The checked-in SPEC already declares both exact private
Torchaudio capabilities; the old staged RPM was excluded from the audited
transaction.

The transaction remains intentionally open. The following target providers did
not produce installable RPMs in this run: OpenAI Harmony 0.0.8, LLGuidance
1.7.6, Py-spy 0.4.1, SMG gRPC Servicer 0.9.1, TorchCodec 0.12, TorchVision
0.29, Triton 3.8, and XGrammar 0.2.7. The ordinary Blobfile and ModelScope
dependency builds also remain blocked by missing development headers, linker
inputs, or Rust registry inputs. The target LLGuidance source archive was not
present in the offline source pool. TorchVision needs the generated Torch 2.14
development header tree and CMake files; the current private SDK does not
expose that complete tree. Triton reached source preparation with the required
LLVM archive, CMake, Git, and pybind11 supplied in an isolated prefix, but the
RISC-V guest timed out extracting the 261 MiB LLVM source tree before `%build`.
XGrammar reached CMake in earlier attempts, but its build macro retained the
absolute `/usr/lib64/llvm22/bin/clang++` path while the compiler was in an
isolated prefix. SMG gRPC failed on missing C++ standard headers and
`grpcio-tools`; TorchCodec failed on missing LLVM compiler binaries and FFmpeg
runtime/development inputs.

An isolated Outlines 1.2.13 experiment with a Python 3.14 marker relaxation
produced `python-outlines-1.2.13-1001.noarch.rpm`, SHA-256
`38900d8cfe58fe4a3c0781a8633788fe5bd29e6f99b0bf1f69fca97b6f229185`.
It is not treated as a repository result: the experiment used `--nodeps
--nocheck`, and its runtime import still needed Pillow's native libraries and
the missing Genson/cloudpickle/diskcache/outlines-core closure.

Because the strict transaction is incomplete, this evidence does not claim a
successful `import sglang`, CLI startup, CPU engine startup, or model
inference. Those checks must run only after the final RPM closure resolves in
the guest. CUDA and ROCm remain reserved, non-buildable flavors.

## Direct guest transaction rerun (2026-10-27)

The existing local QEMU `riscv64` guest was reachable as `openruyi` over
`127.0.0.1:12059`. It reported kernel `7.1.2-533.1.or`, Python 3.14.7, RPM
6.0.1, and 16 GiB of free space. The read-only transaction used the staged
RPMs under `/home/openruyi/closure-transaction-20261026/rpms` and the isolated
database at `/home/openruyi/closure-transaction-20261026/rpmdb`:

```text
rpm --dbpath /home/openruyi/closure-transaction-20261026/rpmdb --test -Uvh \
  --nosignature /home/openruyi/closure-transaction-20261026/rpms/*.rpm
transaction_rc=238
```

The transaction log is
`/home/openruyi/closure-transaction-20261026/logs/transaction-rerun-20261027-final.log`;
its SHA-256 is
`061be7f1068c82fd7aebb07b537dd6d0c2bb74d253e105b43959ca0141b8329c`.
The isolated database still contains 306 packages after the test. No package
was installed into the guest's base database.

The remaining SGLang provider failures are LLGuidance 1.7.6, the exact private
Torchaudio 2.11.0 capability, TorchCodec 0.12.0, TorchVision 0.29.0, Triton
3.8.0, and XGrammar 0.2.7. Supplemental experimental packages in the same
staging set also require lxml, PyCryptodome, cryptography, and outlines-core;
those failures are separate from the SGLang core provider list. Consequently,
the guest still has no complete install transaction or inference-engine
validation for this revision.

A non-installing payload extraction smoke used the staged SGLang, Torch,
Torchaudio, Transformers, Tokenizers, Hub, and CPU-kernel RPMs. `import
sglang` stopped in `sglang.srt.utils.common` with
`ModuleNotFoundError: No module named 'orjson'`. The retained log is
`/home/openruyi/validation-reports/sglang-import-rerun-20261027.log` with
SHA-256
`2a03ecf7ca65c7ab4da540ec730b28ff33307a8b09f4b49658d14669289f6644`.
The temporary extraction tree was removed after the check.

## Corrected guest payload import smoke (2026-10-27)

The earlier extraction set omitted staged public providers. A second
non-installing smoke used the SGLang, Torch, TorchAudio, Transformers,
Tokenizers, Hub, Click, Mistral Common, Regex, Safetensors, CPU-kernel,
`python-orjson-3.11.7`, `python-psutil-7.2.2`, and `python-pybase64-1.4.3`
payloads. They were extracted into a fresh user-owned `/tmp` directory in the
same `rva23s64` guest and removed by a shell `trap` after the check. The guest
base RPM database and the isolated 306-package database were not modified.

`orjson`, `psutil`, `pybase64`, Torch 2.14.0, TorchAudio 2.11.0, and the
Transformers/Tokenizers/Hub stack imported successfully. `import sglang` then
stopped in `sglang.srt.utils.common` with:

```text
ModuleNotFoundError: No module named 'triton'
```

This corrects the earlier `orjson` observation: `orjson` was absent from that
extraction subset, not absent from the staged RPM directory. Triton 3.8.0 is
still one of the six unresolved CPU providers, so this smoke does not claim a
successful SGLang import or engine startup.

The no-`ShortCircuited` audited SGLang RPM
(`edd4f7fc92fa429e0f120c71e5ede6d3bf144b19306f3263c2005ea2627392c8`) also
does not carry the public `python3.14dist(orjson)`,
`python3.14dist(psutil)`, `python3.14dist(pybase64)`,
`python3.14dist(prometheus-client)`, `python3.14dist(pyzmq)`,
`python3.14dist(uvloop)`, or `python3.14dist(zstandard)` requirements
generated from the wheel metadata, nor the private
`sglang(python3.14dist(smg-grpc-servicer))` requirement. The
earlier non-audited candidate retained those generated requirements in its
local `requires.txt` but carried `rpmlib(ShortCircuited)`. Neither artifact is
publishable. The QEMU transaction harness now requires these runtime metadata
lines before it can proceed to a transaction or import stage; the next normal
OBS rebuild must satisfy both the generated public requirements and the
absence of `rpmlib(ShortCircuited)`.

## Bounded provider reruns and QEMU closure staging (2026-10-27)

The validation guest was restarted from the existing validation image with
`-cpu rva23s64`, QEMU 11.1.1, and SSH forwarding on `127.0.0.1:12060`. A
read-only baseline reported `riscv64`, kernel `7.1.2-533.1.or`, Python 3.14.7,
RPM 6.0.1, and 306 installed base packages. All package tests below used a
copied RPM database or payload extraction tree; the base filesystem and RPM
database were not changed.

The staged candidate set was retested in an isolated database. The primary
transaction returned `55`; adding the four validated pure-Python supplemental
RPMs (Cloudpickle 3.1.2, Diskcache 5.6.3, Genson 1.4.0, and Jsonpath-ng
1.8.0) returned `59`; adding the experimental TorchAudio repack returned
`60`. The latter removed only the short TorchAudio capability failure. The
remaining core failures were TorchCodec 0.12.0, Transformers 5.19, Triton
3.8.0, XGrammar 0.2.7, LLGuidance 1.7.6, and Mistral Common, with Pillow and
several lower-level providers also absent. The transaction logs and metadata
inventories were copied to
`/private/tmp/openruyi-build/sglang-final-evidence-20261027/transactions/`
before the larger staging directories were removed.

The following bounded checks produced useful evidence but are not publishable
release artifacts:

* The TorchAudio payload exposes the exact public and private `2.11.0`
  capabilities and passed an extracted functional smoke. It was a metadata
  correct repack of an existing payload; a normal source RPM build did not
  complete, so it remains experimental.
* SMG gRPC proto `0.4.22` and servicer `0.9.1` payloads were generated and
  compiled in the guest using temporary noarch recipes. Their hashes are
  `22ce418872d9f3ff53ff32e447c2d7f5a299b9b5d499401afe6ba149ad515685` and
  `f88a3791de534f3a022d92084dd0a0655ab0c7bc7e0d5840d498fa40594a25b2`.
  The checked-in recipes still require a real `grpcio-tools` provider, so these
  payloads do not establish an OBS build.
* Cloudpickle, Diskcache, Genson, and Jsonpath-ng imported and passed their
  focused function smoke. Prometheus Client and psutil also imported from
  temporary RISC-V wheels. These supplemental providers did not resolve any
  SGLang core transaction failure. The pybase64 wheel was built, but its module
  import was not resolved in the bounded smoke.
* TorchVision `0.29.0` produced a temporary noarch RPM containing a RISC-V
  extension and passed extraction and metadata checks. Guest import/NMS could
  not run because the isolated guest path did not contain the private Torch
  runtime; this artifact is not a release result.

The missing core providers were retried with verified source inputs. Triton
source and its pinned LLVM commit were checksum-verified, but the guest RPM
macro failed on `%autochangelog` before the expensive LLVM build. XGrammar
reached native CMake with the LLVM path override and passed compiler/linker
checks, then stopped because `FindPython` required the absolute
`/usr/include/python3.14/patchlevel.h` path while the headers were in the
private sysroot. LLGuidance reached Cargo metadata but offline resolution
failed because the `anyhow` crate was not in the vendor/index closure.
TorchCodec reached `Preparing metadata (pyproject.toml)` and timed out after
300 seconds. No RPM was produced for any of these four providers. The
temporary source pool was removed after checksum verification; its hashes and
the associated rerun logs remain under
`/private/tmp/openruyi-build/sglang-final-evidence-20261027/`.

The corrected extraction smoke still imports Torch 2.14.0, TorchAudio 2.11.0,
Transformers/Tokenizers/Hub, orjson, psutil, and pybase64 before stopping at
`ModuleNotFoundError: No module named 'triton'`. Therefore this revision still
does not demonstrate a complete RPM transaction, `import sglang`, CLI startup,
CPU engine startup, or `/generate` inference. CUDA and ROCm remain reserved
and non-buildable flavors.

## Host LLVM cross-build and current guest recipe checks (2026-10-27)

The existing disposable RVA23 guest was reused at `127.0.0.1:12061` with
QEMU `rva23s64`, kernel `7.1.2-533.1.or`, Python 3.14.7, and RPM 6.0.1. The
host Homebrew LLVM/LLD toolchain cross-compiled a minimal Python extension with
`--target=riscv64-linux-gnu`, `-march=rv64gc`, and `-mabi=lp64d`. The output was
an ELF64 RISC-V shared object with RVC and the double-float ABI; its SHA-256 is
`8ade212cdb8b44a1f870f3385742e1e82045cc7ccb30c3549ebc205714b4afc6`.

The cross-build helper's first guest `%check` used a stale `cpython-313`
filename while the selected guest ABI was Python 3.14. A corrected temporary
recipe using the same object and the `cpython-314` filename passed `%check`.
The helper's normal install path also attempted to lock the base RPM database
as the unprivileged `openruyi` user. A follow-up test registered the RPM in a
user-owned isolated RPM database with `--justdb`, extracted its payload into a
separate root, and imported it under the guest Python 3.14 interpreter. The
smoke returned `42`, and `readelf` confirmed `Machine: RISC-V` and
`double-float ABI`. This validates the host LLVM-to-RISC-V artifact path and
the isolated guest import path; it does not validate a privileged system RPM
installation.

The current 23 SGLang-related SPEC files all passed guest `rpmspec -P` after
excluding macOS archive metadata files from the temporary transfer. The
`sglang-rpm-macros` regression suite ran all 37 tests successfully in the same
guest. The full SGLang dependency transaction remains open: Triton, XGrammar,
LLGuidance, TorchCodec, TorchVision, exact Torchaudio capability packaging,
and other providers still lack publishable OBS-built RPMs. CUDA and ROCm stay
reserved and non-buildable.

## QEMU target access recheck (2026-10-27)

The earlier Python 3.14.7/RPM 6.0.1 guest at `127.0.0.1:12059` is no longer
available. Its prior validation key and guest disk/overlay were not present in
the local staging paths. A temporary SSH forward was added to another QEMU
process on that port, but the available key was rejected, so that process is
not treated as an accessible guest.

The only guest reachable over SSH during this recheck was `127.0.0.1:22024`,
booted from a disposable overlay on the openRuyi 2026.06 Server-cloud image
with QEMU 11.1.1 and `-cpu rva23s64`. It reported `riscv64`, kernel
`7.1.2-533.1.or`, Python 3.13.8, RPM 4.20.1, and a 733 MiB root filesystem
with approximately 34-42 MiB free. This guest does not satisfy the private
Python 3.14 ABI or RPM 6.0.1 validation target. No SGLang RPM transaction or
installation was attempted in it.

The retained source hash manifest refers to
`/private/tmp/openruyi-build/source-pool-20261027`, but that source pool is no
longer present. The current temporary staging tree has no Triton 3.8.0,
LLVM-pinned, LLGuidance 1.7.6, XGrammar 0.2.7, or TorchCodec 0.12.0 source
archives, and no complete set of publishable provider RPMs. The saved provider
and transaction logs remain evidence of the prior bounded attempts; they do
not establish successful builds, a complete transaction, `import sglang`,
CPU engine startup, or `/generate` inference. Restore verified offline source
inputs and a reachable Python 3.14/RPM 6.0.1 RVA23 guest before resuming those
target checks.

## Torchaudio capability recheck (2026-10-27)

The retained Torchaudio RPM above exposes
`sglang(python3.14dist(torchaudio)) = 2.11`; its embedded SRPM SPEC predates the
explicit capability aliases now present in
`SPECS/python-torchaudio-2.11/python-torchaudio-2.11.spec`. RPM 4.20.1 in the
reachable RVA23 guest reports `rpm.vercmp("2.11", "2.11.0")` as `-1`, so this
archived RPM does not satisfy SGLang's exact `= 2.11.0` requirement. The current
SPEC has not been rebuilt into a replacement RPM, and no Torchaudio package was
installed during this recheck.

## Source recovery and current QEMU recheck (2026-10-27)

This section supersedes the preceding statements about the temporary source
pool being absent and no suitable QEMU guest being reachable. It does not
change the older build or transaction results recorded above.

The source pool at
`/private/tmp/openruyi-build/source-pool-20261027` has been restored. These
archives match the checksums in their current SPEC files:

- Torchaudio 2.11.0: `599ec24e7e1eef476ef21f0178e33da00e2434f930ba42e9cc20bf4002220486`.
- XGrammar 0.2.7: `7674afeee5e6eff9672627b62d5ab0aa2347ea51674f4d78a5c160029f92bc3e`.
- LLGuidance 1.7.6: `db7febbe412ed2015501904646750071d7e00e6df7f85c4b956ad4f206fd2df7`.
- TorchCodec 0.12.0: `f0cc21c1f99439cff30eb43080e9bc8e43c6b9505b4f327cb42ee132075bcec4`.

Triton 3.8.0 and its pinned LLVM source are still absent from the restored
source pool. The current build staging tree contains only three RPM files
(Click, Hugging Face Hub, and Tokenizers); no complete provider set or
Torchaudio SRPM is present there.

The official openRuyi Creek 2026.09 RVA23 Server-cloud image and UEFI firmware
were downloaded from the [release directory](https://releases.openruyi.cn/creek/2026.09/rva23/)
and matched its `SHA256SUMS`: QCOW2
`2045e94d448ec12dbd3d7613c68005e8fdbe0748faf837f6e212af475dc8bc47`, CODE
`4dc955ecb8fa727e3989e8f40c1b846bffc38cd2830601a97eaa620807480c01`, and VARS
template `ea8094e953b1215444bd001ee1cf22818f1f7f8abcb158e62180cbaa6c1f70af`.
`qemu-img check` reported no image errors. QEMU 11.1.1 booted it with
`-cpu rva23s64` on an 8 GiB disposable COW overlay; the base QCOW2 remains
unchanged. The guest reports kernel `7.2.6-1.0_555.1.or`, glibc 2.44,
RPM 6.0.1, and Python 3.13.8, with 5.7 GiB free after automatic filesystem
expansion. A read-only 9p mount exposes the staged source pool and evidence.

The guest's enabled rolling `Base` repository advertises generic Python
3.14.7 packages. Its `python3-devel` RPM provides the `python3.14-devel`
capability, and `python3` provides `python(abi) = 3.14` plus
`/usr/bin/python3.14`. However, a `dnf install --assumeno` simulation for
`python3` 3.14.7 and `python3-devel` 3.14.7 would replace/upgrade 31 installed
packages, including Python 3.13.8 and its Python modules. The simulation was
aborted without installing anything. These generic providers therefore do not
coexist with the guest's 2026.09 Python 3.13 baseline; the `python314`
compatibility flavor in `SPECS/python/python.spec` remains necessary for that
baseline if it is part of the supported target matrix.

The guest has no `rpm-build`, GCC, Clang 22, CMake, or Make installed. No
package build, SGLang RPM transaction, install, private import, coexistence
test, CPU engine startup, or `/generate` inference was performed in this
recheck. The dependency closure and Python 3.14 compatibility provider remain
release blockers.

## Isolated provider install and import probe (2026-10-27)

The current guest is reachable at `127.0.0.1:22025` and remains on Python
3.13.8/RPM 6.0.1. A main-root `dnf install --assumeno` for the three staged
Click, Hugging Face Hub, and Tokenizers RPMs proposed replacing 31 installed
packages, including Python 3.13.8 with Python 3.14.7. The simulation was
aborted; the base guest RPM database was not changed.

An isolated `/var/tmp` installroot using the guest's rolling `Base` repository
successfully installed those three RPMs and their dependencies with Python
3.14.7. With the private core site-packages directory on `PYTHONPATH`, imports
and focused behavior checks passed for Click 8.4.2, Hugging Face Hub 1.31.0,
and Tokenizers 0.23.2. The checks ran a Click command, validated a Hub repo ID,
and encoded text with a Tokenizers WordLevel model. The temporary installroot
was removed after the checks; the base guest remains on Python 3.13.8 with
5.7 GiB free.

This validates only these three provider RPM payloads in an isolated Python
3.14 root. The complete RPM inventory remains three RPMs and no SRPMs. There
are still no usable SGLang, Torch 2.14, SGLang CPU kernel 0.4.7,
TorchVision 0.29, Torchaudio 2.11, TorchCodec 0.12, Transformers 5.19,
Triton 3.8, XGrammar 0.2.7, LLGuidance 1.7.6, or Mistral Common provider RPMs
in the staging paths. The main-root transaction,
full SGLang import, CPU engine startup, compatibility test against existing
software, and `/generate` inference remain unverified.

The host Homebrew LLVM 23.1.3 and LLD expose the RISC-V target, but this guest
has no exported target sysroot or Python 3.14 development headers. Host
`rustc`/`cargo` are unavailable, and Homebrew `rpmbuild` defaults to Darwin
without the openRuyi RPM macros. No dependency RPM was cross-built in this
recheck; the earlier minimal ELF cross-build remains a separate toolchain smoke.

## Isolated RPM Builds and Complete Metadata Scan (2026-10-27)

The reachable QEMU RVA23 guest is `127.0.0.1:22025`. Its system remains at
Python 3.13.8/RPM 6.0.1 with 286 installed RPMs. Builds and installs below ran
only inside `/var/tmp/sglang-mainline-buildroot`, which uses Python 3.14.7/RPM
6.0.1; the guest's main RPM database was not changed. Current Base metadata
reports Torch 2.13.0, TorchAudio 2.11.0, TorchVision 0.28.0, Triton 3.7.1,
Transformers 5.12.1, Tokenizers 0.22.2, Hugging Face Hub 1.16.0, XGrammar
0.2.1, LLGuidance 1.7.5, Apache TVM FFI 0.1.10, and timm 1.0.28. Only timm
meets its selected version and remains a shared Base dependency.

`sglang-rpm-macros` 0.1.2 was built from the current SPEC and passed all 37
`%check` tests. The dependency rewriter now removes installer extras from RPM
distribution capabilities. Mistral Common declares `pydantic-extra-types` and
`pycountry` separately because Base RPM metadata does not provide an extras
capability.

Transformers 5.19.0 matched the source SHA256 in its SPEC:
`87f38dd25e4521151b97e94520ac457f44a0ae8a8358a5b112daff6c64a822d6`. Its
RISC-V RPM passed the SPEC import checks and an offline BERT `AutoConfig` smoke;
its header provides the private Transformers capability and contains no
`rpmlib(Shortcircuited)`. RPM SHA256:
`ba9ace3b5ec4bb603d11eab510061b076ffd326df0ac51a8ef6be92ca507ee9f`. SRPM
SHA256: `755910996dbe6bfc0a9dd88e464955a2d122c17c20abb692b2ac7bbf0cc2221b`.

Mistral Common 1.12.0 source and license matched their SPEC SHA256 values
`d0f150926733cf422d4750ca19b47568df1f714557c9054a432b866f1f30bf52` and
`5ed6f79e77734b5a60740dd821af5ecac9a6f33709c860eea4e20fcb6cca7fcc`. Its
RISC-V `%check` imported all modules. After an isolated install,
`MistralTokenizer`, `Tekkenizer`, and the `pycountry` runtime check passed.
RPM SHA256: `06fe35306dde27f62f39967a408fdb357ccc80e44859db07b9484a281db1c3d4`.
SRPM SHA256: `fb69b3eedc43241acd500737d0c1ac53e13fe6d967103a20be66d46f9d0e96d0`.
An isolated RPM transaction dry-run passed. These results cover these Python
providers only, not SGLang.

The SGLang v0.5.21 archive downloaded in the guest matched its SPEC SHA256
`c44951b7871dac61262fc04e9fca628175758a97fa5f603c522b31dc31b94249`. The
current CPU SPEC `%prep` applied the RISC-V patch and generated its patched
project metadata. After installing Base `python-setuptools-scm` into the
isolated root, `%generate_buildrequires` completed. The local DNF solver ran
with all repositories disabled and still failed, so no SGLang RPM was built.

Unresolved private SGLang providers are Torch CPU 2.14.0, TorchAudio 2.11.0,
TorchVision 0.29.0, Triton 3.8.0, SGLang CPU kernel 0.4.7, XGrammar 0.2.7,
LLGuidance 1.7.6 or newer below 2, TorchCodec 0.12.0, and SMG gRPC Servicer
0.9 or newer. Base has lower versions for Torch, TorchVision, Triton,
XGrammar, LLGuidance, and Apache TVM FFI. Base Torchaudio does not provide the
private SGLang capability.

The same local solver reported public Python requirements missing from the
current isolated RPM database, including aiohttp, compressed-tensors, datasets,
easydict, einops, gguf, interegular, ipython, modelscope, msgspec, orjson,
outlines, partial-json-parser, psutil, py-spy, pybase64, pytest,
python-multipart, scipy, setproctitle, tabulate, uvloop, xxhash, zstandard,
Blobfile 3.2+, OpenAI 2.40+, OpenAI Harmony 0.0.8+, Anthropic, Prometheus
Client, PyZMQ, SentencePiece 0.2.1, SoundFile 0.13.1, and timm 1.0.28. All
repositories were disabled during this check, so this list does not establish
that each public dependency is absent from Base. A separate Base metadata
query confirms timm 1.0.28 is available.

Build artifacts and logs are staged under
`/private/tmp/openruyi-build/offline-sglang-build/ARTIFACTS`. A complete
SGLang RPM transaction, SGLang import, CPU engine startup, coexistence test
against installed Base software, and `/generate` inference remain unverified.
CUDA and ROCm remain reserved non-buildable flavors.

## Reconnected QEMU guest and private import recheck (2026-10-27)

The user-authorized RVA23 guest is reachable at `127.0.0.1:22025` using the
existing SSH key. It reports `openruyi-sglang`, kernel `7.2.6-1.0_555.1.or`,
`riscv64`, system Python 3.13.8, and RPM 6.0.1. Port `12055` is closed;
`22024` reaches a different 2026.06 guest with Python 3.13.8/RPM 4.20.1 and
insufficient disk space, so it was not used for package validation.

The existing isolated buildroot contained Python 3.14.7/RPM 6.0.1 and the
macros, Click 8.4.2, Hugging Face Hub 1.31.0, Tokenizers 0.23.2, Transformers
5.19.0, and Mistral Common 1.12.0 RPMs. With the private `LD_LIBRARY_PATH`
and `PYTHONPATH` set, Python 3.14 imported all five modules and reported those
versions. Transformers warned that PyTorch was unavailable. Torch, Triton,
XGrammar, LLGuidance, and SGLang were absent, so this remains a provider import
smoke, not an SGLang import or engine test.

A cache-only Base solver plan showed CMake 4.3.2, LLVM 22.1.8, Ninja, and
Python 3.14 development files could be installed into that isolated root, but
XGrammar still lacks its exact private Torch 2.14.0 and Apache TVM FFI >=
0.1.11 providers. No build tools were installed and no additional RPM was
built. The private buildroot was removed after confirming no build process was
running; guest root free space increased from 4.1 GiB to 5.7 GiB. Existing
RPM/SRPM artifacts, source archives, and logs remain in host staging. The
guest's system RPM database was not used for installation.

The complete SGLang RPM transaction, `import sglang`, CPU engine startup,
coexistence test, and `/generate` inference remain unverified. CUDA and ROCm
remain reserved non-buildable flavors.

## Python ABI capability isolation (2026-10-28)

A read-only review of OpenRuyi's Python RPM generators confirmed that generic
`python3dist(NAME)` capabilities can be supplied by the default Python minor
version and do not identify the interpreter that can import the files. The
private SGLang Python tree therefore now uses the configured
`%{_sglang_private_python}` ABI in generated and hand-written Python
capabilities. In the current candidate this resolves to
`python3.14dist(NAME)`. Private Python Provides are normalized the same way,
including generated major-version aliases. Build requirements for the versioned
interpreter development metadata use `pkgconfig(python-3.14)`, matching the
versioned `.pc` file shipped by the repository's `python314` flavor.

Private native-library capabilities now use
`sglang(python3.14elf(SONAME))`. This prevents a private Torch or extension
library built for another Python ABI from satisfying the SGLang transaction.
System SONAME dependencies remain ordinary global ELF requirements. The
`timm` 1.0.28 provider is selected from the private SGLang tree so its imports
and Torch dependency use the same ABI. The SGLang SPEC also records Transformers
5.19.0 as a downstream compatibility selection; upstream v0.5.21's CPU
metadata pins 5.12.1.

The regression suite now has 40 cases, including a scan of all 33 private
SGLang package SPECs for generic Python capabilities. All 40 passed on the host
and in the user-authorized QEMU guest (`riscv64` RVA23, Python 3.13.8, RPM
6.0.1). Host `rpmspec` expansion of the SGLang and Mistral Common recipes
confirmed Python 3.14-qualified requirements. The guest's 286-package RPM
database and Python 3.13.8 baseline remained unchanged; temporary test files
were removed and 5.6 GiB remained free.

This validates the dependency capability rules and the target-side regression
suite, not a newly built macro RPM. The guest has no `rpmbuild` or Python 3.14
interpreter, and its enabled Base repository metadata returned no `rpm-build`
candidate. Staged artifacts still lack Torch 2.14.0, Triton 3.8.0 and the
remaining private provider RPM/SRPM closure. A full RPM transaction, SGLang
import, CPU engine startup, coexistence check, and `/generate` inference are
still unverified.

## RVA23 regression rerun (2026-10-28)

The current 43-case `test_sglang_deps.py` suite passed in the local
openRuyi Creek QEMU guest: `python3 -m unittest -v test_sglang_deps.py`
reported `Ran 43 tests in 22.155s` and `OK`. The target was `riscv64` on
QEMU 11.1.1 with the RVA23 CPU, kernel `7.2.6-1.0_555.1.or`, Python 3.13.8,
and RPM 6.0.1. This rerun supersedes the 40-case count above and exercises
capability rewriting, private Python/ELF ABI checks, RPM closure helpers, and
the current SPEC scan.

The guest still has 286 installed RPMs and no `python3.14`, `rpmbuild`, or
`sglang` command. The available offline build staging contains Click 8.4.2,
Hugging Face Hub 1.31.0, Tokenizers 0.23.2, Mistral Common 1.12.0,
Transformers 5.19.0, and `sglang-rpm-macros` 0.1.2 RPMs, plus a SGLang
build-requirements metadata RPM. It contains no SGLang binary RPM and no
selected private Torch CPU 2.14.0, Torchaudio 2.11.0, TorchVision 0.29.0,
Triton 3.8.0, SGLang CPU kernel 0.4.7, XGrammar 0.2.7, LLGuidance 1.7.6,
TorchCodec 0.12.0, or SMG gRPC provider RPMs. The complete RPM transaction was
therefore not attempted.

No SGLang import, CPU engine startup, `/health`, `/generate`, or coexistence
transaction was run in this rerun. The recipe's existing offline dummy-weight
CPU smoke does exercise engine startup and one generated token without model
weights, but it still requires the complete runtime RPM closure and installed
SGLang launchers. The 43 passing tests validate dependency rules and regression
helpers only; they do not establish a complete SGLang installation or working
inference engine. The guest RPM database remained unchanged.

The QEMU RPM transaction harness was updated to require versioned private
Python capabilities (`python3.14dist(...)`) for the selected provider set and
to recognize versioned CUDA/ROCm flavor capabilities when rejecting reserved
candidates. `bash -n` passed on the host and Linux RPM VM. The host `pre-commit`
run could not initialize its external hook checkout because DNS resolution for
`github.com` failed; no pre-commit hook changes were applied.

The Torch compatibility recipe's explicit private SONAME Provides now use the
same ABI-qualified form as the generated ELF attributes,
`sglang(python3.14elf(SONAME))`; this keeps the Torch provider and SGLang
native-extension requirements on one Python ABI.

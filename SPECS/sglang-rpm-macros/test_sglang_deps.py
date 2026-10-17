# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-License-Identifier: MulanPSL-2.0
"""Regression tests for the SGLang RPM dependency generators."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent


def load_helper(filename: str):
    path = ROOT / filename
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DISTDEPS = load_helper("sglangdistdeps.py")
ELFDEPS = load_helper("sglang-elfdeps.py")
CLOSURE = load_helper("check_sglang_rpm_closure.py")


class SglangDependencyTests(unittest.TestCase):
    def run_generator(self, helper: Path, generator_output: str, arguments: list[str],
                      stdin: str = "", status: int = 0):
        """Run a helper against a real executable fake generator."""
        with tempfile.TemporaryDirectory() as temporary:
            fake = Path(temporary) / "fake-generator.py"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import os, sys\n"
                "sys.stderr.write('fake generator stderr\\n')\n"
                "payload = sys.stdin.read()\n"
                "expected = os.environ.get('FAKE_GENERATOR_EXPECTED_STDIN')\n"
                "if expected is not None and payload != expected:\n"
                "    sys.stderr.write('stdin was not forwarded\\n')\n"
                "    raise SystemExit(91)\n"
                "sys.stdout.write(os.environ['FAKE_GENERATOR_OUTPUT'])\n"
                "raise SystemExit(int(os.environ['FAKE_GENERATOR_STATUS']))\n"
            )
            fake.chmod(0o755)
            environment = os.environ.copy()
            environment["FAKE_GENERATOR_OUTPUT"] = generator_output
            environment["FAKE_GENERATOR_STATUS"] = str(status)
            if stdin:
                environment["FAKE_GENERATOR_EXPECTED_STDIN"] = stdin
            return subprocess.run(
                [sys.executable, str(helper), "--generator", str(fake), *arguments],
                input=stdin,
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )

    def test_python_requirements_keep_base_runtime_global(self):
        requirements = "\n".join((
            "python(abi) >= 3.13",
            "python3dist(numpy) >= 2",
            "python3dist(torch) >= 2",
            "python3dist(sglang-kernel) = 0.4.7",
            "python3dist(fsspec)",
            "python3dist(scikit-build-core)",
        ))
        core = DISTDEPS._namespace_requirements(requirements, "core")
        extras = DISTDEPS._rewrite_capabilities(
            requirements,
            "extras",
            private_dists=frozenset({"scikit-build-core"}),
        )

        self.assertIn("python(abi) >= 3.13", core)
        self.assertIn("python3dist(numpy) >= 2", core)
        self.assertIn("sglang(python3dist(torch)) >= 2", core)
        self.assertIn("sglang(python3dist(sglang-kernel)) = 0.4.7", core)
        self.assertIn("python3dist(fsspec)", core)
        self.assertIn("sglang-extras(python3dist(fsspec))", extras)
        self.assertIn("sglang(python3dist(torch)) >= 2", extras)
        self.assertIn("sglang(python3dist(sglang-kernel)) = 0.4.7", extras)
        self.assertIn("sglang(python3dist(scikit-build-core))", extras)
        self.assertNotIn("sglang(python(abi))", extras)
        self.assertNotIn("sglang(python3dist(numpy))", extras)

    def test_torch_flavor_capabilities_follow_package_name(self):
        for package_name, flavor in (
            ("python-torch-sglang-2.14", "cpu"),
            ("python-torch-sglang-2.14-rocm", "rocm"),
            ("python-sglang-cuda", "cuda"),
            ("python-sglang-kernel", "cuda"),
        ):
            with self.subTest(package_name=package_name):
                rewritten = DISTDEPS._rewrite_capabilities(
                    "python3.14dist(torch) >= 2.14\n"
                    "python3dist(torch) = 2.14",
                    "core",
                    torch_flavor=DISTDEPS._torch_flavor(package_name),
                )
                self.assertEqual(
                    rewritten,
                    f"sglang(python3.14dist(torch-{flavor})) >= 2.14\n"
                    f"sglang(python3dist(torch-{flavor})) = 2.14",
                )

    def test_transformers_closure_uses_private_providers_in_both_profiles(self):
        # A system provider must not satisfy the newer private stack's
        # requirements, including normalized distribution names and extras.
        requirements = "\n".join((
            "python3dist(transformers) = 5.19",
            "python3dist(tokenizers) >= 0.23.1",
            "python3dist(huggingface_hub) >= 1.31",
            "python3dist(click) >= 8.4.2",
            "python3dist(huggingface-hub[cli]) < 3",
            "python3dist(packaging) >= 20",
            "python3dist(safetensors) >= 0.8",
        ))
        for profile in ("core", "extras"):
            with self.subTest(profile=profile):
                output = DISTDEPS._namespace_requirements(requirements, profile)
                self.assertEqual(output, "\n".join((
                    "sglang(python3dist(transformers)) = 5.19",
                    "sglang(python3dist(tokenizers)) >= 0.23.1",
                    "sglang(python3dist(huggingface_hub)) >= 1.31",
                    "sglang(python3dist(click)) >= 8.4.2",
                    "sglang(python3dist(huggingface-hub[cli])) < 3",
                    "python3dist(packaging) >= 20",
                    "python3dist(safetensors) >= 0.8",
                )))

    def test_timm_is_private_and_uses_cpu_torch_provider(self):
        requires = DISTDEPS._namespace_requirements(
            "python3dist(timm) >= 1.0.28",
            "core",
            torch_flavor="cpu",
        )
        self.assertEqual(requires, "sglang(python3dist(timm)) >= 1.0.28")

        torch_requires = DISTDEPS._namespace_requirements(
            "python3dist(torch) >= 2.0",
            "core",
            torch_flavor="cpu",
        )
        self.assertEqual(
            torch_requires,
            "sglang(python3dist(torch-cpu)) >= 2.0",
        )

    def test_python_subprocess_protocol_preserves_status_and_stderr(self):
        output = "\n".join((
            "python(abi) = 3.13",
            "python3dist(numpy) >= 2",
            "python3dist(torch) >= 2",
            "python3dist(fsspec)",
        ))
        result = self.run_generator(
            ROOT / "sglangdistdeps.py",
            output,
            [
                "--profile", "extras", "--namespace", "sglang-extras",
                "--private-dists", "scikit-build-core", "--requires",
            ],
            stdin="metadata sent to generator\n",
            status=17,
        )

        self.assertEqual(result.returncode, 17)
        self.assertEqual(result.stderr, "fake generator stderr\n")
        self.assertIn("python(abi) = 3.13", result.stdout)
        self.assertIn("python3dist(numpy) >= 2", result.stdout)
        self.assertIn("sglang(python3dist(torch)) >= 2", result.stdout)
        self.assertIn("sglang-extras(python3dist(fsspec))", result.stdout)

    def test_python_short_generator_option_is_accepted(self):
        result = self.run_generator(
            ROOT / "sglangdistdeps.py",
            "python3dist(torch) = 2.14\n",
            [
                "--profile", "core", "--namespace", "sglang",
                "--package-name", "python-torch-sglang-2.14", "-P",
            ],
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "fake generator stderr\n")
        self.assertIn("sglang(python3dist(torch-cpu)) = 2.14", result.stdout)

    def test_elf_provides_namespace_arbitrary_private_soname(self):
        result = self.run_generator(
            ROOT / "sglang-elfdeps.py",
            "; /buildroot/usr/lib/sglang/extras/lib/libprovider.so\n"
            "libarbitrary_backend.so.1\n",
            [
                "--profile", "extras", "--namespace", "sglang-extras",
                "--provides", "--multifile",
            ],
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "fake generator stderr\n")
        self.assertIn("; /buildroot/usr/lib/sglang/extras/lib/libprovider.so", result.stdout)
        self.assertIn("sglang-extras(libarbitrary_backend.so.1)", result.stdout)

    def test_elf_requires_namespace_known_torch_but_keep_system_libc_global(self):
        result = self.run_generator(
            ROOT / "sglang-elfdeps.py",
            "; /buildroot/usr/lib/sglang/extras/lib/libconsumer.so\n"
            "libtorch_cpu.so.2\n"
            "libarbitrary_backend.so.1\n"
            "libc.so.6\n"
            "libomp.so.5\n",
            [
                "--profile", "extras", "--namespace", "sglang-extras",
                "--requires", "--multifile",
            ],
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("sglang(libtorch_cpu.so.2)", result.stdout)
        self.assertIn("libarbitrary_backend.so.1", result.stdout)
        self.assertIn("libc.so.6", result.stdout)
        self.assertIn("libomp.so.5", result.stdout)
        self.assertNotIn("sglang(libomp.so.5)", result.stdout)
        self.assertNotIn("sglang-extras(libomp.so.5)", result.stdout)
        self.assertNotIn("sglang-extras(libtorch_cpu.so.2)", result.stdout)

    def test_elf_provides_namespace_system_soname_collisions(self):
        result = self.run_generator(
            ROOT / "sglang-elfdeps.py",
            "; /buildroot/usr/lib/sglang/extras/lib/libprovider.so\n"
            "libarbitrary_backend.so.1\n"
            "libc.so.6(GLIBC_2.39)(64bit)\n"
            "libm.so.6\n"
            "libomp.so.5\n"
            "libnuma.so.1\n"
            "libopenblas64.so.0\n"
            "libblas.so.3\n"
            "liblapack.so.3\n",
            [
                "--profile", "extras", "--namespace", "sglang-extras",
                "--provides", "--multifile",
            ],
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("sglang-extras(libarbitrary_backend.so.1)", result.stdout)
        for capability in (
            "libc.so.6(GLIBC_2.39)(64bit)", "libm.so.6", "libomp.so.5",
            "libnuma.so.1", "libopenblas64.so.0", "libblas.so.3", "liblapack.so.3",
        ):
            self.assertIn(f"sglang-extras({capability})", result.stdout)
        self.assertNotIn("\nlibomp.so.5\n", result.stdout)

    def test_elf_requires_private_sonames_only(self):
        result = self.run_generator(
            ROOT / "sglang-elfdeps.py",
            "; /buildroot/usr/lib/sglang/extras/lib/private.so\n"
            "libarbitrary_backend.so.1\n"
            "libtorch_cpu.so.2\n"
            "libnuma.so.1\n",
            [
                "--profile", "extras", "--namespace", "sglang-extras",
                "--requires", "--multifile",
            ],
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("libarbitrary_backend.so.1", result.stdout)
        self.assertIn("sglang(libtorch_cpu.so.2)", result.stdout)
        self.assertIn("libnuma.so.1", result.stdout)
        self.assertNotIn("sglang-extras(libarbitrary_backend.so.1)", result.stdout)

    def test_elf_requires_reset_private_marker_between_files(self):
        result = self.run_generator(
            ROOT / "sglang-elfdeps.py",
            "; /buildroot/usr/lib/sglang/extras/lib/private.so\n"
            "libtorch_cpu.so.2\n"
            "; /buildroot/usr/lib/other/lib/system.so\n"
            "libtorch_cpu.so.3\n",
            [
                "--profile", "extras", "--namespace", "sglang-extras",
                "--requires", "--multifile",
            ],
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("sglang(libtorch_cpu.so.2)", result.stdout)
        self.assertIn("libtorch_cpu.so.3", result.stdout)
        self.assertNotIn("sglang(libtorch_cpu.so.3)", result.stdout)
        self.assertNotIn("sglang-extras(libtorch_cpu.so.3)", result.stdout)

    def test_elf_requires_reject_profile_mismatch(self):
        result = self.run_generator(
            ROOT / "sglang-elfdeps.py",
            "; /buildroot/usr/lib/sglang/core/lib/libconsumer.so\n"
            "libtorch_cpu.so.2\n",
            [
                "--profile", "extras", "--namespace", "sglang-extras",
                "--requires", "--multifile",
            ],
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("libtorch_cpu.so.2", result.stdout)
        self.assertNotIn("sglang(libtorch_cpu.so.2)", result.stdout)
        self.assertNotIn("sglang-extras(libtorch_cpu.so.2)", result.stdout)

    def test_elf_provides_reject_profile_mismatch(self):
        result = self.run_generator(
            ROOT / "sglang-elfdeps.py",
            "; /buildroot/usr/lib/sglang/core/lib/libprovider.so\n"
            "libarbitrary_backend.so.1\n",
            [
                "--profile", "extras", "--namespace", "sglang-extras",
                "--provides", "--multifile",
            ],
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("libarbitrary_backend.so.1", result.stdout)
        self.assertNotIn("sglang-extras(libarbitrary_backend.so.1)", result.stdout)

    def test_rpm_closure_matches_namespaced_capability_names(self):
        packages = (
            CLOSURE.RpmMetadata(
                Path("core.rpm"),
                ("sglang(libtorch_cpu.so.2)",),
                ("sglang(libtorch_cpu.so.2)", "libc.so.6"),
            ),
        )

        self.assertEqual(
            CLOSURE.unresolved_requirements(
                packages, only_namespaces=("sglang",)
            ),
            (),
        )

    def test_rpm_closure_can_use_separate_provider_rpms(self):
        targets = (
            CLOSURE.RpmMetadata(
                Path("extras.rpm"),
                (),
                ("sglang(libtorch_cpu.so.2)",),
            ),
        )
        providers = (
            CLOSURE.RpmMetadata(
                Path("torch.rpm"),
                ("sglang(libtorch_cpu.so.2)",),
                (),
            ),
        )

        self.assertEqual(
            CLOSURE.unresolved_requirements(
                targets,
                provider_packages=providers,
                only_namespaces=("sglang",),
            ),
            (),
        )

    def test_rpm_closure_queries_rpm_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            fake_rpm = temporary_path / "rpm"
            fake_rpm.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                "if '--provides' in sys.argv:\n"
                "    print('sglang(libprivate.so.1)')\n"
                "elif '--requires' in sys.argv:\n"
                "    print('sglang(libprivate.so.1)')\n"
                "else:\n"
                "    raise SystemExit(2)\n"
            )
            fake_rpm.chmod(0o755)
            package = temporary_path / "private.rpm"
            package.touch()

            metadata = CLOSURE.read_metadata(str(fake_rpm), package, "/tmp/rpm-db")

        self.assertEqual(metadata.provides, ("sglang(libprivate.so.1)",))
        self.assertEqual(metadata.requires, ("sglang(libprivate.so.1)",))

    def test_rpm_closure_reports_missing_namespaced_capability(self):
        packages = (
            CLOSURE.RpmMetadata(
                Path("extras.rpm"),
                ("sglang-extras(libprivate.so.1)",),
                (
                    "sglang(libtorch_cpu.so.2)",
                    "sglang-extras(libmissing.so.1)",
                ),
            ),
        )

        unresolved = CLOSURE.unresolved_requirements(
            packages, only_namespaces=("sglang", "sglang-extras")
        )
        self.assertEqual(
            unresolved,
            ((Path("extras.rpm"), "sglang(libtorch_cpu.so.2)"),
             (Path("extras.rpm"), "sglang-extras(libmissing.so.1)")),
        )

    def test_rpm_closure_allows_explicit_base_capability(self):
        packages = (
            CLOSURE.RpmMetadata(
                Path("extras.rpm"),
                (),
                ("sglang-extras(libmissing.so.1)",),
            ),
        )

        self.assertEqual(
            CLOSURE.unresolved_requirements(
                packages,
                only_namespaces=("sglang-extras",),
                allow_patterns=("sglang-extras(libmissing.so.1)",),
            ),
            (),
        )

    def test_rpm_inventory_marks_versioned_requirements_unverified(self):
        packages = (
            CLOSURE.RpmMetadata(
                Path("core.rpm"),
                ("sglang(python3dist(torch)) = 2.14.0",),
                ("sglang(python3dist(torch)) >= 2.14.0",),
            ),
        )

        self.assertEqual(
            CLOSURE.unresolved_requirements(
                packages, only_namespaces=("sglang",)
            ),
            (),
        )
        self.assertEqual(
            CLOSURE.unverified_requirements(
                packages, only_namespaces=("sglang",)
            ),
            ((Path("core.rpm"), "sglang(python3dist(torch)) >= 2.14.0"),),
        )

    def test_rpm_inventory_does_not_skip_rich_namespaced_requirements(self):
        packages = (
            CLOSURE.RpmMetadata(
                Path("core.rpm"),
                ("sglang(python3dist(foo)) = 1", "sglang(python3dist(bar)) = 2"),
                ("(sglang(python3dist(foo)) >= 1 with sglang(python3dist(bar)) < 3)",),
            ),
        )

        self.assertEqual(
            CLOSURE.unverified_requirements(
                packages, only_namespaces=("sglang",)
            ),
            ((
                Path("core.rpm"),
                "(sglang(python3dist(foo)) >= 1 with sglang(python3dist(bar)) < 3)",
            ),),
        )

    def test_rpm_inventory_exit_status_is_nonzero_for_unverified(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            fake_rpm = temporary_path / "rpm"
            fake_rpm.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                "if '--provides' in sys.argv:\n"
                "    print('sglang(foo) = 1')\n"
                "elif '--requires' in sys.argv:\n"
                "    print('sglang(foo) >= 1')\n"
                "else:\n"
                "    raise SystemExit(2)\n"
            )
            fake_rpm.chmod(0o755)
            package = temporary_path / "private.rpm"
            package.touch()

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "check_sglang_rpm_closure.py"),
                    "--namespace", "sglang",
                    "--rpm-command", str(fake_rpm),
                    str(package),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("UNVERIFIED", result.stdout)
        self.assertNotIn("closure: complete", result.stdout)

    def test_rpm_inventory_reports_missing_rpm_executable(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "private.rpm"
            package.touch()
            with self.assertRaisesRegex(RuntimeError, "rpm executable not found"):
                CLOSURE.read_metadata("missing-rpm-command", package)


if __name__ == "__main__":
    unittest.main()

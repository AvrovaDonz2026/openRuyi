# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
#
# SPDX-File-AttributionText: Sponsored by cha86.dev <https://cha86.dev>
# SPDX-License-Identifier: MulanPSL-2.0
"""Regression tests for the SGLang RPM dependency generators."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent
SYSTEM_SONAMES = (
    "libc.so.6", "libcpuinfo.so.0", "libomp.so.5", "libpthreadpool.so.0", "libuv.so.1",
    "libpython3.13.so.1.0", "libunwind.so.8", "libtinfo.so.6", "libxml2.so.2",
    "libtiff.so.6", "libfreetype.so.6", "liblcms2.so.2", "libssl.so.3", "libcrypto.so.3",
    "libavcodec.so.60", "libavdevice.so.60", "libavfilter.so.9", "libavformat.so.60",
    "libavutil.so.58", "libswresample.so.4", "libswscale.so.7", "libgfortran.so.5",
    "libmvec.so.1", "libjpeg.so.62",
    "libpng16.so.16", "libwebp.so.7", "libwebpdecoder.so.3", "libwebpdemux.so.2", "libwebpmux.so.3",
    "libsharpyuv.so.0", "libfmt.so.10", "libgtest.so.1.17.0", "libgmock.so.1.17.0",
    "libsleef.so.3", "libsleefgnuabi.so.3",
    "libsleefdft.so.3", "libsleefquad.so.3", "libonnx.so.1", "libonnx_proto.so.1",
    "libonnxruntime.so.1", "libonnxruntime_providers_shared.so.1", "libfoxi_loader.so.1",
    "libprotobuf.so.32", "libprotobuf-lite.so.32", "libabsl_strings.so.2407",
    "libutf8_validity.so.0", "libutf8_range_lib.so.0", "libupb.so.1",
)


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
PRIVATE_PATHS = load_helper("sglang_private_paths.py")


class SglangDependencyTests(unittest.TestCase):
    def test_private_install_rewrites_python_entrypoint_shebangs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "env-entrypoint").write_bytes(b"#!/usr/bin/env python3 -s\nprint(1)\n")
            (root / "absolute-entrypoint").write_bytes(b"#!/usr/bin/python3.13\nprint(2)\n")
            (root / "shell-script").write_bytes(b"#!/bin/sh\nprintf ok\n")

            PRIVATE_PATHS.rewrite_python_shebangs(root, "/usr/bin/python3.14")

            self.assertEqual(
                (root / "env-entrypoint").read_bytes(),
                b"#!/usr/bin/python3.14 -s\nprint(1)\n",
            )
            self.assertEqual(
                (root / "absolute-entrypoint").read_bytes(),
                b"#!/usr/bin/python3.14\nprint(2)\n",
            )
            self.assertEqual(
                (root / "shell-script").read_bytes(),
                b"#!/bin/sh\nprintf ok\n",
            )

    def test_private_install_resolves_shebang_tree_inside_buildroot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private = root / "usr/lib64/sglang/core/python3.14/site-packages"
            private.mkdir(parents=True)
            entrypoint = private / "tool.py"
            entrypoint.write_bytes(b"#!/usr/bin/python3\nprint(1)\n")

            PRIVATE_PATHS.rewrite_python_shebangs(
                PRIVATE_PATHS.buildroot_path(root, "/usr/lib64/sglang/core/python3.14/site-packages"),
                "/usr/bin/python3.14",
            )

            self.assertEqual(
                entrypoint.read_bytes(),
                b"#!/usr/bin/python3.14\nprint(1)\n",
            )

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
            "python3dist(sglang-kernel-cpu) = 0.4.7",
            "python3dist(fsspec)",
            "python3dist(msgspec)",
            "python3dist(partial-json-parser)",
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
        self.assertIn("sglang(python3dist(sglang-kernel-cpu)) = 0.4.7", core)
        self.assertIn("python3dist(fsspec)", core)
        self.assertIn("python3dist(msgspec)", core)
        self.assertIn("python3dist(partial-json-parser)", core)
        self.assertIn("sglang-extras(python3dist(fsspec))", extras)
        self.assertIn("python3dist(msgspec)", extras)
        self.assertIn("python3dist(partial-json-parser)", extras)
        self.assertIn("sglang(python3dist(torch)) >= 2", extras)
        self.assertIn("sglang(python3dist(sglang-kernel)) = 0.4.7", extras)
        self.assertIn("sglang(python3dist(sglang-kernel-cpu)) = 0.4.7", extras)
        self.assertIn("sglang(python3dist(scikit-build-core))", extras)
        self.assertNotIn("sglang(python(abi))", extras)
        self.assertNotIn("sglang(python3dist(numpy))", extras)

    def test_python_capabilities_collapse_nested_private_namespaces(self):
        requirements = "\n".join((
            "sglang(sglang(python3dist(torch))) >= 2",
            "sglang(sglang-extras(python3dist(fsspec)))",
        ))
        self.assertEqual(
            DISTDEPS._rewrite_capabilities(
                requirements,
                "extras",
                provides=True,
                default_namespace="sglang-extras",
            ),
            "\n".join((
                "sglang(python3dist(torch)) >= 2",
                "sglang-extras(python3dist(fsspec))",
            )),
        )

    def test_torch_flavor_capabilities_follow_package_name(self):
        for package_name, flavor in (
            ("python-torch-sglang-2.14", "cpu"),
            ("python-torch-sglang-2.14-rocm", "rocm"),
            ("python-sglang-cuda", "cuda"),
            ("python-sglang-kernel", "cuda"),
            ("python-torch-sglang-2.14-cuda", "cuda"),
            ("python-widget-cuda", "cuda"),
            ("python-widget-rocm", "rocm"),
            ("python-torch-sglang-2.14-CUDA", "cuda"),
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

    def test_torch_flavor_rewrites_extras(self):
        rewritten = DISTDEPS._rewrite_capabilities(
            "python3dist(torch[cuda]) >= 2.14\n"
            "python3.14dist(torch[rocm,foo]) = 2.14\n"
            "sglang(python3dist(torch[cuda]))",
            "core",
            torch_flavor="cpu",
        )
        self.assertEqual(
            rewritten,
            "sglang(python3dist(torch-cpu)) >= 2.14\n"
            "sglang(python3.14dist(torch-cpu)) = 2.14\n"
            "sglang(python3dist(torch-cpu))",
        )

    def test_selected_system_dependencies_remain_global_in_both_profiles(self):
        requirements = "\n".join((
            "python3dist(transformers) = 5.12.1",
            "python3dist(timm) = 1.0.28",
            "python3dist(tokenizers) >= 0.23.1",
            "python3dist(huggingface_hub) >= 1.31",
            "python3dist(click) >= 8.4.2",
            "python3dist(huggingface-hub[cli]) < 3",
            "python3dist(packaging) >= 20",
            "python3dist(safetensors) >= 0.8",
        ))
        for profile in ("core", "extras"):
            with self.subTest(profile=profile):
                output = DISTDEPS._namespace_requirements(
                    requirements,
                    profile,
                    shared_dists=frozenset(("transformers", "timm")),
                )
                self.assertEqual(output, "\n".join((
                    "python3dist(transformers) = 5.12.1",
                    "python3dist(timm) = 1.0.28",
                    "sglang(python3dist(tokenizers)) >= 0.23.1",
                    "sglang(python3dist(huggingface_hub)) >= 1.31",
                    "sglang(python3dist(click)) >= 8.4.2",
                    "sglang(python3dist(huggingface-hub[cli])) < 3",
                    "python3dist(packaging) >= 20",
                    "python3dist(safetensors) >= 0.8",
                )))

    def test_shared_dependency_requires_do_not_change_private_provides(self):
        rewritten = DISTDEPS._rewrite_capabilities(
            "python3dist(transformers) = 5.12.1",
            "core",
            provides=True,
            default_namespace="sglang",
            shared_dists=frozenset(("transformers",)),
        )
        self.assertEqual(
            rewritten,
            "sglang(python3dist(transformers)) = 5.12.1",
        )

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
            "python3dist(transformers) = 5.12.1",
            "python3dist(fsspec)",
        ))
        result = self.run_generator(
            ROOT / "sglangdistdeps.py",
            output,
            [
                "--profile", "extras", "--namespace", "sglang-extras",
                "--private-dists", "scikit-build-core",
                "--shared-dists", "transformers", "--requires",
            ],
            stdin="metadata sent to generator\n",
            status=17,
        )

        self.assertEqual(result.returncode, 17)
        self.assertEqual(result.stderr, "fake generator stderr\n")
        self.assertIn("python(abi) = 3.13", result.stdout)
        self.assertIn("python3dist(numpy) >= 2", result.stdout)
        self.assertIn("sglang(python3dist(torch)) >= 2", result.stdout)
        self.assertIn("python3dist(transformers) = 5.12.1", result.stdout)
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

    def test_pyproject_wrappers_force_offline_cargo(self):
        macros = (ROOT / "macros.sglang").read_text()
        self.assertEqual(macros.count("export CARGO_NET_OFFLINE=true"), 2)
        self.assertEqual(macros.count("export PIP_NO_INDEX=1"), 2)
        self.assertIn(
            'export CARGO_NET_OFFLINE=true\n  export PIP_NO_INDEX=1\n  %%pyproject_wheel',
            macros,
        )
        self.assertIn(
            'export CARGO_NET_OFFLINE=true\n  export PIP_NO_INDEX=1\n  %%pyproject_buildrequires',
            macros,
        )

    def test_pyproject_wrappers_use_private_python_abi_and_torch_prefix(self):
        macros = (ROOT / "macros.sglang").read_text()
        self.assertIn("%%global __python3 %%{_sglang_private_interpreter}", macros)
        for export in (
            'export PYTHON_EXECUTABLE="%{_sglang_private_interpreter}"',
            'export Python_INCLUDE_DIR="%{_sglang_private_include}"',
            'export CMAKE_PREFIX_PATH="%{_sglang_private_cmake_prefix}"',
        ):
            self.assertEqual(macros.count(export), 4)
        self.assertIn(
            "%_sglang_private_cmake_prefix %{_prefix}:%{_libdir}/cmake:%{_sglang_private_sitearch}/torch/share/cmake:%{_sglang_private_sitearch}",
            macros,
        )

    def test_check_import_wrapper_forwards_option_values(self):
        macros = (ROOT / "macros.sglang").read_text()
        self.assertIn(
            "%%pyproject_check_import %{?**}",
            macros,
        )

    def test_coexistence_private_probe_checks_shared_runtime_modules(self):
        source = (ROOT.parent / "python-sglang" / "sglang-coexistence-test.py").read_text()
        self.assertIn(
            'env["COEXIST_MODULES"] = json.dumps(MODULES)',
            source,
        )
        self.assertIn(
            'env["COEXIST_ALLOW_ABSENT"] = ",".join(sorted(SYSTEM_MODULES))',
            source,
        )

    def test_elf_exclude_path_covers_rpm6_buildroot_and_installed_paths(self):
        macros = (ROOT / "macros.sglang").read_text()
        line = next(
            item for item in macros.splitlines()
            if item.startswith("%%global __elf_exclude_path ")
        )
        expression = line.split(None, 2)[2].replace("\\\\", "\\")
        expression = expression.replace("[[:digit:]]", "[0-9]")
        expression = expression.replace("[[:alnum:]]", "[A-Za-z0-9]")
        path_pattern = re.compile(expression)
        for path in (
            "/usr/lib/sglang/core/lib/libtorch_cpu.so",
            "/usr/lib64/sglang/extras/python3.13/site-packages/torch/lib/libtorch_cpu.so",
            "/buildroot/usr/lib/sglang/core/lib/libtorch_cpu.so",
            "/buildroot/usr/lib64/sglang/extras/python3.13/site-packages/torch/lib/libtorch_cpu.so",
        ):
            with self.subTest(path=path):
                self.assertRegex(path, path_pattern)
        self.assertNotRegex(
            "/usr/lib/python3.13/site-packages/torch/lib/libtorch_cpu.so",
            path_pattern,
        )

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

    def test_elf_short_generator_options_are_accepted(self):
        for option, expected in (("-P", "sglang-extras(libarbitrary_backend.so.1)"),
                                 ("-R", "sglang-extras(libarbitrary_backend.so.1)")):
            with self.subTest(option=option):
                result = self.run_generator(
                    ROOT / "sglang-elfdeps.py",
                    "; /buildroot/usr/lib/sglang/extras/lib/libprovider.so\n"
                    "libarbitrary_backend.so.1\n",
                    [
                        "--profile", "extras", "--namespace", "sglang-extras",
                        option, "--multifile",
                    ],
                )

                self.assertEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_elf_attrs_cover_private_executables_in_python_trees(self):
        for profile in ("core", "extras"):
            with self.subTest(profile=profile):
                attr = ROOT / f"sglang_{profile}_elf.attr"
                line = next(
                    item for item in attr.read_text().splitlines()
                    if item.startswith(f"%__sglang_{profile}_elf_path ")
                )
                expression = line.split(None, 1)[1]
                expression = expression.replace("\\\\", "\\")
                expression = expression.replace("[[:digit:]]", "[0-9]")
                path_pattern = re.compile(expression)

                self.assertRegex(
                    f"/usr/lib64/sglang/{profile}/python3.13/site-packages/torch/bin/FileStoreTest",
                    path_pattern,
                )
                self.assertRegex(
                    f"/usr/lib/sglang/{profile}/lib/libtorch_cpu.so",
                    path_pattern,
                )
                self.assertNotRegex(
                    "/usr/lib64/python3.13/site-packages/torch/bin/FileStoreTest",
                    path_pattern,
                )

    def test_elf_requires_namespace_private_sonames_for_private_executable(self):
        result = self.run_generator(
            ROOT / "sglang-elfdeps.py",
            "; /buildroot/usr/lib64/sglang/core/python3.13/site-packages/torch/bin/FileStoreTest\n"
            "libtorch_cpu.so.2\n"
            "libstdc++.so.6\n",
            [
                "--profile", "core", "--namespace", "sglang",
                "--requires", "--multifile",
            ],
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("sglang(libtorch_cpu.so.2)", result.stdout)
        self.assertIn("libstdc++.so.6", result.stdout)
        self.assertNotIn("sglang(libstdc++.so.6)", result.stdout)

    def test_elf_requires_namespace_known_torch_but_keep_system_libc_global(self):
        generator_output = "\n".join((
            "; /buildroot/usr/lib/sglang/extras/lib/libconsumer.so",
            "libtorch_cpu.so.2",
            "libarbitrary_backend.so.1",
            *SYSTEM_SONAMES,
            "",
        ))
        result = self.run_generator(
            ROOT / "sglang-elfdeps.py",
            generator_output,
            [
                "--profile", "extras", "--namespace", "sglang-extras",
                "--requires", "--multifile",
            ],
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("sglang(libtorch_cpu.so.2)", result.stdout)
        self.assertIn("libarbitrary_backend.so.1", result.stdout)
        for capability in SYSTEM_SONAMES:
            self.assertIn(capability, result.stdout)
            self.assertNotIn(f"sglang({capability})", result.stdout)
            self.assertNotIn(f"sglang-extras({capability})", result.stdout)
        self.assertNotIn("sglang-extras(libomp.so.5)", result.stdout)
        self.assertNotIn("sglang-extras(libtorch_cpu.so.2)", result.stdout)

    def test_elf_system_sonames_are_global_and_private_sonames_are_namespaced(self):
        for capability in SYSTEM_SONAMES:
            with self.subTest(capability=capability):
                self.assertFalse(ELFDEPS._private(capability))

        for capability in ("libarbitrary_backend.so.1", "libsglang_backend.so.1"):
            with self.subTest(capability=capability):
                self.assertTrue(ELFDEPS._private(capability))

    def test_elf_protobuf_system_sonames_stay_global(self):
        result = self.run_generator(
            ROOT / "sglang-elfdeps.py",
            "; /buildroot/usr/lib/sglang/core/lib/libconsumer.so\n"
            "libutf8_validity.so.0\n"
            "libutf8_range_lib.so.0\n"
            "libupb.so.1\n"
            "libupb_message.so.1\n",
            [
                "--profile", "core", "--namespace", "sglang",
                "--requires", "--multifile",
            ],
        )

        self.assertEqual(result.returncode, 0)
        for capability in (
            "libutf8_validity.so.0", "libutf8_range_lib.so.0",
            "libupb.so.1", "libupb_message.so.1",
        ):
            with self.subTest(capability=capability):
                self.assertIn(capability, result.stdout)
                self.assertNotIn(f"sglang({capability})", result.stdout)
                self.assertFalse(ELFDEPS._private(capability))

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
        self.assertIn("sglang-extras(libarbitrary_backend.so.1)", result.stdout)
        self.assertIn("sglang(libtorch_cpu.so.2)", result.stdout)
        self.assertIn("libnuma.so.1", result.stdout)
        self.assertNotIn("\nlibarbitrary_backend.so.1\n", result.stdout)

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

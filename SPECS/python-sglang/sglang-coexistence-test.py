# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: A.Donz <avrova.minix@donz.si>
# SPDX-FileContributor: MMLA-org <https://github.com/MMLA-org>
# SPDX-License-Identifier: MIT
"""Check that the private SGLang Python root coexists with system packages."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import re


MODULES = (
    "torch", "transformers", "tokenizers", "huggingface_hub", "click",
    "numpy", "scipy", "fsspec", "datasets", "pandas", "PIL",
)
# These distributions remain shared with the base system.  Transformers,
# tokenizers, Hugging Face Hub and Click are private compatibility providers.
SYSTEM_MODULES = ("numpy", "scipy", "fsspec", "datasets", "pandas", "PIL")
BASELINE_MODULES = MODULES
DIST_NAMES = {
    "huggingface_hub": "huggingface-hub",
    "PIL": "Pillow",
}
PRIVATE_MODULE_VERSIONS = {
    "transformers": "5.19.0",
    "tokenizers": "0.23.2",
    "huggingface_hub": "1.31.0",
    "click": "8.4.2",
}
OPTIONAL_BASELINE_MODULES = frozenset(PRIVATE_MODULE_VERSIONS)
DEFAULT_ROOTS = (
    "/usr/lib64/sglang/core",
    "/usr/lib/sglang/core",
)
PROBE = r'''
import importlib
import importlib.metadata
import json
import os
import pathlib
import re
import sys

DIST_NAMES = {
    "huggingface_hub": "huggingface-hub",
    "PIL": "Pillow",
}
names = json.loads(os.environ["COEXIST_MODULES"])
private_module = os.environ.get("COEXIST_PRIVATE_MODULE")
if private_module:
    names = names + [private_module]
result = {"modules": {}, "torch": {}}
for name in names:
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError as exc:
        allowed = os.environ.get("COEXIST_ALLOW_ABSENT", "").split(",")
        missing_requested = exc.name == name or (exc.name or "").startswith(name + ".")
        if name not in allowed or not missing_requested:
            raise
        result["modules"][name] = {"absent": True}
        continue
    path = getattr(module, "__file__", None)
    if not path:
        raise RuntimeError("module has no __file__: " + name)
    try:
        version = importlib.metadata.version(DIST_NAMES.get(name, name))
    except importlib.metadata.PackageNotFoundError:
        version = getattr(module, "__version__", None)
    result["modules"][name] = {"version": version, "path": str(path)}

import torch
x = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float32)
result["torch"]["tensor_sum"] = float((x * 2).sum().item())
import torch.distributed as dist
result["torch"]["distributed"] = bool(dist.is_available())
result["torch"]["gloo"] = bool(dist.is_gloo_available())
try:
    from torch.distributed import Backend
    result["torch"]["backend"] = str(Backend.GLOO)
except Exception as exc:
    result["torch"]["backend_error"] = type(exc).__name__ + ": " + str(exc)

maps = pathlib.Path("/proc/self/maps")
result["native_paths"] = sorted({
    line.split()[-1]
    for line in maps.read_text().splitlines()
    if line.split() and re.search(r"\.so(?:\.[0-9]+)*$", line.split()[-1])
})
print(json.dumps(result, sort_keys=True))
'''


DEFAULT_PROBE_TIMEOUT = 300.0


def positive_finite_timeout(value):
    try:
        timeout = float(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("probe timeout must be a positive finite number") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("probe timeout must be a positive finite number")
    return timeout


def run_probe(command, env, label, timeout):
    try:
        completed = subprocess.run(
            command,
            env=env,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        detail = getattr(exc, "stderr", None)
        raise RuntimeError("%s probe failed: %s%s" % (label, exc, ("; stderr: " + detail.strip()) if detail else "")) from exc
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("%s probe did not produce exactly one JSON line" % label)
    try:
        return json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise RuntimeError("%s probe returned invalid JSON" % label) from exc


def baseline_probe(timeout):
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env.pop("LD_LIBRARY_PATH", None)
    env.pop("LD_PRELOAD", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["COEXIST_MODULES"] = json.dumps(BASELINE_MODULES)
    env["COEXIST_ALLOW_ABSENT"] = ",".join(sorted(OPTIONAL_BASELINE_MODULES))
    return run_probe([sys.executable, "-c", PROBE], env, "baseline", timeout)


def rpm_verify_snapshot(packages=None):
    """Return a stable summary of rpm verification for the baseline set."""
    rpm = shutil.which("rpm")
    if not rpm:
        return {"available": False}
    if packages is None:
        query = subprocess.run(
            [rpm, "-qa", "--qf", "%{NAME}\\n"],
            check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        packages = sorted(set(line for line in query.stdout.splitlines() if line))
    output = []
    for start in range(0, len(packages), 256):
        completed = subprocess.run(
            [rpm, "-V", *packages[start:start + 256]],
            check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        output.append(completed.stdout)
        if completed.stderr:
            output.append("[stderr]\\n" + completed.stderr)
    verification = "".join(output)
    return {
        "available": True,
        "packages": packages,
        "verify_lines": len(verification.splitlines()),
        "verify_sha256": hashlib.sha256(verification.encode()).hexdigest(),
    }


def rpm_installed_packages():
    rpm = shutil.which("rpm")
    if not rpm:
        return None
    completed = subprocess.run(
        [rpm, "-qa", "--qf", "%{NAME}\\n"], check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return set(line for line in completed.stdout.splitlines() if line)


def private_probe(launcher, private_roots, private_module, timeout):
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env.pop("LD_LIBRARY_PATH", None)
    env.pop("LD_PRELOAD", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["COEXIST_MODULES"] = json.dumps(MODULES)
    env.pop("COEXIST_ALLOW_ABSENT", None)
    env["COEXIST_PRIVATE_ROOT"] = os.pathsep.join(str(root) for root in private_roots)
    env["COEXIST_PRIVATE_MODULE"] = private_module
    return run_probe([*launcher, "-c", PROBE], env, "private", timeout)


def verbose_import_paths(output):
    """Extract Python files reported by ``PYTHONVERBOSE`` from launcher output."""
    return sorted(set(re.findall(
        r"(/[\w./+@:-]+?\.(?:py|pyc|so(?:\.[0-9]+)*))", output,
    )))


def validate_sglang_launcher_probe(output, private_roots):
    paths = verbose_import_paths(output)
    private_paths = [path for path in paths if under_any(path, private_roots)]
    if not private_paths:
        raise RuntimeError("SGLang launcher probe loaded no private modules")
    if not any(
        "/sglang/" in path or path.endswith("/sglang.py")
        for path in private_paths
    ):
        raise RuntimeError("SGLang launcher probe did not import private sglang")


def run_sglang_launcher(launcher, private_roots, timeout):
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env.pop("LD_LIBRARY_PATH", None)
    env.pop("LD_PRELOAD", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONSAFEPATH"] = "1"
    # The console entry point accepts its normal CLI only.  Python's verbose
    # import trace gives us a probe without assuming it supports ``-c``.
    env["PYTHONVERBOSE"] = "1"
    env["PYTHONPATH"] = os.pathsep.join(
        str(root / ("python" + ".".join(map(str, sys.version_info[:2]))) / "site-packages")
        for root in private_roots
    )
    try:
        completed = subprocess.run(
            [*launcher, "--help"], env=env, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        detail = getattr(exc, "stderr", None)
        raise RuntimeError("SGLang launcher failed: %s%s" % (exc, ("; stderr: " + detail.strip()) if detail else "")) from exc
    if not (completed.stdout.strip() or completed.stderr.strip()):
        raise RuntimeError("SGLang launcher produced no help output")
    validate_sglang_launcher_probe(completed.stderr, private_roots)


def under_any(path, roots):
    try:
        real = os.path.realpath(path)
        return any(os.path.commonpath((real, os.path.realpath(root))) == os.path.realpath(root) for root in roots)
    except ValueError:
        return False


def validate_private(result, expected, roots, private_module, private_versions):
    if not result.get("modules"):
        raise RuntimeError("private probe returned no modules")
    torch_path = result["modules"].get("torch", {}).get("path")
    if not torch_path or not under_any(torch_path, roots):
        raise RuntimeError("private torch is outside private roots: %s" % torch_path)
    for name in SYSTEM_MODULES:
        actual = result["modules"].get(name, {})
        if actual != expected["modules"].get(name):
            raise RuntimeError("system module %s changed under private launcher" % name)
    private_names = dict(private_versions)
    private_names[private_module] = private_names.get(private_module)
    for name, version in private_names.items():
        actual = result["modules"].get(name, {})
        private_path = actual.get("path")
        if not private_path or not under_any(private_path, roots):
            raise RuntimeError("private module %s is outside private roots: %s" % (name, private_path))
        if version is not None and actual.get("version") != version:
            raise RuntimeError(
                "private module %s has version %s, expected %s"
                % (name, actual.get("version"), version)
            )
    native = [path for path in result.get("native_paths", []) if under_any(path, roots)]
    if not native:
        raise RuntimeError("private probe loaded no native .so from private roots")
    system_torch_native = [
        path for path in result.get("native_paths", [])
        if re.search(r"/(?:libtorch|libc10)[^/]*\.so(?:\.[0-9]+)*$", path)
        and not under_any(path, roots)
    ]
    if system_torch_native:
        raise RuntimeError("system Torch native library loaded: %s" % system_torch_native[0])
    private_torch_native = [
        path for path in native
        if re.search(r"/(?:libtorch|libc10)[^/]*\.so(?:\.[0-9]+)*$", path)
    ]
    if len(private_torch_native) < 2:
        raise RuntimeError("private Torch did not load both libtorch and libc10 native libraries")
    torch = result.get("torch", {})
    if not torch.get("distributed") or not torch.get("gloo") or torch.get("backend") != "gloo":
        raise RuntimeError("private Torch lacks native distributed Gloo support")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-json", required=True, type=Path)
    parser.add_argument(
        "--probe-timeout", type=positive_finite_timeout,
        default=DEFAULT_PROBE_TIMEOUT,
        help="timeout in seconds for each coexistence probe (default: %(default)s)",
    )
    parser.add_argument("--snapshot", action="store_true")
    parser.add_argument("--private-launcher", nargs="+", default=["/usr/bin/sglang-python"])
    parser.add_argument("--sglang-launcher", nargs="+", default=["/usr/bin/sglang"])
    parser.add_argument("--private-root", type=Path, action="append", dest="private_roots")
    parser.add_argument("--private-module", default="sglang")
    parser.add_argument(
        "--private-version", action="append", metavar="MODULE=VERSION",
        help="override an expected private module version (repeatable)",
    )
    args = parser.parse_args()

    private_versions = dict(PRIVATE_MODULE_VERSIONS)
    for item in args.private_version or ():
        name, separator, version = item.partition("=")
        if not separator or not name or not version:
            parser.error("--private-version requires MODULE=VERSION")
        private_versions[name] = version

    baseline = baseline_probe(args.probe_timeout)
    rpm_baseline = rpm_verify_snapshot()
    if args.snapshot:
        args.baseline_json.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=args.baseline_json.parent, delete=False) as handle:
            snapshot = {"probe": baseline, "rpm": rpm_baseline}
            json.dump(snapshot, handle, indent=2, sort_keys=True)
            handle.write("\n")
            temporary = handle.name
        os.replace(temporary, args.baseline_json)
        print("coexistence baseline snapshot: PASS")
        return

    recorded = json.loads(args.baseline_json.read_text())
    expected = recorded.get("probe", recorded)
    expected_rpm = recorded.get("rpm")
    if baseline != expected:
        raise RuntimeError("baseline probe differs from recorded snapshot")
    if expected_rpm and expected_rpm.get("available"):
        current_rpm = rpm_verify_snapshot(expected_rpm.get("packages", []))
        for key in ("verify_lines", "verify_sha256"):
            if current_rpm.get(key) != expected_rpm.get(key):
                raise RuntimeError("RPM verification differs from recorded baseline: %s" % key)
    roots = args.private_roots or [Path(root) for root in DEFAULT_ROOTS if Path(root).is_dir()]
    if not roots or any(not root.is_dir() for root in roots):
        raise RuntimeError("provide existing --private-root paths")
    if not any(root.joinpath("python" + ".".join(map(str, sys.version_info[:2])), "site-packages").is_dir() for root in roots):
        raise RuntimeError("private roots do not contain the running Python site-packages tree")
    private = private_probe(args.private_launcher, roots, args.private_module, args.probe_timeout)
    validate_private(private, expected, roots, args.private_module, private_versions)
    run_sglang_launcher(args.sglang_launcher, roots, args.probe_timeout)
    after = baseline_probe(args.probe_timeout)
    if after != expected:
        raise RuntimeError("baseline probe changed after private launcher invocation")
    if expected_rpm and expected_rpm.get("available"):
        after_rpm = rpm_verify_snapshot(expected_rpm.get("packages", []))
        installed = rpm_installed_packages()
        missing = set(expected_rpm.get("packages", [])) - (installed or set())
        if missing:
            raise RuntimeError("baseline RPM packages were removed: %s" % ", ".join(sorted(missing)[:10]))
        for key in ("verify_lines", "verify_sha256"):
            if after_rpm.get(key) != expected_rpm.get(key):
                raise RuntimeError("RPM verification changed after private installation: %s" % key)
    print("coexistence check: PASS")


if __name__ == "__main__":
    main()

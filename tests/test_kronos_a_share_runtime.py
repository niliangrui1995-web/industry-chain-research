from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = (
    ROOT / ".agents" / "skills" / "kronos-market-forecasting" / "scripts"
)
RUNTIME_PATH = SKILL_SCRIPTS / "kronos_a_share_runtime.py"
MIGRATOR_PATH = SKILL_SCRIPTS / "migrate_kronos_storage.ps1"
EXPECTED_ROOT = Path(r"D:\vcp_hunter\产业链投研\_training\kronos_ashare")


def load_runtime_module():
    spec = importlib.util.spec_from_file_location("kronos_a_share_runtime", RUNTIME_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {RUNTIME_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class KronosAshareRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = load_runtime_module()

    def test_default_layout_uses_the_fixed_training_root(self) -> None:
        layout = self.runtime.get_training_layout()
        self.assertEqual(layout.root, EXPECTED_ROOT.resolve())
        expected = {
            "runtime": "runtime",
            "uv_cache": "runtime/uv-cache",
            "uv_python": "runtime/uv-python",
            "pip_cache": "runtime/pip-cache",
            "venvs": "runtime/venvs",
            "huggingface": "runtime/huggingface",
            "torch": "runtime/torch",
            "tmp": "runtime/tmp",
            "data": "data",
            "runs": "runs",
            "registry": "registry",
        }
        for name, relative in expected.items():
            with self.subTest(name=name):
                self.assertEqual(
                    getattr(layout, name), (layout.root / Path(relative)).resolve()
                )

    def test_layout_creation_and_environment_mapping_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "training"
            with mock.patch.object(self.runtime, "DEFAULT_TRAINING_ROOT", root):
                layout = self.runtime.get_training_layout(root, create=True)
                for path in layout.to_dict().values():
                    self.assertTrue(Path(path).is_dir())

                mapping = self.runtime.environment_mapping(layout)
                self.assertEqual(mapping["UV_CACHE_DIR"], str(layout.uv_cache))
                self.assertEqual(mapping["UV_PYTHON_INSTALL_DIR"], str(layout.uv_python))
                self.assertEqual(mapping["PIP_CACHE_DIR"], str(layout.pip_cache))
                self.assertEqual(mapping["HF_HOME"], str(layout.huggingface))
                self.assertEqual(mapping["TORCH_HOME"], str(layout.torch))
                self.assertEqual(mapping["QLIB_PROVIDER_URI"], str(layout.data / "qlib"))
                self.assertEqual(mapping["QLIB_DATA_PATH"], str(layout.data / "qlib"))
                for name in ("TEMP", "TMP", "TMPDIR"):
                    self.assertEqual(mapping[name], str(layout.tmp))

                custom_environment = {"KEEP": "yes", "UV_CACHE_DIR": "old"}
                previous = self.runtime.apply_environment_mapping(
                    layout, custom_environment
                )
                self.assertEqual(previous["UV_CACHE_DIR"], "old")
                self.assertEqual(custom_environment["KEEP"], "yes")
                self.assertEqual(custom_environment["UV_CACHE_DIR"], str(layout.uv_cache))

    def test_global_mapping_overrides_an_already_cached_tempfile_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root = base / "training"
            stale = base / "stale-c-temp"
            stale.mkdir()
            with mock.patch.object(self.runtime, "DEFAULT_TRAINING_ROOT", root):
                layout = self.runtime.get_training_layout(root, create=True)
                prior_tempdir = tempfile.tempdir
                previous: dict[str, str | None] = {}
                try:
                    tempfile.tempdir = str(stale)
                    self.assertEqual(Path(tempfile.gettempdir()).resolve(), stale)
                    previous = self.runtime.apply_environment_mapping(layout)
                    self.assertEqual(
                        Path(tempfile.gettempdir()).resolve(), layout.tmp.resolve()
                    )
                finally:
                    tempfile.tempdir = prior_tempdir
                    for name, value in previous.items():
                        if value is None:
                            os.environ.pop(name, None)
                        else:
                            os.environ[name] = value

    def test_relative_training_root_and_escape_paths_are_rejected(self) -> None:
        with self.assertRaises(self.runtime.KronosAshareRuntimeError):
            self.runtime.resolve_training_root("relative/root")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "root"
            sibling = Path(temporary).resolve() / "root-sibling" / "file.json"
            root.mkdir()
            with self.assertRaises(self.runtime.KronosAshareRuntimeError):
                self.runtime.resolve_under(root, "../escape.json")
            with self.assertRaises(self.runtime.KronosAshareRuntimeError):
                self.runtime.resolve_under(root, sibling)
            with self.assertRaises(self.runtime.KronosAshareRuntimeError):
                self.runtime.resolve_under(root, root)
            self.assertEqual(
                self.runtime.resolve_under(root, root, allow_root=True), root
            )

        for outside in (
            Path(r"C:\kronos-training"),
            Path(r"D:\HT\kronos-training"),
            Path(r"D:\other-project\kronos-training"),
        ):
            with self.subTest(outside=outside):
                with self.assertRaisesRegex(
                    self.runtime.KronosAshareRuntimeError,
                    "path_outside_training_root",
                ):
                    self.runtime.resolve_training_root(outside)

    def test_existing_symlink_cannot_escape_training_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root = base / "root"
            outside = base / "outside"
            root.mkdir()
            outside.mkdir()
            link = root / "link"
            try:
                os.symlink(outside, link, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink unavailable: {exc}")
            with self.assertRaises(self.runtime.KronosAshareRuntimeError):
                self.runtime.resolve_under(root, link / "payload.json")

    def test_run_and_dataset_identifiers_are_path_safe(self) -> None:
        accepted = ["csi800_20260731", "smoke-001", "a"]
        for value in accepted:
            with self.subTest(value=value):
                self.assertEqual(self.runtime.validate_identifier(value), value)
        rejected = [
            "",
            "UpperCase",
            "../escape",
            "has.dot",
            "has space",
            "con",
            "nul",
            "a" * 65,
        ]
        for value in rejected:
            with self.subTest(value=value):
                with self.assertRaises(self.runtime.KronosAshareRuntimeError):
                    self.runtime.validate_identifier(value)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "training"
            with mock.patch.object(self.runtime, "DEFAULT_TRAINING_ROOT", root):
                layout = self.runtime.get_training_layout(root, create=True)
                dataset = self.runtime.dataset_directory(
                    "csi800_20260731", layout, create=True
                )
                run = self.runtime.run_directory("smoke-001", layout, create=True)
                self.assertTrue(dataset.is_dir())
                self.assertTrue(run.is_dir())
                self.assertTrue(self.runtime.is_within(dataset, layout.data))
                self.assertTrue(self.runtime.is_within(run, layout.runs))

    def test_atomic_json_and_sha256_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            destination = root / "registry" / "manifest.json"
            payload = {"中文": "保留", "number": 3, "nested": {"ok": True}}
            result = self.runtime.atomic_write_json(
                destination, payload, allowed_root=root
            )
            self.assertEqual(result, destination)
            self.assertEqual(json.loads(destination.read_text(encoding="utf-8")), payload)
            expected_hash = hashlib.sha256(destination.read_bytes()).hexdigest()
            self.assertEqual(self.runtime.sha256_file(destination), expected_hash)
            self.assertEqual(
                list(destination.parent.glob(f".{destination.name}.*.tmp")), []
            )

            replacement = {"status": "replaced"}
            self.runtime.atomic_write_json(
                destination, replacement, allowed_root=root
            )
            self.assertEqual(
                json.loads(destination.read_text(encoding="utf-8")), replacement
            )

            outside = root.parent / f"{root.name}-outside.json"
            with self.assertRaises(self.runtime.KronosAshareRuntimeError):
                self.runtime.atomic_write_json(
                    outside, {"blocked": True}, allowed_root=root
                )
            self.assertFalse(outside.exists())

    def test_preflight_reports_ok_and_blocked_resources(self) -> None:
        gib = 1024**3
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            healthy_disk = SimpleNamespace(total=100 * gib, used=30 * gib, free=70 * gib)
            healthy_memory = {
                "source": "fixture",
                "total_bytes": 16 * gib,
                "available_bytes": 8 * gib,
            }
            healthy_cuda = {
                "available": True,
                "devices": [
                    {
                        "index": 0,
                        "name": "fixture",
                        "capability": [6, 1],
                        "total_memory_bytes": 5 * gib,
                    }
                ],
            }
            with (
                mock.patch.object(
                    self.runtime.shutil, "disk_usage", return_value=healthy_disk
                ),
                mock.patch.object(
                    self.runtime, "memory_info", return_value=healthy_memory
                ),
                mock.patch.object(
                    self.runtime, "cuda_info", return_value=healthy_cuda
                ),
            ):
                with mock.patch.object(self.runtime, "DEFAULT_TRAINING_ROOT", root):
                    report = self.runtime.preflight_training(root)
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["blockers"], [])

            low_disk = SimpleNamespace(total=100 * gib, used=99 * gib, free=1 * gib)
            low_memory = {
                "source": "fixture",
                "total_bytes": 16 * gib,
                "available_bytes": 1 * gib,
            }
            no_cuda = {"available": False, "devices": []}
            with (
                mock.patch.object(
                    self.runtime.shutil, "disk_usage", return_value=low_disk
                ),
                mock.patch.object(
                    self.runtime, "memory_info", return_value=low_memory
                ),
                mock.patch.object(self.runtime, "cuda_info", return_value=no_cuda),
            ):
                with mock.patch.object(self.runtime, "DEFAULT_TRAINING_ROOT", root):
                    report = self.runtime.preflight_training(root)
            self.assertEqual(report["status"], "blocked")
            self.assertTrue(
                any(value.startswith("disk_free_below_threshold") for value in report["blockers"])
            )
            self.assertTrue(
                any(value.startswith("ram_available_below_threshold") for value in report["blockers"])
            )
            self.assertIn("cuda_required_but_unavailable", report["blockers"])

    def test_preflight_does_not_create_the_training_root(self) -> None:
        gib = 1024**3
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "not-created"
            disk = SimpleNamespace(total=100 * gib, used=30 * gib, free=70 * gib)
            memory = {
                "source": "fixture",
                "total_bytes": 16 * gib,
                "available_bytes": 8 * gib,
            }
            with (
                mock.patch.object(self.runtime.shutil, "disk_usage", return_value=disk),
                mock.patch.object(self.runtime, "memory_info", return_value=memory),
                mock.patch.object(
                    self.runtime,
                    "cuda_info",
                    return_value={"available": False, "devices": []},
                ),
            ):
                with mock.patch.object(self.runtime, "DEFAULT_TRAINING_ROOT", root):
                    report = self.runtime.preflight_training(root, require_cuda=False)
            self.assertEqual(report["status"], "ok")
            self.assertFalse(root.exists())
            self.assertFalse(report["root_exists"])


class KronosStorageMigratorStaticSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = MIGRATOR_PATH.read_bytes()
        cls.text = cls.raw.decode("utf-8-sig")

    def test_script_has_utf8_bom_for_windows_powershell_51(self) -> None:
        self.assertTrue(self.raw.startswith(b"\xef\xbb\xbf"))

    def test_default_mode_is_read_only_and_apply_is_explicit(self) -> None:
        for needle in [
            "[switch]$Apply",
            "if (-not $Apply)",
            "audit_only",
            "exit 0",
        ]:
            self.assertIn(needle, self.text)
        self.assertLess(
            self.text.index("if (-not $Apply)"),
            self.text.index("$operationId = [guid]::NewGuid().ToString('N')"),
        )

    def test_audit_revalidates_historical_manifests_and_runtime_read_only(self) -> None:
        for needle in [
            "function Assert-StoredHashManifestShape",
            "function Assert-AlreadyMigratedIntegrity",
            "Assert-ManifestsEqual",
            "manifest_sha256 = [ordered]@{",
            "Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256",
            "current_target_policy = 'mutable_runtime_verified_by_junction_and_tools'",
            "function Invoke-ReadOnlyRuntimeVerification",
            "& $managedPython -I -B -c $pythonProbe",
            "'pip_version': pip.__version__",
            "$record['historical_manifest_integrity'] = Assert-AlreadyMigratedIntegrity $spec",
            "$runtimeVerification = Invoke-ReadOnlyRuntimeVerification",
            "$record['functional_verification'] = 'verified'",
            "runtime_verification = $runtimeVerification",
        ]:
            with self.subTest(needle=needle):
                self.assertIn(needle, self.text)

        audit_start = self.text.index("if (-not $Apply)")
        audit_exit = self.text.index("exit 0", audit_start)
        apply_operation = self.text.index(
            "$operationId = [guid]::NewGuid().ToString('N')"
        )
        for validation in [
            "$record['historical_manifest_integrity'] = Assert-AlreadyMigratedIntegrity $spec",
            "$runtimeVerification = Invoke-ReadOnlyRuntimeVerification",
        ]:
            self.assertLess(audit_start, self.text.index(validation, audit_start))
            self.assertLess(self.text.index(validation, audit_start), audit_exit)
        self.assertLess(audit_exit, apply_operation)

    def test_only_the_three_exact_sources_are_migrated(self) -> None:
        sources = [
            r"C:\Users\Administrator\AppData\Local\uv\cache",
            r"C:\Users\Administrator\AppData\Local\pip\cache",
            r"C:\Users\Administrator\AppData\Roaming\uv\python",
        ]
        for source in sources:
            self.assertEqual(self.text.count(f"Source = '{source}'"), 1)
        self.assertEqual(self.text.count("Source = 'C:\\"), 3)
        self.assertIn(
            r"D:\vcp_hunter\产业链投研\_training\kronos_ashare", self.text
        )

    def test_excluded_paths_are_named_and_never_migration_sources(self) -> None:
        excluded = [
            r"C:\Users\Administrator\.cache\huggingface\token",
            r"C:\Users\Administrator\AppData\Roaming\uv\tools",
            r"C:\Python314",
            r"C:\Users\Administrator\AppData\Roaming\Python",
        ]
        for path in excluded:
            self.assertIn(f"'{path}'", self.text)
            self.assertNotIn(f"Source = '{path}'", self.text)

    def test_migration_uses_native_literal_path_operations_and_hashes(self) -> None:
        for needle in [
            "Get-FileHash -LiteralPath",
            "Copy-Item -LiteralPath",
            "Move-Item -LiteralPath",
            "New-Item -ItemType Junction",
            "Assert-ManifestsEqual",
            "Undo-MigrationStage",
            "Remove-VerifiedBackup",
            "Invoke-ToolVerification",
        ]:
            self.assertIn(needle, self.text)
        lowered = self.text.casefold()
        for forbidden in [
            "cmd /c",
            "cmd.exe",
            "mklink",
            "robocopy",
            "rmdir",
            "remove-item -path",
            "git clean",
        ]:
            self.assertNotIn(forbidden, lowered)

    def test_internal_uv_python_junctions_are_rebuilt_and_user_env_is_persisted(self) -> None:
        for needle in [
            "Restore-InternalJunctions",
            "-RelocatedFromRoot $spec.Target",
            "-RelocatedFromRoot $spec.Source",
            "-IgnoreJunctions",
            "SetEnvironmentVariable(",
            "'User'",
            "用户级环境变量写后回读失败",
        ]:
            self.assertIn(needle, self.text)

    def test_apply_has_d_drive_capacity_preflight_and_short_stage_path(self) -> None:
        for needle in [
            "Get-DirectoryPayloadStats",
            "required_free_bytes",
            "available_free_bytes",
            "$spacePreflight.status -ne 'ok'",
            "('m-' + $operationId.Substring(0, 12))",
        ]:
            self.assertIn(needle, self.text)

    def test_apply_blocks_concurrent_clients_and_revalidates_before_cleanup(self) -> None:
        for needle in [
            "Local\\KronosAshareStorageMigration",
            "Assert-NoActiveMigrationClients",
            "Assert-AlreadyMigratedIntegrity",
            "target cleanup preflight",
            "backup cleanup preflight",
            "blocked_backup_exists",
            "Assert-NoReparseAncestors $TrainingRoot",
            "$_.Modules",
            "$sourceRoots",
            "正在使用迁移源的 Python/uv/pip",
        ]:
            self.assertIn(needle, self.text)

    def test_every_remove_item_uses_literal_path_and_known_exact_targets(self) -> None:
        remove_lines = [
            line.strip()
            for line in self.text.splitlines()
            if line.strip().startswith("Remove-Item")
        ]
        self.assertGreaterEqual(len(remove_lines), 5)
        allowed_targets = {
            "$spec.Target",
            "$spec.Source",
            "$Context.Stage",
            "$spec.Backup",
            "$operationTemp",
        }
        for line in remove_lines:
            with self.subTest(line=line):
                self.assertIn("-LiteralPath", line)
                parts = line.split()
                target = parts[parts.index("-LiteralPath") + 1]
                self.assertIn(target, allowed_targets)
        recursive_lines = [line for line in remove_lines if "-Recurse" in line]
        recursive_targets = {
            "$spec.Target",
            "$Context.Stage",
            "$spec.Backup",
            "$operationTemp",
        }
        for line in recursive_lines:
            parts = line.split()
            target = parts[parts.index("-LiteralPath") + 1]
            self.assertIn(target, recursive_targets)


if __name__ == "__main__":
    unittest.main()

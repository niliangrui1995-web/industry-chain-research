from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "kronos-market-forecasting"
    / "scripts"
    / "run_kronos_forecast.py"
)


def load_runner_module():
    spec = importlib.util.spec_from_file_location("kronos_market_forecasting_runner", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class KronosMarketForecastingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner_module()

    def test_history_hash_matches_the_bytes_that_were_parsed(self) -> None:
        payload = (
            b"timestamps,open,high,low,close\n"
            b"2026-08-01 09:30:00,10,11,9,10.5\n"
            b"2026-08-01 09:35:00,10.5,11.5,10,11\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.csv"
            path.write_bytes(payload)
            _, _, _, details = self.runner.load_history(path, "timestamps", 2)
            path.write_bytes(payload + b"2026-08-01 09:40:00,11,12,10.5,11.5\n")

        self.assertEqual(details["input_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(details["history_rows"], 2)

    def test_future_timestamps_are_converted_to_history_timezone(self) -> None:
        payload = b"timestamps\n2026-08-03T02:00:00Z\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "future.csv"
            path.write_bytes(payload)
            future, source, future_hash, warnings = self.runner.load_future_timestamps(
                path,
                None,
                "timestamps",
                pd.Timestamp("2026-08-03T09:30:00+08:00"),
                1,
            )

        self.assertEqual(future.iloc[0].hour, 10)
        self.assertEqual(future.iloc[0].utcoffset().total_seconds(), 8 * 3600)
        self.assertTrue(source.startswith("file:"))
        self.assertEqual(future_hash, hashlib.sha256(payload).hexdigest())
        self.assertTrue(any("转换" in warning for warning in warnings))

    def test_source_checkout_rejects_tracked_modifications(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "source"
            repo.mkdir()
            self._git(repo, "init")
            self._git(repo, "config", "user.email", "kronos-test@example.invalid")
            self._git(repo, "config", "user.name", "Kronos Test")
            tracked = repo / "model.py"
            tracked.write_text("value = 1\n", encoding="utf-8")
            self._git(repo, "add", "model.py")
            self._git(repo, "commit", "-m", "test fixture")
            revision = self._git(repo, "rev-parse", "HEAD").stdout.strip()

            self.assertEqual(
                self.runner.validate_source_checkout(repo, revision),
                revision,
            )
            tracked.write_text("value = 2\n", encoding="utf-8")
            with self.assertRaisesRegex(self.runner.KronosRuntimeError, "工作树"):
                self.runner.validate_source_checkout(repo, revision)

    def test_hash_validation_rejects_config_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_bytes(b'{"version": 1}\n')
            expected = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(
                self.runner.validate_file_hash(path, expected, "config"),
                expected,
            )
            path.write_bytes(b'{"version": 2}\n')
            with self.assertRaisesRegex(self.runner.KronosRuntimeError, "SHA256"):
                self.runner.validate_file_hash(path, expected, "config")

    def test_output_cannot_overwrite_inputs_or_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            runtime = root / "runtime"
            runtime.mkdir()
            history = root / "history.csv"
            future = root / "future.csv"
            history.touch()
            future.touch()

            with self.assertRaisesRegex(self.runner.KronosRuntimeError, "输入"):
                self.runner.validate_output_paths(
                    history,
                    future,
                    future,
                    future.with_suffix(".csv.metadata.json"),
                    runtime,
                )
            runtime_output = runtime / "forecast.csv"
            with self.assertRaisesRegex(self.runner.KronosRuntimeError, "运行目录"):
                self.runner.validate_output_paths(
                    history,
                    future,
                    runtime_output,
                    runtime_output.with_suffix(".csv.metadata.json"),
                    runtime,
                )

    def test_output_pair_commits_complete_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "forecast.csv"
            metadata = root / "forecast.csv.metadata.json"
            self.runner.write_output_pair(output, metadata, b"forecast\n", b"{}\n", False)

            self.assertEqual(output.read_bytes(), b"forecast\n")
            self.assertEqual(metadata.read_bytes(), b"{}\n")
            self.assertEqual(list(root.glob(".*.tmp")), [])
            self.assertEqual(list(root.glob(".*.lock")), [])

    def test_interrupted_pair_is_recovered_before_reuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "forecast.csv"
            metadata = root / "forecast.csv.metadata.json"
            crash_script = """
import importlib.util
import os
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("kronos_crash_fixture", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
output = Path(sys.argv[2])
metadata = Path(sys.argv[3])
paths = module.output_transaction_paths(output, metadata)
with module.OutputPathLock(paths["lock"]):
    module.write_payload(paths["pending_output"], b"forecast\\n")
    module.write_payload(paths["pending_metadata"], b"{}\\n")
    os.link(paths["pending_output"], output)
    os._exit(73)
"""
            crashed = subprocess.run(
                [sys.executable, "-c", crash_script, str(RUNNER_PATH), str(output), str(metadata)],
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(crashed.returncode, 0)
            paths = self.runner.output_transaction_paths(output, metadata)

            self.runner.prepare_output_pair(output, metadata, False)

            self.assertFalse(output.exists())
            self.assertFalse(metadata.exists())
            for key in (
                "pending_output",
                "pending_metadata",
                "backup_output",
                "backup_metadata",
                "commit_pending",
                "commit",
            ):
                self.assertFalse(paths[key].exists())

    def test_force_replaces_a_complete_pair_without_residue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "forecast.csv"
            metadata = root / "forecast.csv.metadata.json"
            output.write_bytes(b"old forecast\n")
            metadata.write_bytes(b"old metadata\n")

            self.runner.write_output_pair(output, metadata, b"new forecast\n", b"{}\n", True)

            self.assertEqual(output.read_bytes(), b"new forecast\n")
            self.assertEqual(metadata.read_bytes(), b"{}\n")
            paths = self.runner.output_transaction_paths(output, metadata)
            for key in (
                "pending_output",
                "pending_metadata",
                "backup_output",
                "backup_metadata",
                "commit_pending",
                "commit",
            ):
                self.assertFalse(paths[key].exists())

    def test_committed_pair_is_verified_and_preserved_after_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "forecast.csv"
            metadata = root / "forecast.csv.metadata.json"
            output_payload = b"forecast\n"
            metadata_payload = b"{}\n"
            paths = self.runner.output_transaction_paths(output, metadata)
            self.runner.write_payload(paths["pending_output"], output_payload)
            self.runner.write_payload(paths["pending_metadata"], metadata_payload)
            self.runner.os.link(paths["pending_output"], output)
            self.runner.os.link(paths["pending_metadata"], metadata)
            marker = {
                "protocol": "kronos-output-pair-v1",
                "transaction_key": paths["lock"].stem,
                "output_sha256": hashlib.sha256(output_payload).hexdigest(),
                "output_size": len(output_payload),
                "metadata_sha256": hashlib.sha256(metadata_payload).hexdigest(),
                "metadata_size": len(metadata_payload),
                "had_output": False,
                "had_metadata": False,
            }
            self.runner.write_payload(
                paths["commit"],
                json.dumps(marker, sort_keys=True).encode("ascii"),
            )

            with self.assertRaisesRegex(self.runner.KronosRuntimeError, "输出已存在"):
                self.runner.prepare_output_pair(output, metadata, False)

            self.assertEqual(output.read_bytes(), output_payload)
            self.assertEqual(metadata.read_bytes(), metadata_payload)
            for key in (
                "pending_output",
                "pending_metadata",
                "backup_output",
                "backup_metadata",
                "commit_pending",
                "commit",
            ):
                self.assertFalse(paths[key].exists())

    def test_output_pair_rolls_back_when_metadata_is_claimed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "forecast.csv"
            metadata = root / "forecast.csv.metadata.json"
            real_link = self.runner.os.link

            def racing_link(source, destination):
                if Path(destination) == metadata:
                    metadata.write_bytes(b"external\n")
                return real_link(source, destination)

            with mock.patch.object(self.runner.os, "link", side_effect=racing_link):
                with self.assertRaisesRegex(self.runner.KronosRuntimeError, "未覆盖"):
                    self.runner.write_output_pair(
                        output,
                        metadata,
                        b"forecast\n",
                        b"{}\n",
                        False,
                    )

            self.assertFalse(output.exists())
            self.assertEqual(metadata.read_bytes(), b"external\n")
            self.assertEqual(list(root.glob(".*.tmp")), [])
            self.assertEqual(list(root.glob(".*.lock")), [])

    def _git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()

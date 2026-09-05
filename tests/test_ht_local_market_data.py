from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
from io import StringIO
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class HtLocalMarketDataTests(unittest.TestCase):
    def test_cli_defaults_to_ht_root(self) -> None:
        module = load_module(
            "inspect_ht_data_default_root",
            ROOT / ".agents" / "skills" / "ht-local-market-data" / "scripts" / "inspect_ht_data.py",
        )
        with patch.object(module, "inspect", return_value={}) as inspect_mock:
            with redirect_stdout(StringIO()):
                exit_code = module.main(["--json"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(inspect_mock.call_args.args[0], Path(r"D:\HT"))

    def test_inspector_rejects_root_without_market_data_sentinels(self) -> None:
        module = load_module(
            "inspect_ht_data_invalid_root",
            ROOT / ".agents" / "skills" / "ht-local-market-data" / "scripts" / "inspect_ht_data.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "htlog").mkdir()

            with self.assertRaisesRegex(FileNotFoundError, "vipdoc.*T0002"):
                module.inspect(root, [], include_block_samples=False)

    def test_inspector_rejects_empty_market_data_sentinels(self) -> None:
        module = load_module(
            "inspect_ht_data_empty_sentinels",
            ROOT / ".agents" / "skills" / "ht-local-market-data" / "scripts" / "inspect_ht_data.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in module.REQUIRED_DATA_DIRS:
                (root / relative).mkdir(parents=True)

            with self.assertRaisesRegex(FileNotFoundError, "valid.*day"):
                module.inspect(root, [], include_block_samples=False)

    def test_inspector_skips_account_trading_log_boundaries(self) -> None:
        module = load_module(
            "inspect_ht_data",
            ROOT / ".agents" / "skills" / "ht-local-market-data" / "scripts" / "inspect_ht_data.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "htlog").mkdir()
            (root / "htlog" / "account.log").write_text("should not be counted", encoding="utf-8")
            (root / "T0001").mkdir()
            (root / "T0001" / "trade.dat").write_text("should not be counted", encoding="utf-8")
            (root / "funcs_jy").mkdir()
            (root / "funcs_jy" / "trade_runtime.dat").write_text("should not be counted", encoding="utf-8")
            (root / "vipdoc" / "sh" / "lday").mkdir(parents=True)
            (root / "vipdoc" / "sz" / "lday").mkdir(parents=True)
            (root / "T0002" / "hq_cache").mkdir(parents=True)
            day_record = module.DAY_STRUCT.pack(20260710, 10000, 11000, 9000, 10500, 1000.0, 100, 0)
            (root / "vipdoc" / "sh" / "lday" / "sh000001.day").write_bytes(day_record)
            (root / "vipdoc" / "sz" / "lday" / "sz399001.day").write_bytes(day_record)
            (root / "T0002" / "hq_cache" / "base.dbf").write_bytes(b"dbf")
            (root / "vipdoc" / "htlog").mkdir()
            (root / "vipdoc" / "htlog" / "nested.log").write_text("should not be counted", encoding="utf-8")
            (root / "vipdoc" / "keep.txt").write_text("market data placeholder", encoding="utf-8")

            top_dirs = module.summarize_top_dirs(root)
            result = module.inspect(root, [], include_block_samples=False)

            self.assertEqual(set(top_dirs), {"vipdoc", "T0002"})
            self.assertEqual(top_dirs["vipdoc"]["files"], 2)
            self.assertIn("privacy_boundary", result)

    def test_whitelist_never_stats_private_files_or_enumerates_unapproved_directories(self) -> None:
        module = load_module(
            "inspect_ht_data_whitelist",
            ROOT / ".agents" / "skills" / "ht-local-market-data" / "scripts" / "inspect_ht_data.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in module.REQUIRED_DATA_DIRS:
                (root / relative).mkdir(parents=True)
            record = module.DAY_STRUCT.pack(20260710, 10000, 11000, 9000, 10500, 1000.0, 100, 0)
            for relative in module.REQUIRED_DAY_FILES:
                (root / relative).write_bytes(record)
            (root / "T0002" / "hq_cache" / "base.dbf").write_bytes(b"dbf")
            private = root / "T0002" / "account"
            private.mkdir()
            (private / "secret.pass").write_bytes(b"private")
            (root / "vipdoc" / "sh" / "lday" / "secret.pass").write_bytes(b"private")
            original_iterdir = Path.iterdir
            original_stat = Path.stat
            original_lstat = Path.lstat

            def guarded_iterdir(path):
                if path == root or path == root / "T0002" or "account" in path.parts:
                    raise AssertionError("unapproved directory enumerated")
                return original_iterdir(path)

            def guarded_stat(path, *args, **kwargs):
                if "account" in path.parts or path.suffix == ".pass":
                    raise AssertionError("private metadata queried")
                return original_stat(path, *args, **kwargs)

            def guarded_lstat(path, *args, **kwargs):
                if "account" in path.parts or path.suffix == ".pass":
                    raise AssertionError("private link metadata queried")
                return original_lstat(path, *args, **kwargs)

            with patch.object(Path, "iterdir", guarded_iterdir), patch.object(Path, "stat", guarded_stat), patch.object(Path, "lstat", guarded_lstat):
                result = module.inspect(root, [], include_block_samples=False)
            self.assertEqual(result["daily_day"]["files"], 2)
            self.assertEqual(result["top_dirs"]["T0002"]["files"], 1)

    def test_market_symlink_and_code_traversal_are_rejected(self) -> None:
        module = load_module(
            "inspect_ht_data_symlink",
            ROOT / ".agents" / "skills" / "ht-local-market-data" / "scripts" / "inspect_ht_data.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            outside = Path(tmp) / "outside"
            root.mkdir()
            outside.mkdir()
            (root / "vipdoc" / "sh").mkdir(parents=True)
            record = module.DAY_STRUCT.pack(20260710, 10000, 11000, 9000, 10500, 1000.0, 100, 0)
            (outside / "sh000001.day").write_bytes(record)
            linked_dir = root / "vipdoc" / "sh" / "lday"
            try:
                linked_dir.symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"directory symlink unavailable: {exc}")
            self.assertEqual(module.summarize_day(root, ["sh000001"])["files"], 0)
            with self.assertRaisesRegex(ValueError, "code"):
                module.summarize_day(root, ["sh../../outside/sh000001"])

    def test_regular_market_filename_symlink_is_not_read(self) -> None:
        module = load_module(
            "inspect_ht_data_file_link",
            ROOT / ".agents" / "skills" / "ht-local-market-data" / "scripts" / "inspect_ht_data.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            folder = root / "vipdoc" / "sh" / "lday"
            folder.mkdir(parents=True)
            outside = Path(tmp) / "outside.day"
            outside.write_bytes(b"must not read")
            try:
                (folder / "sh000001.day").symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"file symlink unavailable: {exc}")
            with patch.object(Path, "read_bytes", side_effect=AssertionError("linked file read")):
                result = module.summarize_day(root, ["sh000001"])
            self.assertEqual(result["files"], 0)
            self.assertFalse(result["samples"][0]["exists"])


if __name__ == "__main__":
    unittest.main()

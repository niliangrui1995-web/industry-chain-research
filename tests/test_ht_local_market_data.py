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
    def test_cli_defaults_to_zd_huatai_root(self) -> None:
        module = load_module(
            "inspect_ht_data_default_root",
            ROOT / ".agents" / "skills" / "ht-local-market-data" / "scripts" / "inspect_ht_data.py",
        )
        with patch.object(module, "inspect", return_value={}) as inspect_mock:
            with redirect_stdout(StringIO()):
                exit_code = module.main(["--json"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(inspect_mock.call_args.args[0], Path(r"C:\zd_huatai"))

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

            self.assertTrue(top_dirs["htlog"]["skipped"])
            self.assertTrue(top_dirs["T0001"]["skipped"])
            self.assertTrue(top_dirs["funcs_jy"]["skipped"])
            self.assertEqual(top_dirs["vipdoc"]["files"], 3)
            self.assertIn("privacy_boundary", result)


if __name__ == "__main__":
    unittest.main()

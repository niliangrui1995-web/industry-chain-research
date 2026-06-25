from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class HtLocalMarketDataTests(unittest.TestCase):
    def test_inspector_skips_account_trading_log_boundaries(self) -> None:
        module = load_module(
            "inspect_ht_data",
            ROOT / "skills" / "ht-local-market-data" / "scripts" / "inspect_ht_data.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "htlog").mkdir()
            (root / "htlog" / "account.log").write_text("should not be counted", encoding="utf-8")
            (root / "T0001").mkdir()
            (root / "T0001" / "trade.dat").write_text("should not be counted", encoding="utf-8")
            (root / "vipdoc" / "htlog").mkdir(parents=True)
            (root / "vipdoc" / "htlog" / "nested.log").write_text("should not be counted", encoding="utf-8")
            (root / "vipdoc" / "keep.txt").write_text("market data placeholder", encoding="utf-8")

            top_dirs = module.summarize_top_dirs(root)
            result = module.inspect(root, [], include_block_samples=False)

            self.assertTrue(top_dirs["htlog"]["skipped"])
            self.assertTrue(top_dirs["T0001"]["skipped"])
            self.assertEqual(top_dirs["vipdoc"]["files"], 1)
            self.assertIn("privacy_boundary", result)


if __name__ == "__main__":
    unittest.main()

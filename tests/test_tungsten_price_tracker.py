from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TungstenPriceTrackerTests(unittest.TestCase):
    def test_na_current_day_does_not_reuse_old_price_in_today_table(self) -> None:
        module = load_module("update_tungsten_price_tracker", ROOT / "scripts" / "update_tungsten_price_tracker.py")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            history = tmp_path / "price_history.csv"
            report_dir = tmp_path / "reports"
            rows = [
                {
                    "date": "2026-06-23",
                    "indicator": "black_tungsten_concentrate_65",
                    "name": "65%黑钨精矿",
                    "low": "",
                    "high": "",
                    "mid": "12.5",
                    "unit": "万元/标吨",
                    "currency": "CNY",
                    "source_name": "seed",
                    "source_url": "",
                    "source_grade": "secondary_media",
                    "notes": "old value",
                },
                {
                    "date": "2026-06-24",
                    "indicator": "black_tungsten_concentrate_65",
                    "name": "65%黑钨精矿",
                    "low": "N/A",
                    "high": "N/A",
                    "mid": "N/A",
                    "unit": "万元/标吨",
                    "currency": "CNY",
                    "source_name": "same-day-public-check",
                    "source_url": "",
                    "source_grade": "observation",
                    "notes": "no public same-day price",
                },
            ]
            with history.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=module.FIELDNAMES)
                writer.writeheader()
                writer.writerows(rows)

            report = module.generate_report(history, report_dir, date(2026, 6, 24))
            text = report.read_text(encoding="utf-8")
            today_table = text.split("## 当日价格", 1)[1].split("## 跟踪口径", 1)[0]

            self.assertIn("| 65%黑钨精矿 | N/A |", today_table)
            self.assertNotIn("| 65%黑钨精矿 | 12.5 |", today_table)


if __name__ == "__main__":
    unittest.main()

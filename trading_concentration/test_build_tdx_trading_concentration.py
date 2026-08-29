from __future__ import annotations

import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("build_tdx_trading_concentration.py")
SPEC = importlib.util.spec_from_file_location("trading_concentration_builder", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import setup guard
    raise RuntimeError("无法加载交易集中度构建器")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

DAY_RECORD = struct.Struct("<IIIIIfII")


def write_day(path: Path, rows: list[tuple[int, float, float, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = bytearray()
    for date, close, amount, volume in rows:
        body.extend(
            DAY_RECORD.pack(
                date,
                100,
                100,
                100,
                int(round(close * 100)),
                float(amount),
                int(volume),
                0,
            )
        )
    path.write_bytes(bytes(body))


class TradingConcentrationBuilderTests(unittest.TestCase):
    def test_compact_date_conversion_and_prefix_filters(self) -> None:
        self.assertEqual(MODULE.compact_date_to_iso(20160126), "2016-01-26")
        self.assertEqual(MODULE.parse_compact_date("20220802"), 20220802)
        self.assertTrue("689" in MODULE.CANDIDATE_PREFIXES["sh"])
        self.assertFalse("899" in MODULE.CANDIDATE_PREFIXES["bj"])

    def test_builds_segments_top5_and_manifest_without_raw_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project_root = root / "project"
            project_root.mkdir()
            (project_root / "AGENTS.md").write_text("test\n", encoding="utf-8")
            tdx_root = root / "HT"
            sh_dir = tdx_root / "vipdoc/sh/lday"
            sz_dir = tdx_root / "vipdoc/sz/lday"
            bj_dir = tdx_root / "vipdoc/bj/lday"

            write_day(
                sh_dir / "sh000002.day",
                [(20160125, 1, 10_000, 1), (20160126, 1, 10_000, 1)],
            )
            write_day(
                sz_dir / "sz399107.day",
                [(20160125, 1, 20_000, 1), (20160126, 1, 20_000, 1)],
            )
            write_day(
                sh_dir / "sh880005.day",
                [
                    (20160126, 1, 50_000, 1),
                    (20220801, 1, 50_000, 1),
                    (20220802, 1, 50_000, 1),
                ],
            )
            write_day(
                sz_dir / "sz399006.day",
                [
                    (20160125, 1_500, 1, 1),
                    (20160126, 1_501, 1, 1),
                    (20220801, 2_500, 1, 1),
                    (20220802, 2_510, 1, 1),
                ],
            )
            write_day(
                sh_dir / "sh000001.day",
                [(20160125, 1, 9_999_999, 1), (20160126, 1, 9_999_999, 1)],
            )
            for offset in range(21):
                code = f"600{offset:03d}"
                rows = [(20160125, 1, 100 + offset, 1)] if offset < 20 else []
                rows.extend(
                    [
                        (20160126, 1, 100 + offset, 1),
                        (20220801, 1, 100 + offset, 1),
                        (20220802, 1, 100 + offset, 1),
                    ]
                )
                write_day(sh_dir / f"sh{code}.day", rows)
            write_day(
                bj_dir / "bj920001.day",
                [(20220801, 1, 10_000, 1), (20220802, 1, 10_000, 1)],
            )

            output_dir = root / "output"
            command = [
                sys.executable,
                str(SCRIPT_PATH),
                "--project-root",
                str(project_root),
                "--tdx-root",
                str(tdx_root),
                "--output-dir",
                str(output_dir),
                "--start-date",
                "20160125",
            ]
            result = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"records": 4', result.stdout)

            payload = json.loads((output_dir / MODULE.PAYLOAD_FILENAME).read_text(encoding="utf-8"))
            manifest = json.loads((output_dir / MODULE.MANIFEST_FILENAME).read_text(encoding="utf-8"))
            by_date = {record["date"]: record for record in payload["records"]}
            self.assertEqual(by_date["2016-01-25"]["active_stock_count"], 20)
            self.assertEqual(by_date["2016-01-25"]["top5_stock_count"], 1)
            self.assertEqual(by_date["2016-01-25"]["chinext_close"], 1500)
            self.assertEqual(by_date["2016-01-25"]["denominator_source"], "sh000002_plus_sz399107")
            self.assertEqual(by_date["2016-01-26"]["active_stock_count"], 21)
            self.assertEqual(by_date["2016-01-26"]["top5_stock_count"], 2)
            self.assertEqual(by_date["2022-08-01"]["active_stock_count"], 21)
            self.assertEqual(by_date["2022-08-01"]["numerator_scope"], "sh_sz_active_a")
            self.assertEqual(by_date["2022-08-02"]["active_stock_count"], 22)
            self.assertEqual(by_date["2022-08-02"]["numerator_scope"], "sh_sz_bj_active_a")
            self.assertGreater(by_date["2022-08-02"]["c5_pct"], by_date["2022-08-01"]["c5_pct"])
            self.assertFalse(manifest["raw_data_copied"])
            self.assertEqual(manifest["candidate_file_count"]["bj"], 1)
            self.assertEqual(manifest["comparison_index_input"]["code"], "399006")
            self.assertEqual(manifest["comparison_index_input"]["missing_output_records"], 0)
            MODULE.verify_artifact_bundle(
                output_dir / MODULE.PAYLOAD_FILENAME,
                output_dir / MODULE.MANIFEST_FILENAME,
                output_dir / MODULE.CSV_FILENAME,
            )


if __name__ == "__main__":
    unittest.main()

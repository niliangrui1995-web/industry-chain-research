from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TASK_DIRECTORY = Path(__file__).parent
BUILDER_SCRIPT = TASK_DIRECTORY / "build_tdx_trading_concentration.py"
APPEND_SCRIPT = TASK_DIRECTORY / "append_tdx_trading_concentration_tail.py"
DAY_RECORD = struct.Struct("<IIIIIfII")
PAYLOAD_FILENAME = "trading-concentration-dashboard.json"
MANIFEST_FILENAME = "trading-concentration-dashboard.manifest.json"
CSV_FILENAME = "trading-concentration-daily.csv"


def write_day(path: Path, rows: list[tuple[int, float, float, float]], *, append: bool = False) -> None:
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
    with path.open("ab" if append else "wb") as handle:
        handle.write(body)


class TradingConcentrationTailAppendTests(unittest.TestCase):
    def create_baseline(self, root: Path) -> tuple[Path, Path, Path]:
        project_root = root / "project"
        project_root.mkdir()
        (project_root / "AGENTS.md").write_text("test\n", encoding="utf-8")
        tdx_root = root / "HT"
        sh_dir = tdx_root / "vipdoc/sh/lday"
        sz_dir = tdx_root / "vipdoc/sz/lday"
        bj_dir = tdx_root / "vipdoc/bj/lday"
        write_day(sh_dir / "sh880008.day", [(20220729, 1, 10_000, 1)])
        write_day(sz_dir / "sz399006.day", [(20220729, 2_490, 1, 1)])
        for offset in range(20):
            write_day(sh_dir / f"sh600{offset:03d}.day", [(20220729, 1, 100 + offset, 1)])
        write_day(bj_dir / "bj920001.day", [(20220729, 1, 500, 1)])
        output_dir = root / "output"
        self.run_builder(project_root, tdx_root, output_dir)
        return project_root, tdx_root, output_dir

    def run_builder(self, project_root: Path, tdx_root: Path, output_dir: Path) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(BUILDER_SCRIPT),
                "--project-root",
                str(project_root),
                "--tdx-root",
                str(tdx_root),
                "--output-dir",
                str(output_dir),
                "--start-date",
                "20220729",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def run_append(self, project_root: Path, tdx_root: Path, output_dir: Path) -> dict[str, object]:
        result = subprocess.run(
            [
                sys.executable,
                str(APPEND_SCRIPT),
                "--project-root",
                str(project_root),
                "--tdx-root",
                str(tdx_root),
                "--output-dir",
                str(output_dir),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_appends_tail_without_rewriting_history_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project_root, tdx_root, output_dir = self.create_baseline(root)
            sh_dir = tdx_root / "vipdoc/sh/lday"
            sz_dir = tdx_root / "vipdoc/sz/lday"
            bj_dir = tdx_root / "vipdoc/bj/lday"

            baseline = json.loads((output_dir / PAYLOAD_FILENAME).read_text(encoding="utf-8"))
            baseline_records = baseline["records"]
            baseline_csv_lines = (output_dir / CSV_FILENAME).read_text(encoding="utf-8").splitlines()

            write_day(
                sh_dir / "sh880008.day",
                [(20220801, 1, 10_000, 1), (20220802, 1, 20_000, 1)],
                append=True,
            )
            write_day(
                sz_dir / "sz399006.day",
                [(20220801, 2_500, 1, 1), (20220802, 2_510, 1, 1)],
                append=True,
            )
            for offset in range(20):
                write_day(
                    sh_dir / f"sh600{offset:03d}.day",
                    [(20220801, 1, 100 + offset, 1), (20220802, 1, 100 + offset, 1)],
                    append=True,
                )
            write_day(sh_dir / "sh600020.day", [(20220802, 1, 300, 1)])
            write_day(sh_dir / "sh600021.day", [(20220802, 0, 9_999, 1)])
            write_day(bj_dir / "bj920001.day", [(20220801, 1, 500, 1), (20220802, 1, 500, 1)], append=True)

            result = self.run_append(project_root, tdx_root, output_dir)
            self.assertEqual(result["status"], "updated")
            self.assertEqual(result["records_added"], 2)
            self.assertEqual(result["processed_source_date_range"], {"start": "2022-08-01", "end": "2022-08-02"})

            payload = json.loads((output_dir / PAYLOAD_FILENAME).read_text(encoding="utf-8"))
            manifest = json.loads((output_dir / MANIFEST_FILENAME).read_text(encoding="utf-8"))
            self.assertEqual(payload["records"][: len(baseline_records)], baseline_records)
            self.assertEqual((output_dir / CSV_FILENAME).read_text(encoding="utf-8").splitlines()[: len(baseline_csv_lines)], baseline_csv_lines)
            by_date = {record["date"]: record for record in payload["records"]}
            self.assertEqual(by_date["2022-08-01"]["active_stock_count"], 20)
            self.assertEqual(by_date["2022-08-01"]["top5_stock_count"], 1)
            self.assertEqual(by_date["2022-08-01"]["top5_amount_yi"], 0.00000119)
            self.assertEqual(by_date["2022-08-01"]["market_amount_yi"], 0.0001)
            self.assertEqual(by_date["2022-08-01"]["c5_pct"], 1.19)
            self.assertEqual(by_date["2022-08-01"]["numerator_scope"], "sh_sz_active_a")
            self.assertEqual(by_date["2022-08-01"]["chinext_close"], 2500)
            self.assertEqual(by_date["2022-08-02"]["active_stock_count"], 22)
            self.assertEqual(by_date["2022-08-02"]["top5_stock_count"], 2)
            self.assertEqual(by_date["2022-08-02"]["top5_amount_yi"], 0.000008)
            self.assertEqual(by_date["2022-08-02"]["market_amount_yi"], 0.0002)
            self.assertEqual(by_date["2022-08-02"]["c5_pct"], 4.0)
            self.assertEqual(by_date["2022-08-02"]["numerator_scope"], "sh_sz_bj_active_a")
            self.assertEqual(by_date["2022-08-02"]["chinext_close"], 2510)
            self.assertTrue(all(record["denominator_source"] == "sh880008" for record in payload["records"]))
            self.assertEqual(manifest["append_checkpoint"]["last_denominator_date"], "2022-08-02")
            self.assertEqual(manifest["denominator_segments"][0]["end"], "2022-08-02")
            self.assertEqual(manifest["numerator_segments"][1]["end"], "2022-08-02")
            self.assertEqual({path.name for path in output_dir.iterdir()}, {PAYLOAD_FILENAME, MANIFEST_FILENAME, CSV_FILENAME})

            before_rerun = {name: (output_dir / name).read_bytes() for name in (PAYLOAD_FILENAME, MANIFEST_FILENAME, CSV_FILENAME)}
            no_change = self.run_append(project_root, tdx_root, output_dir)
            self.assertEqual(no_change["status"], "no_changes")
            self.assertEqual(
                {name: (output_dir / name).read_bytes() for name in before_rerun}, before_rerun
            )

    def test_advances_checkpoint_for_nonpositive_denominator_without_output_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project_root, tdx_root, output_dir = self.create_baseline(root)
            sh_dir = tdx_root / "vipdoc/sh/lday"
            sz_dir = tdx_root / "vipdoc/sz/lday"
            write_day(sh_dir / "sh880008.day", [(20220801, 1, 0, 1)], append=True)
            write_day(sz_dir / "sz399006.day", [(20220801, 2_500, 1, 1)], append=True)

            updated = self.run_append(project_root, tdx_root, output_dir)
            self.assertEqual(updated["status"], "updated")
            self.assertEqual(updated["records_added"], 0)
            payload = json.loads((output_dir / PAYLOAD_FILENAME).read_text(encoding="utf-8"))
            manifest = json.loads((output_dir / MANIFEST_FILENAME).read_text(encoding="utf-8"))
            self.assertEqual(payload["records"][-1]["date"], "2022-07-29")
            self.assertEqual(manifest["append_checkpoint"]["last_denominator_date"], "2022-08-01")
            self.assertEqual(manifest["omitted_dates"][-1], {"date": "2022-08-01", "reason": "sh880008_not_positive"})

            before_rerun = {name: (output_dir / name).read_bytes() for name in (PAYLOAD_FILENAME, MANIFEST_FILENAME, CSV_FILENAME)}
            no_change = self.run_append(project_root, tdx_root, output_dir)
            self.assertEqual(no_change["status"], "no_changes")
            self.assertEqual(
                {name: (output_dir / name).read_bytes() for name in before_rerun}, before_rerun
            )


if __name__ == "__main__":
    unittest.main()

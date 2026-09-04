from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
from datetime import datetime, timezone
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


def write_ai_chain_workbook(project_root: Path, codes: list[str]) -> None:
    workbook_path = project_root / "watchlists" / "AI产业链.xlsx"
    workbook_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        '<x:row r="1"><x:c r="B1" t="inlineStr"><x:is><x:t>代码</x:t></x:is></x:c></x:row>',
        *[
            f'<x:row r="{index}"><x:c r="B{index}" t="inlineStr"><x:is><x:t>{code}</x:t></x:is></x:c></x:row>'
            for index, code in enumerate(codes, start=2)
        ],
    ]
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<x:workbook xmlns:x="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<x:sheets><x:sheet name="AI产业链" sheetId="1" r:id="rId1"/></x:sheets></x:workbook>'
    )
    relationships_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/></Relationships>'
    )
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<x:worksheet xmlns:x="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<x:sheetData>{"".join(rows)}</x:sheetData></x:worksheet>'
    )
    with zipfile.ZipFile(workbook_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", relationships_xml)
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)


class TradingConcentrationTailAppendTests(unittest.TestCase):
    def create_baseline(self, root: Path) -> tuple[Path, Path, Path]:
        project_root = root / "project"
        project_root.mkdir()
        (project_root / "AGENTS.md").write_text("test\n", encoding="utf-8")
        write_ai_chain_workbook(project_root, ["600000", "920001"])
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
            comparison_index_input = manifest["comparison_index_input"]
            comparison_index_path = sz_dir / "sz399006.day"
            self.assertEqual(
                comparison_index_input["data_range"],
                {"start": "2022-07-29", "end": "2022-08-02"},
            )
            self.assertEqual(comparison_index_input["bytes"], comparison_index_path.stat().st_size)
            self.assertEqual(
                comparison_index_input["sha256"],
                hashlib.sha256(comparison_index_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                comparison_index_input["last_write_time_utc"],
                datetime.fromtimestamp(
                    comparison_index_path.stat().st_mtime_ns / 1_000_000_000,
                    tz=timezone.utc,
                ).isoformat(timespec="seconds"),
            )
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

    def test_appends_ai_chain_series_after_its_start_date(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project_root = root / "project"
            project_root.mkdir()
            (project_root / "AGENTS.md").write_text("test\n", encoding="utf-8")
            write_ai_chain_workbook(project_root, ["600000", "920139"])
            tdx_root = root / "HT"
            sh_dir = tdx_root / "vipdoc/sh/lday"
            sz_dir = tdx_root / "vipdoc/sz/lday"
            bj_dir = tdx_root / "vipdoc/bj/lday"
            write_day(sh_dir / "sh880008.day", [(20241231, 1, 10_000, 1)])
            write_day(sz_dir / "sz399006.day", [(20241231, 2_400, 1, 1)])
            for offset in range(20):
                write_day(sh_dir / f"sh600{offset:03d}.day", [(20241231, 1, 100 + offset, 1)])
            write_day(bj_dir / "bj920139.day", [(20250102, 1, 500, 1)])
            output_dir = root / "output"
            built = subprocess.run(
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
                    "20241231",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            baseline = json.loads((output_dir / PAYLOAD_FILENAME).read_text(encoding="utf-8"))
            baseline_records = baseline["records"]
            baseline_csv_lines = (output_dir / CSV_FILENAME).read_text(encoding="utf-8").splitlines()
            self.assertEqual(baseline["ai_chain_series"]["records"], [])

            write_day(sh_dir / "sh880008.day", [(20250102, 1, 10_000, 1)], append=True)
            write_day(sz_dir / "sz399006.day", [(20250102, 2_500, 1, 1)], append=True)
            for offset in range(20):
                write_day(
                    sh_dir / f"sh600{offset:03d}.day", [(20250102, 1, 100 + offset, 1)], append=True
                )

            result = self.run_append(project_root, tdx_root, output_dir)
            self.assertEqual(result["status"], "updated")
            self.assertEqual(result["ai_chain_records_added"], 1)
            payload = json.loads((output_dir / PAYLOAD_FILENAME).read_text(encoding="utf-8"))
            self.assertEqual(payload["records"][: len(baseline_records)], baseline_records)
            self.assertEqual(
                (output_dir / CSV_FILENAME).read_text(encoding="utf-8").splitlines()[: len(baseline_csv_lines)],
                baseline_csv_lines,
            )
            self.assertEqual(
                payload["ai_chain_series"]["records"],
                [
                    {
                        "date": "2025-01-02",
                        "ai_chain_amount_pct": 6.0,
                        "ai_chain_amount_yi": 0.000006,
                        "ai_chain_active_stock_count": 2,
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()

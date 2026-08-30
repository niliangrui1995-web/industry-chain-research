from __future__ import annotations

import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
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


class TradingConcentrationBuilderTests(unittest.TestCase):
    def test_compact_date_conversion_and_prefix_filters(self) -> None:
        self.assertEqual(MODULE.compact_date_to_iso(20160126), "2016-01-26")
        self.assertEqual(MODULE.parse_compact_date("20220802"), 20220802)
        self.assertTrue("689" in MODULE.CANDIDATE_PREFIXES["sh"])
        self.assertFalse("899" in MODULE.CANDIDATE_PREFIXES["bj"])

    def test_ai_series_skips_c5_omitted_calendar_date(self) -> None:
        denominator_rows = [
            MODULE.DenominatorRow(date=20250102, amount_yuan=10_000, source="sh880008"),
            MODULE.DenominatorRow(date=20250103, amount_yuan=10_000, source="sh880008"),
        ]
        amount_matrix = MODULE.np.asarray([[0.0], [500.0]], dtype=MODULE.np.float32)

        records = MODULE.build_ai_chain_series_records(
            denominator_rows,
            amount_matrix,
            c5_output_dates={20250103},
        )

        self.assertEqual(
            records,
            [
                {
                    "date": "2025-01-03",
                    "ai_chain_amount_pct": 5.0,
                    "ai_chain_amount_yi": 0.000005,
                    "ai_chain_active_stock_count": 1,
                }
            ],
        )

    def test_ai_universe_rejects_workbook_change_during_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary)
            write_ai_chain_workbook(project_root, ["600000"])
            universe = MODULE.load_ai_chain_universe(project_root)
            universe.workbook_path.write_bytes(b"changed during calculation")

            with self.assertRaisesRegex(RuntimeError, "工作簿发生变化"):
                MODULE.assert_ai_chain_universe_unchanged(universe)

    def test_builds_segments_top5_and_manifest_without_raw_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project_root = root / "project"
            project_root.mkdir()
            (project_root / "AGENTS.md").write_text("test\n", encoding="utf-8")
            write_ai_chain_workbook(project_root, ["600000", "920001"])
            tdx_root = root / "HT"
            sh_dir = tdx_root / "vipdoc/sh/lday"
            sz_dir = tdx_root / "vipdoc/sz/lday"
            bj_dir = tdx_root / "vipdoc/bj/lday"

            write_day(
                sh_dir / "sh880008.day",
                [
                    (20160125, 1, 50_000, 1),
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
            self.assertEqual(by_date["2016-01-25"]["denominator_source"], "sh880008")
            self.assertEqual(by_date["2016-01-26"]["active_stock_count"], 21)
            self.assertEqual(by_date["2016-01-26"]["top5_stock_count"], 2)
            self.assertEqual(by_date["2022-08-01"]["active_stock_count"], 21)
            self.assertEqual(by_date["2022-08-01"]["numerator_scope"], "sh_sz_active_a")
            self.assertEqual(by_date["2022-08-02"]["active_stock_count"], 22)
            self.assertEqual(by_date["2022-08-02"]["numerator_scope"], "sh_sz_bj_active_a")
            self.assertGreater(by_date["2022-08-02"]["c5_pct"], by_date["2022-08-01"]["c5_pct"])
            self.assertFalse(manifest["raw_data_copied"])
            self.assertEqual(
                manifest["denominator_segments"],
                [
                    {
                        "start": "2013-01-01",
                        "end": "2022-08-02",
                        "source": "sh880008",
                        "formula": "sh880008.day.amount",
                    }
                ],
            )
            self.assertTrue(all(record["denominator_source"] == "sh880008" for record in payload["records"]))
            self.assertEqual(manifest["candidate_file_count"]["bj"], 1)
            self.assertEqual(manifest["comparison_index_input"]["code"], "399006")
            self.assertEqual(manifest["comparison_index_input"]["missing_output_records"], 0)
            self.assertEqual(payload["ai_chain_series"]["records"], [])
            self.assertEqual(manifest["ai_chain_series"]["universe"]["resolved_code_count"], 2)
            MODULE.verify_artifact_bundle(
                output_dir / MODULE.PAYLOAD_FILENAME,
                output_dir / MODULE.MANIFEST_FILENAME,
                output_dir / MODULE.CSV_FILENAME,
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import build_tdx_trading_concentration as builder


TASK_DIRECTORY = Path(__file__).parent
BUILDER_SCRIPT = TASK_DIRECTORY / "build_tdx_trading_concentration.py"
BACKFILL_SCRIPT = TASK_DIRECTORY / "backfill_ai_chain_turnover_share.py"
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


class AIChainBackfillTests(unittest.TestCase):
    def test_backfill_preserves_c5_and_csv_and_refreshes_same_universe_metadata(self) -> None:
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
            calendar = [(20241231, 1, 10_000, 1), (20250102, 1, 10_000, 1)]
            write_day(sh_dir / "sh880008.day", calendar)
            write_day(sz_dir / "sz399006.day", [(20241231, 2_400, 1, 1), (20250102, 2_500, 1, 1)])
            for offset in range(20):
                write_day(
                    sh_dir / f"sh600{offset:03d}.day",
                    [(20241231, 1, 100 + offset, 1), (20250102, 1, 100 + offset, 1)],
                )
            write_day(bj_dir / "bj920139.day", [(20250102, 1, 500, 1)])
            output_dir = root / "output"
            build = subprocess.run(
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
            self.assertEqual(build.returncode, 0, build.stderr)

            payload_path = output_dir / builder.PAYLOAD_FILENAME
            manifest_path = output_dir / builder.MANIFEST_FILENAME
            csv_path = output_dir / builder.CSV_FILENAME
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            legacy_records = payload["records"]
            legacy_csv = csv_path.read_bytes()
            payload.pop("ai_chain_series")
            manifest.pop("ai_chain_series")
            builder.atomic_write_bytes(builder.json_bytes(payload), payload_path)
            manifest["payload_sha256"] = builder.sha256_file(payload_path)
            manifest["csv_sha256"] = builder.sha256_file(csv_path)
            builder.atomic_write_bytes(builder.json_bytes(manifest), manifest_path)
            builder.verify_artifact_bundle(payload_path, manifest_path, csv_path)

            backfill = subprocess.run(
                [
                    sys.executable,
                    str(BACKFILL_SCRIPT),
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
            self.assertEqual(backfill.returncode, 0, backfill.stderr)
            result = json.loads(backfill.stdout)
            self.assertEqual(result["status"], "backfilled")
            self.assertTrue(result["c5_records_preserved"])
            self.assertTrue(result["csv_bytes_preserved"])

            migrated_payload = json.loads(payload_path.read_text(encoding="utf-8"))
            migrated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(migrated_payload["records"], legacy_records)
            self.assertEqual(csv_path.read_bytes(), legacy_csv)
            self.assertEqual(
                migrated_payload["ai_chain_series"]["records"],
                [
                    {
                        "date": "2025-01-02",
                        "ai_chain_amount_pct": 6.0,
                        "ai_chain_amount_yi": 0.000006,
                        "ai_chain_active_stock_count": 2,
                    }
                ],
            )
            self.assertEqual(migrated_manifest["ai_chain_series"]["universe"]["code_aliases"], [])
            builder.verify_artifact_bundle(payload_path, manifest_path, csv_path)

            refresh = subprocess.run(
                [
                    sys.executable,
                    str(BACKFILL_SCRIPT),
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
            self.assertEqual(refresh.returncode, 0, refresh.stderr)
            refresh_result = json.loads(refresh.stdout)
            self.assertEqual(refresh_result["status"], "universe_metadata_refreshed")
            self.assertTrue(refresh_result["ai_chain_records_preserved"])
            refreshed_payload = json.loads(payload_path.read_text(encoding="utf-8"))
            self.assertEqual(refreshed_payload["records"], legacy_records)
            self.assertEqual(refreshed_payload["ai_chain_series"]["records"], migrated_payload["ai_chain_series"]["records"])
            self.assertEqual(csv_path.read_bytes(), legacy_csv)
            builder.verify_artifact_bundle(payload_path, manifest_path, csv_path)


if __name__ == "__main__":
    unittest.main()

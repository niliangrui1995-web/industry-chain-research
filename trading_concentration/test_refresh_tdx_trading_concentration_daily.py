from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import build_tdx_trading_concentration as builder
import refresh_tdx_trading_concentration_daily as refresher


TASK_DIRECTORY = Path(__file__).parent
BUILDER_SCRIPT = TASK_DIRECTORY / "build_tdx_trading_concentration.py"
REFRESH_SCRIPT = TASK_DIRECTORY / "refresh_tdx_trading_concentration_daily.py"
DAY_RECORD = struct.Struct("<IIIIIfII")


def day_bytes(rows: list[tuple[int, float, float, float]]) -> bytes:
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
    return bytes(body)


def write_day(path: Path, rows: list[tuple[int, float, float, float]], *, append: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = day_bytes(rows)
    path.write_bytes(path.read_bytes() + payload if append and path.exists() else payload)


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


class DailyRefreshTests(unittest.TestCase):
    def create_baseline(
        self, root: Path, *, codes: list[str] = ["600000", "920139"]
    ) -> tuple[Path, Path, Path]:
        project_root = root / "project"
        project_root.mkdir()
        (project_root / "AGENTS.md").write_text("test\n", encoding="utf-8")
        write_ai_chain_workbook(project_root, codes)
        tdx_root = root / "HT"
        sh_dir = tdx_root / "vipdoc/sh/lday"
        sz_dir = tdx_root / "vipdoc/sz/lday"
        bj_dir = tdx_root / "vipdoc/bj/lday"
        write_day(sh_dir / "sh880008.day", [(20250102, 1, 10_000, 1)])
        write_day(sz_dir / "sz399006.day", [(20250102, 2_500, 1, 1)])
        for offset in range(20):
            write_day(sh_dir / f"sh600{offset:03d}.day", [(20250102, 1, 100 + offset, 1)])
        write_day(bj_dir / "bj920139.day", [(20250102, 1, 500, 1)])
        write_day(bj_dir / "bj920001.day", [(20250102, 1, 900, 1)])
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
                "20250102",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(built.returncode, 0, built.stderr)
        return project_root, tdx_root, output_dir

    def append_tail(self, tdx_root: Path) -> None:
        sh_dir = tdx_root / "vipdoc/sh/lday"
        sz_dir = tdx_root / "vipdoc/sz/lday"
        bj_dir = tdx_root / "vipdoc/bj/lday"
        write_day(sh_dir / "sh880008.day", [(20250103, 1, 20_000, 1)], append=True)
        write_day(sz_dir / "sz399006.day", [(20250103, 2_510, 1, 1)], append=True)
        for offset in range(20):
            write_day(
                sh_dir / f"sh600{offset:03d}.day",
                [(20250103, 1, 200 + offset, 1)],
                append=True,
            )
        write_day(bj_dir / "bj920139.day", [(20250103, 1, 600, 1)], append=True)
        write_day(bj_dir / "bj920001.day", [(20250103, 1, 1_000, 1)], append=True)

    def run_refresh(self, project_root: Path, tdx_root: Path, output_dir: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(REFRESH_SCRIPT),
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

    def test_member_change_rebuilds_ai_then_appends_and_preserves_c5_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_root, tdx_root, output_dir = self.create_baseline(Path(temporary))
            payload_path = output_dir / builder.PAYLOAD_FILENAME
            manifest_path = output_dir / builder.MANIFEST_FILENAME
            csv_path = output_dir / builder.CSV_FILENAME
            baseline_payload = json.loads(payload_path.read_text(encoding="utf-8"))
            baseline_records = baseline_payload["records"]
            baseline_csv = csv_path.read_bytes()

            write_ai_chain_workbook(project_root, ["600000", "920001"])
            self.append_tail(tdx_root)
            refreshed = self.run_refresh(project_root, tdx_root, output_dir)
            self.assertEqual(refreshed.returncode, 0, refreshed.stderr + refreshed.stdout)
            result = json.loads(refreshed.stdout)
            self.assertEqual(result["status"], "updated")
            self.assertEqual(result["ai_chain_action"], "rebuild_then_append")
            self.assertEqual(result["ai_chain_membership"]["status"], "changed")
            self.assertEqual(result["rebuild"]["status"], "universe_rebuilt")
            self.assertEqual(result["append"]["status"], "updated")
            self.assertFalse(result["published"])

            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["records"][: len(baseline_records)], baseline_records)
            self.assertTrue(csv_path.read_bytes().startswith(baseline_csv))
            self.assertEqual(
                payload["ai_chain_series"]["records"],
                [
                    {
                        "date": "2025-01-02",
                        "ai_chain_amount_pct": 10.0,
                        "ai_chain_amount_yi": 0.00001,
                        "ai_chain_active_stock_count": 2,
                    },
                    {
                        "date": "2025-01-03",
                        "ai_chain_amount_pct": 6.0,
                        "ai_chain_amount_yi": 0.000012,
                        "ai_chain_active_stock_count": 2,
                    },
                ],
            )
            builder.verify_artifact_bundle(payload_path, manifest_path, csv_path)

    def test_row_reorder_uses_tail_append_without_ai_rebuild(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_root, tdx_root, output_dir = self.create_baseline(Path(temporary))
            payload_path = output_dir / builder.PAYLOAD_FILENAME
            baseline_payload = json.loads(payload_path.read_text(encoding="utf-8"))
            baseline_ai_records = baseline_payload["ai_chain_series"]["records"]

            write_ai_chain_workbook(project_root, ["920139", "600000"])
            self.append_tail(tdx_root)
            refreshed = self.run_refresh(project_root, tdx_root, output_dir)
            self.assertEqual(refreshed.returncode, 0, refreshed.stderr + refreshed.stdout)
            result = json.loads(refreshed.stdout)
            self.assertEqual(result["status"], "updated")
            self.assertEqual(result["ai_chain_action"], "append")
            self.assertEqual(result["ai_chain_membership"]["status"], "matched")
            self.assertIsNone(result["rebuild"])
            self.assertEqual(result["append"]["status"], "updated")

            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["ai_chain_series"]["records"][: len(baseline_ai_records)],
                baseline_ai_records,
            )
            self.assertEqual(len(payload["ai_chain_series"]["records"]), 2)

    def test_legacy_member_fingerprint_rebuilds_once_even_when_members_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_root, tdx_root, output_dir = self.create_baseline(Path(temporary))
            payload_path = output_dir / builder.PAYLOAD_FILENAME
            manifest_path = output_dir / builder.MANIFEST_FILENAME
            csv_path = output_dir / builder.CSV_FILENAME
            baseline_payload = json.loads(payload_path.read_text(encoding="utf-8"))
            baseline_records = baseline_payload["records"]
            baseline_csv = csv_path.read_bytes()
            baseline_payload["ai_chain_series"]["universe"].pop("member_codes_sha256")
            baseline_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            baseline_manifest["ai_chain_series"]["universe"].pop("member_codes_sha256")
            builder.atomic_write_bytes(builder.json_bytes(baseline_payload), payload_path)
            baseline_manifest["payload_sha256"] = builder.sha256_file(payload_path)
            baseline_manifest["csv_sha256"] = builder.sha256_file(csv_path)
            builder.atomic_write_bytes(builder.json_bytes(baseline_manifest), manifest_path)
            builder.verify_artifact_bundle(payload_path, manifest_path, csv_path)

            refreshed = self.run_refresh(project_root, tdx_root, output_dir)
            self.assertEqual(refreshed.returncode, 0, refreshed.stderr + refreshed.stdout)
            result = json.loads(refreshed.stdout)
            self.assertEqual(result["status"], "ai_chain_rebuilt")
            self.assertEqual(result["ai_chain_action"], "rebuild_then_append")
            self.assertEqual(
                result["ai_chain_membership"]["status"], "legacy_member_fingerprint_missing"
            )
            self.assertEqual(result["rebuild"]["status"], "universe_rebuilt")
            self.assertEqual(result["append"]["status"], "no_changes")
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["records"], baseline_records)
            self.assertEqual(csv_path.read_bytes(), baseline_csv)
            self.assertIn("member_codes_sha256", payload["ai_chain_series"]["universe"])
            builder.verify_artifact_bundle(payload_path, manifest_path, csv_path)

    def test_missing_new_member_day_file_fails_with_machine_readable_json_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_root, tdx_root, output_dir = self.create_baseline(Path(temporary))
            payload_path = output_dir / builder.PAYLOAD_FILENAME
            manifest_path = output_dir / builder.MANIFEST_FILENAME
            csv_path = output_dir / builder.CSV_FILENAME
            before = {path.name: path.read_bytes() for path in (payload_path, manifest_path, csv_path)}
            write_ai_chain_workbook(project_root, ["600000", "920002"])

            failed = self.run_refresh(project_root, tdx_root, output_dir)
            self.assertNotEqual(failed.returncode, 0)
            failure = json.loads(failed.stdout)
            self.assertEqual(failure["status"], "failed")
            self.assertEqual(failure["error_type"], "FileNotFoundError")
            self.assertIn("920002.BJ", failure["error"])
            self.assertEqual(
                {path.name: path.read_bytes() for path in (payload_path, manifest_path, csv_path)},
                before,
            )

    def test_rebuild_append_failure_leaves_formal_bundle_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_root, tdx_root, output_dir = self.create_baseline(Path(temporary))
            paths = [
                output_dir / builder.PAYLOAD_FILENAME,
                output_dir / builder.MANIFEST_FILENAME,
                output_dir / builder.CSV_FILENAME,
            ]
            before = {path.name: path.read_bytes() for path in paths}
            write_ai_chain_workbook(project_root, ["600000", "920001"])

            with mock.patch.object(
                refresher.appender,
                "run_append",
                side_effect=RuntimeError("simulated_append_failure"),
            ):
                with self.assertRaisesRegex(RuntimeError, "simulated_append_failure"):
                    refresher.run_daily_refresh(
                        project_root=project_root,
                        tdx_root=tdx_root,
                        output_directory=output_dir,
                        publish_directory=None,
                    )

            self.assertEqual({path.name: path.read_bytes() for path in paths}, before)

    def test_staged_publish_uses_final_bundle_only_after_refresh_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project_root, tdx_root, output_dir = self.create_baseline(root)
            publish_dir = root / "publish"
            write_ai_chain_workbook(project_root, ["600000", "920001"])
            self.append_tail(tdx_root)

            with mock.patch.object(builder, "PUBLISH_DIRECTORY", publish_dir):
                result = refresher.run_daily_refresh(
                    project_root=project_root,
                    tdx_root=tdx_root,
                    output_directory=output_dir,
                    publish_directory=publish_dir,
                )

            self.assertEqual(result["status"], "updated")
            self.assertTrue(result["published"])
            self.assertEqual(
                (publish_dir / builder.PAYLOAD_FILENAME).read_bytes(),
                (output_dir / builder.PAYLOAD_FILENAME).read_bytes(),
            )
            self.assertEqual(
                (publish_dir / builder.MANIFEST_FILENAME).read_bytes(),
                (output_dir / builder.MANIFEST_FILENAME).read_bytes(),
            )

    def test_unapproved_publish_dir_is_rejected_before_formal_output_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project_root, tdx_root, output_dir = self.create_baseline(root)
            paths = [
                output_dir / builder.PAYLOAD_FILENAME,
                output_dir / builder.MANIFEST_FILENAME,
                output_dir / builder.CSV_FILENAME,
            ]
            before = {path.name: path.read_bytes() for path in paths}
            write_ai_chain_workbook(project_root, ["600000", "920001"])

            with self.assertRaisesRegex(ValueError, "publish-dir 必须是已授权"):
                refresher.run_daily_refresh(
                    project_root=project_root,
                    tdx_root=tdx_root,
                    output_directory=output_dir,
                    publish_directory=root / "unapproved-publish",
                )

            self.assertEqual({path.name: path.read_bytes() for path in paths}, before)

    def test_publish_failure_rolls_back_formal_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project_root, tdx_root, output_dir = self.create_baseline(root)
            paths = [
                output_dir / builder.PAYLOAD_FILENAME,
                output_dir / builder.MANIFEST_FILENAME,
                output_dir / builder.CSV_FILENAME,
            ]
            before = {path.name: path.read_bytes() for path in paths}
            publish_dir = root / "publish"
            write_ai_chain_workbook(project_root, ["600000", "920001"])
            self.append_tail(tdx_root)

            with (
                mock.patch.object(builder, "PUBLISH_DIRECTORY", publish_dir),
                mock.patch.object(
                    refresher.builder,
                    "publish_bundle_atomically",
                    side_effect=RuntimeError("simulated_publish_failure"),
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "simulated_publish_failure"):
                    refresher.run_daily_refresh(
                        project_root=project_root,
                        tdx_root=tdx_root,
                        output_directory=output_dir,
                        publish_directory=publish_dir,
                    )

            self.assertEqual({path.name: path.read_bytes() for path in paths}, before)
            self.assertFalse(publish_dir.exists())


if __name__ == "__main__":
    unittest.main()

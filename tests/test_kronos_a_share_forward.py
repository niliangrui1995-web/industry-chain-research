from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "kronos-market-forecasting" / "scripts"
sys.path.insert(0, str(SCRIPTS))
MODULE_PATH = SCRIPTS / "kronos_a_share_forward.py"


def load_module():
    spec = importlib.util.spec_from_file_location("kronos_a_share_forward", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ForwardRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def setUp(self) -> None:
        patcher = mock.patch.object(
            self.module,
            "verify_inference_snapshot",
            side_effect=lambda path, **_kwargs: json.loads(
                Path(path).read_text(encoding="utf-8")
            ),
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def _training_root(temporary: str) -> Path:
        root = Path(temporary).resolve() / "_training" / "kronos_ashare"
        root.mkdir(parents=True)
        return root

    def _rehash_batch(self, path: Path, payload: dict) -> None:
        semantic = dict(payload)
        semantic.pop("payload_sha256", None)
        semantic.pop("content_sha256", None)
        semantic.pop("recorded_at", None)
        payload["content_sha256"] = self.module._payload_hash(semantic)
        unsigned = dict(payload)
        unsigned.pop("payload_sha256", None)
        payload["payload_sha256"] = self.module._payload_hash(unsigned)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _record(
        self,
        root: Path,
        score: float = 0.1,
        *,
        path_override=None,
        receipt_binding_override=None,
        as_of_value=None,
        calendar_source_override=None,
    ):
        adapter_hash = "a" * 64
        scorer_hash = "c" * 64
        local_now = datetime.now(ZoneInfo("Asia/Shanghai"))
        as_of_value = (
            local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            if as_of_value is None
            else as_of_value
        )
        as_of = as_of_value.isoformat()
        inference_binding = {
            "schema_version": "kronos-a-share-inference-input-v1",
            "as_of": as_of,
            "universe_count": 2,
        }
        inference_hash = hashlib.sha256(
            json.dumps(
                inference_binding,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        inference_snapshot_id = (
            f"{as_of_value.strftime('%Y%m%d')}-{inference_hash[:16]}"
        )
        path = []
        future_dates = []
        target = as_of_value
        while len(future_dates) < 10:
            target += timedelta(days=1)
            if target.weekday() >= 5:
                continue
            future_dates.append(target.date().isoformat())
            path.append(
                {
                    "timestamp": target.date().isoformat(),
                    "open": 10.0,
                    "high": 10.5,
                    "low": 9.5,
                    "close": 10.1,
                    "volume": 100.0,
                    "amount": 1000.0,
                }
            )
        if path_override is not None:
            path = path_override
        snapshot_root = (
            root
            / "data"
            / "inference"
            / "snapshots"
            / inference_snapshot_id
        )
        calendar_path = snapshot_root / "pit" / "raw" / "official-calendar.csv"
        calendar_path.parent.mkdir(parents=True, exist_ok=True)
        calendar_path.write_text(
            "timestamps\n" + "\n".join(future_dates) + "\n",
            encoding="utf-8",
        )
        calendar_hash = hashlib.sha256(calendar_path.read_bytes()).hexdigest()
        source = {
            "path": calendar_path.relative_to(snapshot_root / "pit").as_posix(),
            "source_class": "official_primary",
            "role": "authoritative",
            "artifact_role": "trading_calendar",
            "artifact_schema_version": "kronos-a-share-trading-calendar-v1",
            "url": "https://www.sse.com.cn/official-calendar.csv",
            "sha256": calendar_hash,
        }
        if calendar_source_override is not None:
            source.update(calendar_source_override)
        provenance_path = snapshot_root / "pit" / "provenance" / "calendar.json"
        provenance_path.parent.mkdir(parents=True, exist_ok=True)
        provenance_path.write_text(
            json.dumps(
                {
                    "schema_version": "kronos-a-share-pit-provenance-v1",
                    "sources": [source],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        manifest = {
            "schema_version": "kronos-a-share-inference-snapshot-v1",
            "snapshot_id": inference_snapshot_id,
            "as_of": as_of,
            "input_binding": inference_binding,
            "input_sha256": inference_hash,
            "market_files": [],
            "pit_files": [
                {
                    "relative_path": calendar_path.relative_to(snapshot_root).as_posix(),
                    "role": "raw_response",
                    "dataset": "trading_calendar",
                    "bytes": calendar_path.stat().st_size,
                    "sha256": calendar_hash,
                },
                {
                    "relative_path": provenance_path.relative_to(snapshot_root).as_posix(),
                    "role": "provenance_manifest",
                    "dataset": "trading_calendar",
                    "bytes": provenance_path.stat().st_size,
                    "sha256": hashlib.sha256(provenance_path.read_bytes()).hexdigest(),
                },
            ],
        }
        manifest["payload_sha256"] = self.module._payload_hash(manifest)
        manifest_path = snapshot_root / "inference_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        record = {
            "as_of": as_of,
            "ticker": "300620.SZ",
            "horizon": 10,
            "raw_score": score,
            "percentile": 0.7,
            "forecast_path": path,
            "path_dispersion": 0.01,
            "dataset_id": "dataset-v1",
            "run_id": "run-v1",
            "adapter_hash": adapter_hash,
            "inference_snapshot_id": inference_snapshot_id,
            "inference_input_sha256": inference_hash,
            "gate_status": "passed",
            "constraint_flags": [],
            "evidence_class": "model_output",
            "output_type": "model_output",
        }
        gate = {
            "gate_status": "passed",
            "adapter_hash": adapter_hash,
            "scorer_checkpoint_hash": scorer_hash,
            "evaluated_checkpoint": "scorer-step-00000001",
            "binding": {"data_sha256": "b" * 64},
        }
        receipt = {
            "schema_version": "kronos-a-share-gate-receipt-v2",
            "gate_sha256": "e" * 64,
            "gate_status": "passed",
            "run_id": "run-v1",
            "binding": gate["binding"],
            "adapter_hash": adapter_hash,
            "scorer_checkpoint_hash": scorer_hash,
            "evaluated_checkpoint": gate["evaluated_checkpoint"],
            "gate_sequence": 1,
        }
        checkpoint_dir = root / "runs" / "run-v1" / "checkpoints"
        receipt_path = checkpoint_dir / "gate-receipts" / ("e" * 64 + ".json")
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        receipt_hash = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        event_core = {
            "schema_version": "kronos-a-share-gate-head-v1",
            "sequence": 1,
            "gate_sha256": "e" * 64,
            "gate_receipt_sha256": receipt_hash,
            "previous_event_sha256": None,
            "created_at": "2026-08-03T00:00:00+00:00",
        }
        event_hash = self.module._payload_hash(event_core)
        event = {**event_core, "event_sha256": event_hash}
        lineage_path = (
            checkpoint_dir / "gate-lineage" / f"00000001-{event_hash}.json"
        )
        lineage_path.parent.mkdir(parents=True, exist_ok=True)
        lineage_path.write_text(
            json.dumps(event, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (checkpoint_dir / "gate-head.json").write_text(
            json.dumps(event, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        receipt_binding = {
            "schema_version": "kronos-a-share-gate-receipt-binding-v2",
            "gate_sha256": "e" * 64,
            "gate_receipt_sha256": receipt_hash,
            "gate_receipt_schema_version": "kronos-a-share-gate-receipt-v2",
            "gate_receipt_path": str(receipt_path),
            "gate_sequence": 1,
        }
        if receipt_binding_override is not None:
            receipt_binding = receipt_binding_override
        return self.module.record_forward_batch(
            training_root=root,
            registry_root=root / "registry" / "forward-observations",
            as_of=as_of,
            records=[record],
            universe_scores=[
                {"ticker": "300620.SZ", "raw_score": score, "percentile": 0.7},
                {"ticker": "600330.SH", "raw_score": -score, "percentile": 0.3},
            ],
            gate=gate,
            inference_input_binding=inference_binding,
            inference_input_sha256=inference_hash,
            inference_snapshot_id=inference_snapshot_id,
            inference_manifest_path=manifest_path,
            inference_manifest_sha256=manifest_hash,
            future_calendar_path=calendar_path,
            release_receipt_binding=receipt_binding,
            authoritative_future_trading_dates=future_dates,
            minimum_days=60,
            recommended_days=120,
        )

    def test_atomic_record_is_idempotent_and_counted_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            first = self._record(root)
            second = self._record(root)
            self.assertEqual(first["status"], "recorded")
            self.assertEqual(second["status"], "reused")
            self.assertEqual(second["summary"]["observation_days"], 0)
            self.assertEqual(second["summary"]["pending_observation_days"], 1)
            self.assertFalse(second["summary"]["minimum_met"])
            batch = json.loads(Path(first["batch_path"]).read_text(encoding="utf-8"))
            self.assertEqual(
                batch["inference_input_sha256"],
                batch["records"][0]["inference_input_sha256"],
            )
            self.assertEqual(
                batch["release_receipt_binding"]["gate_sha256"], "e" * 64
            )
            self.assertEqual(batch["release_receipt_binding"]["gate_sequence"], 1)
            self.assertEqual(
                batch["authoritative_future_trading_dates"],
                [item["timestamp"] for item in batch["records"][0]["forecast_path"]],
            )
            self.assertFalse(Path(batch["inference_manifest_path"]).is_absolute())
            self.assertFalse(Path(batch["future_calendar_path"]).is_absolute())
            self.assertEqual(len(second["summary"]["batch_commitments"]), 1)
            self.assertEqual(
                set(second["summary"]["batch_commitments"][0]),
                {
                    "date",
                    "path",
                    "file_sha256",
                    "content_sha256",
                    "payload_sha256",
                    "gate_sha256",
                    "gate_receipt_sha256",
                    "gate_sequence",
                },
            )
            self.assertEqual(
                second["summary"]["batch_commitments"][0]["gate_sequence"], 1
            )

    def test_empty_root_is_stable_and_extra_batch_changes_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            empty_a = self.module.inspect_forward_registry(
                root / "registry" / "empty-a",
                root,
                minimum_days=60,
                recommended_days=120,
            )
            empty_b = self.module.inspect_forward_registry(
                root / "registry" / "empty-b",
                root,
                minimum_days=60,
                recommended_days=120,
            )
            self.assertEqual(empty_a["batch_commitments"], [])
            self.assertEqual(
                empty_a["registry_root_sha256"], empty_b["registry_root_sha256"]
            )

            first = self._record(root)
            first_root = first["summary"]["registry_root_sha256"]
            first_as_of = datetime.now(ZoneInfo("Asia/Shanghai")).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            second_as_of = first_as_of + timedelta(days=1)
            simulated_now = (second_as_of + timedelta(hours=1)).astimezone(
                timezone.utc
            )
            with mock.patch.object(
                self.module,
                "_utc_now",
                return_value=simulated_now,
            ):
                second = self._record(root, as_of_value=second_as_of)
            self.assertEqual(len(second["summary"]["batch_commitments"]), 2)
            self.assertNotEqual(
                first_root, second["summary"]["registry_root_sha256"]
            )

    def test_same_date_different_payload_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            self._record(root)
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "同一 adapter/as_of"
            ):
                self._record(root, score=0.2)

    def test_registry_rejects_duplicate_batch_date(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            result = self._record(root)
            path = Path(result["batch_path"])
            duplicate = path.with_name(path.name[:9] + "f" * 16 + ".json")
            duplicate.write_bytes(path.read_bytes())
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "重复批次日"
            ):
                self.module.inspect_forward_registry(
                    path.parent,
                    root,
                    minimum_days=60,
                    recommended_days=120,
                )

    def test_tampered_batch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            result = self._record(root)
            path = Path(result["batch_path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["records"][0]["raw_score"] = 99
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "SHA256 漂移"
            ):
                self.module.inspect_forward_registry(
                    path.parent,
                    root,
                    minimum_days=60,
                    recommended_days=120,
                )

    def test_rehashed_semantic_tamper_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            result = self._record(root)
            path = Path(result["batch_path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["records"][0]["gate_status"] = "forged"
            semantic = dict(payload)
            semantic.pop("payload_sha256", None)
            semantic.pop("content_sha256", None)
            semantic.pop("recorded_at", None)
            payload["content_sha256"] = self.module._payload_hash(semantic)
            unsigned = dict(payload)
            unsigned.pop("payload_sha256", None)
            payload["payload_sha256"] = self.module._payload_hash(unsigned)
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "gate/output_type"
            ):
                self.module.inspect_forward_registry(
                    path.parent,
                    root,
                    minimum_days=60,
                    recommended_days=120,
                )

    def test_payload_rehash_cannot_bypass_content_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            result = self._record(root)
            path = Path(result["batch_path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["records"][0]["raw_score"] = 99.0
            unsigned = dict(payload)
            unsigned.pop("payload_sha256", None)
            payload["payload_sha256"] = self.module._payload_hash(unsigned)
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "content SHA256"
            ):
                self.module.inspect_forward_registry(
                    path.parent,
                    root,
                    minimum_days=60,
                    recommended_days=120,
                )

    def test_fake_or_missing_receipt_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            fake = {
                "schema_version": "kronos-a-share-gate-receipt-binding-v2",
                "gate_sha256": "e" * 64,
                "gate_receipt_sha256": "f" * 64,
                "gate_receipt_schema_version": "kronos-a-share-gate-receipt-v2",
                "gate_receipt_path": str(root / "missing.json"),
                "gate_sequence": 1,
            }
            missing_sequence = dict(fake)
            missing_sequence.pop("gate_sequence")
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "gate_sequence"
            ):
                self._record(root, receipt_binding_override=missing_sequence)
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "receipt"
            ):
                self._record(root, receipt_binding_override=fake)

            result = self._record(root)
            path = Path(result["batch_path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            receipt = root / payload["release_receipt_binding"]["gate_receipt_path"]
            receipt.unlink()
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "receipt"
            ):
                self.module.inspect_forward_registry(
                    path.parent,
                    root,
                    minimum_days=60,
                    recommended_days=120,
                )

    def test_rehashed_receipt_still_must_match_gate_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            result = self._record(root)
            path = Path(result["batch_path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            receipt_path = root / payload["release_receipt_binding"][
                "gate_receipt_path"
            ]
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["run_id"] = "forged-run"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            payload["release_receipt_binding"]["gate_receipt_sha256"] = (
                hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            )
            semantic = dict(payload)
            semantic.pop("payload_sha256", None)
            semantic.pop("content_sha256", None)
            semantic.pop("recorded_at", None)
            payload["content_sha256"] = self.module._payload_hash(semantic)
            unsigned = dict(payload)
            unsigned.pop("payload_sha256", None)
            payload["payload_sha256"] = self.module._payload_hash(unsigned)
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "gate/批次绑定"
            ):
                self.module.inspect_forward_registry(
                    path.parent,
                    root,
                    minimum_days=60,
                    recommended_days=120,
                )

    def test_standalone_receipt_without_active_lineage_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            result = self._record(root)
            batch_path = Path(result["batch_path"])
            head_path = root / "runs" / "run-v1" / "checkpoints" / "gate-head.json"
            head_path.unlink()
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "lineage/head"
            ):
                self.module.inspect_forward_registry(
                    batch_path.parent,
                    root,
                    minimum_days=60,
                    recommended_days=120,
                )

    def test_minute_forecast_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            as_of = datetime.now(ZoneInfo("Asia/Shanghai")).replace(
                hour=15, minute=0, second=0, microsecond=0
            )
            minute_path = [
                {
                    "timestamp": (as_of + timedelta(minutes=offset)).isoformat(),
                    "open": 10.0,
                    "high": 10.5,
                    "low": 9.5,
                    "close": 10.1,
                    "volume": 100.0,
                    "amount": 1000.0,
                }
                for offset in range(1, 11)
            ]
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "日频交易日"
            ):
                self._record(root, path_override=minute_path)

    def test_rehashed_batch_cannot_drift_from_inference_input_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            result = self._record(root)
            path = Path(result["batch_path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["inference_input_binding"]["universe_count"] = 999
            semantic = dict(payload)
            semantic.pop("payload_sha256", None)
            semantic.pop("content_sha256", None)
            semantic.pop("recorded_at", None)
            payload["content_sha256"] = self.module._payload_hash(semantic)
            unsigned = dict(payload)
            unsigned.pop("payload_sha256", None)
            payload["payload_sha256"] = self.module._payload_hash(unsigned)
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError,
                "inference input SHA256 不匹配",
            ):
                self.module.inspect_forward_registry(
                    path.parent,
                    root,
                    minimum_days=60,
                    recommended_days=120,
                )

    def test_inference_snapshot_manifest_and_inventory_are_reverified(self) -> None:
        for mutation, expected in (
            ("delete_file", "文件缺失"),
            ("tamper_manifest", "manifest 文件 SHA256"),
            ("add_file", "文件集合漂移"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = self._training_root(temporary)
                result = self._record(root)
                batch_path = Path(result["batch_path"])
                payload = json.loads(batch_path.read_text(encoding="utf-8"))
                manifest_path = root / payload["inference_manifest_path"]
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if mutation == "delete_file":
                    (manifest_path.parent / manifest["pit_files"][0]["relative_path"]).unlink()
                elif mutation == "tamper_manifest":
                    manifest["snapshot_id"] = "forged"
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                else:
                    (manifest_path.parent / "unexpected.bin").write_bytes(b"unexpected")
                with self.assertRaisesRegex(
                    self.module.ForwardRegistryError,
                    expected,
                ):
                    self.module.inspect_forward_registry(
                        batch_path.parent,
                        root,
                        minimum_days=60,
                        recommended_days=120,
                    )

    def test_rehashed_batch_future_dates_must_match_bound_calendar(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            result = self._record(root)
            path = Path(result["batch_path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            dates = [datetime.fromisoformat(value) for value in payload["authoritative_future_trading_dates"]]
            next_date = dates[-1]
            while True:
                next_date += timedelta(days=1)
                if next_date.weekday() < 5:
                    break
            shifted = [item.date().isoformat() for item in [*dates[1:], next_date]]
            payload["authoritative_future_trading_dates"] = shifted
            payload["target_date"] = shifted[-1]
            for row, value in zip(payload["records"][0]["forecast_path"], shifted):
                row["timestamp"] = value
            self._rehash_batch(path, payload)
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError,
                "绑定交易日历不一致",
            ):
                self.module.inspect_forward_registry(
                    path.parent,
                    root,
                    minimum_days=60,
                    recommended_days=120,
                )

    def test_forecast_path_requires_exact_finite_valid_ohlcva(self) -> None:
        cases = (
            ("extra", lambda row: row.__setitem__("extra", 1), "固定 OHLCVA"),
            ("nan", lambda row: row.__setitem__("amount", "NaN"), "NaN/Inf"),
            ("nonpositive", lambda row: row.__setitem__("open", 0), "OHLC 必须为正数"),
            ("ohlc", lambda row: row.__setitem__("high", 9.0), "OHLC 关系无效"),
            ("negative_volume", lambda row: row.__setitem__("volume", -1), "不得为负"),
        )
        for name, mutate, expected in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = self._training_root(temporary)
                result = self._record(root)
                path = Path(result["batch_path"])
                payload = json.loads(path.read_text(encoding="utf-8"))
                mutate(payload["records"][0]["forecast_path"][0])
                self._rehash_batch(path, payload)
                with self.assertRaisesRegex(
                    self.module.ForwardRegistryError,
                    expected,
                ):
                    self.module.inspect_forward_registry(
                        path.parent,
                        root,
                        minimum_days=60,
                        recommended_days=120,
                    )

    def test_future_calendar_requires_dedicated_official_schema(self) -> None:
        cases = (
            ({"artifact_role": "arbitrary"}, "artifact role"),
            ({"artifact_schema_version": "unknown"}, "schema"),
            ({"url": "https://example.com/calendar.csv"}, "官方来源"),
        )
        for override, expected in cases:
            with self.subTest(override=override), tempfile.TemporaryDirectory() as temporary:
                root = self._training_root(temporary)
                with self.assertRaisesRegex(
                    self.module.ForwardRegistryError,
                    expected,
                ):
                    self._record(root, calendar_source_override=override)

    def test_blocked_gate_cannot_write_forward_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._training_root(temporary)
            with self.assertRaisesRegex(
                self.module.ForwardRegistryError, "passed 或前瞻观察专用 gate"
            ):
                self.module.record_forward_batch(
                    training_root=root,
                    registry_root=root / "registry" / "forward-observations",
                    as_of="2026-08-03T15:00:00+08:00",
                    records=[],
                    universe_scores=[],
                    gate={"gate_status": "blocked", "adapter_hash": "a" * 64},
                    inference_input_binding={},
                    inference_input_sha256="b" * 64,
                    inference_snapshot_id="20260803-" + "b" * 16,
                    inference_manifest_path=root / "missing-inference-manifest.json",
                    inference_manifest_sha256="d" * 64,
                    future_calendar_path=root / "missing-calendar.csv",
                    release_receipt_binding={
                        "schema_version": "kronos-a-share-gate-receipt-binding-v2",
                        "gate_sha256": "e" * 64,
                        "gate_receipt_sha256": "f" * 64,
                        "gate_receipt_schema_version": "kronos-a-share-gate-receipt-v2",
                        "gate_receipt_path": str(root / "missing.json"),
                        "gate_sequence": 1,
                    },
                    authoritative_future_trading_dates=[
                        f"2026-08-{day:02d}" for day in range(4, 14)
                    ],
                    minimum_days=60,
                    recommended_days=120,
                )


if __name__ == "__main__":
    unittest.main()

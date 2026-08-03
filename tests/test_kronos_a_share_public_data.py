from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / ".agents" / "skills" / "kronos-market-forecasting" / "scripts" / "kronos_a_share_public_data.py"


def load_module():
    spec = importlib.util.spec_from_file_location("kronos_a_share_public_data", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(
        self,
        payload: bytes,
        final_url: str = "https://example.invalid/source.csv",
    ) -> None:
        self.payload = payload
        self.final_url = final_url
        self.headers = {"Content-Type": "text/csv"}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return None

    def read(self) -> bytes:
        return self.payload

    def geturl(self) -> str:
        return self.final_url


class FakeQueryResult:
    def __init__(
        self,
        rows: list[list[str]],
        *,
        fields: list[str] | None = None,
        error_code: str = "0",
        error_msg: str = "",
    ) -> None:
        self.fields = fields or ["date", "code", "tradestatus", "isST"]
        self.error_code = error_code
        self.error_msg = error_msg
        self._rows = rows
        self._index = -1

    def next(self) -> bool:
        self._index += 1
        return self._index < len(self._rows)

    def get_row_data(self) -> list[str]:
        return self._rows[self._index]


class FakeBaostock:
    def __init__(self, results: dict[str, FakeQueryResult]) -> None:
        self.results = results
        self.login_count = 0
        self.logout_count = 0
        self.queries: list[tuple[str, str, str]] = []

    def login(self):
        self.login_count += 1
        return SimpleNamespace(error_code="0", error_msg="")

    def logout(self):
        self.logout_count += 1
        return SimpleNamespace(error_code="0", error_msg="")

    def query_history_k_data_plus(
        self,
        symbol: str,
        fields: str,
        *,
        start_date: str,
        end_date: str,
        frequency: str,
        adjustflag: str,
    ) -> FakeQueryResult:
        self.queries.append((symbol, start_date, end_date))
        return self.results[symbol]


def tree_bytes(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in directory.rglob("*")
        if path.is_file()
    }


class KronosAsharePublicDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_rejects_output_outside_training_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            with self.assertRaisesRegex(self.module.PublicDataError, "path_outside_training_root"):
                self.module.ensure_within(Path(tmp) / "other", root)

    def test_snapshots_explicit_https_source_with_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = root / "sources.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": self.module.SOURCE_SCHEMA,
                        "sources": [
                            {
                                "source_id": "official-test",
                                "source_class": "official_primary",
                                "url": "https://example.invalid/source.csv",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(
                self.module.urllib.request,
                "urlopen",
                return_value=FakeResponse(b"date,value\n2026-01-01,1\n"),
            ):
                result = self.module.snapshot_url_manifest(manifest, root / "raw", root)
            self.assertEqual(result["source_count"], 1)
            self.assertTrue((root / "raw" / "official-test.csv").is_file())
            self.assertTrue((root / "raw" / "snapshot_manifest.json").is_file())

    def test_calendar_snapshot_cryptographically_binds_fixed_artifact_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = root / "sources.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": self.module.SOURCE_SCHEMA,
                        "sources": [
                            {
                                "source_id": "official-calendar",
                                "source_class": "official_primary",
                                "url": "https://www.sse.com.cn/calendar.csv",
                                "artifact_role": "trading_calendar",
                                "artifact_schema_version": (
                                    "kronos-a-share-trading-calendar-v1"
                                ),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(
                self.module.urllib.request,
                "urlopen",
                return_value=FakeResponse(
                    b"timestamps\n2026-08-03\n",
                    final_url="https://www.sse.com.cn/calendar.csv",
                ),
            ):
                result = self.module.snapshot_url_manifest(
                    manifest, root / "raw", root
                )
            record = result["sources"][0]
            self.assertEqual(record["artifact_role"], "trading_calendar")
            self.assertEqual(
                record["artifact_schema_version"],
                "kronos-a-share-trading-calendar-v1",
            )
            persisted = json.loads(
                (root / "raw" / "snapshot_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(persisted["sources"][0]["sha256"], record["sha256"])

            invalid = dict(record)
            invalid["source_class"] = "public_secondary"
            with self.assertRaisesRegex(self.module.PublicDataError, "official_primary"):
                self.module._validate_source(
                    {
                        key: invalid[key]
                        for key in (
                            "source_id",
                            "source_class",
                            "url",
                            "artifact_role",
                            "artifact_schema_version",
                        )
                    }
                )

    def test_url_snapshot_failure_leaves_previous_tree_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            output = root / "raw"
            output.mkdir(parents=True)
            (output / "old.csv").write_bytes(b"old\n")
            (output / "snapshot_manifest.json").write_text("old-manifest\n", encoding="utf-8")
            before = tree_bytes(output)
            manifest = root / "sources.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": self.module.SOURCE_SCHEMA,
                        "sources": [
                            {
                                "source_id": "first",
                                "source_class": "official_primary",
                                "url": "https://example.invalid/first.csv",
                            },
                            {
                                "source_id": "second",
                                "source_class": "official_primary",
                                "url": "https://example.invalid/second.csv",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(
                self.module.urllib.request,
                "urlopen",
                side_effect=[FakeResponse(b"first\n"), OSError("network failed")],
            ):
                with self.assertRaisesRegex(self.module.PublicDataError, "下载失败"):
                    self.module.snapshot_url_manifest(manifest, output, root)
            self.assertEqual(tree_bytes(output), before)
            self.assertEqual(list(root.glob(".raw.pending-*")), [])

    def test_url_snapshot_publish_failure_rolls_back_previous_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            output = root / "raw"
            output.mkdir(parents=True)
            (output / "old.csv").write_bytes(b"old\n")
            before = tree_bytes(output)
            manifest = root / "sources.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": self.module.SOURCE_SCHEMA,
                        "sources": [
                            {
                                "source_id": "official-test",
                                "source_class": "official_primary",
                                "url": "https://example.invalid/source.csv",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            real_replace = self.module.os.replace

            def fail_staging_promotion(source, destination):
                source_path = Path(source)
                destination_path = Path(destination)
                if source_path.name.startswith(".raw.pending-") and destination_path.name == "raw":
                    raise OSError("simulated publication failure")
                return real_replace(source, destination)

            with mock.patch.object(
                self.module.urllib.request,
                "urlopen",
                return_value=FakeResponse(b"new\n"),
            ), mock.patch.object(self.module.os, "replace", side_effect=fail_staging_promotion):
                with self.assertRaisesRegex(self.module.PublicDataError, "原子发布失败"):
                    self.module.snapshot_url_manifest(manifest, output, root)
            self.assertEqual(tree_bytes(output), before)
            self.assertEqual(list(root.glob(".raw.pending-*")), [])
            self.assertEqual(list(root.glob(".raw.backup-*")), [])

    def test_rejects_insecure_or_unlisted_redirect_target(self) -> None:
        for final_url, expected in (
            ("http://example.invalid/source.csv", "HTTPS"),
            ("https://evil.invalid/source.csv", "允许列表"),
        ):
            with self.subTest(final_url=final_url), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "training"
                root.mkdir()
                manifest = root / "sources.json"
                manifest.write_text(
                    json.dumps(
                        {
                            "schema_version": self.module.SOURCE_SCHEMA,
                            "sources": [
                                {
                                    "source_id": "official-test",
                                    "source_class": "official_primary",
                                    "url": "https://example.invalid/source.csv",
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                with mock.patch.object(
                    self.module.urllib.request,
                    "urlopen",
                    return_value=FakeResponse(b"new\n", final_url=final_url),
                ):
                    with self.assertRaisesRegex(self.module.PublicDataError, expected):
                        self.module.snapshot_url_manifest(manifest, root / "raw", root)
                self.assertFalse((root / "raw").exists())

    def test_accepts_redirect_within_explicit_allowed_domain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = root / "sources.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": self.module.SOURCE_SCHEMA,
                        "sources": [
                            {
                                "source_id": "official-test",
                                "source_class": "official_primary",
                                "url": "https://downloads.example.invalid/source.csv",
                                "allowed_domains": ["example.invalid"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(
                self.module.urllib.request,
                "urlopen",
                return_value=FakeResponse(
                    b"new\n", final_url="https://cdn.example.invalid/source.csv"
                ),
            ):
                result = self.module.snapshot_url_manifest(manifest, root / "raw", root)
            self.assertEqual(
                result["sources"][0]["resolved_url"],
                "https://cdn.example.invalid/source.csv",
            )

    def test_rejects_non_https_source(self) -> None:
        with self.assertRaisesRegex(self.module.PublicDataError, "HTTPS"):
            self.module._validate_source(
                {
                    "source_id": "bad",
                    "source_class": "official_primary",
                    "url": "http://example.invalid/data.csv",
                }
            )

    def test_baostock_valid_manifest_reuses_verified_shard_offline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            output = root / "baostock"
            fake = FakeBaostock(
                {
                    "sh.600000": FakeQueryResult(
                        [
                            ["2024-01-02", "sh.600000", "1", "0"],
                            ["2024-01-03", "sh.600000", "1", "0"],
                        ]
                    )
                }
            )
            with mock.patch.dict(sys.modules, {"baostock": fake}):
                first = self.module.fetch_baostock_trade_status_shards(
                    ["sh.600000"], "2024-01-01", "2024-01-31", output, root
                )
            self.assertFalse(first["shards"][0]["resumed"])
            self.assertEqual(fake.queries, [("sh.600000", "2024-01-01", "2024-01-31")])
            with mock.patch.dict(sys.modules, {"baostock": None}):
                second = self.module.fetch_baostock_trade_status_shards(
                    ["sh.600000"], "2024-01-01", "2024-01-31", output, root
                )
            self.assertTrue(second["shards"][0]["resumed"])
            self.assertEqual(second["shards"][0]["row_count"], 2)
            persisted = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(persisted["symbols"], ["sh.600000"])
            self.assertEqual(
                persisted["shards"][0]["sha256"],
                self.module.sha256_file(output / "sh.600000.csv"),
            )

    def test_baostock_tampered_or_wrong_range_shard_is_refetched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            output = root / "baostock"
            initial = FakeBaostock(
                {
                    "sh.600000": FakeQueryResult(
                        [["2024-01-02", "sh.600000", "1", "0"]]
                    )
                }
            )
            with mock.patch.dict(sys.modules, {"baostock": initial}):
                self.module.fetch_baostock_trade_status_shards(
                    ["sh.600000"], "2024-01-01", "2024-01-31", output, root
                )
            (output / "sh.600000.csv").write_text(
                "date,code,tradestatus,isST\n2024-01-03,sh.600000,1,1\n",
                encoding="utf-8",
            )
            refreshed = FakeBaostock(
                {
                    "sh.600000": FakeQueryResult(
                        [["2024-01-04", "sh.600000", "1", "0"]]
                    )
                }
            )
            with mock.patch.dict(sys.modules, {"baostock": refreshed}):
                report = self.module.fetch_baostock_trade_status_shards(
                    ["sh.600000"], "2024-01-01", "2024-01-31", output, root
                )
            self.assertFalse(report["shards"][0]["resumed"])
            self.assertEqual(report["shards"][0]["min_date"], "2024-01-04")
            self.assertEqual(len(refreshed.queries), 1)

            different_range = FakeBaostock(
                {
                    "sh.600000": FakeQueryResult(
                        [["2024-02-01", "sh.600000", "1", "0"]]
                    )
                }
            )
            with mock.patch.dict(sys.modules, {"baostock": different_range}):
                report = self.module.fetch_baostock_trade_status_shards(
                    ["sh.600000"], "2024-02-01", "2024-02-29", output, root
                )
            self.assertFalse(report["shards"][0]["resumed"])
            self.assertEqual(len(different_range.queries), 1)

    def test_baostock_manifest_hash_cannot_authorize_invalid_csv_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            output = root / "baostock"
            initial = FakeBaostock(
                {
                    "sh.600000": FakeQueryResult(
                        [["2024-01-02", "sh.600000", "1", "0"]]
                    )
                }
            )
            with mock.patch.dict(sys.modules, {"baostock": initial}):
                self.module.fetch_baostock_trade_status_shards(
                    ["sh.600000"], "2024-01-01", "2024-01-31", output, root
                )
            shard = output / "sh.600000.csv"
            shard.write_text(
                "date,code,tradestatus\n2024-01-02,sh.600000,1\n",
                encoding="utf-8",
            )
            manifest_path = output / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["shards"][0]["sha256"] = self.module.sha256_file(shard)
            manifest["shards"][0]["bytes"] = shard.stat().st_size
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            refreshed = FakeBaostock(
                {
                    "sh.600000": FakeQueryResult(
                        [["2024-01-03", "sh.600000", "1", "0"]]
                    )
                }
            )
            with mock.patch.dict(sys.modules, {"baostock": refreshed}):
                report = self.module.fetch_baostock_trade_status_shards(
                    ["sh.600000"], "2024-01-01", "2024-01-31", output, root
                )
            self.assertFalse(report["shards"][0]["resumed"])
            self.assertEqual(len(refreshed.queries), 1)

    def test_baostock_nonempty_shard_without_manifest_is_not_reused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            output = root / "baostock"
            output.mkdir(parents=True)
            (output / "sh.600000.csv").write_text(
                "date,code,tradestatus,isST\n2024-01-02,sh.600000,1,0\n",
                encoding="utf-8",
            )
            fake = FakeBaostock(
                {
                    "sh.600000": FakeQueryResult(
                        [["2024-01-03", "sh.600000", "1", "0"]]
                    )
                }
            )
            with mock.patch.dict(sys.modules, {"baostock": fake}):
                report = self.module.fetch_baostock_trade_status_shards(
                    ["sh.600000"], "2024-01-01", "2024-01-31", output, root
                )
            self.assertFalse(report["shards"][0]["resumed"])
            self.assertEqual(len(fake.queries), 1)

    def test_baostock_failed_incremental_query_keeps_previous_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            output = root / "baostock"
            initial = FakeBaostock(
                {
                    "sh.600000": FakeQueryResult(
                        [["2024-01-02", "sh.600000", "1", "0"]]
                    )
                }
            )
            with mock.patch.dict(sys.modules, {"baostock": initial}):
                self.module.fetch_baostock_trade_status_shards(
                    ["sh.600000"], "2024-01-01", "2024-01-31", output, root
                )
            before = tree_bytes(output)
            failing = FakeBaostock(
                {
                    "sz.000001": FakeQueryResult(
                        [], error_code="1001", error_msg="simulated failure"
                    )
                }
            )
            with mock.patch.dict(sys.modules, {"baostock": failing}):
                with self.assertRaisesRegex(self.module.PublicDataError, "查询失败"):
                    self.module.fetch_baostock_trade_status_shards(
                        ["sh.600000", "sz.000001"],
                        "2024-01-01",
                        "2024-01-31",
                        output,
                        root,
                    )
            self.assertEqual(tree_bytes(output), before)
            self.assertEqual(list(root.glob(".baostock.pending-*")), [])

    def _normalization_fixture(self, root: Path, *, with_expected_keys: bool = False) -> Path:
        raw_root = root / "raw-url-snapshot"
        raw_root.mkdir(parents=True)
        rows = {
            "security_master": (
                "ticker,exchange,board,security_type,list_date,delist_date\n"
                "600000.SH,SH,main,A_STOCK,2010-01-01,\n"
            ),
            "st_status": (
                "ticker,effective_from,effective_to,is_st\n"
                "600000.SH,2010-01-01,,0\n"
            ),
            "suspensions": (
                "ticker,trade_date,is_suspended\n"
                "600000.SH,2018-01-02,0\n"
            ),
            "price_limits": (
                "ticker,trade_date,up_limit,down_limit,rule_version,no_limit_reason\n"
                "600000.SH,2018-01-02,12.10,9.90,main-v1,\n"
            ),
            "index_membership": (
                "index_code,ticker,effective_from,effective_to\n"
                "000300.SH,600000.SH,2010-01-01,\n"
                "000905.SH,600000.SH,2010-01-01,\n"
            ),
            "corporate_actions": (
                "ticker,announcement_date,ex_date,cash_div,bonus_ratio,rights_ratio,rights_price\n"
                "600000.SH,2017-12-01,2018-01-02,0.10,0,0,0\n"
            ),
            "trading_calendar": (
                "timestamps\n"
                "2018-01-02\n"
            ),
        }
        source_records = []
        datasets = {}
        for dataset, text_payload in rows.items():
            source_id = f"official-{dataset}"
            raw_path = raw_root / f"{source_id}.csv"
            raw_path.write_text(text_payload, encoding="utf-8")
            source_url = (
                f"https://www.sse.com.cn/{source_id}.csv"
                if dataset == "trading_calendar"
                else f"https://example.invalid/{source_id}.csv"
            )
            artifact_metadata = (
                {
                    "artifact_role": "trading_calendar",
                    "artifact_schema_version": "kronos-a-share-trading-calendar-v1",
                }
                if dataset == "trading_calendar"
                else {}
            )
            source_records.append(
                {
                    "source_id": source_id,
                    "source_class": "official_primary",
                    "url": source_url,
                    "resolved_url": source_url,
                    "retrieved_at": "2026-08-03T00:00:00+00:00",
                    "valid_from": "2018-01-02",
                    "valid_to": "2018-01-02",
                    "local_path": str(raw_path),
                    "sha256": self.module.sha256_file(raw_path),
                    "bytes": raw_path.stat().st_size,
                    **artifact_metadata,
                }
            )
            header = text_payload.splitlines()[0].split(",")
            mapping = (
                {
                    "trade_date": "timestamps",
                }
                if dataset == "trading_calendar"
                else {column: column for column in header}
            )
            source_config = {
                "source_id": source_id,
                "source_class": "official_primary",
                "snapshot_manifest": str(raw_root / "snapshot_manifest.json"),
                "format": "csv",
                "encoding": "utf-8",
                "mapping": mapping,
                **({"constants": {"is_open": True}} if dataset == "trading_calendar" else {}),
                **artifact_metadata,
            }
            datasets[dataset] = {
                "sources": [source_config],
                "expected_keys": dict(source_config) if with_expected_keys else None,
            }
        (raw_root / "snapshot_manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": self.module.SOURCE_SCHEMA,
                    "status": "ok",
                    "source_count": len(source_records),
                    "sources": source_records,
                }
            ),
            encoding="utf-8",
        )
        manifest = root / "normalization.json"
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": self.module.NORMALIZATION_SCHEMA,
                    "coverage_start": "2018-01-02",
                    "coverage_end": "2018-01-02",
                    "source_priority": list(self.module.SOURCE_PRIORITY),
                    "datasets": datasets,
                }
            ),
            encoding="utf-8",
        )
        return manifest

    def test_publishes_raw_responses_as_atomic_hash_bound_pit_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = self._normalization_fixture(root)
            output = root / "data" / "normalized" / "pit-v1"
            report = self.module.publish_normalized_pit_bundle(manifest, output, root)
            self.assertEqual(report["status"], "local_provisional")
            self.assertEqual(set(report["tables"]), set(self.module.NORMALIZED_DATASETS))
            self.assertTrue((output / "coverage.csv").is_file())
            self.assertTrue((output / "publication_manifest.json").is_file())
            self.assertTrue((output / "publication_manifest.sha256").is_file())
            self.assertTrue(report["artifact_inventory"])
            self.assertEqual(
                report["publication_manifest_sha256"],
                self.module.sha256_file(output / "publication_manifest.json"),
            )
            for dataset in self.module.NORMALIZED_DATASETS:
                self.assertTrue((output / f"{dataset}.csv").is_file())
                self.assertTrue((output / "provenance" / f"{dataset}.json").is_file())
                self.assertFalse(report["tables"][dataset]["is_complete"])
            calendar_provenance = json.loads(
                (output / "provenance" / "trading_calendar.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                calendar_provenance["sources"][0]["artifact_role"],
                "trading_calendar",
            )
            self.assertEqual(
                calendar_provenance["sources"][0]["artifact_schema_version"],
                "kronos-a-share-trading-calendar-v1",
            )
            coverage = (output / "coverage.csv").read_text(encoding="utf-8")
            self.assertIn("binding_schema", coverage)
            self.assertNotIn("kronos-a-share-pit-coverage-v1", coverage)

    def test_normalization_rejects_tampered_raw_response_without_partial_publish(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = self._normalization_fixture(root)
            tampered = root / "raw-url-snapshot" / "official-security_master.csv"
            tampered.write_text(tampered.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
            output = root / "data" / "normalized" / "pit-v1"
            with self.assertRaisesRegex(self.module.PublicDataError, "SHA256"):
                self.module.publish_normalized_pit_bundle(manifest, output, root)
            self.assertFalse(output.exists())
            self.assertEqual(list(output.parent.glob(".pit-v1.pending-*")), [])

    def test_expected_keys_enable_only_cryptographically_bound_complete_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = self._normalization_fixture(root, with_expected_keys=True)
            output = root / "data" / "normalized" / "pit-v1"
            report = self.module.publish_normalized_pit_bundle(manifest, output, root)
            self.assertTrue(all(item["is_complete"] for item in report["tables"].values()))
            coverage = (output / "coverage.csv").read_text(encoding="utf-8")
            self.assertIn("kronos-a-share-pit-coverage-v1", coverage)
            self.assertEqual(report["pit_validation"]["errors"], [])

    def test_equal_priority_conflict_excludes_only_conflicting_security_date(self) -> None:
        import pandas as pd

        first = pd.DataFrame(
            {
                "ticker": ["600000.SH", "600001.SH"],
                "trade_date": ["2018-01-02", "2018-01-02"],
                "is_suspended": [False, False],
            }
        )
        second = pd.DataFrame(
            {
                "ticker": ["600000.SH", "600001.SH"],
                "trade_date": ["2018-01-02", "2018-01-02"],
                "is_suspended": [True, False],
            }
        )
        contract_a = {"source_id": "official-a", "source_class": "official_primary"}
        contract_b = {"source_id": "official-b", "source_class": "official_primary"}
        merged, conflicts, _ = self.module._merge_authoritative_sources(
            "suspensions", [(contract_a, first), (contract_b, second)]
        )
        self.assertEqual(set(merged["ticker"]), {"600001.SH"})
        self.assertEqual(conflicts, {("600000.SH", "2018-01-02")})

    def test_tdx_mechanical_source_cannot_supply_normalized_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            raw = root / "tdx-check.csv"
            raw.write_text("ticker,trade_date,is_suspended\n600000.SH,2018-01-02,0\n", encoding="utf-8")
            source = {
                "source_id": "tdx-check",
                "source_class": "tdx_mechanical",
                "role": "authoritative",
                "raw_path": str(raw),
                "sha256": self.module.sha256_file(raw),
                "valid_from": "2018-01-02",
                "valid_to": "2018-01-02",
                "retrieved_at": "2026-08-03T00:00:00+00:00",
                "format": "csv",
                "mapping": {
                    "ticker": "ticker",
                    "trade_date": "trade_date",
                    "is_suspended": "is_suspended",
                },
            }
            with self.assertRaisesRegex(self.module.PublicDataError, "不得作为供值"):
                self.module._source_contract(
                    source,
                    training_root=root,
                    output=root / "pit-v1",
                    label="tdx",
                )


if __name__ == "__main__":
    unittest.main()

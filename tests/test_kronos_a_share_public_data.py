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
        final_url: str = "https://www.sse.com.cn/source.csv",
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
                                "url": "https://www.sse.com.cn/source.csv",
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
            invalid["url"] = "https://www.baostock.com/calendar.csv"
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
                                "url": "https://www.sse.com.cn/first.csv",
                            },
                            {
                                "source_id": "second",
                                "source_class": "official_primary",
                                "url": "https://www.sse.com.cn/second.csv",
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
                                "url": "https://www.sse.com.cn/source.csv",
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
            ("http://www.sse.com.cn/source.csv", "HTTPS"),
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
                                    "url": "https://www.sse.com.cn/source.csv",
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
                                "url": "https://downloads.sse.com.cn/source.csv",
                                "allowed_domains": ["sse.com.cn"],
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
                    b"new\n", final_url="https://cdn.sse.com.cn/source.csv"
                ),
            ):
                result = self.module.snapshot_url_manifest(manifest, root / "raw", root)
            self.assertEqual(
                result["sources"][0]["resolved_url"],
                "https://cdn.sse.com.cn/source.csv",
            )

    def test_fixed_source_domains_reject_self_labeled_official_and_expansion(self) -> None:
        with self.assertRaisesRegex(self.module.PublicDataError, "代码固定白名单"):
            self.module._validate_source(
                {
                    "source_id": "evil-official",
                    "source_class": "official_primary",
                    "url": "https://evil.example/source.csv",
                    "allowed_domains": ["evil.example"],
                }
            )
        with self.assertRaisesRegex(self.module.PublicDataError, "只能收窄"):
            self.module._validate_source(
                {
                    "source_id": "expanded-official",
                    "source_class": "official_primary",
                    "url": "https://www.sse.com.cn/source.csv",
                    "allowed_domains": ["sse.com.cn", "evil.example"],
                }
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
                f"https://www.csindex.com.cn/{source_id}.csv"
                if dataset == "index_membership"
                else (
                    f"https://www.cninfo.com.cn/{source_id}.csv"
                    if dataset == "corporate_actions"
                    else f"https://www.sse.com.cn/{source_id}.csv"
                )
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

    def _v2_normalization_fixture(self, root: Path) -> Path:
        import pandas as pd

        raw_root = root / "raw-url-snapshot-v2"
        raw_root.mkdir(parents=True, exist_ok=True)
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
                "ticker,trade_date,up_limit,down_limit,rule_version,no_limit_reason,"
                "previous_trade_date,previous_close_raw\n"
                "600000.SH,2018-01-02,11.00,9.00,main_normal_10pct,,2017-12-29,10.00\n"
            ),
            "index_membership": (
                "index_code,ticker,effective_from,effective_to\n"
                "000300.SH,600000.SH,2010-01-01,\n"
                "000905.SH,600000.SH,2010-01-01,\n"
            ),
            "corporate_actions": (
                "ticker,announcement_date,ex_date,cash_div,bonus_ratio,rights_ratio,rights_price,"
                "receipt_total_records,receipt_total_pages,receipt_page_number\n"
                "600000.SH,2017-12-01,2018-01-02,0.10,0,0,0,1,1,1\n"
            ),
            "trading_calendar": (
                "timestamps\n"
                "2017-12-29\n"
                "2018-01-02\n"
            ),
        }
        artifact_by_dataset = {
            "index_membership": (
                self.module.INDEX_MEMBERSHIP_ARTIFACT_ROLE,
                self.module.INDEX_MEMBERSHIP_ARTIFACT_SCHEMA,
            ),
            "corporate_actions": (
                self.module.CORPORATE_ACTIONS_ARTIFACT_ROLE,
                self.module.CORPORATE_ACTIONS_ARTIFACT_SCHEMA,
            ),
            "trading_calendar": (
                self.module.TRADING_CALENDAR_ARTIFACT_ROLE,
                self.module.TRADING_CALENDAR_ARTIFACT_SCHEMA,
            ),
        }
        source_records = []
        datasets = {}
        for dataset, text_payload in rows.items():
            source_id = f"official-v2-{dataset}"
            raw_path = raw_root / f"{source_id}.csv"
            raw_path.write_text(text_payload, encoding="utf-8")
            source_url = {
                "index_membership": f"https://www.csindex.com.cn/{source_id}.csv",
                "corporate_actions": f"https://www.cninfo.com.cn/{source_id}.csv",
                "trading_calendar": f"https://www.sse.com.cn/{source_id}.csv",
            }.get(dataset, f"https://www.sse.com.cn/{source_id}.csv")
            artifact = artifact_by_dataset.get(dataset)
            artifact_metadata = (
                {
                    "artifact_role": artifact[0],
                    "artifact_schema_version": artifact[1],
                }
                if artifact is not None
                else {}
            )
            valid_from = (
                "2017-12-29"
                if dataset in {"price_limits", "trading_calendar"}
                else "2018-01-02"
            )
            source_records.append(
                {
                    "source_id": source_id,
                    "source_class": "official_primary",
                    "url": source_url,
                    "resolved_url": source_url,
                    "retrieved_at": "2026-08-03T00:00:00+00:00",
                    "valid_from": valid_from,
                    "valid_to": "2026-07-31",
                    "local_path": str(raw_path),
                    "sha256": self.module.sha256_file(raw_path),
                    "bytes": raw_path.stat().st_size,
                    **artifact_metadata,
                }
            )
            extracted = pd.read_csv(
                raw_path, dtype=str, keep_default_na=False, encoding="utf-8"
            )
            extracted_bytes = self.module._canonical_extracted_bytes(extracted)
            extractor_config = {"encoding": "utf-8", "delimiter": ","}
            extracted_hash = self.module.hashlib.sha256(extracted_bytes).hexdigest()
            audit_path = raw_root / f"{source_id}.row-audit.csv"
            audit_rows = pd.DataFrame(
                {
                    "source_row_number": [str(index) for index in range(1, len(extracted) + 1)],
                    "raw_locator": [f"csv:data-row:{index}" for index in range(1, len(extracted) + 1)],
                    "extracted_row_sha256": [
                        self.module._canonical_extracted_row_sha256(
                            row, list(extracted.columns)
                        )
                        for row in extracted.to_dict(orient="records")
                    ],
                    "audit_status": ["passed"] * len(extracted),
                }
            )
            audit_path.write_text(
                audit_rows.to_csv(index=False, lineterminator="\n"),
                encoding="utf-8",
            )
            header = text_payload.splitlines()[0].split(",")
            mapping = (
                {"trade_date": "timestamps"}
                if dataset == "trading_calendar"
                else {
                    column: column
                    for column in header
                    if not column.startswith("receipt_")
                }
            )
            source_config = {
                "source_id": source_id,
                "source_class": "official_primary",
                "snapshot_manifest": str(raw_root / "snapshot_manifest.json"),
                "format": "csv",
                "extractor_id": "csv-table-v1",
                "extractor_version": "1",
                "extractor_config": extractor_config,
                "extractor_config_sha256": self.module._canonical_json_sha256(
                    extractor_config
                ),
                "extracted_sha256": extracted_hash,
                "extracted_row_count": len(extracted),
                "row_audit_status": "passed",
                "row_audit": {
                    "schema_version": self.module.ROW_AUDIT_SCHEMA,
                    "path": str(audit_path),
                    "sha256": self.module.sha256_file(audit_path),
                    "bytes": audit_path.stat().st_size,
                    "row_count": len(extracted),
                    "source_sha256": self.module.sha256_file(raw_path),
                    "extracted_sha256": extracted_hash,
                    "audit_status": "passed",
                    "audited_at": "2026-08-03T01:00:00+00:00",
                    "auditor": "unit-test-reviewer",
                },
                "mapping": mapping,
                **(
                    {"constants": {"is_open": True}}
                    if dataset == "trading_calendar"
                    else {}
                ),
                **artifact_metadata,
            }
            coverage_key_contract = self.module.V2_COVERAGE_KEY_CONTRACTS[dataset]
            datasets[dataset] = {
                "sources": [source_config],
                "coverage_key_contract": coverage_key_contract,
                "expected_keys": (
                    dict(source_config) if coverage_key_contract == "source_bound" else None
                ),
            }
        membership_source_hash = next(
            item["sha256"]
            for item in source_records
            if item["source_id"] == "official-v2-index_membership"
        )
        membership_receipt = {
            "schema_version": self.module.CSI_MEMBERSHIP_RECEIPT_SCHEMA,
            "dataset": "index_membership",
            "coverage_start": "2018-01-02",
            "coverage_end": "2026-07-31",
            "status": "passed",
            "indexes": [],
        }
        for index_code in ("000300.SH", "000905.SH"):
            anchor_members = ["600000.SH"]
            membership_receipt["indexes"].append(
                {
                    "index_code": index_code,
                    "anchor_date": "2018-01-02",
                    "anchor_members": anchor_members,
                    "anchor_source_sha256": membership_source_hash,
                    "adjustments": [],
                    "final_members_sha256": self.module._canonical_json_sha256(
                        {"members": anchor_members}
                    ),
                }
            )
        membership_receipt_path = raw_root / "index-membership-receipt.json"
        membership_receipt_path.write_text(
            json.dumps(membership_receipt, ensure_ascii=False), encoding="utf-8"
        )
        datasets["index_membership"]["completeness_receipt"] = {
            "path": str(membership_receipt_path),
            "sha256": self.module.sha256_file(membership_receipt_path),
            "bytes": membership_receipt_path.stat().st_size,
        }

        actions_source_hash = next(
            item["sha256"]
            for item in source_records
            if item["source_id"] == "official-v2-corporate_actions"
        )
        action_keys = [["600000.SH", "2017-12-01", "2018-01-02"]]
        actions_receipt = {
            "schema_version": self.module.CNINFO_PAGINATION_RECEIPT_SCHEMA,
            "dataset": "corporate_actions",
            "coverage_start": "2018-01-02",
            "coverage_end": "2026-07-31",
            "status": "passed",
            "page_size": 1,
            "total_records": 1,
            "total_pages": 1,
            "pages": [
                {
                    "page_number": 1,
                    "row_count": 1,
                    "source_sha256": actions_source_hash,
                    "keys_sha256": self.module._canonical_json_sha256(
                        {"keys": action_keys}
                    ),
                }
            ],
        }
        actions_receipt_path = raw_root / "corporate-actions-receipt.json"
        actions_receipt_path.write_text(
            json.dumps(actions_receipt, ensure_ascii=False), encoding="utf-8"
        )
        datasets["corporate_actions"]["completeness_receipt"] = {
            "path": str(actions_receipt_path),
            "sha256": self.module.sha256_file(actions_receipt_path),
            "bytes": actions_receipt_path.stat().st_size,
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
        manifest = root / "normalization-v2.json"
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": self.module.NORMALIZATION_SCHEMA_V2,
                    "model_coverage_start": "2018-01-02",
                    "model_coverage_end": "2026-07-31",
                    "evidence_lookback_start": "2017-12-29",
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
            self.assertEqual(report["status"], "local_provisional")
            self.assertFalse(report["formal_release_allowed"])

    def test_v2_publishes_separate_model_and_evidence_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = self._v2_normalization_fixture(root)
            output = root / "data" / "normalized" / "pit-v2"
            report = self.module.publish_normalized_pit_bundle(manifest, output, root)
            self.assertEqual(report["schema_version"], self.module.PUBLICATION_SCHEMA_V2)
            self.assertTrue(report["formal_release_allowed"])
            self.assertEqual(report["status"], "local_provisional")
            self.assertEqual(report["model_coverage_start"], "2018-01-02")
            self.assertEqual(report["evidence_lookback_start"], "2017-12-29")
            self.assertTrue(all(item["is_complete"] for item in report["tables"].values()))
            coverage = (output / "coverage.csv").read_text(encoding="utf-8")
            self.assertIn("price_limits,2017-12-29,2026-07-31", coverage)
            self.assertIn("trading_calendar,2017-12-29,2026-07-31", coverage)
            provenance = json.loads(
                (output / "provenance" / "security_master.json").read_text(
                    encoding="utf-8"
                )
            )
            extraction = provenance["sources"][0]["extraction"]
            self.assertEqual(extraction["row_audit_status"], "passed")
            self.assertTrue((output / extraction["path"]).is_file())
            self.assertEqual(extraction["raw_sha256"], provenance["sources"][0]["sha256"])

            validation = self.module._load_data_contract().validate_pit_bundle(output)
            self.assertEqual(validation.errors, [])
            self.assertTrue(
                validation.capabilities["normalization_release_contract"]
            )
            audit_path = output / provenance["sources"][0]["row_audit"]["path"]
            audit_bytes = audit_path.read_bytes()
            audit_path.write_bytes(audit_bytes + b"tampered\n")
            audit_tampered = self.module._load_data_contract().validate_pit_bundle(output)
            self.assertTrue(any("row_audit" in error for error in audit_tampered.errors))
            audit_path.write_bytes(audit_bytes)

            membership_provenance = json.loads(
                (output / "provenance" / "index_membership.json").read_text(
                    encoding="utf-8"
                )
            )
            receipt_path = output / membership_provenance["normalization"][
                "completeness_receipt"
            ]["path"]
            receipt_bytes = receipt_path.read_bytes()
            receipt_path.write_bytes(receipt_bytes + b" ")
            receipt_tampered = self.module._load_data_contract().validate_pit_bundle(output)
            self.assertTrue(
                any("completeness_receipt" in error for error in receipt_tampered.errors)
            )
            receipt_path.write_bytes(receipt_bytes)

            extracted_path = output / extraction["path"]
            extracted_path.write_bytes(extracted_path.read_bytes() + b"tampered\n")
            tampered = self.module._load_data_contract().validate_pit_bundle(output)
            self.assertTrue(any("解析结果 SHA256" in error for error in tampered.errors))

    def test_v2_complete_provenance_without_publication_is_not_production_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = self._v2_normalization_fixture(root)
            output = root / "data" / "normalized" / "pit-v2"
            self.module.publish_normalized_pit_bundle(manifest, output, root)
            (output / "publication_manifest.json").unlink()
            (output / "publication_manifest.sha256").unlink()

            validation = self.module._load_data_contract().validate_pit_bundle(output)

            contract = validation.table_reports["normalization_release_contract"]
            self.assertFalse(contract["verified"])
            self.assertEqual(contract["reason"], "publication_manifest_absent")
            self.assertFalse(validation.production_ready)

    def test_consumer_rebuilds_canonical_source_from_bound_normalization_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = self._v2_normalization_fixture(root)
            output = root / "data" / "normalized" / "pit-v2"
            self.module.publish_normalized_pit_bundle(manifest, output, root)

            provenance_path = output / "provenance" / "security_master.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            extraction = provenance["sources"][0]["extraction"]
            canonical_path = output / extraction["canonical_source_path"]
            canonical_path.write_text(
                canonical_path.read_text(encoding="utf-8").replace(
                    "600000.SH", "600001.SH"
                ),
                encoding="utf-8",
            )
            extraction["canonical_source_sha256"] = self.module.sha256_file(
                canonical_path
            )
            extraction["canonical_source_bytes"] = canonical_path.stat().st_size
            binding_payload = {
                key: extraction[key]
                for key in (
                    "raw_sha256",
                    "extractor_id",
                    "extractor_version",
                    "extractor_config_sha256",
                    "extracted_sha256",
                    "extracted_row_count",
                    "row_audit_status",
                    "row_audit_sha256",
                    "canonical_source_sha256",
                    "canonical_source_row_count",
                )
            }
            extraction["binding_sha256"] = self.module._canonical_json_sha256(
                binding_payload
            )
            provenance_path.write_text(
                json.dumps(provenance, ensure_ascii=False), encoding="utf-8"
            )

            import pandas as pd

            coverage_path = output / "coverage.csv"
            coverage = pd.read_csv(coverage_path, dtype=str, keep_default_na=False)
            coverage.loc[
                coverage["dataset"] == "security_master", "source_manifest_sha256"
            ] = self.module.sha256_file(provenance_path)
            coverage_path.write_text(
                coverage.to_csv(index=False, lineterminator="\n"), encoding="utf-8"
            )

            publication_path = output / "publication_manifest.json"
            publication = json.loads(publication_path.read_text(encoding="utf-8"))
            changed = {
                extraction["canonical_source_path"]: canonical_path,
                "provenance/security_master.json": provenance_path,
                "coverage.csv": coverage_path,
            }
            inventory = {
                item["path"]: item for item in publication["artifact_inventory"]
            }
            for relative, path in changed.items():
                inventory[relative]["sha256"] = self.module.sha256_file(path)
                inventory[relative]["bytes"] = path.stat().st_size
            publication_path.write_text(
                json.dumps(publication, ensure_ascii=False), encoding="utf-8"
            )
            publication_hash = self.module.sha256_file(publication_path)
            (output / "publication_manifest.sha256").write_text(
                f"{publication_hash}  publication_manifest.json\n", encoding="ascii"
            )

            validation = self.module._load_data_contract().validate_pit_bundle(output)

            self.assertTrue(
                any("canonical source" in error for error in validation.errors),
                validation.errors,
            )
            self.assertFalse(validation.production_ready)

    def test_v2_rejects_unknown_fields_wrong_key_contract_and_extracted_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = self._v2_normalization_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["unknown"] = True
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(self.module.PublicDataError, "未知字段"):
                self.module.publish_normalized_pit_bundle(
                    manifest, root / "pit-unknown", root
                )

            manifest = self._v2_normalization_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["datasets"]["suspensions"]["coverage_key_contract"] = "source_bound"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(self.module.PublicDataError, "固定为 'derived'"):
                self.module.publish_normalized_pit_bundle(
                    manifest, root / "pit-contract", root
                )

            manifest = self._v2_normalization_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["datasets"]["security_master"]["sources"][0][
                "extracted_sha256"
            ] = "0" * 64
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(self.module.PublicDataError, "extracted SHA256"):
                self.module.publish_normalized_pit_bundle(
                    manifest, root / "pit-hash", root
                )

    def test_v2_example_matches_row_audit_and_receipt_static_contract(self) -> None:
        example = (
            Path(__file__).resolve().parents[1]
            / ".agents"
            / "skills"
            / "kronos-market-forecasting"
            / "configs"
            / "pit_normalization_v2.example.json"
        )
        payload, _ = self.module._normalization_manifest(example)
        for dataset, config in payload["datasets"].items():
            contracts = list(config["sources"])
            if config["expected_keys"] is not None:
                contracts.append(config["expected_keys"])
            self.assertTrue(all(isinstance(item.get("row_audit"), dict) for item in contracts))
            if dataset in {"index_membership", "corporate_actions"}:
                self.assertIsInstance(config.get("completeness_receipt"), dict)
        corporate = payload["datasets"]["corporate_actions"]["sources"][0]
        self.assertIn("pagination_metadata", corporate["extractor_config"])
        with self.assertRaisesRegex(self.module.PublicDataError, "带时区 ISO-8601"):
            self.module._validate_extractor_config(
                payload["datasets"]["security_master"]["sources"][0],
                label="example.security_master",
            )

    def test_v2_rejects_scalar_row_audit_and_row_audit_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = self._v2_normalization_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["datasets"]["security_master"]["sources"][0].pop("row_audit")
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(self.module.PublicDataError, "逐行审计工件"):
                self.module.publish_normalized_pit_bundle(
                    manifest, root / "pit-scalar-audit", root
                )

            manifest = self._v2_normalization_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            audit = payload["datasets"]["security_master"]["sources"][0]["row_audit"]
            audit_path = Path(audit["path"])
            audit_path.write_text(
                audit_path.read_text(encoding="utf-8").replace("passed", "failed"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(self.module.PublicDataError, "row_audit.sha256 漂移"):
                self.module.publish_normalized_pit_bundle(
                    manifest, root / "pit-audit-drift", root
                )

    def test_v2_rejects_missing_csi_anchor_missing_cninfo_page_and_broken_chain(self) -> None:
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            manifest = self._v2_normalization_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            receipt_config = payload["datasets"]["index_membership"][
                "completeness_receipt"
            ]
            receipt_path = Path(receipt_config["path"])
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["indexes"].pop()
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            receipt_config["sha256"] = self.module.sha256_file(receipt_path)
            receipt_config["bytes"] = receipt_path.stat().st_size
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(self.module.PublicDataError, "全部 index_code"):
                self.module.publish_normalized_pit_bundle(
                    manifest, root / "pit-missing-anchor", root
                )

            manifest = self._v2_normalization_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            receipt_config = payload["datasets"]["corporate_actions"][
                "completeness_receipt"
            ]
            receipt_path = Path(receipt_config["path"])
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["total_pages"] = 2
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            receipt_config["sha256"] = self.module.sha256_file(receipt_path)
            receipt_config["bytes"] = receipt_path.stat().st_size
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(self.module.PublicDataError, "pagination 数量合同"):
                self.module.publish_normalized_pit_bundle(
                    manifest, root / "pit-missing-page", root
                )

        source_hash = "1" * 64
        expected = pd.DataFrame(
            [
                {
                    "index_code": "000300.SH",
                    "ticker": "600000.SH",
                    "effective_from": pd.Timestamp("2018-01-01"),
                    "effective_to": pd.Timestamp("2018-01-02"),
                },
                {
                    "index_code": "000300.SH",
                    "ticker": "600001.SH",
                    "effective_from": pd.Timestamp("2018-01-03"),
                    "effective_to": pd.NaT,
                },
            ]
        )
        broken = {
            "schema_version": self.module.CSI_MEMBERSHIP_RECEIPT_SCHEMA,
            "dataset": "index_membership",
            "coverage_start": "2018-01-02",
            "coverage_end": "2018-01-03",
            "status": "passed",
            "indexes": [
                {
                    "index_code": "000300.SH",
                    "anchor_date": "2018-01-02",
                    "anchor_members": ["600000.SH"],
                    "anchor_source_sha256": source_hash,
                    "adjustments": [
                        {
                            "sequence": 1,
                            "effective_date": "2018-01-03",
                            "added": ["600001.SH"],
                            "removed": ["600000.SH"],
                            "source_sha256": source_hash,
                            "previous_receipt_sha256": "0" * 64,
                            "receipt_sha256": "0" * 64,
                        }
                    ],
                    "final_members_sha256": self.module._canonical_json_sha256(
                        {"members": ["600001.SH"]}
                    ),
                }
            ],
        }
        with self.assertRaisesRegex(self.module.PublicDataError, "previous_receipt_sha256 断链"):
            self.module._validate_csi_membership_receipt(
                broken,
                expected,
                start=self.module.date(2018, 1, 2),
                end=self.module.date(2018, 1, 3),
                authoritative_sha256s={source_hash},
            )

    def test_json_html_and_pdf_extractors_are_deterministic(self) -> None:
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = pd.DataFrame([{"ticker": "600000.SH", "value": "1"}])
            expected_bytes = self.module._canonical_extracted_bytes(expected)
            expected_hash = self.module.hashlib.sha256(expected_bytes).hexdigest()
            fixtures = {
                "json": (
                    b'{"totalRecordNum":1,"totalpages":1,"pageNum":1,'
                    b'"data":[{"ticker":"600000.SH","value":"1"}]}',
                    {
                        "encoding": "utf-8",
                        "records_path": ["data"],
                        "pagination_metadata": {
                            "total_records_path": ["totalRecordNum"],
                            "total_pages_path": ["totalpages"],
                            "page_number_path": ["pageNum"],
                        },
                    },
                ),
                "html": (
                    b"<table><tr><th>ticker</th><th>value</th></tr>"
                    b"<tr><td>600000.SH</td><td>1</td></tr></table>",
                    {"encoding": "utf-8", "table_index": 0},
                ),
            }
            for source_format, (raw, config) in fixtures.items():
                path = root / f"source.{source_format}"
                path.write_bytes(raw)
                frame, extracted = self.module._extract_tabular_source(
                    {
                        "source_id": source_format,
                        "raw_path": path,
                        "source_format": source_format,
                        "extractor_config": config,
                        "extracted_sha256": expected_hash,
                        "extracted_row_count": 1,
                    }
                )
                self.assertEqual(frame.to_dict(orient="records"), expected.to_dict(orient="records"))
                self.assertEqual(extracted, expected_bytes)
                if source_format == "json":
                    self.assertEqual(
                        frame.attrs["pagination_metadata"],
                        {
                            "total_records_path": 1,
                            "total_pages_path": 1,
                            "page_number_path": 1,
                        },
                    )

            pdf_path = root / "source.pdf"
            pdf_path.write_bytes(b"%PDF-reviewed-fixture")

            class FakePage:
                def extract_tables(self):
                    return [[["ticker", "value"], ["600000.SH", "1"]]]

            class FakeDocument:
                pages = [FakePage()]

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, traceback):
                    return None

            fake_pdfplumber = SimpleNamespace(open=lambda _: FakeDocument())
            with mock.patch.dict(sys.modules, {"pdfplumber": fake_pdfplumber}):
                frame, extracted = self.module._extract_tabular_source(
                    {
                        "source_id": "pdf",
                        "raw_path": pdf_path,
                        "source_format": "pdf",
                        "extractor_config": {"pages": [0], "table_index": 0},
                        "extracted_sha256": expected_hash,
                        "extracted_row_count": 1,
                    }
                )
            self.assertEqual(frame.to_dict(orient="records"), expected.to_dict(orient="records"))
            self.assertEqual(extracted, expected_bytes)

    def test_reviewed_overlay_binds_source_row_and_extractor_identity(self) -> None:
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "training"
            root.mkdir()
            overlay_path = root / "overlay.csv"
            pd.DataFrame(
                [
                    {
                        "source_row_number": 1,
                        "correction_reason": "官方勘误",
                        "ticker": "600000.SH",
                        "trade_date": "2018-01-02",
                        "is_suspended": "1",
                    }
                ]
            ).to_csv(overlay_path, index=False, encoding="utf-8")
            contract = {
                "source_id": "official-overlay",
                "normalization_schema": self.module.NORMALIZATION_SCHEMA_V2,
                "sha256": "1" * 64,
                "extracted_sha256": "2" * 64,
                "extractor_id": "csv-table-v1",
                "extractor_version": "1",
                "extractor_config_sha256": "3" * 64,
                "_training_root": root,
                "_output": root / "pit-v2",
                "reviewed_overlay": {
                    "schema_version": self.module.REVIEWED_OVERLAY_SCHEMA,
                    "path": str(overlay_path),
                    "sha256": self.module.sha256_file(overlay_path),
                    "row_count": 1,
                    "raw_sha256": "1" * 64,
                    "extracted_sha256": "2" * 64,
                    "extractor_id": "csv-table-v1",
                    "extractor_version": "1",
                    "extractor_config_sha256": "3" * 64,
                    "review_status": "approved",
                    "reviewed_at": "2026-08-03T00:00:00+00:00",
                    "reviewer": "reviewer-a",
                    "reason": "官方勘误",
                },
            }
            frame = pd.DataFrame(
                [
                    {
                        "ticker": "600000.SH",
                        "trade_date": "2018-01-02",
                        "is_suspended": "0",
                    }
                ]
            )
            corrected = self.module._apply_reviewed_overlay(
                frame, contract, dataset="suspensions"
            )
            self.assertEqual(corrected.iloc[0]["is_suspended"], "1")
            contract["reviewed_overlay"]["raw_sha256"] = "4" * 64
            with self.assertRaisesRegex(self.module.PublicDataError, "不匹配"):
                self.module._apply_reviewed_overlay(
                    frame, contract, dataset="suspensions"
                )

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

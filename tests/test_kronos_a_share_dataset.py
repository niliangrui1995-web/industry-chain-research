from __future__ import annotations

import importlib.util
import struct
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd
import numpy as np
import json
import hashlib


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / ".agents" / "skills" / "kronos-market-forecasting" / "scripts" / "kronos_a_share_dataset.py"


def load_module():
    spec = importlib.util.spec_from_file_location("kronos_a_share_dataset", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_day(path: Path, dates: pd.DatetimeIndex, start: float = 10.0) -> None:
    record = struct.Struct("<IIIIIfII")
    payload = bytearray()
    for index, date in enumerate(dates):
        close = start + index * 0.01
        payload.extend(
            record.pack(
                int(date.strftime("%Y%m%d")),
                int(close * 100),
                int((close + 0.1) * 100),
                int((close - 0.1) * 100),
                int(close * 100),
                float(100000 + index),
                1000 + index,
                0,
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(payload))


def write_suspensions(
    path: Path,
    tickers: list[str],
    dates: pd.DatetimeIndex,
    *,
    suspended: set[tuple[str, pd.Timestamp]] | None = None,
) -> None:
    suspended = suspended or set()
    rows = []
    for ticker in tickers:
        for trade_date in dates:
            rows.append(
                {
                    "ticker": ticker,
                    "trade_date": trade_date,
                    "is_suspended": (ticker, trade_date) in suspended,
                }
            )
    pd.DataFrame(rows).to_csv(path, index=False)


class KronosAshareDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_read_day_rejects_non_multiple_of_record_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.day"
            path.write_bytes(b"bad")
            with self.assertRaisesRegex(self.module.DatasetBuildError, "32字节"):
                self.module.read_day_file(path)

    def test_build_index_requires_target_strictly_before_split_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            snapshot = training / "data" / "raw" / "s1"
            dates = pd.bdate_range("2020-01-01", periods=130)
            write_day(snapshot / "sh600000.day", dates)
            write_day(snapshot / "sh000906.day", dates, start=100.0)
            splits = {
                "train": [dates[0].strftime("%Y-%m-%d"), dates[-1].strftime("%Y-%m-%d")],
                "validation": ["2021-01-01", "2021-02-01"],
                "development_test": ["2021-02-02", "2021-03-01"],
                "locked_retrospective": ["2021-03-02", "2021-04-01"],
            }
            report = self.module.build_sample_index(
                snapshot,
                training / "data" / "datasets" / "d1",
                training,
                splits=splits,
            )
            index = pd.read_csv(report["sample_index"])
            self.assertTrue((index["target_date"] < int(dates[-1].strftime("%Y%m%d"))).all())
            self.assertEqual(report["status"], "local_provisional")

    def test_smoke_sample_cap_is_applied_during_index_construction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            snapshot = training / "raw"
            dates = pd.bdate_range("2020-01-01", periods=150)
            write_day(snapshot / "sh600000.day", dates)
            write_day(snapshot / "sz000001.day", dates)
            write_day(snapshot / "sh000906.day", dates, start=100.0)
            splits = {
                "train": [dates[0].strftime("%Y-%m-%d"), dates[-1].strftime("%Y-%m-%d")],
                "validation": ["2021-01-01", "2021-02-01"],
                "development_test": ["2021-02-02", "2021-03-01"],
                "locked_retrospective": ["2021-03-02", "2021-04-01"],
            }
            report = self.module.build_sample_index(
                snapshot,
                training / "dataset",
                training,
                splits=splits,
                max_samples_per_split=2,
            )
            self.assertEqual(report["split_counts"]["train"], 2)
            self.assertEqual(report["selection"]["mode"], "deterministic_bounded_smoke")
            index = pd.read_csv(report["sample_index"])
            self.assertEqual(index.groupby(["ticker", "split"]).size().max(), 1)
            self.assertGreaterEqual(index.groupby("origin_date").size().max(), 2)

    def test_membership_filters_non_members(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            snapshot = training / "raw"
            dates = pd.bdate_range("2020-01-01", periods=130)
            write_day(snapshot / "sh600000.day", dates)
            write_day(snapshot / "sz000001.day", dates)
            write_day(snapshot / "sh000906.day", dates, start=100.0)
            membership = training / "membership.csv"
            pd.DataFrame(
                {
                    "ticker": ["600000.SH"],
                    "index_code": ["000300.SH"],
                    "effective_from": [dates[0]],
                    "effective_to": [""],
                }
            ).to_csv(membership, index=False)
            splits = {
                "train": [dates[0].strftime("%Y-%m-%d"), dates[-1].strftime("%Y-%m-%d")],
                "validation": ["2021-01-01", "2021-02-01"],
                "development_test": ["2021-02-02", "2021-03-01"],
                "locked_retrospective": ["2021-03-02", "2021-04-01"],
            }
            report = self.module.build_sample_index(
                snapshot,
                training / "dataset",
                training,
                splits=splits,
                membership_path=membership,
            )
            index = pd.read_csv(report["sample_index"])
            self.assertEqual(set(index["ticker"]), {"sh600000"})

    def test_formal_coverage_blocks_missing_historical_constituent_day_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            snapshot = training / "raw"
            dates = pd.bdate_range("2020-01-01", periods=130)
            write_day(snapshot / "sh600000.day", dates)
            write_day(snapshot / "sh000906.day", dates, start=100.0)
            membership = training / "membership.csv"
            pd.DataFrame(
                {
                    "ticker": ["600000.SH", "000001.SZ"],
                    "index_code": ["000300.SH", "000905.SH"],
                    "effective_from": [dates[0], dates[0]],
                    "effective_to": ["", ""],
                }
            ).to_csv(membership, index=False)
            suspensions = training / "suspensions.csv"
            write_suspensions(
                suspensions,
                ["600000.SH", "000001.SZ"],
                dates,
            )
            splits = {
                "train": [dates[0].strftime("%Y-%m-%d"), dates[-1].strftime("%Y-%m-%d")],
                "validation": ["2021-01-01", "2021-02-01"],
                "development_test": ["2021-02-02", "2021-03-01"],
                "locked_retrospective": ["2021-03-02", "2021-04-01"],
            }
            with self.assertRaisesRegex(
                self.module.DatasetBuildError,
                "missing_historical_day_files=1",
            ):
                self.module.build_sample_index(
                    snapshot,
                    training / "dataset",
                    training,
                    splits=splits,
                    membership_path=membership,
                    suspensions_path=suspensions,
                    require_complete_membership_coverage=True,
                )

    def test_missing_member_quote_requires_explicit_pit_suspension(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            snapshot = training / "raw"
            dates = pd.bdate_range("2020-01-01", periods=220)
            missing_date = dates[50]
            write_day(snapshot / "sh600000.day", dates.delete(50))
            write_day(snapshot / "sh000906.day", dates, start=100.0)
            membership = pd.DataFrame(
                {
                    "ticker": ["sh600000"],
                    "index_code": ["000300"],
                    "effective_from": [dates[0]],
                    "effective_to": [pd.Timestamp.max.normalize()],
                }
            )
            splits = {
                "train": [dates[0].strftime("%Y-%m-%d"), dates[-1].strftime("%Y-%m-%d")],
                "validation": ["2021-01-01", "2021-02-01"],
                "development_test": ["2021-02-02", "2021-03-01"],
                "locked_retrospective": ["2021-03-02", "2021-04-01"],
            }
            suspensions = pd.DataFrame(
                {
                    "ticker": ["sh600000"] * len(dates),
                    "trade_date": dates,
                    "is_suspended": [value == missing_date for value in dates],
                }
            )
            audit = self.module.audit_membership_market_coverage(
                snapshot,
                membership=membership,
                suspensions=suspensions,
                splits=splits,
            )
            self.assertTrue(audit["verified"])
            self.assertEqual(audit["explicit_suspension_member_dates"], 1)
            self.assertEqual(audit["unexplained_missing_quote_member_dates"], 0)

            suspensions["is_suspended"] = False
            failed = self.module.audit_membership_market_coverage(
                snapshot,
                membership=membership,
                suspensions=suspensions,
                splits=splits,
            )
            self.assertFalse(failed["verified"])
            self.assertEqual(failed["unexplained_missing_quote_member_dates"], 1)

    def test_suspension_gap_is_not_concatenated_into_a_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            snapshot = training / "raw"
            dates = pd.bdate_range("2020-01-01", periods=140)
            write_day(snapshot / "sh600000.day", dates)
            write_day(snapshot / "sz000001.day", dates.delete(50))
            write_day(snapshot / "sh000906.day", dates, start=100.0)
            splits = {
                "train": [dates[0].strftime("%Y-%m-%d"), dates[-1].strftime("%Y-%m-%d")],
                "validation": ["2021-01-01", "2021-02-01"],
                "development_test": ["2021-02-02", "2021-03-01"],
                "locked_retrospective": ["2021-03-02", "2021-04-01"],
            }
            report = self.module.build_sample_index(
                snapshot,
                training / "dataset",
                training,
                splits=splits,
            )
            index = pd.read_csv(report["sample_index"])
            self.assertEqual(set(index["ticker"]), {"sh600000"})
            self.assertGreater(report["skipped"]["suspension_or_calendar_gap"], 0)

    def test_formal_trade_state_checker_is_consumed_per_sample(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            training = Path(tmp) / "training"
            snapshot = training / "raw"
            dates = pd.bdate_range("2020-01-01", periods=130)
            write_day(snapshot / "sh600000.day", dates)
            write_day(snapshot / "sz000001.day", dates)
            write_day(snapshot / "sh000906.day", dates, start=100.0)
            calls = []

            def checker(ticker, signal_date, raw_close):
                calls.append((ticker, signal_date, raw_close))
                allowed = ticker == "sh600000"
                return {
                    "state_confirmed": allowed,
                    "eligible_for_formal_sample": allowed,
                }

            splits = {
                "train": [dates[0].strftime("%Y-%m-%d"), dates[-1].strftime("%Y-%m-%d")],
                "validation": ["2021-01-01", "2021-02-01"],
                "development_test": ["2021-02-02", "2021-03-01"],
                "locked_retrospective": ["2021-03-02", "2021-04-01"],
            }
            report = self.module.build_sample_index(
                snapshot,
                training / "dataset",
                training,
                splits=splits,
                trade_state_checker=checker,
            )
            index = pd.read_csv(report["sample_index"])
            self.assertEqual(set(index["ticker"]), {"sh600000"})
            self.assertTrue(report["sample_trade_state_checked"])
            self.assertGreater(report["skipped"]["unconfirmed_trade_state"], 0)
            self.assertGreater(len(calls), 0)

    def test_causal_adjustment_uses_only_actions_known_and_effective_by_origin(self) -> None:
        dates = pd.bdate_range("2020-01-01", periods=12)
        frame = pd.DataFrame(
            {
                "date": [int(value.strftime("%Y%m%d")) for value in dates],
                "open": np.linspace(10, 11.1, 12),
                "high": np.linspace(10.2, 11.3, 12),
                "low": np.linspace(9.8, 10.9, 12),
                "close": np.linspace(10, 11.1, 12),
                "volume": np.full(12, 1000.0),
                "amount": np.full(12, 10000.0),
            }
        )
        actions = pd.DataFrame(
            {
                "ticker": ["sh600000", "sh600000"],
                "announcement_date": [dates[2], dates[8]],
                "ex_date": [dates[5], dates[10]],
                "cash_div": [0.5, 0.5],
                "bonus_ratio": [0.0, 0.0],
                "rights_ratio": [0.0, 0.0],
                "rights_price": [0.0, 0.0],
            }
        )
        spec = self.module.WindowSpec(lookback=8, horizon=2)
        adjusted_raw, raw_applied = self.module.causal_adjusted_price_window(
            frame,
            0,
            spec,
            corporate_actions=actions,
            ticker="sh600000",
            origin_date=int(dates[7].strftime("%Y%m%d")),
        )
        adjusted, applied = self.module.causal_adjusted_normalized_window(
            frame,
            0,
            spec,
            corporate_actions=actions,
            ticker="sh600000",
            origin_date=int(dates[7].strftime("%Y%m%d")),
        )
        raw = self.module.normalized_window(frame, 0, spec)
        self.assertEqual(raw_applied, 1)
        self.assertEqual(applied, 1)
        self.assertEqual(adjusted_raw.shape, (10, 6))
        self.assertFalse(
            np.allclose(
                adjusted_raw[:, :4],
                frame.iloc[:10][["open", "high", "low", "close"]].to_numpy(),
            )
        )
        self.assertFalse(np.allclose(adjusted[:, :4], raw[:, :4]))

    def test_load_token_cache_rejects_array_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            arrays = {
                "s1.npy": np.zeros((1, 100), dtype=np.uint16),
                "s2.npy": np.zeros((1, 100), dtype=np.uint16),
                "stamp.npy": np.zeros((1, 100, 5), dtype=np.uint8),
                "label.npy": np.zeros((1,), dtype=np.float32),
                "trade_date.npy": np.zeros((1,), dtype=np.int32),
                "instrument_id.npy": np.zeros((1,), dtype=np.int32),
                "split.npy": np.zeros((1,), dtype=np.uint8),
            }
            files = {}
            for name, array in arrays.items():
                path = directory / name
                np.save(path, array)
                files[name] = {
                    "bytes": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            (directory / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "kronos-a-share-token-cache-v1",
                        "sample_count": 1,
                        "files": files,
                    }
                ),
                encoding="utf-8",
            )
            self.module.load_token_cache(directory)
            with (directory / "s1.npy").open("ab") as handle:
                handle.write(b"tampered")
            with self.assertRaisesRegex(self.module.DatasetBuildError, "字节数不匹配"):
                self.module.load_token_cache(directory)

    def test_token_memmaps_are_closed_before_windows_atomic_publish(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tokens.npy"
            array = np.lib.format.open_memmap(
                path, mode="w+", dtype=np.uint16, shape=(2, 2)
            )
            array[:] = 1
            self.module._close_token_memmaps({"tokens.npy": array})
            self.assertTrue(array._mmap.closed)

    def test_realized_label_removes_known_ex_dividend_mechanical_drop(self) -> None:
        dates = pd.bdate_range("2020-01-01", periods=12)
        closes = np.array([10.0] * 6 + [9.5] * 6)
        frame = pd.DataFrame(
            {
                "date": [int(value.strftime("%Y%m%d")) for value in dates],
                "open": closes,
                "high": closes,
                "low": closes,
                "close": closes,
                "volume": np.full(12, 1000.0),
                "amount": np.full(12, 10000.0),
            }
        )
        actions = pd.DataFrame(
            {
                "ticker": ["sh600000"],
                "announcement_date": [dates[3]],
                "ex_date": [dates[6]],
                "cash_div": [0.5],
                "bonus_ratio": [0.0],
                "rights_ratio": [0.0],
                "rights_price": [0.0],
            }
        )
        raw = self.module.realized_total_log_return(
            frame,
            origin_index=5,
            target_index=10,
            corporate_actions=None,
            ticker="sh600000",
        )
        adjusted = self.module.realized_total_log_return(
            frame,
            origin_index=5,
            target_index=10,
            corporate_actions=actions,
            ticker="sh600000",
        )
        self.assertLess(raw, 0)
        self.assertAlmostEqual(adjusted, 0.0, places=7)


if __name__ == "__main__":
    unittest.main()

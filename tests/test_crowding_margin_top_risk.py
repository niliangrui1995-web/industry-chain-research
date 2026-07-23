from __future__ import annotations

import importlib.util
from pathlib import Path
import hashlib
import struct
import sys

import numpy as np
import pandas as pd
import pytest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / ".agents"
    / "skills"
    / "a-share-leverage-capitulation-analyst"
    / "scripts"
    / "analyze_crowding_margin_top_risk.py"
)
SPEC = importlib.util.spec_from_file_location("crowding_margin_top_risk", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_causal_percentile_never_reads_future_values() -> None:
    original = pd.Series(np.arange(300, dtype=float))
    changed_future = original.copy()
    changed_future.iloc[250:] = -10_000

    original_rank = MODULE.causal_percentile(
        original, window=100, min_periods=20
    )
    changed_rank = MODULE.causal_percentile(
        changed_future, window=100, min_periods=20
    )

    pd.testing.assert_series_equal(
        original_rank.iloc[:250], changed_rank.iloc[:250]
    )
    assert original_rank.iloc[249] > 0.99


def test_forward_max_drawdown_uses_only_strictly_future_values() -> None:
    values = pd.Series([100.0, 105.0, 90.0, 95.0])
    result = MODULE.forward_max_drawdown_pct(values, horizon=2)

    assert result.iloc[0] == pytest.approx(-10.0)
    assert result.iloc[1] == pytest.approx((90.0 / 105.0 - 1.0) * 100.0)
    assert np.isnan(result.iloc[2])
    assert np.isnan(result.iloc[3])


def test_forward_max_drawdown_rejects_internal_invalid_observation() -> None:
    values = pd.Series([100.0, 105.0, 90.0, 95.0])
    valid = pd.Series([True, True, False, True])
    result = MODULE.forward_max_drawdown_pct(
        values, horizon=2, valid_observation=valid
    )

    assert result.isna().all()


def test_peak_events_are_declustered_at_highest_value() -> None:
    prefix = np.linspace(80.0, 99.0, 59)
    values = pd.Series(
        np.concatenate(
            [
                prefix,
                [100.0, 101.0, 102.0, 101.0, 100.0, 90.0, 88.0],
                np.linspace(89.0, 95.0, 30),
            ]
        )
    )
    events = MODULE.detect_peak_events(
        values,
        horizon=10,
        drawdown_threshold_pct=-8.0,
        trailing_high_window=40,
        decluster_days=20,
    )

    assert events == [61]


def test_peak_event_is_rejected_when_confirmation_window_has_gap() -> None:
    prefix = np.linspace(80.0, 99.0, 59)
    values = pd.Series(
        np.concatenate(
            [
                prefix,
                [100.0, 101.0, 102.0, 101.0, 100.0, 90.0, 88.0],
                np.linspace(89.0, 95.0, 30),
            ]
        )
    )
    valid = pd.Series(True, index=values.index)
    valid.iloc[65] = False
    events = MODULE.detect_peak_events(
        values,
        horizon=10,
        drawdown_threshold_pct=-8.0,
        trailing_high_window=40,
        decluster_days=20,
        valid_observation=valid,
    )

    assert events == []


def test_event_labels_cover_only_pre_event_window() -> None:
    labels = MODULE.label_event_within_horizon(10, [5], horizon=2)
    assert str(labels.dtype) == "Int64"
    assert labels.iloc[:8].tolist() == [0, 0, 0, 1, 1, 0, 0, 0]
    assert labels.iloc[8:].isna().all()


def test_event_labels_include_confirmation_right_censoring() -> None:
    labels = MODULE.label_event_within_horizon(
        20, [8], horizon=3, confirmation_horizon=5
    )
    assert labels.iloc[5:8].tolist() == [1, 1, 1]
    assert labels.iloc[8] == 0
    assert labels.iloc[-8:].isna().all()


def test_event_labels_propagate_invalid_confirmation_window() -> None:
    valid = pd.Series(True, index=range(20))
    valid.iloc[10] = False
    labels = MODULE.label_event_within_horizon(
        20,
        [8],
        horizon=3,
        confirmation_horizon=5,
        valid_observation=valid,
    )

    assert pd.isna(labels.iloc[4])
    assert pd.isna(labels.iloc[5])
    assert labels.iloc[0] == 0


def test_long_break_eve_definition() -> None:
    dates = pd.Series(
        pd.to_datetime(["2024-02-07", "2024-02-08", "2024-02-19", "2024-02-20"])
    )
    result = MODULE.mark_long_break_eves(dates)
    assert result.tolist() == [False, True, False, False]


def test_verified_output_tree_is_rejected_before_creation(tmp_path: Path) -> None:
    forbidden = tmp_path / "VERIFIED_2016_PRESENT" / "child"
    with pytest.raises(ValueError, match="verified_2016_present"):
        MODULE.validate_output_dir(forbidden)
    assert not forbidden.exists()

    allowed = tmp_path / "verified_2016_present_backup"
    assert MODULE.validate_output_dir(allowed) == allowed.resolve()


def test_trend_regime_is_three_state_and_missing_aware() -> None:
    close = pd.Series([120.0, 80.0, 105.0, 100.0])
    ma20 = pd.Series([110.0, 90.0, 95.0, np.nan])
    ma50 = pd.Series([105.0, 95.0, 100.0, 95.0])
    ma250 = pd.Series([100.0, 100.0, 90.0, 90.0])

    result = MODULE.classify_trend_regime(close, ma20, ma50, ma250)

    assert result.iloc[:3].tolist() == ["uptrend", "downtrend", "transition"]
    assert pd.isna(result.iloc[3])


def test_tdx_stock_code_is_normalized_to_database_key() -> None:
    assert MODULE.canonical_tdx_stock_code(Path("sz000001.day")) == "000001.SZ"
    assert MODULE.canonical_tdx_stock_code(Path("sh600000.day")) == "600000.SH"


def test_tdx_prefix_check_ignores_only_records_after_research_end(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sz000001.day"

    def day_record(date_i: int, close_i: int) -> bytes:
        return struct.pack(
            "<IIIIIfII",
            date_i,
            close_i,
            close_i,
            close_i,
            close_i,
            1.0,
            1,
            0,
        )

    historical = day_record(20260722, 1000)
    path.write_bytes(historical)
    expected = {str(path): (len(historical), hashlib.sha256(historical).hexdigest())}

    path.write_bytes(historical + day_record(20260723, 1010))
    MODULE.verify_tdx_relevant_prefixes(expected, pd.Timestamp("2026-07-22"))

    path.write_bytes(day_record(20260722, 999) + day_record(20260723, 1010))
    with pytest.raises(RuntimeError, match="research end date changed"):
        MODULE.verify_tdx_relevant_prefixes(expected, pd.Timestamp("2026-07-22"))


def test_top_targets_are_part_of_model_contract() -> None:
    assert {
        "target_crowd_drawdown_20d",
        "target_market_drawdown_20d",
        "target_crowd_top_within_10d",
        "target_market_top_within_10d",
    }.issubset(MODULE.MODEL_TARGETS)


def test_margin_coverage_is_measured_within_financing_eligible_subset() -> None:
    frame = pd.DataFrame(
        {
            "crowd_count": [100, 100],
            "crowd_margin_coverage": [0.50, 0.50],
            "crowd_financing_eligible_t_minus_1_count": [50, 50],
            "crowd_margin_continuity_coverage": [0.90, 0.70],
            "crowd_flow_comparable_count": [45, 35],
        }
    )

    result = MODULE.margin_flow_validity(frame, coverage_threshold=0.80)

    assert result.tolist() == [True, False]

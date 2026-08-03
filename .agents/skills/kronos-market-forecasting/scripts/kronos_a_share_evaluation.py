#!/usr/bin/env python3
"""Deterministic evaluation and release gates for Kronos A-share adapters."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any, Iterable

import numpy as np
import pandas as pd


EVIDENCE_CLASS = "model_output"
GATE_SCHEMA_VERSION = "kronos-a-share-gate-v1"


class EvaluationError(ValueError):
    """Raised when an evaluation input violates the fixed contract."""


@dataclass(frozen=True)
class GateThresholds:
    adapter_ce_improvement_min: float = 0.01
    validation_rank_ic_min: float = 0.03
    baseline_rank_ic_lift_min: float = 0.005
    positive_quarter_fraction_min: float = 0.5
    bootstrap_lower_bound_min: float = 0.0
    base_round_trip_cost_bps: Decimal = Decimal("35")
    stress_round_trip_cost_bps: Decimal = Decimal("70")


def _require_columns(frame: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise EvaluationError(f"评估输入缺少字段：{missing}")


def _finite_numeric(frame: pd.DataFrame, columns: Iterable[str]) -> None:
    for column in columns:
        values = pd.to_numeric(frame[column], errors="coerce").to_numpy(dtype=np.float64)
        if not np.isfinite(values).all():
            raise EvaluationError(f"字段 {column} 存在非数值、NaN 或 Inf")


def _strict_boolean(series: pd.Series, *, column: str) -> pd.Series:
    """Parse booleans without treating the non-empty string ``False`` as true."""

    mapping = {
        True: True,
        False: False,
        1: True,
        0: False,
        "true": True,
        "false": False,
        "1": True,
        "0": False,
    }
    parsed: list[bool] = []
    for value in series.tolist():
        key: Any = value
        if isinstance(value, str):
            key = value.strip().lower()
        if key not in mapping:
            raise EvaluationError(f"字段 {column} 含非严格布尔值：{value!r}")
        parsed.append(mapping[key])
    return pd.Series(parsed, index=series.index, dtype=bool)


def spearman_rank_correlation(score: pd.Series, label: pd.Series) -> float:
    """Compute Spearman correlation without a scipy dependency."""

    if len(score) != len(label):
        raise EvaluationError("score 与 label 长度不一致")
    if len(score) < 2:
        return float("nan")
    left = pd.to_numeric(score, errors="coerce")
    right = pd.to_numeric(label, errors="coerce")
    if left.isna().any() or right.isna().any():
        raise EvaluationError("RankIC 输入存在 NaN")
    left_rank = left.rank(method="average")
    right_rank = right.rank(method="average")
    if left_rank.nunique() < 2 or right_rank.nunique() < 2:
        return float("nan")
    return float(left_rank.corr(right_rank, method="pearson"))


def daily_rank_ic(
    frame: pd.DataFrame,
    *,
    score_column: str = "raw_score",
    label_column: str = "label_excess_10d",
    date_column: str = "trade_date",
    min_instruments: int = 2,
    active_member_count_column: str | None = None,
    min_coverage_ratio: float | None = None,
    require_eligible_cross_section: bool = False,
) -> pd.DataFrame:
    """Return one RankIC observation per date, never mixing cross-sections."""

    if min_instruments < 2:
        raise EvaluationError("RankIC min_instruments 不得小于 2")
    if min_coverage_ratio is not None and not 0 < min_coverage_ratio <= 1:
        raise EvaluationError("RankIC min_coverage_ratio 必须位于 (0, 1]")
    if min_coverage_ratio is not None and active_member_count_column is None:
        raise EvaluationError("设置 RankIC coverage 门时必须提供 active_member_count_column")
    _require_columns(frame, [score_column, label_column, date_column])
    if active_member_count_column is not None:
        _require_columns(frame, [active_member_count_column])
    _finite_numeric(frame, [score_column, label_column])
    dates = pd.to_datetime(frame[date_column], errors="coerce")
    if dates.isna().any():
        raise EvaluationError("trade_date 存在无法解析的日期")
    selected_columns = [score_column, label_column]
    if active_member_count_column is not None:
        selected_columns.append(active_member_count_column)
    work = frame[selected_columns].copy()
    work[date_column] = dates.dt.normalize()
    rows: list[dict[str, Any]] = []
    for trade_date, group in work.groupby(date_column, sort=True):
        instrument_count = int(len(group))
        active_member_count: int | None = None
        coverage_ratio: float | None = None
        if active_member_count_column is not None:
            active_values = pd.to_numeric(
                group[active_member_count_column], errors="coerce"
            )
            if (
                active_values.isna().any()
                or (active_values <= 0).any()
                or active_values.nunique() != 1
                or not np.equal(active_values, np.floor(active_values)).all()
            ):
                raise EvaluationError(
                    f"{trade_date.date()} active_member_count 必须为同日唯一正整数"
                )
            active_member_count = int(active_values.iloc[0])
            if instrument_count > active_member_count:
                raise EvaluationError(
                    f"{trade_date.date()} eligible_count 超过 active_member_count"
                )
            coverage_ratio = instrument_count / active_member_count
        eligible = instrument_count >= min_instruments and (
            min_coverage_ratio is None
            or (coverage_ratio is not None and coverage_ratio >= min_coverage_ratio)
        )
        if require_eligible_cross_section and not eligible:
            raise EvaluationError(
                "正式 RankIC 横截面不满足准出门："
                f"date={trade_date.date()} eligible={instrument_count} "
                f"active={active_member_count} coverage={coverage_ratio}"
            )
        value = (
            spearman_rank_correlation(group[score_column], group[label_column])
            if eligible
            else float("nan")
        )
        rows.append(
            {
                "trade_date": trade_date,
                "rank_ic": value,
                "instrument_count": instrument_count,
                "active_member_count": active_member_count,
                "coverage_ratio": coverage_ratio,
                "eligible_cross_section": eligible,
            }
        )
    return pd.DataFrame(rows)


def quarterly_rank_ic_summary(daily: pd.DataFrame) -> dict[str, Any]:
    _require_columns(daily, ["trade_date", "rank_ic"])
    work = daily.copy()
    work["trade_date"] = pd.to_datetime(work["trade_date"], errors="coerce")
    work = work[np.isfinite(pd.to_numeric(work["rank_ic"], errors="coerce"))]
    if work.empty:
        return {
            "quarter_count": 0,
            "positive_quarter_count": 0,
            "positive_fraction": 0.0,
            "window_contract": "three_consecutive_calendar_months_monthly_step",
        }
    work["month"] = work["trade_date"].dt.to_period("M")
    months = sorted(work["month"].unique())
    rolling: dict[str, float] = {}
    for end_index in range(2, len(months)):
        window = months[end_index - 2 : end_index + 1]
        if int(window[-1].ordinal) - int(window[0].ordinal) != 2:
            continue
        selected = work[work["month"].isin(window)]
        key = f"{window[0]}/{window[-1]}"
        rolling[key] = float(pd.to_numeric(selected["rank_ic"]).mean())
    positive = sum(value > 0 for value in rolling.values())
    return {
        "quarter_count": int(len(rolling)),
        "positive_quarter_count": int(positive),
        "positive_fraction": float(positive / len(rolling)) if rolling else 0.0,
        "quarterly_mean_rank_ic": rolling,
        "window_contract": "three_consecutive_calendar_months_monthly_step",
    }


def monthly_block_bootstrap_difference(
    model_daily: pd.DataFrame,
    baseline_daily: pd.DataFrame,
    *,
    iterations: int = 2000,
    seed: int = 100,
) -> dict[str, float | int]:
    """Bootstrap monthly blocks of paired daily RankIC differences."""

    if iterations < 100:
        raise EvaluationError("bootstrap iterations 不得少于 100")
    _require_columns(model_daily, ["trade_date", "rank_ic"])
    _require_columns(baseline_daily, ["trade_date", "rank_ic"])
    left = model_daily[["trade_date", "rank_ic"]].rename(columns={"rank_ic": "model"})
    right = baseline_daily[["trade_date", "rank_ic"]].rename(columns={"rank_ic": "baseline"})
    left["trade_date"] = pd.to_datetime(left["trade_date"], errors="coerce")
    right["trade_date"] = pd.to_datetime(right["trade_date"], errors="coerce")
    paired = left.merge(right, on="trade_date", how="inner", validate="one_to_one")
    paired = paired.replace([np.inf, -np.inf], np.nan).dropna()
    if paired.empty:
        raise EvaluationError("模型与基线没有可配对的日 RankIC")
    paired["month"] = paired["trade_date"].dt.to_period("M").astype(str)
    blocks = [group["model"].to_numpy() - group["baseline"].to_numpy() for _, group in paired.groupby("month")]
    if len(blocks) < 2:
        raise EvaluationError("月度 block bootstrap 至少需要两个自然月")
    rng = np.random.default_rng(seed)
    samples = np.empty(iterations, dtype=np.float64)
    for index in range(iterations):
        selected = rng.integers(0, len(blocks), size=len(blocks))
        draw = np.concatenate([blocks[item] for item in selected])
        samples[index] = float(np.mean(draw))
    return {
        "iterations": iterations,
        "paired_days": int(len(paired)),
        "month_blocks": int(len(blocks)),
        "mean_difference": float(np.mean(paired["model"] - paired["baseline"])),
        "ci95_lower": float(np.quantile(samples, 0.025)),
        "ci95_upper": float(np.quantile(samples, 0.975)),
    }


def top_quantile_return_after_cost(
    frame: pd.DataFrame,
    *,
    cost_bps: Decimal,
    top_fraction: float = 0.1,
    score_column: str = "raw_score",
    date_column: str = "trade_date",
) -> dict[str, float | int | str]:
    """Evaluate executable next-session entries and 10-session exits after costs."""

    if not 0 < top_fraction <= 1:
        raise EvaluationError("top_fraction 必须位于 (0, 1]")
    execution_columns = [
        "entry_date",
        "exit_date",
        "entry_price_raw",
        "exit_price_raw",
        "entry_tradable",
        "exit_tradable",
        "entry_limit_blocked",
        "exit_limit_blocked",
        "stamp_duty_rate",
        "corporate_action_factor",
        "corporate_action_event_count",
        "holding_period_sessions",
    ]
    _require_columns(frame, [score_column, date_column, *execution_columns])
    _finite_numeric(
        frame,
        [
            score_column,
            "entry_price_raw",
            "exit_price_raw",
            "stamp_duty_rate",
            "corporate_action_factor",
            "corporate_action_event_count",
        ],
    )
    work = frame.copy()
    for column in (date_column, "entry_date", "exit_date"):
        work[column] = pd.to_datetime(work[column], errors="coerce")
        if work[column].isna().any():
            raise EvaluationError(f"{column} 含无效日期")
    if not bool((work["entry_date"] > work[date_column]).all()):
        raise EvaluationError("成交入口必须晚于信号日")
    if not bool((work["exit_date"] > work["entry_date"]).all()):
        raise EvaluationError("成交退出必须晚于入口")
    if not bool((pd.to_numeric(work["holding_period_sessions"], errors="coerce") == 10).all()):
        raise EvaluationError("持有期必须固定为10个交易日")
    if bool((work[["entry_price_raw", "exit_price_raw"]] <= 0).any().any()):
        raise EvaluationError("原始成交价必须为正")
    factors = pd.to_numeric(work["corporate_action_factor"], errors="coerce")
    action_counts = pd.to_numeric(work["corporate_action_event_count"], errors="coerce")
    if (factors <= 0).any() or (action_counts < 0).any() or not np.equal(
        action_counts.to_numpy(dtype=float),
        np.floor(action_counts.to_numpy(dtype=float)),
    ).all():
        raise EvaluationError("corporate action 因子/事件数无效")
    expected_stamp = np.where(
        work["exit_date"] < pd.Timestamp("2023-08-28"),
        0.001,
        0.0005,
    )
    if not np.allclose(
        pd.to_numeric(work["stamp_duty_rate"], errors="coerce"),
        expected_stamp,
        rtol=0,
        atol=1e-12,
    ):
        raise EvaluationError("卖方印花税未按有效期版本化")
    for column in (
        "entry_tradable",
        "exit_tradable",
        "entry_limit_blocked",
        "exit_limit_blocked",
    ):
        work[column] = _strict_boolean(work[column], column=column)
    daily_returns: list[float] = []
    selected_count = 0
    for _, group in work.groupby(date_column, sort=True):
        entry_eligible = group[
            group["entry_tradable"]
            & ~group["entry_limit_blocked"]
        ]
        if entry_eligible.empty:
            raise EvaluationError("至少一个信号日没有可成交候选")
        count = max(1, int(np.ceil(len(entry_eligible) * top_fraction)))
        selected = entry_eligible.nlargest(count, score_column)
        if not bool(
            (
                selected["exit_tradable"].astype(bool)
                & ~selected["exit_limit_blocked"]
            ).all()
        ):
            raise EvaluationError("入选组合存在无法按合同退出的证券")
        gross_ratio = (
            pd.to_numeric(selected["exit_price_raw"], errors="raise")
            / (
                pd.to_numeric(selected["entry_price_raw"], errors="raise")
                * pd.to_numeric(selected["corporate_action_factor"], errors="raise")
            )
        )
        net = (
            gross_ratio
            * (1.0 - pd.to_numeric(selected["stamp_duty_rate"], errors="raise"))
            - 1.0
        )
        daily_returns.append(float(net.mean()))
        selected_count += len(selected)
    cost = float(cost_bps / Decimal("10000"))
    after_cost = np.asarray(daily_returns, dtype=np.float64) - cost
    return {
        "cost_bps": str(cost_bps),
        "observation_count": int(len(after_cost)),
        "selected_trade_count": int(selected_count),
        "holding_period_sessions": 10,
        "execution_contract": (
            "next_session_raw_price_with_limit_suspension_corporate_action_"
            "and_exit_value_stamp_duty_checks"
        ),
        "mean_return_after_cost": float(after_cost.mean()) if len(after_cost) else float("nan"),
    }


def evaluate_gate(
    *,
    data_status: str,
    adapter_ce_improvement: float,
    validation_rank_ic: float,
    zero_shot_rank_ic: float,
    head_only_rank_ic: float,
    positive_quarter_fraction: float,
    bootstrap_ci95_lower: float,
    base_after_cost_return: float,
    stress_after_cost_return: float,
    thresholds: GateThresholds | None = None,
) -> dict[str, Any]:
    """Apply the non-negotiable model release gate."""

    limits = thresholds or GateThresholds()
    values = [
        adapter_ce_improvement,
        validation_rank_ic,
        zero_shot_rank_ic,
        head_only_rank_ic,
        positive_quarter_fraction,
        bootstrap_ci95_lower,
        base_after_cost_return,
        stress_after_cost_return,
    ]
    if not np.isfinite(np.asarray(values, dtype=np.float64)).all():
        raise EvaluationError("准出指标存在 NaN 或 Inf")
    reasons: list[str] = []
    if data_status != "production_ready":
        reasons.append(f"data_status={data_status}，未达到 production_ready")
    if adapter_ce_improvement < limits.adapter_ce_improvement_min:
        reasons.append("adapter Token CE 改善不足 1%")
    if validation_rank_ic < limits.validation_rank_ic_min:
        reasons.append("验证集日均 RankIC 低于 0.03")
    strongest_simple = max(zero_shot_rank_ic, head_only_rank_ic)
    if validation_rank_ic - strongest_simple < limits.baseline_rank_ic_lift_min:
        reasons.append("相对 zero-shot/head-only 的 RankIC 提升不足 0.005")
    if positive_quarter_fraction <= limits.positive_quarter_fraction_min:
        reasons.append("正 RankIC 季度未超过半数")
    if bootstrap_ci95_lower <= limits.bootstrap_lower_bound_min:
        reasons.append("相对最强基线的 bootstrap 95% 下界未大于 0")
    if base_after_cost_return <= 0:
        reasons.append("35 bp 成本后收益不为正")
    if stress_after_cost_return < 0:
        reasons.append("70 bp 压力成本后收益为负")
    passed = not reasons
    return {
        "schema_version": GATE_SCHEMA_VERSION,
        "gate_status": "passed" if passed else "blocked",
        "publishable": passed,
        "evidence_class": EVIDENCE_CLASS,
        "output_type": "model_output" if passed else "N/A",
        "reasons": reasons,
        "thresholds": {key: str(value) if isinstance(value, Decimal) else value for key, value in asdict(limits).items()},
    }


def build_score_record(
    *,
    as_of: str,
    ticker: str,
    raw_score: float,
    percentile: float,
    forecast_path: list[dict[str, Any]],
    path_dispersion: float,
    dataset_id: str,
    run_id: str,
    adapter_hash: str,
    gate_status: str,
    constraint_flags: list[str],
    horizon: int = 10,
) -> dict[str, Any]:
    if gate_status not in {"passed", "blocked"}:
        raise EvaluationError("gate_status 必须为 passed 或 blocked")
    if not 0 <= percentile <= 1:
        raise EvaluationError("percentile 必须位于 [0, 1]")
    if horizon != 10:
        raise EvaluationError("kronos-a-share-v1 固定 horizon=10")
    if not np.isfinite([raw_score, percentile, path_dispersion]).all():
        raise EvaluationError("score 输出存在 NaN 或 Inf")
    return {
        "as_of": as_of,
        "ticker": ticker,
        "horizon": horizon,
        "raw_score": raw_score,
        "percentile": percentile,
        "forecast_path": forecast_path,
        "path_dispersion": path_dispersion,
        "dataset_id": dataset_id,
        "run_id": run_id,
        "adapter_hash": adapter_hash,
        "gate_status": gate_status,
        "constraint_flags": list(constraint_flags),
        "evidence_class": EVIDENCE_CLASS,
        "output_type": "model_output" if gate_status == "passed" else "N/A",
    }

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image


DAY_STRUCT = struct.Struct("<IIIIIfII")
DFCF_STATUS = "dfcf_vendor_only_unverified_by_exchange"
CAP_STATUS = "vendor_only_unverified_by_official_source_with_date_quality_flags"
RATIO_QUANTUM = Decimal("0.00000001")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8-sig")
    os.replace(temporary, path)


def atomic_write_json(payload: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def parse_day_bytes(payload: bytes) -> pd.DataFrame:
    if len(payload) % DAY_STRUCT.size:
        raise ValueError("创业板指 .day 文件长度不是 32 字节的整数倍")
    rows: list[dict[str, object]] = []
    for offset in range(0, len(payload), DAY_STRUCT.size):
        value = DAY_STRUCT.unpack(payload[offset : offset + DAY_STRUCT.size])
        raw_date, _, _, _, close, _, _, _ = value
        rows.append(
            {
                "date": pd.to_datetime(str(raw_date), format="%Y%m%d", errors="raise"),
                "chinext_close": Decimal(close) / Decimal("100"),
            }
        )
    frame = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    if frame.empty or frame["date"].duplicated().any() or frame["chinext_close"].le(0).any():
        raise ValueError("创业板指 .day 数据为空、重复或包含无效收盘价")
    return frame


def load_audited_inputs(project_root: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object], dict[str, object]]:
    dfcf_dir = project_root / "artifacts" / "leverage_capitulation" / "dfcf_daily"
    cap_dir = project_root / "artifacts" / "leverage_capitulation" / "market_cap"
    margin_path = dfcf_dir / "dfcf_margin_balances.csv"
    dfcf_audit_path = dfcf_dir / "dfcf_margin_audit.json"
    cap_path = cap_dir / "a_share_total_market_cap_vendor_history.csv"
    cap_audit_path = cap_dir / "a_share_total_market_cap_audit.json"
    dfcf_audit = json.loads(dfcf_audit_path.read_text(encoding="utf-8"))
    cap_audit = json.loads(cap_audit_path.read_text(encoding="utf-8"))
    if not dfcf_audit.get("dfcf_only") or dfcf_audit.get("exchange_requests") != 0:
        raise ValueError("DFCF 审计门未通过")
    if dfcf_audit.get("dfcf_margin_balances_sha256") != sha256_file(margin_path):
        raise ValueError("DFCF 合并表哈希不匹配")
    if cap_audit.get("a_share_total_market_cap_sha256") != sha256_file(cap_path):
        raise ValueError("A股总市值原始表哈希不匹配")
    margin = pd.read_csv(margin_path, encoding="utf-8-sig", dtype={"total_margin_y": "string"})
    market_cap = pd.read_csv(
        cap_path,
        encoding="utf-8-sig",
        dtype={"a_share_total_market_cap_yi": "string"},
    )
    margin["date"] = pd.to_datetime(margin["date"], errors="raise")
    market_cap["source_date_raw"] = pd.to_datetime(market_cap["source_date_raw"], errors="raise")
    return margin, market_cap, dfcf_audit, cap_audit


def decimal_ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = 50
        return (numerator / denominator * Decimal("100")).quantize(
            RATIO_QUANTUM, rounding=ROUND_HALF_UP
        )


def build_panel(
    margin: pd.DataFrame,
    market_cap: pd.DataFrame,
    chinext: pd.DataFrame,
    *,
    start_date: str,
) -> tuple[pd.DataFrame, dict[str, int]]:
    required_margin = {"date", "total_margin_y", "sample_status"}
    required_cap = {
        "source_date_raw",
        "a_share_total_market_cap_yi",
        "duplicate_count_for_date",
        "is_weekend",
        "date_mapping_status",
        "reporting_eligible",
    }
    if required_margin - set(margin.columns) or required_cap - set(market_cap.columns):
        raise ValueError("输入表缺少必要字段")
    if not margin["sample_status"].eq(DFCF_STATUS).all():
        raise ValueError("DFCF 表的厂商口径标记异常")
    if margin["date"].duplicated().any():
        raise ValueError("DFCF 合并表包含重复日期")

    lower = pd.Timestamp(start_date)
    margin = margin.loc[margin["date"].ge(lower), ["date", "total_margin_y"]].copy()
    market_cap = market_cap.loc[market_cap["source_date_raw"].ge(lower)].copy()
    market_cap["recomputed_duplicate_count"] = market_cap.groupby("source_date_raw")[
        "source_date_raw"
    ].transform("size")
    if not market_cap["duplicate_count_for_date"].astype(int).eq(
        market_cap["recomputed_duplicate_count"]
    ).all():
        raise ValueError("A股总市值表的重复日期标记与原始日期不一致")
    eligible_cap = market_cap.loc[
        market_cap["recomputed_duplicate_count"].eq(1)
        & ~market_cap["is_weekend"].astype(bool)
        & market_cap["date_mapping_status"].eq("unverified"),
        ["source_date_raw", "a_share_total_market_cap_yi"],
    ].rename(columns={"source_date_raw": "date"})
    if eligible_cap["date"].duplicated().any() or chinext["date"].duplicated().any():
        raise ValueError("用于精确对齐的市值或创业板指日期不唯一")
    panel = (
        margin.merge(eligible_cap, on="date", how="inner", validate="one_to_one")
        .merge(chinext, on="date", how="inner", validate="one_to_one")
        .sort_values("date")
        .reset_index(drop=True)
    )
    if panel.empty:
        raise ValueError("没有同时满足 DFCF、市值和创业板指日期门槛的观测")

    panel["total_margin_y"] = panel["total_margin_y"].map(Decimal)
    panel["a_share_total_market_cap_yi"] = panel["a_share_total_market_cap_yi"].map(Decimal)
    if panel["total_margin_y"].le(0).any() or panel["a_share_total_market_cap_yi"].le(0).any():
        raise ValueError("两融余额或市值存在非正值")
    base_close = panel.iloc[0]["chinext_close"]
    panel["sh_sz_margin_to_all_a_market_cap_pct"] = panel.apply(
        lambda row: decimal_ratio(row["total_margin_y"], row["a_share_total_market_cap_yi"]), axis=1
    )
    panel["chinext_normalized"] = panel["chinext_close"].map(
        lambda value: decimal_ratio(value, base_close)
    )
    panel["date_alignment_status"] = "exact_date_with_local_tdx_chinext_calendar"
    panel["market_cap_vendor_status"] = "date_validated_by_local_tdx_only"
    panel["reporting_eligible"] = False
    panel["total_margin_y"] = panel["total_margin_y"].map(str)
    panel["a_share_total_market_cap_yi"] = panel["a_share_total_market_cap_yi"].map(str)
    panel["chinext_close"] = panel["chinext_close"].map(str)
    panel["sh_sz_margin_to_all_a_market_cap_pct"] = panel[
        "sh_sz_margin_to_all_a_market_cap_pct"
    ].map(str)
    panel["chinext_normalized"] = panel["chinext_normalized"].map(str)
    diagnostics = {
        "dfcf_rows_since_start": len(margin),
        "market_cap_rows_since_start": len(market_cap),
        "market_cap_duplicate_dates_excluded": int(
            market_cap.loc[market_cap["recomputed_duplicate_count"].gt(1), "source_date_raw"].nunique()
        ),
        "market_cap_weekend_rows_excluded": int(market_cap["is_weekend"].astype(bool).sum()),
        "common_rows": len(panel),
        "dfcf_rows_not_in_common": len(margin) - len(panel),
    }
    return panel, diagnostics


def build_monthly_panel(panel: pd.DataFrame) -> pd.DataFrame:
    copy = panel.copy()
    copy["month"] = copy["date"].dt.to_period("M")
    return copy.groupby("month", as_index=False).tail(1).drop(columns="month").reset_index(drop=True)


def draw_chart(monthly: pd.DataFrame, output_path: Path) -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    dates = monthly["date"]
    ratio = pd.to_numeric(monthly["sh_sz_margin_to_all_a_market_cap_pct"])
    chinext_normalized = pd.to_numeric(monthly["chinext_normalized"])
    fig, primary = plt.subplots(figsize=(16, 8), constrained_layout=True)
    primary.plot(dates, ratio, color="#c0392b", linewidth=1.8, label="沪深融资余额/全A市值")
    primary.set_ylabel("沪深融资余额 / 全A市值（%）", color="#c0392b")
    primary.tick_params(axis="y", labelcolor="#c0392b")
    primary.grid(axis="y", alpha=0.25)
    secondary = primary.twinx()
    secondary.plot(
        dates,
        chinext_normalized,
        color="#1f77b4",
        linewidth=1.5,
        label="创业板指（首个共同日=100）",
    )
    secondary.set_ylabel("创业板指 399006（2014-01-02=100）", color="#1f77b4")
    secondary.tick_params(axis="y", labelcolor="#1f77b4")
    primary.set_title("探索性厂商口径：沪深融资余额/全A市值 与 创业板指走势（2014年至今）")
    primary.set_xlabel("日期（每月最后一个可精确对齐观测）")
    primary.text(
        0.01,
        -0.16,
        "分子仅含沪深融资余额，分母按提供方声明含沪深北A股；仅精确日期交集，不补值、不前填，不用于正式回测。",
        transform=primary.transAxes,
        fontsize=9,
    )
    lines = primary.get_lines() + secondary.get_lines()
    primary.legend(lines, [line.get_label() for line in lines], loc="upper left")
    temporary = output_path.with_suffix(".tmp.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(temporary, dpi=180, bbox_inches="tight")
    plt.close(fig)
    with Image.open(temporary) as image:
        image.verify()
    os.replace(temporary, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="绘制融资余额/全A市值与创业板指探索性曲线")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--tdx-root", default=r"D:\HT")
    parser.add_argument("--start-date", default="2014-01-01")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve() if args.project_root else Path(__file__).resolve().parents[1]
    if not (project_root / "AGENTS.md").exists():
        raise FileNotFoundError(f"cannot confirm project root: {project_root}")
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else project_root / "artifacts" / "leverage_capitulation" / "exploratory_margin_market_cap"
    )
    margin, market_cap, dfcf_audit, market_cap_audit = load_audited_inputs(project_root)
    day_path = Path(args.tdx_root) / "vipdoc" / "sz" / "lday" / "sz399006.day"
    chinext = parse_day_bytes(day_path.read_bytes())
    panel, diagnostics = build_panel(
        margin,
        market_cap,
        chinext,
        start_date=args.start_date,
    )
    monthly = build_monthly_panel(panel)
    daily_path = output_dir / "dfcf_margin_to_a_share_market_cap_chinext_2014_present_daily.csv"
    monthly_path = output_dir / "dfcf_margin_to_a_share_market_cap_chinext_2014_present_monthly.csv"
    chart_path = output_dir / "dfcf_margin_to_a_share_market_cap_chinext_2014_present.png"
    audit_path = output_dir / "dfcf_margin_to_a_share_market_cap_chinext_2014_present_audit.json"
    atomic_write_csv(panel, daily_path)
    atomic_write_csv(monthly, monthly_path)
    draw_chart(monthly, chart_path)
    audit = {
        "analysis_type": "exploratory_vendor_series_not_for_formal_backtest",
        "formula": "sh_sz_margin_to_all_a_market_cap_pct = total_margin_y / a_share_total_market_cap_yi * 100",
        "scope_mismatch_warning": (
            "分子为 DFCF 沪深两市融资余额，分母为提供方声明覆盖沪深北已上市A股的总市值；"
            "因此这是范围不完全一致的描述性代理，不能解读为全A融资余额占比。"
        ),
        "date_alignment_rule": (
            "date >= start; DFCF date unique; market-cap source_date_raw globally unique and not weekend; "
            "exact inner join with local TDX sz399006 daily close dates; no fill or date shifting"
        ),
        "source_boundaries": {
            "margin": "DFCF/东方财富Choice厂商口径，未经交易所复核",
            "market_cap": "乐咕乐股厂商原始辅助序列，未经交易所/中国结算复核",
            "chinext": "本地 TDX 厂商日线 sz399006，非交易所官方",
        },
        "dfcf_input_audit_sha256": sha256_file(
            project_root / "artifacts" / "leverage_capitulation" / "dfcf_daily" / "dfcf_margin_audit.json"
        ),
        "dfcf_margin_table_sha256": sha256_file(
            project_root / "artifacts" / "leverage_capitulation" / "dfcf_daily" / "dfcf_margin_balances.csv"
        ),
        "market_cap_input_audit_sha256": sha256_file(
            project_root / "artifacts" / "leverage_capitulation" / "market_cap" / "a_share_total_market_cap_audit.json"
        ),
        "market_cap_table_sha256": sha256_file(
            project_root / "artifacts" / "leverage_capitulation" / "market_cap" / "a_share_total_market_cap_vendor_history.csv"
        ),
        "chinext_day_path": str(day_path),
        "chinext_day_sha256": sha256_file(day_path),
        "start_date": panel.iloc[0]["date"].date().isoformat(),
        "end_date": panel.iloc[-1]["date"].date().isoformat(),
        "first_ratio_pct": panel.iloc[0]["sh_sz_margin_to_all_a_market_cap_pct"],
        "last_ratio_pct": panel.iloc[-1]["sh_sz_margin_to_all_a_market_cap_pct"],
        "minimum_ratio_pct": str(
            min(map(Decimal, panel["sh_sz_margin_to_all_a_market_cap_pct"]))
        ),
        "maximum_ratio_pct": str(
            max(map(Decimal, panel["sh_sz_margin_to_all_a_market_cap_pct"]))
        ),
        "dfcf_audit_flags": {
            "dfcf_only": dfcf_audit["dfcf_only"],
            "exchange_requests": dfcf_audit["exchange_requests"],
        },
        "market_cap_source_warning": market_cap_audit["date_quality_warning"],
        "market_cap_reporting_eligible": False,
        "tdx_evidence_label": "market_data_vendor",
        "diagnostics": diagnostics,
        "daily_csv_sha256": sha256_file(daily_path),
        "monthly_csv_sha256": sha256_file(monthly_path),
        "chart_png_sha256": sha256_file(chart_path),
        "updated_at_utc": utc_now(),
    }
    atomic_write_json(audit, audit_path)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

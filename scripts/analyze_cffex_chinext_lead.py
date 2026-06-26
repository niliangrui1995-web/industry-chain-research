"""Analyze CFFEX index-futures position changes vs next-day ChiNext returns.

Data scope:
- CFFEX official post-close ranking CSVs:
  http://www.cffex.com.cn/sj/ccpm/YYYYMM/DD/{IF|IH|IC|IM}_1.csv
- CFFEX official daily contract trading CSVs for main-contract selection:
  http://www.cffex.com.cn/sj/hqsj/rtj/YYYYMM/DD/YYYYMMDD_1.csv
- ChiNext Index daily K-line from Tencent Finance:
  https://web.ifzq.gtimg.cn/appstock/app/fqkline/get
"""

from __future__ import annotations

import argparse
import io
import json
import math
import re
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests


PRODUCTS = ("IF", "IH", "IC", "IM")
DEFAULT_START = "2025-04-09"
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    )
}


@dataclass(frozen=True)
class FetchStats:
    rank_files: int
    daily_files: int
    cache_hits: int
    fetch_failures: int


class Downloader:
    def __init__(self, cache_root: Path, sleep_seconds: float = 0.12) -> None:
        self.cache_root = cache_root
        self.sleep_seconds = sleep_seconds
        self.rank_files = 0
        self.daily_files = 0
        self.cache_hits = 0
        self.fetch_failures = 0
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)

    def stats(self) -> FetchStats:
        return FetchStats(
            rank_files=self.rank_files,
            daily_files=self.daily_files,
            cache_hits=self.cache_hits,
            fetch_failures=self.fetch_failures,
        )

    def fetch_bytes(self, url: str, cache_path: Path, force: bool = False) -> bytes | None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        if cache_path.exists() and not force:
            self.cache_hits += 1
            return cache_path.read_bytes()

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=25)
                if response.status_code == 200 and response.content.strip():
                    cache_path.write_bytes(response.content)
                    time.sleep(self.sleep_seconds)
                    return response.content
                last_error = RuntimeError(f"HTTP {response.status_code}")
            except requests.RequestException as exc:
                last_error = exc
            time.sleep(self.sleep_seconds * (attempt + 1))

        self.fetch_failures += 1
        print(f"WARN fetch failed: {url} ({last_error})")
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and analyze CFFEX IF/IH/IC/IM main-contract position changes vs next-day ChiNext returns."
    )
    parser.add_argument("--start", default=DEFAULT_START, help="Start date, YYYY-MM-DD.")
    parser.add_argument(
        "--end",
        default=date.today().isoformat(),
        help="End date, YYYY-MM-DD. Defaults to today.",
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts/futures_chinext_lead_analysis",
        help="Output directory for cached raw data, CSVs, and report.",
    )
    parser.add_argument("--force", action="store_true", help="Refetch cached raw files.")
    return parser.parse_args()


def parse_yyyymmdd(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def cffex_date_parts(trade_date: str) -> tuple[str, str]:
    normalized = trade_date.replace("-", "")
    return normalized[:6], normalized[6:]


def decode_gbk_csv(content: bytes) -> str:
    return content.decode("gbk", errors="replace")


def fetch_chinext_daily(start: str, end: str) -> pd.DataFrame:
    url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    params = {
        "_var": "kline_dayqfq",
        "param": f"sz399006,day,{start},{end},1000,qfq",
    }
    response = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=25)
    response.raise_for_status()
    text = response.text
    payload_text = text.split("=", 1)[1] if "=" in text else text
    payload = json.loads(payload_text)
    rows = payload["data"]["sz399006"]["day"]
    df = pd.DataFrame(rows, columns=["date", "open", "close", "high", "low", "volume"])
    numeric_cols = ["open", "close", "high", "low", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.sort_values("date").reset_index(drop=True)
    df["return_pct"] = df["close"].pct_change() * 100
    df["next_date"] = df["date"].shift(-1)
    df["next_return_pct"] = df["return_pct"].shift(-1)
    df["next_up"] = df["next_return_pct"] > 0
    return df


def parse_cffex_daily_contracts(content: bytes, trade_date: date) -> pd.DataFrame:
    text = decode_gbk_csv(content)
    raw = pd.read_csv(io.StringIO(text))
    raw = raw[~raw["合约代码"].isin(["小计", "合计"])].copy()
    raw["合约代码"] = raw["合约代码"].astype(str).str.strip()
    raw = raw[raw["合约代码"].str.match(r"^(IF|IH|IC|IM)\d{4}$", na=False)].copy()
    if raw.empty:
        return pd.DataFrame()

    # CFFEX hqsj CSV columns are stable; keep names explicit for auditability.
    raw.columns = [
        "contract",
        "open",
        "high",
        "low",
        "volume",
        "turnover",
        "open_interest",
        "_unused_1",
        "close",
        "settle",
        "pre_settle",
        "_unused_2",
        "_unused_3",
        "_unused_4",
    ]
    keep = [
        "contract",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "open_interest",
        "turnover",
        "settle",
        "pre_settle",
    ]
    df = raw[keep].copy()
    for col in keep[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["date"] = trade_date
    df["product"] = df["contract"].str.extract(r"^([A-Z]+)")
    return df[
        [
            "date",
            "product",
            "contract",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "open_interest",
            "turnover",
            "settle",
            "pre_settle",
        ]
    ]


def parse_cffex_rank(content: bytes, product: str) -> pd.DataFrame:
    text = decode_gbk_csv(content)
    df = pd.read_csv(io.StringIO(text), header=[0, 1])
    df.columns = [
        "trade_date",
        "contract",
        "rank",
        "vol_member",
        "vol",
        "vol_chg",
        "long_member",
        "long_oi",
        "long_oi_chg",
        "short_member",
        "short_oi",
        "short_oi_chg",
    ]
    df = df[pd.to_numeric(df["rank"], errors="coerce").notna()].copy()
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["trade_date"].astype(str), format="%Y%m%d").dt.date
    df["product"] = product
    for col in ["rank", "vol", "vol_chg", "long_oi", "long_oi_chg", "short_oi", "short_oi_chg"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["contract", "vol_member", "long_member", "short_member"]:
        df[col] = df[col].astype(str).str.strip()
    return df[
        [
            "date",
            "product",
            "contract",
            "rank",
            "vol_member",
            "vol",
            "vol_chg",
            "long_member",
            "long_oi",
            "long_oi_chg",
            "short_member",
            "short_oi",
            "short_oi_chg",
        ]
    ]


def fetch_cffex_dataset(
    dates: Iterable[date], downloader: Downloader, force: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    contract_rows: list[pd.DataFrame] = []
    rank_rows: list[pd.DataFrame] = []

    for trade_date in dates:
        yyyymm = trade_date.strftime("%Y%m")
        dd = trade_date.strftime("%d")
        yyyymmdd = trade_date.strftime("%Y%m%d")
        daily_url = f"http://www.cffex.com.cn/sj/hqsj/rtj/{yyyymm}/{dd}/{yyyymmdd}_1.csv"
        daily_cache = downloader.cache_root / "cffex_daily" / yyyymm / f"{yyyymmdd}_1.csv"
        daily_content = downloader.fetch_bytes(daily_url, daily_cache, force=force)
        if daily_content is None:
            continue
        downloader.daily_files += 1
        daily_df = parse_cffex_daily_contracts(daily_content, trade_date)
        if daily_df.empty:
            continue
        contract_rows.append(daily_df)

        for product in PRODUCTS:
            rank_url = f"http://www.cffex.com.cn/sj/ccpm/{yyyymm}/{dd}/{product}_1.csv"
            rank_cache = downloader.cache_root / "cffex_rank" / yyyymm / f"{yyyymmdd}_{product}_1.csv"
            rank_content = downloader.fetch_bytes(rank_url, rank_cache, force=force)
            if rank_content is None:
                continue
            downloader.rank_files += 1
            rank_df = parse_cffex_rank(rank_content, product)
            if not rank_df.empty:
                rank_rows.append(rank_df)

    contracts = pd.concat(contract_rows, ignore_index=True) if contract_rows else pd.DataFrame()
    ranks = pd.concat(rank_rows, ignore_index=True) if rank_rows else pd.DataFrame()
    if contracts.empty or ranks.empty:
        return contracts, ranks, pd.DataFrame()

    main_contracts = (
        contracts.sort_values(["date", "product", "volume", "open_interest", "contract"])
        .groupby(["date", "product"], as_index=False)
        .tail(1)
        .sort_values(["date", "product"])
        .reset_index(drop=True)
    )
    main_contracts = main_contracts.rename(
        columns={
            "contract": "main_contract",
            "volume": "main_contract_volume",
            "open_interest": "main_contract_open_interest",
        }
    )
    main_contracts = main_contracts[
        [
            "date",
            "product",
            "main_contract",
            "main_contract_volume",
            "main_contract_open_interest",
            "close",
            "settle",
            "pre_settle",
        ]
    ]
    return contracts, ranks, main_contracts


def build_daily_signals(ranks: pd.DataFrame, main_contracts: pd.DataFrame) -> pd.DataFrame:
    if ranks.empty or main_contracts.empty:
        return pd.DataFrame()

    main_keys = main_contracts[["date", "product", "main_contract"]].copy()
    main_ranks = ranks.merge(
        main_keys,
        left_on=["date", "product", "contract"],
        right_on=["date", "product", "main_contract"],
        how="inner",
    )
    grouped = (
        main_ranks.groupby(["date", "product", "contract"], as_index=False)
        .agg(
            top20_rank_rows=("rank", "count"),
            top20_volume=("vol", "sum"),
            top20_volume_chg=("vol_chg", "sum"),
            top20_long_oi=("long_oi", "sum"),
            top20_long_oi_chg=("long_oi_chg", "sum"),
            top20_short_oi=("short_oi", "sum"),
            top20_short_oi_chg=("short_oi_chg", "sum"),
        )
        .rename(columns={"contract": "main_contract"})
    )
    grouped["top20_net_oi"] = grouped["top20_long_oi"] - grouped["top20_short_oi"]
    grouped["top20_net_oi_chg"] = grouped["top20_long_oi_chg"] - grouped["top20_short_oi_chg"]
    grouped["net_buy_qty"] = grouped["top20_net_oi_chg"].clip(lower=0)
    grouped["net_sell_qty"] = (-grouped["top20_net_oi_chg"]).clip(lower=0)
    grouped["long_chg_positive"] = grouped["top20_long_oi_chg"] > 0
    grouped["short_chg_positive"] = grouped["top20_short_oi_chg"] > 0
    grouped["net_chg_positive"] = grouped["top20_net_oi_chg"] > 0
    grouped = grouped.merge(main_contracts, on=["date", "product", "main_contract"], how="left")
    return grouped.sort_values(["date", "product"]).reset_index(drop=True)


def build_model_dataset(signals: pd.DataFrame, chinext: pd.DataFrame) -> pd.DataFrame:
    wide = signals.pivot(index="date", columns="product")
    wide.columns = [f"{product}_{metric}" for metric, product in wide.columns]
    wide = wide.reset_index()
    dataset = wide.merge(
        chinext[["date", "return_pct", "next_date", "next_return_pct", "next_up"]],
        on="date",
        how="inner",
    )
    net_cols = [f"{product}_top20_net_oi_chg" for product in PRODUCTS]
    long_cols = [f"{product}_top20_long_oi_chg" for product in PRODUCTS]
    short_cols = [f"{product}_top20_short_oi_chg" for product in PRODUCTS]
    dataset["all_products_net_oi_chg_sum"] = dataset[net_cols].sum(axis=1, skipna=False)
    dataset["all_products_long_oi_chg_sum"] = dataset[long_cols].sum(axis=1, skipna=False)
    dataset["all_products_short_oi_chg_sum"] = dataset[short_cols].sum(axis=1, skipna=False)
    dataset = dataset[dataset["next_return_pct"].notna()].copy()
    return dataset.sort_values("date").reset_index(drop=True)


def build_product_direction_dataset(signals: pd.DataFrame, chinext: pd.DataFrame) -> pd.DataFrame:
    df = signals.merge(
        chinext[["date", "return_pct", "next_date", "next_return_pct", "next_up"]],
        on="date",
        how="left",
    )
    df["net_direction"] = np.select(
        [df["top20_net_oi_chg"] > 0, df["top20_net_oi_chg"] < 0],
        ["net_buy", "net_sell"],
        default="flat",
    )
    df["net_direction_cn"] = np.select(
        [df["top20_net_oi_chg"] > 0, df["top20_net_oi_chg"] < 0],
        ["净买入", "净卖出"],
        default="中性",
    )
    df["direction_qty"] = df["top20_net_oi_chg"].abs()
    df["next_down"] = df["next_return_pct"] < 0
    df["next_flat"] = df["next_return_pct"].eq(0)
    return df.sort_values(["date", "product"]).reset_index(drop=True)


def build_validation_tables(
    trading_dates: list[date],
    contracts: pd.DataFrame,
    ranks: pd.DataFrame,
    main_contracts: pd.DataFrame,
    signals: pd.DataFrame,
    chinext: pd.DataFrame,
    dataset: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    expected = pd.MultiIndex.from_product(
        [trading_dates, PRODUCTS], names=["date", "product"]
    ).to_frame(index=False)

    contract_coverage = (
        contracts.groupby(["date", "product"], as_index=False)
        .agg(
            contract_count=("contract", "nunique"),
            max_volume=("volume", "max"),
            contracts=("contract", lambda values: ";".join(sorted(set(values)))),
        )
        if not contracts.empty
        else pd.DataFrame(columns=["date", "product", "contract_count", "max_volume", "contracts"])
    )
    rank_coverage = (
        ranks.groupby(["date", "product"], as_index=False)
        .agg(
            rank_contract_count=("contract", "nunique"),
            rank_row_count=("rank", "count"),
            rank_contracts=("contract", lambda values: ";".join(sorted(set(values)))),
        )
        if not ranks.empty
        else pd.DataFrame(columns=["date", "product", "rank_contract_count", "rank_row_count", "rank_contracts"])
    )
    signal_coverage = (
        signals.groupby(["date", "product"], as_index=False)
        .agg(
            signal_count=("main_contract", "count"),
            main_contract=("main_contract", "first"),
            top20_rank_rows=("top20_rank_rows", "first"),
        )
        if not signals.empty
        else pd.DataFrame(columns=["date", "product", "signal_count", "main_contract", "top20_rank_rows"])
    )
    product_validation = (
        expected.merge(contract_coverage, on=["date", "product"], how="left")
        .merge(rank_coverage, on=["date", "product"], how="left")
        .merge(signal_coverage, on=["date", "product"], how="left")
    )
    product_validation["has_contract_daily"] = product_validation["contract_count"].notna()
    product_validation["has_rank_file"] = product_validation["rank_contract_count"].notna()
    product_validation["has_main_signal"] = product_validation["signal_count"].fillna(0).eq(1)
    product_validation["rank_rows_ok_for_main"] = product_validation["top20_rank_rows"].fillna(0).eq(20)
    product_validation["status"] = np.select(
        [
            ~product_validation["has_contract_daily"],
            ~product_validation["has_rank_file"],
            ~product_validation["has_main_signal"],
            ~product_validation["rank_rows_ok_for_main"],
        ],
        [
            "missing_cffex_daily_contract",
            "missing_cffex_rank",
            "missing_main_contract_signal",
            "main_contract_rank_rows_not_20",
        ],
        default="ok",
    )

    daily_expected = pd.DataFrame({"date": trading_dates})
    daily_validation = daily_expected.merge(
        chinext[["date", "return_pct", "next_date", "next_return_pct"]], on="date", how="left"
    )
    signal_counts = (
        signals.groupby("date", as_index=False).agg(product_signal_count=("product", "nunique"))
        if not signals.empty
        else pd.DataFrame(columns=["date", "product_signal_count"])
    )
    model_dates = dataset[["date"]].copy()
    model_dates["in_model_dataset"] = True
    daily_validation = (
        daily_validation.merge(signal_counts, on="date", how="left")
        .merge(model_dates, on="date", how="left")
    )
    daily_validation["has_chinext"] = daily_validation["return_pct"].notna()
    daily_validation["has_all_four_signals"] = daily_validation["product_signal_count"].fillna(0).eq(len(PRODUCTS))
    daily_validation["has_next_chinext_return"] = daily_validation["next_return_pct"].notna()
    daily_validation["in_model_dataset"] = daily_validation["in_model_dataset"].fillna(False).astype(bool)
    daily_validation["status"] = np.select(
        [
            ~daily_validation["has_chinext"],
            ~daily_validation["has_all_four_signals"],
            ~daily_validation["has_next_chinext_return"],
            ~daily_validation["in_model_dataset"],
        ],
        [
            "missing_chinext",
            "missing_all_four_futures_signals",
            "missing_next_chinext_return",
            "not_in_model_dataset",
        ],
        default="ok",
    )

    validation_summary = pd.DataFrame(
        [
            {"check": "expected_chinext_trading_days", "value": len(trading_dates)},
            {"check": "cffex_contract_rows", "value": len(contracts)},
            {"check": "cffex_rank_rows", "value": len(ranks)},
            {"check": "main_contract_rows", "value": len(main_contracts)},
            {"check": "main_signal_rows", "value": len(signals)},
            {"check": "model_dataset_rows", "value": len(dataset)},
            {"check": "product_date_rows_ok", "value": int(product_validation["status"].eq("ok").sum())},
            {"check": "product_date_rows_total", "value": len(product_validation)},
            {"check": "daily_rows_ok", "value": int(daily_validation["status"].eq("ok").sum())},
            {"check": "daily_rows_total", "value": len(daily_validation)},
            {"check": "latest_futures_signal_date", "value": str(signals["date"].max()) if not signals.empty else ""},
            {"check": "latest_model_signal_date", "value": str(dataset["date"].max()) if not dataset.empty else ""},
            {"check": "latest_chinext_date", "value": str(chinext["date"].max()) if not chinext.empty else ""},
        ]
    )
    return product_validation, daily_validation, validation_summary


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    phat = successes / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return center - margin, center + margin


def summarize_condition(
    dataset: pd.DataFrame, signal_col: str, condition_name: str, mask: pd.Series
) -> dict[str, object]:
    sample = dataset[mask & dataset["next_return_pct"].notna()].copy()
    n = len(sample)
    up_count = int(sample["next_up"].sum()) if n else 0
    down_count = int((~sample["next_up"]).sum()) if n else 0
    ci_low, ci_high = wilson_interval(up_count, n)
    return {
        "signal": signal_col,
        "condition": condition_name,
        "sample_size": n,
        "next_up_count": up_count,
        "next_down_or_flat_count": down_count,
        "next_up_probability": up_count / n if n else math.nan,
        "next_up_prob_ci95_low": ci_low,
        "next_up_prob_ci95_high": ci_high,
        "avg_next_return_pct": sample["next_return_pct"].mean() if n else math.nan,
        "median_next_return_pct": sample["next_return_pct"].median() if n else math.nan,
        "avg_abs_next_return_pct": sample["next_return_pct"].abs().mean() if n else math.nan,
    }


def correlation_table(dataset: pd.DataFrame, signal_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for col in signal_cols:
        paired = dataset[[col, "next_return_pct"]].dropna()
        spearman_corr = math.nan
        if len(paired) > 1:
            spearman_corr = paired[col].rank().corr(paired["next_return_pct"].rank(), method="pearson")
        rows.append(
            {
                "signal": col,
                "sample_size": len(paired),
                "pearson_corr_next_return": paired[col].corr(paired["next_return_pct"], method="pearson")
                if len(paired) > 1
                else math.nan,
                "spearman_corr_next_return": spearman_corr,
            }
        )
    return pd.DataFrame(rows)


def conditional_probability_table(dataset: pd.DataFrame, signal_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for col in signal_cols:
        series = dataset[col]
        rows.append(summarize_condition(dataset, col, "> 0", series > 0))
        rows.append(summarize_condition(dataset, col, "< 0", series < 0))
        rows.append(summarize_condition(dataset, col, "top quartile", series >= series.quantile(0.75)))
        rows.append(summarize_condition(dataset, col, "bottom quartile", series <= series.quantile(0.25)))
    return pd.DataFrame(rows)


def summarize_direction_group(group: pd.DataFrame) -> dict[str, object]:
    sample = group[group["next_return_pct"].notna()].copy()
    n = len(sample)
    up_count = int(sample["next_up"].sum()) if n else 0
    down_count = int(sample["next_down"].sum()) if n else 0
    flat_count = int(sample["next_flat"].sum()) if n else 0
    ci_low, ci_high = wilson_interval(up_count, n)
    up_sample = sample[sample["next_return_pct"] > 0]
    down_sample = sample[sample["next_return_pct"] < 0]
    return {
        "sample_size": n,
        "next_up_count": up_count,
        "next_down_count": down_count,
        "next_flat_count": flat_count,
        "next_up_probability": up_count / n if n else math.nan,
        "next_down_probability": down_count / n if n else math.nan,
        "next_flat_probability": flat_count / n if n else math.nan,
        "next_up_prob_ci95_low": ci_low,
        "next_up_prob_ci95_high": ci_high,
        "avg_next_return_pct": sample["next_return_pct"].mean() if n else math.nan,
        "median_next_return_pct": sample["next_return_pct"].median() if n else math.nan,
        "avg_abs_next_return_pct": sample["next_return_pct"].abs().mean() if n else math.nan,
        "avg_up_return_pct": up_sample["next_return_pct"].mean() if len(up_sample) else math.nan,
        "avg_down_return_pct": down_sample["next_return_pct"].mean() if len(down_sample) else math.nan,
        "avg_direction_qty": sample["direction_qty"].mean() if n else math.nan,
        "median_direction_qty": sample["direction_qty"].median() if n else math.nan,
    }


def direction_probability_table(product_direction: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (product, direction, direction_cn), group in product_direction.groupby(
        ["product", "net_direction", "net_direction_cn"], observed=True
    ):
        row = {
            "product": product,
            "net_direction": direction,
            "net_direction_cn": direction_cn,
        }
        row.update(summarize_direction_group(group))
        rows.append(row)
    order = {"net_buy": 0, "net_sell": 1, "flat": 2}
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["_direction_order"] = df["net_direction"].map(order).fillna(9)
    df = df.sort_values(["product", "_direction_order"]).drop(columns=["_direction_order"])
    return df.reset_index(drop=True)


def quantity_return_relationship_table(product_direction: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    sample = product_direction[
        product_direction["next_return_pct"].notna()
        & product_direction["net_direction"].isin(["net_buy", "net_sell"])
        & (product_direction["direction_qty"] > 0)
    ].copy()
    for (product, direction, direction_cn), group in sample.groupby(
        ["product", "net_direction", "net_direction_cn"], observed=True
    ):
        n = len(group)
        pearson_corr = group["direction_qty"].corr(group["next_return_pct"], method="pearson") if n > 1 else math.nan
        spearman_corr = (
            group["direction_qty"].rank().corr(group["next_return_pct"].rank(), method="pearson")
            if n > 1
            else math.nan
        )
        abs_corr = group["direction_qty"].corr(group["next_return_pct"].abs(), method="pearson") if n > 1 else math.nan
        qty_var = group["direction_qty"].var(ddof=0)
        slope = (
            group["direction_qty"].cov(group["next_return_pct"], ddof=0) / qty_var
            if n > 1 and qty_var and not pd.isna(qty_var)
            else math.nan
        )
        rows.append(
            {
                "product": product,
                "net_direction": direction,
                "net_direction_cn": direction_cn,
                "sample_size": n,
                "qty_min": group["direction_qty"].min(),
                "qty_median": group["direction_qty"].median(),
                "qty_max": group["direction_qty"].max(),
                "pearson_corr_qty_next_return": pearson_corr,
                "spearman_corr_qty_next_return": spearman_corr,
                "pearson_corr_qty_abs_next_return": abs_corr,
                "ols_slope_return_pct_per_1000_contracts": slope * 1000 if not pd.isna(slope) else math.nan,
                "avg_next_return_pct": group["next_return_pct"].mean(),
                "next_up_probability": float(group["next_up"].mean()),
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    order = {"net_buy": 0, "net_sell": 1}
    df["_direction_order"] = df["net_direction"].map(order).fillna(9)
    df = df.sort_values(["product", "_direction_order"]).drop(columns=["_direction_order"])
    return df.reset_index(drop=True)


def quantity_bucket_probability_table(product_direction: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    sample = product_direction[
        product_direction["next_return_pct"].notna()
        & product_direction["net_direction"].isin(["net_buy", "net_sell"])
        & (product_direction["direction_qty"] > 0)
    ].copy()
    for (product, direction, direction_cn), group in sample.groupby(
        ["product", "net_direction", "net_direction_cn"], observed=True
    ):
        if len(group) < 20 or group["direction_qty"].nunique() < 4:
            continue
        group = group.copy()
        try:
            group["qty_bucket"] = pd.qcut(
                group["direction_qty"],
                q=4,
                labels=["Q1_数量低", "Q2", "Q3", "Q4_数量高"],
                duplicates="drop",
            )
        except ValueError:
            continue
        for bucket, bucket_group in group.groupby("qty_bucket", observed=True):
            n = len(bucket_group)
            rows.append(
                {
                    "product": product,
                    "net_direction": direction,
                    "net_direction_cn": direction_cn,
                    "qty_bucket": str(bucket),
                    "sample_size": n,
                    "qty_min": bucket_group["direction_qty"].min(),
                    "qty_max": bucket_group["direction_qty"].max(),
                    "next_up_probability": float(bucket_group["next_up"].mean()),
                    "avg_next_return_pct": bucket_group["next_return_pct"].mean(),
                    "median_next_return_pct": bucket_group["next_return_pct"].median(),
                    "avg_abs_next_return_pct": bucket_group["next_return_pct"].abs().mean(),
                }
            )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    order = {"net_buy": 0, "net_sell": 1}
    df["_direction_order"] = df["net_direction"].map(order).fillna(9)
    df = df.sort_values(["product", "_direction_order", "qty_bucket"]).drop(columns=["_direction_order"])
    return df.reset_index(drop=True)


def quantile_table(dataset: pd.DataFrame, signal_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for col in signal_cols:
        sample = dataset[[col, "next_return_pct", "next_up"]].dropna().copy()
        unique_count = sample[col].nunique()
        if len(sample) < 20 or unique_count < 4:
            continue
        try:
            sample["quantile"] = pd.qcut(sample[col], q=4, labels=["Q1_low", "Q2", "Q3", "Q4_high"], duplicates="drop")
        except ValueError:
            continue
        for quantile, group in sample.groupby("quantile", observed=True):
            n = len(group)
            up_count = int(group["next_up"].sum())
            rows.append(
                {
                    "signal": col,
                    "quantile": str(quantile),
                    "sample_size": n,
                    "signal_min": group[col].min(),
                    "signal_max": group[col].max(),
                    "next_up_probability": up_count / n if n else math.nan,
                    "avg_next_return_pct": group["next_return_pct"].mean(),
                    "median_next_return_pct": group["next_return_pct"].median(),
                }
            )
    return pd.DataFrame(rows)


def make_report(
    output_dir: Path,
    start: str,
    end: str,
    fetch_stats: FetchStats,
    chinext: pd.DataFrame,
    signals: pd.DataFrame,
    dataset: pd.DataFrame,
    correlations: pd.DataFrame,
    conditional: pd.DataFrame,
    quantiles: pd.DataFrame,
    product_direction: pd.DataFrame,
    direction_probability: pd.DataFrame,
    quantity_relationship: pd.DataFrame,
    quantity_buckets: pd.DataFrame,
    validation_summary: pd.DataFrame,
    product_validation: pd.DataFrame,
    daily_validation: pd.DataFrame,
) -> str:
    latest_signal_date = dataset["date"].max()
    first_signal_date = dataset["date"].min()
    sample_size = len(dataset)
    baseline_up_prob = float(dataset["next_up"].mean())
    baseline_avg_return = float(dataset["next_return_pct"].mean())

    def fmt_pct(value: float) -> str:
        if pd.isna(value):
            return "N/A"
        return f"{value:.2%}"

    def fmt_num(value: float) -> str:
        if pd.isna(value):
            return "N/A"
        return f"{value:.4f}"

    corr_top = correlations.reindex(
        correlations["pearson_corr_next_return"].abs().sort_values(ascending=False).index
    ).head(10)
    cond_focus = conditional[
        conditional["condition"].isin(["> 0", "< 0", "top quartile", "bottom quartile"])
    ].copy()
    cond_focus["edge_vs_baseline"] = cond_focus["next_up_probability"] - baseline_up_prob
    cond_top = cond_focus.reindex(cond_focus["edge_vs_baseline"].abs().sort_values(ascending=False).index).head(12)
    qty_focus = quantity_relationship.copy()
    validation_map = dict(zip(validation_summary["check"], validation_summary["value"]))
    bad_product_rows = product_validation[product_validation["status"] != "ok"].copy()
    bad_daily_rows = daily_validation[daily_validation["status"] != "ok"].copy()

    lines = [
        "# 股指期货主力持仓变化与次日创业板涨跌分析",
        "",
        f"- 样本区间：{first_signal_date} 至 {latest_signal_date}，请求区间 {start} 至 {end}。",
        f"- 有效信号样本：{sample_size} 个交易日；创业板次日上涨基准概率：{fmt_pct(baseline_up_prob)}；次日平均涨跌幅：{baseline_avg_return:.3f}%。",
        f"- 抓取结果：CFFEX 日交易文件 {fetch_stats.daily_files} 个，成交持仓排名文件 {fetch_stats.rank_files} 个，缓存命中 {fetch_stats.cache_hits} 次，失败 {fetch_stats.fetch_failures} 次。",
        "",
        "## 口径",
        "",
        "- 主力合约：每天按中金所日交易数据中同品种 `volume` 最大的合约确定。",
        "- 净买入/净卖出：中金所排名表披露的是会员 `持买单量` 和 `持卖单量` 及其较上一交易日增减，并非逐笔成交买卖；本报告使用主力合约前 20 名会员的持买单量增减合计、持卖单量增减合计。",
        "- 派生方向：`top20_net_oi_chg = top20_long_oi_chg - top20_short_oi_chg`；正值判定为净买入，负值判定为净卖出，绝对值作为对应方向数量。",
        "- 领先关系：用 T 日盘后公布的持仓变化，对齐 T+1 创业板指数涨跌幅，避免前视。",
        "",
        "## 真实性和完整性检查",
        "",
        f"- 创业板交易日数：{validation_map.get('expected_chinext_trading_days')}；中金所主力信号行数：{validation_map.get('main_signal_rows')}；模型有效样本：{validation_map.get('model_dataset_rows')}。",
        f"- 期货品种-日期覆盖：{validation_map.get('product_date_rows_ok')}/{validation_map.get('product_date_rows_total')} 通过。",
        f"- 日频 T+1 对齐覆盖：{validation_map.get('daily_rows_ok')}/{validation_map.get('daily_rows_total')} 通过。",
        f"- 最新创业板日期：{validation_map.get('latest_chinext_date')}；最新期货信号日期：{validation_map.get('latest_futures_signal_date')}；最新可用于 T+1 分析的信号日期：{validation_map.get('latest_model_signal_date')}。",
        "",
    ]
    if not bad_product_rows.empty:
        lines.extend(["### 期货覆盖异常样例", "", "| 日期 | 品种 | 状态 | 主力合约 | 排名行数 |", "|---|---|---|---|---:|"])
        for _, row in bad_product_rows.head(20).iterrows():
            lines.append(
                f"| {row['date']} | {row['product']} | {row['status']} | {row.get('main_contract', '')} | {row.get('top20_rank_rows', '')} |"
            )
        lines.append("")
    if not bad_daily_rows.empty:
        lines.extend(["### 日频对齐异常样例", "", "| 日期 | 状态 | 期货信号品种数 | 次日创业板日期 |", "|---|---|---:|---|"])
        for _, row in bad_daily_rows.head(20).iterrows():
            lines.append(
                f"| {row['date']} | {row['status']} | {row.get('product_signal_count', '')} | {row.get('next_date', '')} |"
            )
        lines.append("")

    lines.extend(
        [
            "## 每个品种净买入/净卖出后的次日概率",
            "",
            "| 品种 | 方向 | 样本数 | 次日上涨概率 | 次日下跌概率 | 次日平均涨跌幅 | 平均方向数量 |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in direction_probability.iterrows():
        lines.append(
            f"| {row['product']} | {row['net_direction_cn']} | {int(row['sample_size'])} | {fmt_pct(row['next_up_probability'])} | {fmt_pct(row['next_down_probability'])} | {row['avg_next_return_pct']:.3f}% | {row['avg_direction_qty']:.0f} |"
        )

    lines.extend(
        [
            "",
            "## 净买入/净卖出数量与次日涨跌幅",
            "",
            "| 品种 | 方向 | 样本数 | 数量中位数 | Pearson | Spearman | 每 1000 手斜率 | 次日平均涨跌幅 |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in qty_focus.iterrows():
        lines.append(
            f"| {row['product']} | {row['net_direction_cn']} | {int(row['sample_size'])} | {row['qty_median']:.0f} | {fmt_num(row['pearson_corr_qty_next_return'])} | {fmt_num(row['spearman_corr_qty_next_return'])} | {row['ols_slope_return_pct_per_1000_contracts']:.3f}% | {row['avg_next_return_pct']:.3f}% |"
        )

    bucket_focus = quantity_buckets[
        quantity_buckets["qty_bucket"].isin(["Q1_数量低", "Q4_数量高"])
    ].copy()
    if not bucket_focus.empty:
        lines.extend(
            [
                "",
                "## 数量高低分位对比",
                "",
                "| 品种 | 方向 | 数量分位 | 样本数 | 数量区间 | 次日上涨概率 | 次日平均涨跌幅 |",
                "|---|---|---|---:|---|---:|---:|",
            ]
        )
        for _, row in bucket_focus.iterrows():
            lines.append(
                f"| {row['product']} | {row['net_direction_cn']} | {row['qty_bucket']} | {int(row['sample_size'])} | {row['qty_min']:.0f}-{row['qty_max']:.0f} | {fmt_pct(row['next_up_probability'])} | {row['avg_next_return_pct']:.3f}% |"
            )

    lines.extend(
        [
            "",
            "## 单列宽表相关性补充",
            "",
            "| 信号 | 样本数 | Pearson | Spearman |",
            "|---|---:|---:|---:|",
        ]
    )
    for _, row in corr_top.iterrows():
        lines.append(
            f"| `{row['signal']}` | {int(row['sample_size'])} | {fmt_num(row['pearson_corr_next_return'])} | {fmt_num(row['spearman_corr_next_return'])} |"
        )

    lines.extend(
        [
            "",
            "## 条件概率偏离较大的情形",
            "",
            "| 信号 | 条件 | 样本数 | 次日上涨概率 | 相对基准 | 次日平均涨跌幅 |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in cond_top.iterrows():
        lines.append(
            f"| `{row['signal']}` | {row['condition']} | {int(row['sample_size'])} | {fmt_pct(row['next_up_probability'])} | {fmt_pct(row['edge_vs_baseline'])} | {row['avg_next_return_pct']:.3f}% |"
        )

    lines.extend(
        [
            "",
            "## 结论提示",
            "",
            "- 方向概率回答的是“当某品种 T 日净买入/净卖出后，T+1 创业板涨或跌的历史频率”。",
            "- 数量关系回答的是“在同一方向内部，净买入或净卖出数量越大，T+1 创业板涨跌幅是否线性变大或变小”。",
            "- 这是一段约一年多的日频样本，概率和相关性只能视作历史统计线索，不应单独作为交易规则。",
            "",
            "## 输出文件",
            "",
            f"- `data/chinext_daily.csv`：创业板指数日线与次日收益。",
            f"- `data/cffex_contract_daily.csv`：中金所股指期货日交易数据。",
            f"- `data/cffex_rank_rows.csv`：中金所成交持仓排名明细。",
            f"- `data/main_contract_signals.csv`：IF/IH/IC/IM 主力合约持仓变化信号。",
            f"- `data/product_direction_daily.csv`：每天每个品种的净买入/净卖出方向、数量和次日创业板涨跌幅。",
            f"- `data/model_dataset.csv`：T 日信号和 T+1 创业板涨跌幅对齐样本。",
            f"- `analysis/direction_probabilities.csv`：每个品种净买入/净卖出后的次日涨跌概率。",
            f"- `analysis/quantity_return_relationship.csv`：方向数量与次日涨跌幅的相关和斜率。",
            f"- `analysis/quantity_bucket_probabilities.csv`：数量分位对应的次日涨跌概率和平均涨跌幅。",
            f"- `analysis/correlations.csv`、`analysis/conditional_probabilities.csv`、`analysis/quantile_probabilities.csv`：统计结果。",
            f"- `analysis/validation_summary.csv`、`analysis/product_date_validation.csv`、`analysis/daily_alignment_validation.csv`：真实性和完整性检查。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    start_date = parse_yyyymmdd(args.start)
    end_date = parse_yyyymmdd(args.end)
    output_dir = Path(args.output_dir)
    data_dir = output_dir / "data"
    analysis_dir = output_dir / "analysis"
    cache_dir = output_dir / "raw_cache"
    data_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    chinext_fetch_start = (start_date - timedelta(days=14)).isoformat()
    chinext = fetch_chinext_daily(chinext_fetch_start, args.end)
    chinext = chinext[(chinext["date"] >= start_date) & (chinext["date"] <= end_date)].copy()
    trading_dates = chinext["date"].tolist()

    downloader = Downloader(cache_dir)
    contracts, ranks, main_contracts = fetch_cffex_dataset(trading_dates, downloader, force=args.force)
    if contracts.empty or ranks.empty or main_contracts.empty:
        raise RuntimeError("No CFFEX data was fetched; check network access and official endpoint availability.")

    signals = build_daily_signals(ranks, main_contracts)
    dataset = build_model_dataset(signals, chinext)
    product_direction = build_product_direction_dataset(signals, chinext)
    product_validation, daily_validation, validation_summary = build_validation_tables(
        trading_dates, contracts, ranks, main_contracts, signals, chinext, dataset
    )
    signal_cols = []
    for product in PRODUCTS:
        signal_cols.extend(
            [
                f"{product}_top20_long_oi_chg",
                f"{product}_top20_short_oi_chg",
                f"{product}_top20_net_oi_chg",
                f"{product}_net_buy_qty",
                f"{product}_net_sell_qty",
            ]
        )
    signal_cols.extend(
        [
            "all_products_long_oi_chg_sum",
            "all_products_short_oi_chg_sum",
            "all_products_net_oi_chg_sum",
        ]
    )
    signal_cols = [col for col in signal_cols if col in dataset.columns]

    correlations = correlation_table(dataset, signal_cols)
    conditional = conditional_probability_table(dataset, signal_cols)
    quantiles = quantile_table(dataset, signal_cols)
    direction_probability = direction_probability_table(product_direction)
    quantity_relationship = quantity_return_relationship_table(product_direction)
    quantity_buckets = quantity_bucket_probability_table(product_direction)

    chinext.to_csv(data_dir / "chinext_daily.csv", index=False, encoding="utf-8-sig")
    contracts.to_csv(data_dir / "cffex_contract_daily.csv", index=False, encoding="utf-8-sig")
    ranks.to_csv(data_dir / "cffex_rank_rows.csv", index=False, encoding="utf-8-sig")
    main_contracts.to_csv(data_dir / "cffex_main_contracts.csv", index=False, encoding="utf-8-sig")
    signals.to_csv(data_dir / "main_contract_signals.csv", index=False, encoding="utf-8-sig")
    product_direction.to_csv(data_dir / "product_direction_daily.csv", index=False, encoding="utf-8-sig")
    dataset.to_csv(data_dir / "model_dataset.csv", index=False, encoding="utf-8-sig")
    correlations.to_csv(analysis_dir / "correlations.csv", index=False, encoding="utf-8-sig")
    conditional.to_csv(analysis_dir / "conditional_probabilities.csv", index=False, encoding="utf-8-sig")
    quantiles.to_csv(analysis_dir / "quantile_probabilities.csv", index=False, encoding="utf-8-sig")
    direction_probability.to_csv(analysis_dir / "direction_probabilities.csv", index=False, encoding="utf-8-sig")
    quantity_relationship.to_csv(analysis_dir / "quantity_return_relationship.csv", index=False, encoding="utf-8-sig")
    quantity_buckets.to_csv(analysis_dir / "quantity_bucket_probabilities.csv", index=False, encoding="utf-8-sig")
    product_validation.to_csv(analysis_dir / "product_date_validation.csv", index=False, encoding="utf-8-sig")
    daily_validation.to_csv(analysis_dir / "daily_alignment_validation.csv", index=False, encoding="utf-8-sig")
    validation_summary.to_csv(analysis_dir / "validation_summary.csv", index=False, encoding="utf-8-sig")

    report = make_report(
        output_dir=output_dir,
        start=args.start,
        end=args.end,
        fetch_stats=downloader.stats(),
        chinext=chinext,
        signals=signals,
        dataset=dataset,
        correlations=correlations,
        conditional=conditional,
        quantiles=quantiles,
        product_direction=product_direction,
        direction_probability=direction_probability,
        quantity_relationship=quantity_relationship,
        quantity_buckets=quantity_buckets,
        validation_summary=validation_summary,
        product_validation=product_validation,
        daily_validation=daily_validation,
    )
    (output_dir / "report.md").write_text(report, encoding="utf-8")

    print(f"wrote {output_dir}")
    print(f"valid signal days: {len(dataset)}")
    print(f"latest signal date: {dataset['date'].max()}")


if __name__ == "__main__":
    main()

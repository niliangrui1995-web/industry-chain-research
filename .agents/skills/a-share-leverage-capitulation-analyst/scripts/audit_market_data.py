from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from collections import Counter
from pathlib import Path

import pandas as pd
import requests


DAY_STRUCT = struct.Struct("<IIIIIfII")
CNI_URL = "https://hq.cnindex.com.cn/market/market/getIndexDailyDataWithDataFormat"
INDEX_CODES = {"sz_comp": "399106", "chinext": "399006", "chinext_comp": "399102"}
A_SHARE_PATTERNS = (
    re.compile(r"sh(?:600|601|603|605|688|689)\d{3}"),
    re.compile(r"sz(?:000|001|002|003|300|301)\d{3}"),
    re.compile(r"bj(?:43|83|87|88|92)\d{4}"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_a_share(path: Path) -> bool:
    return any(pattern.fullmatch(path.stem.lower()) for pattern in A_SHARE_PATTERNS)


def discover_files(ht_root: Path) -> list[Path]:
    files: list[Path] = []
    for market in ("sh", "sz", "bj"):
        folder = ht_root / "vipdoc" / market / "lday"
        if folder.exists():
            files.extend(path for path in folder.glob("*.day") if is_a_share(path))
    return sorted(files)


def inspect_a_share_files(paths: list[Path]) -> tuple[pd.DataFrame, dict[str, object]]:
    daily: dict[int, list[int]] = {}
    invalid_size: list[str] = []
    invalid_order: list[str] = []
    invalid_ohlc_rows = 0
    extreme_return_rows = 0
    first_dates: Counter[int] = Counter()
    last_dates: Counter[int] = Counter()

    for path in paths:
        raw = path.read_bytes()
        if not raw or len(raw) % DAY_STRUCT.size:
            invalid_size.append(str(path))
            continue
        previous_date = 0
        previous_close = 0
        file_first = 0
        file_last = 0
        ordered = True
        for offset in range(0, len(raw), DAY_STRUCT.size):
            date_value, open_value, high_value, low_value, close_value, _, _, _ = DAY_STRUCT.unpack_from(raw, offset)
            if not 19900101 <= date_value <= 20991231:
                ordered = False
                continue
            if date_value <= previous_date:
                ordered = False
            if not file_first:
                file_first = date_value
            file_last = date_value
            if min(open_value, high_value, low_value, close_value) <= 0:
                invalid_ohlc_rows += 1
            elif high_value < max(open_value, close_value, low_value) or low_value > min(open_value, close_value):
                invalid_ohlc_rows += 1
            if previous_close > 0 and close_value > 0:
                values = daily.setdefault(date_value, [0, 0, 0, 0, 0, 0])
                values[0] += 1
                change = close_value / previous_close - 1.0
                if change < 0:
                    values[1] += 1
                elif change > 0:
                    values[2] += 1
                else:
                    values[3] += 1
                if abs(change) > 0.30:
                    values[4] += 1
                    if change < 0:
                        values[5] += 1
                    extreme_return_rows += 1
            previous_date = date_value
            previous_close = close_value
        if not ordered:
            invalid_order.append(str(path))
        if file_first:
            first_dates[file_first] += 1
            last_dates[file_last] += 1

    rows = [
        (date, values[0], values[1], values[2], values[3], values[4], values[5])
        for date, values in sorted(daily.items())
    ]
    breadth = pd.DataFrame(
        rows,
        columns=[
            "date",
            "breadth_total",
            "down_count",
            "up_count",
            "flat_count",
            "extreme_return_count",
            "extreme_down_count",
        ],
    )
    breadth["date"] = pd.to_datetime(breadth["date"].astype(str), format="%Y%m%d", errors="raise")
    breadth["down_pct"] = breadth["down_count"] / breadth["breadth_total"] * 100.0
    non_extreme_total = breadth["breadth_total"] - breadth["extreme_return_count"]
    breadth["down_pct_excluding_extreme"] = (
        (breadth["down_count"] - breadth["extreme_down_count"])
        / non_extreme_total.replace(0, pd.NA)
        * 100.0
    )
    report = {
        "a_share_files": len(paths),
        "invalid_size_files": len(invalid_size),
        "invalid_order_files": len(invalid_order),
        "invalid_ohlc_rows": invalid_ohlc_rows,
        "extreme_return_rows": extreme_return_rows,
        "earliest_a_share_date": str(min(first_dates)) if first_dates else None,
        "latest_a_share_date": str(max(last_dates)) if last_dates else None,
        "latest_date_file_count": int(last_dates[max(last_dates)]) if last_dates else 0,
        "invalid_size_examples": invalid_size[:10],
        "invalid_order_examples": invalid_order[:10],
    }
    return breadth, report


def read_local_index(path: Path) -> pd.DataFrame:
    raw = path.read_bytes()
    if not raw or len(raw) % DAY_STRUCT.size:
        raise ValueError(f"invalid index day file: {path}")
    rows = []
    for offset in range(0, len(raw), DAY_STRUCT.size):
        date_value, open_value, high_value, low_value, close_value, _, _, _ = DAY_STRUCT.unpack_from(
            raw, offset
        )
        rows.append(
            (
                date_value,
                open_value / 100.0,
                high_value / 100.0,
                low_value / 100.0,
                close_value / 100.0,
            )
        )
    frame = pd.DataFrame(
        rows,
        columns=["date", "local_open", "local_high", "local_low", "local_close"],
    )
    frame["date"] = pd.to_datetime(frame["date"].astype(str), format="%Y%m%d", errors="raise")
    frame["local_return_pct"] = frame["local_close"].pct_change() * 100.0
    return frame


def read_official_index(
    code: str,
    start_date: str,
    end_date: str,
    snapshot_path: Path | None = None,
) -> pd.DataFrame:
    if snapshot_path is None:
        response = requests.get(
            CNI_URL,
            params={
                "indexCode": code,
                "startDate": start_date,
                "endDate": end_date,
                "frequency": "day",
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
    else:
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if payload.get("code") != 200:
        raise ValueError(f"CNIndex error for {code}: {payload.get('message')}")
    rows = payload.get("data", {}).get("data", [])
    frame = pd.DataFrame(
        rows,
        columns=[
            "date",
            "_1",
            "official_high",
            "official_open",
            "official_low",
            "official_close",
            "_2",
            "return",
            "amount",
            "volume",
            "_3",
        ],
    )
    frame = frame[
        [
            "date",
            "official_open",
            "official_high",
            "official_low",
            "official_close",
            "return",
        ]
    ].copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    for column in ("official_open", "official_high", "official_low", "official_close"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    frame["official_return_pct"] = pd.to_numeric(
        frame.pop("return").astype(str).str.replace("%", "", regex=False), errors="raise"
    )
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    return frame.loc[frame["date"].between(start, end)].copy()


def compare_index(
    ht_root: Path,
    code: str,
    start_date: str,
    end_date: str,
    snapshot_path: Path | None = None,
) -> tuple[dict[str, object], pd.DataFrame]:
    local_path = ht_root / "vipdoc" / "sz" / "lday" / f"sz{code}.day"
    local = read_local_index(local_path)
    official = read_official_index(code, start_date, end_date, snapshot_path)
    compared = official.merge(local, on="date", how="outer", indicator=True)
    both = compared["_merge"].eq("both")
    compared["close_abs_error"] = (compared["official_close"] - compared["local_close"]).abs()
    compared["open_abs_error"] = (compared["official_open"] - compared["local_open"]).abs()
    compared["high_abs_error"] = (compared["official_high"] - compared["local_high"]).abs()
    compared["low_abs_error"] = (compared["official_low"] - compared["local_low"]).abs()
    compared["return_abs_error_pct_point"] = (
        compared["official_return_pct"] - compared["local_return_pct"]
    ).abs()
    report = {
        "official_rows": len(official),
        "official_start": official["date"].min().strftime("%Y-%m-%d"),
        "official_end": official["date"].max().strftime("%Y-%m-%d"),
        "missing_official_dates_in_local": int(compared["_merge"].eq("left_only").sum()),
        "local_dates_absent_from_official": int(compared["_merge"].eq("right_only").sum()),
        "close_mismatches_over_0_011": int((both & compared["close_abs_error"].gt(0.011)).sum()),
        "open_mismatches_over_0_011": int((both & compared["open_abs_error"].gt(0.011)).sum()),
        "high_mismatches_over_0_011": int((both & compared["high_abs_error"].gt(0.011)).sum()),
        "low_mismatches_over_0_011": int((both & compared["low_abs_error"].gt(0.011)).sum()),
        "return_mismatches_over_0_02_pct_point": int(
            (both & compared["return_abs_error_pct_point"].gt(0.02)).sum()
        ),
        "max_close_abs_error": float(compared.loc[both, "close_abs_error"].max()),
        "max_open_abs_error": float(compared.loc[both, "open_abs_error"].max()),
        "max_high_abs_error": float(compared.loc[both, "high_abs_error"].max()),
        "max_low_abs_error": float(compared.loc[both, "low_abs_error"].max()),
        "max_return_abs_error_pct_point": float(
            compared.loc[both, "return_abs_error_pct_point"].max()
        ),
        "official_source": CNI_URL if snapshot_path is None else str(snapshot_path.resolve()),
        "official_snapshot_sha256": None if snapshot_path is None else sha256_file(snapshot_path),
    }
    return report, compared


def to_jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit local TDX market data used by the factor")
    parser.add_argument("--ht-root", type=Path, default=Path(r"D:\HT"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--start-date", default="2014-01-01")
    parser.add_argument("--end-date", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    parser.add_argument("--snapshot-dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    files = discover_files(args.ht_root)
    if not files:
        raise FileNotFoundError(f"no A-share day files found under {args.ht_root}")
    breadth, report = inspect_a_share_files(files)
    breadth.to_csv(args.output_dir / "breadth_audit.csv", index=False, encoding="utf-8-sig")
    report["indexes"] = {}
    official_calendar: pd.Series | None = None
    for label, code in INDEX_CODES.items():
        snapshot_path: Path | None = None
        if args.snapshot_dir is not None:
            matches = sorted(
                args.snapshot_dir.glob(f"cnindex_{code}_*.json"),
                key=lambda path: path.stat().st_mtime,
            )
            if not matches:
                raise FileNotFoundError(f"No CNIndex snapshot for {code} under {args.snapshot_dir}")
            snapshot_path = matches[-1]
        index_report, compared = compare_index(
            args.ht_root,
            code,
            args.start_date,
            args.end_date,
            snapshot_path,
        )
        report["indexes"][label] = index_report
        compared.to_csv(args.output_dir / f"index_comparison_{code}.csv", index=False, encoding="utf-8-sig")
        if label == "sz_comp":
            official_calendar = compared.loc[compared["_merge"].ne("right_only"), "date"]

    assert official_calendar is not None
    coverage = pd.DataFrame({"date": official_calendar.drop_duplicates()}).merge(
        breadth, on="date", how="left", validate="one_to_one"
    )
    rolling_reference = coverage["breadth_total"].rolling(20, min_periods=1).median()
    coverage["coverage_ratio"] = coverage["breadth_total"] / rolling_reference
    coverage_fail = coverage["breadth_total"].lt(1000) | coverage["coverage_ratio"].lt(0.70)
    report["breadth_calendar_rows"] = len(coverage)
    report["breadth_missing_calendar_rows"] = int(coverage["breadth_total"].isna().sum())
    report["breadth_excluded_low_coverage_rows"] = int(coverage_fail.fillna(True).sum())
    report["breadth_excluded_low_coverage_dates"] = coverage.loc[
        coverage_fail.fillna(True), "date"
    ].dt.strftime("%Y-%m-%d").tolist()
    report["breadth_latest_date"] = breadth["date"].max().strftime("%Y-%m-%d")
    report["breadth_latest_count"] = int(breadth.iloc[-1]["breadth_total"])
    report["local_data_boundary"] = (
        "TDX is vendor data. Structural and official-index cross-checks do not convert stock-level breadth into official exchange data."
    )
    report["pass_for_backtest"] = (
        report["invalid_size_files"] == 0
        and report["invalid_order_files"] == 0
        and report["invalid_ohlc_rows"] == 0
        and report["breadth_missing_calendar_rows"] == 0
        and all(
            item["missing_official_dates_in_local"] == 0
            and item["close_mismatches_over_0_011"] == 0
            and item["open_mismatches_over_0_011"] == 0
            and item["high_mismatches_over_0_011"] == 0
            and item["low_mismatches_over_0_011"] == 0
            for item in report["indexes"].values()
        )
    )
    (args.output_dir / "market_data_audit.json").write_text(
        json.dumps(to_jsonable(report), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(to_jsonable(report), ensure_ascii=False, indent=2))
    return 0 if report["pass_for_backtest"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

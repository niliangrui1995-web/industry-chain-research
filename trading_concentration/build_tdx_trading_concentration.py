"""构建“通达信全A等权 AMOUNT 口径 C5”交易集中度日度发布包。

原始输入只读自用户的 ``D:\\HT\\vipdoc`` 日线目录；本任务目录只落盘
加工后的 CSV、JSON 和 manifest，不复制任何原始 .day 文件。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import posixpath
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree

import numpy as np


DAY_DTYPE = np.dtype(
    [
        ("date", "<u4"),
        ("open", "<u4"),
        ("high", "<u4"),
        ("low", "<u4"),
        ("close", "<u4"),
        ("amount", "<f4"),
        ("volume", "<u4"),
        ("reserved", "<u4"),
    ]
)
DAY_RECORD_BYTES = DAY_DTYPE.itemsize

START_DATE = 20130101
BEIJING_UNIVERSE_SWITCH_DATE = 20220802
AI_CHAIN_START_DATE = 20250101
TASK_DIRECTORY = Path("trading_concentration")
DEFAULT_OUTPUT_DIRECTORY = TASK_DIRECTORY / "data"
PUBLISH_DIRECTORY = Path(r"D:\vcp_hunter\基金持仓\public\data")
PAYLOAD_FILENAME = "trading-concentration-dashboard.json"
MANIFEST_FILENAME = "trading-concentration-dashboard.manifest.json"
CSV_FILENAME = "trading-concentration-daily.csv"
AI_CHAIN_WORKBOOK_RELATIVE_PATH = Path("watchlists") / "AI产业链.xlsx"
AI_CHAIN_SHEET_NAME = "AI产业链"
AI_CHAIN_CODE_HEADER = "代码"

MARKET_DIRECTORIES = {
    "sh": Path("vipdoc/sh/lday"),
    "sz": Path("vipdoc/sz/lday"),
    "bj": Path("vipdoc/bj/lday"),
}
CANDIDATE_PREFIXES = {
    "sh": ("600", "601", "603", "605", "688", "689"),
    "sz": ("000", "001", "002", "003", "300", "301"),
    "bj": ("43", "83", "87", "88", "92"),
}
DENOMINATOR_PATHS = {
    "sh880008": Path("vipdoc/sh/lday/sh880008.day"),
}
CHINEXT_INDEX_PATH = Path("vipdoc/sz/lday/sz399006.day")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SECURITY_CODE_PATTERN = re.compile(r"^\d{6}$")
OOXML_MAIN_NAMESPACE = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
OOXML_RELATIONSHIP_NAMESPACE = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
OOXML_PACKAGE_RELATIONSHIP_NAMESPACE = "{http://schemas.openxmlformats.org/package/2006/relationships}"


@dataclass(frozen=True)
class FileSnapshot:
    path: Path
    market: str
    code: str
    size: int
    mtime_ns: int


@dataclass(frozen=True)
class DenominatorRow:
    date: int
    amount_yuan: float
    source: str


@dataclass(frozen=True)
class AIChainUniverse:
    workbook_path: Path
    workbook_sha256: str
    input_codes: tuple[str, ...]
    resolved_codes: tuple[str, ...]
    non_stock_code_rows_excluded: int


def beijing_now() -> str:
    return datetime.now(timezone(timedelta(hours=8), name="Asia/Shanghai")).isoformat(
        timespec="seconds"
    )


def compact_date_to_iso(value: int) -> str:
    raw = f"{int(value):08d}"
    try:
        return datetime.strptime(raw, "%Y%m%d").date().isoformat()
    except ValueError as exc:
        raise ValueError(f"无效 .day 日期: {value}") from exc


def parse_compact_date(value: str) -> int:
    if re.fullmatch(r"\d{8}", value) is None:
        raise ValueError("日期必须是 YYYYMMDD")
    compact_date_to_iso(int(value))
    return int(value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_bytes(payload: object) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def atomic_write_bytes(payload: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def code_from_day_path(path: Path, market: str) -> str | None:
    stem = path.stem.lower()
    if not stem.startswith(market):
        return None
    code = stem[len(market) :]
    return code if len(code) == 6 and code.isdigit() else None


def snapshot_file(path: Path, market: str, code: str) -> FileSnapshot:
    stat = path.stat()
    return FileSnapshot(
        path=path,
        market=market,
        code=code,
        size=stat.st_size,
        mtime_ns=stat.st_mtime_ns,
    )


def _column_from_cell_reference(value: str) -> str:
    match = re.fullmatch(r"([A-Z]+)\d+", value)
    if match is None:
        raise ValueError(f"XLSX 单元格坐标无效: {value}")
    return match.group(1)


def _xlsx_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        raw = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ElementTree.fromstring(raw)
    return ["".join(item.itertext()) for item in root.findall(f"{OOXML_MAIN_NAMESPACE}si")]


def _xlsx_cell_text(cell: ElementTree.Element, shared_strings: list[str]) -> str | None:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        inline = cell.find(f"{OOXML_MAIN_NAMESPACE}is")
        return "" if inline is None else "".join(inline.itertext())
    value = cell.find(f"{OOXML_MAIN_NAMESPACE}v")
    if value is None or value.text is None:
        return None
    if cell_type == "s":
        try:
            return shared_strings[int(value.text)]
        except (IndexError, ValueError) as exc:
            raise ValueError("XLSX sharedStrings 索引无效") from exc
    return value.text


def _xlsx_sheet_path(archive: zipfile.ZipFile, sheet_name: str) -> str:
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    target_sheet = next(
        (
            sheet
            for sheet in workbook.findall(f"{OOXML_MAIN_NAMESPACE}sheets/{OOXML_MAIN_NAMESPACE}sheet")
            if sheet.attrib.get("name") == sheet_name
        ),
        None,
    )
    if target_sheet is None:
        raise ValueError(f"XLSX 缺少工作表: {sheet_name}")
    relationship_id = target_sheet.attrib.get(f"{OOXML_RELATIONSHIP_NAMESPACE}id")
    if not relationship_id:
        raise ValueError(f"XLSX 工作表缺少关系标识: {sheet_name}")
    relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    target = next(
        (
            relation.attrib.get("Target")
            for relation in relationships.findall(f"{OOXML_PACKAGE_RELATIONSHIP_NAMESPACE}Relationship")
            if relation.attrib.get("Id") == relationship_id
        ),
        None,
    )
    if not target:
        raise ValueError(f"XLSX 工作表关系不存在: {sheet_name}")
    path = target.lstrip("/") if target.startswith("/") else posixpath.normpath(f"xl/{target}")
    if not path.startswith("xl/"):
        raise ValueError(f"XLSX 工作表路径不受支持: {target}")
    return path


def _xlsx_code_column_values(workbook_path: Path) -> list[str]:
    try:
        with zipfile.ZipFile(workbook_path) as archive:
            shared_strings = _xlsx_shared_strings(archive)
            sheet = ElementTree.fromstring(archive.read(_xlsx_sheet_path(archive, AI_CHAIN_SHEET_NAME)))
    except (OSError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise ValueError(f"无法读取 AI 产业链工作簿: {workbook_path}") from exc

    code_column: str | None = None
    values: list[str] = []
    for row in sheet.findall(f"{OOXML_MAIN_NAMESPACE}sheetData/{OOXML_MAIN_NAMESPACE}row"):
        cells: dict[str, str] = {}
        for cell in row.findall(f"{OOXML_MAIN_NAMESPACE}c"):
            reference = cell.attrib.get("r")
            if reference is None:
                continue
            text = _xlsx_cell_text(cell, shared_strings)
            if text is not None:
                cells[_column_from_cell_reference(reference)] = text.strip()
        if code_column is None:
            code_column = next(
                (column for column, value in cells.items() if value == AI_CHAIN_CODE_HEADER), None
            )
            if code_column is not None:
                continue
        elif code_column in cells:
            values.append(cells[code_column])
    if code_column is None:
        raise ValueError(f"{AI_CHAIN_SHEET_NAME} 未找到“{AI_CHAIN_CODE_HEADER}”列")
    return values


def ai_chain_codes_sha256(codes: Iterable[str]) -> str:
    canonical = "\n".join(codes).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def ai_chain_member_codes_sha256(codes: Iterable[str]) -> str:
    """返回与工作簿行顺序无关的 AI 成分集合指纹。"""

    return ai_chain_codes_sha256(sorted(codes))


def load_ai_chain_universe(project_root: Path) -> AIChainUniverse:
    workbook_path = (project_root / AI_CHAIN_WORKBOOK_RELATIVE_PATH).resolve()
    if not workbook_path.is_file():
        raise FileNotFoundError(f"缺少 AI 产业链工作簿: {workbook_path}")
    input_codes: list[str] = []
    resolved_codes: list[str] = []
    input_seen: set[str] = set()
    resolved_seen: set[str] = set()
    non_stock_code_rows_excluded = 0
    for raw_code in _xlsx_code_column_values(workbook_path):
        if not SECURITY_CODE_PATTERN.fullmatch(raw_code):
            if raw_code:
                non_stock_code_rows_excluded += 1
            continue
        if raw_code in input_seen:
            raise ValueError(f"AI 产业链工作簿代码重复: {raw_code}")
        input_seen.add(raw_code)
        resolved_code = raw_code
        if resolved_code in resolved_seen:
            raise ValueError(f"AI 产业链代码归一化后重复: {resolved_code}")
        input_codes.append(raw_code)
        resolved_codes.append(resolved_code)
        resolved_seen.add(resolved_code)
    if not resolved_codes:
        raise ValueError("AI 产业链工作簿没有可用证券代码")
    for code in resolved_codes:
        market_for_code(code)
    return AIChainUniverse(
        workbook_path=workbook_path,
        workbook_sha256=sha256_file(workbook_path),
        input_codes=tuple(input_codes),
        resolved_codes=tuple(resolved_codes),
        non_stock_code_rows_excluded=non_stock_code_rows_excluded,
    )


def assert_ai_chain_universe_unchanged(universe: AIChainUniverse) -> None:
    try:
        current_sha256 = sha256_file(universe.workbook_path)
    except OSError as exc:
        raise RuntimeError(f"计算期间 AI 产业链工作簿不可读: {universe.workbook_path}") from exc
    if current_sha256 != universe.workbook_sha256:
        raise RuntimeError("计算期间 AI 产业链工作簿发生变化，拒绝混合快照输出")


def market_for_code(code: str) -> str:
    for market, prefixes in CANDIDATE_PREFIXES.items():
        if code.startswith(prefixes):
            return market
    raise ValueError(f"AI 产业链代码不属于受支持的 A/BJ 市场: {code}")


def ai_chain_candidate_snapshots(
    universe: AIChainUniverse, candidates: Iterable[FileSnapshot]
) -> list[FileSnapshot]:
    by_key = {(candidate.market, candidate.code): candidate for candidate in candidates}
    selected: list[FileSnapshot] = []
    missing: list[str] = []
    for code in universe.resolved_codes:
        market = market_for_code(code)
        candidate = by_key.get((market, code))
        if candidate is None:
            missing.append(f"{code}.{market.upper()}")
        else:
            selected.append(candidate)
    if missing:
        raise FileNotFoundError(
            "AI 产业链成分缺少通达信 .day 日线，拒绝静默缩减分子: " + "、".join(missing)
        )
    return selected


def candidate_column_indexes(
    candidates: list[FileSnapshot], selected: Iterable[FileSnapshot]
) -> np.ndarray:
    positions = {(candidate.market, candidate.code): index for index, candidate in enumerate(candidates)}
    indexes: list[int] = []
    for candidate in selected:
        index = positions.get((candidate.market, candidate.code))
        if index is None:
            raise ValueError(f"AI 产业链候选股不在全 A 候选矩阵中: {candidate.path}")
        indexes.append(index)
    return np.asarray(indexes, dtype=np.intp)


def discover_candidate_files(tdx_root: Path) -> list[FileSnapshot]:
    snapshots: list[FileSnapshot] = []
    for market, prefixes in CANDIDATE_PREFIXES.items():
        directory = tdx_root / MARKET_DIRECTORIES[market]
        if not directory.is_dir():
            raise FileNotFoundError(f"缺少 {market} 日线目录: {directory}")
        for path in sorted(directory.glob(f"{market}*.day")):
            code = code_from_day_path(path, market)
            if code is None or not code.startswith(prefixes):
                continue
            snapshots.append(snapshot_file(path, market, code))
    if not snapshots:
        raise ValueError("未找到任何普通 A 股候选 .day 文件")
    return snapshots


def denominator_snapshots(tdx_root: Path) -> dict[str, FileSnapshot]:
    result: dict[str, FileSnapshot] = {}
    for name, relative_path in DENOMINATOR_PATHS.items():
        path = tdx_root / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"缺少分母日线: {path}")
        market = "sh" if name.startswith("sh") else "sz"
        code = name[2:]
        result[name] = snapshot_file(path, market, code)
    return result


def comparison_index_snapshot(tdx_root: Path) -> FileSnapshot:
    path = tdx_root / CHINEXT_INDEX_PATH
    if not path.is_file():
        raise FileNotFoundError(f"缺少创业板指日线: {path}")
    return snapshot_file(path, "sz", "399006")


def assert_snapshots_unchanged(snapshots: Iterable[FileSnapshot]) -> None:
    changed: list[str] = []
    for snapshot in snapshots:
        try:
            stat = snapshot.path.stat()
        except OSError:
            changed.append(str(snapshot.path))
            continue
        if stat.st_size != snapshot.size or stat.st_mtime_ns != snapshot.mtime_ns:
            changed.append(str(snapshot.path))
    if changed:
        preview = "；".join(changed[:5])
        suffix = " 等" if len(changed) > 5 else ""
        raise RuntimeError(f"计算期间本地日线发生变化，拒绝混合快照输出: {preview}{suffix}")


def read_day_array(path: Path, *, label: str) -> np.ndarray:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise OSError(f"无法读取 {label}: {path}") from exc
    if size == 0:
        raise ValueError(f"{label} 是空文件: {path}")
    if size % DAY_RECORD_BYTES != 0:
        raise ValueError(f"{label} 长度不是 {DAY_RECORD_BYTES} 字节记录的整数倍: {path}")
    return np.fromfile(path, dtype=DAY_DTYPE)


def amount_by_date(records: np.ndarray, *, label: str) -> dict[int, float]:
    result: dict[int, float] = {}
    for raw_date, raw_amount in zip(records["date"], records["amount"], strict=True):
        date = int(raw_date)
        compact_date_to_iso(date)
        if date in result:
            raise ValueError(f"{label} 出现重复交易日: {compact_date_to_iso(date)}")
        amount = float(raw_amount)
        if not math.isfinite(amount):
            raise ValueError(f"{label} 出现非有限成交额: {compact_date_to_iso(date)}")
        result[date] = amount
    return result


def close_by_date(records: np.ndarray, *, label: str) -> dict[int, float]:
    """读取指数收盘价；无效点留给调用方按日期呈现为缺口。"""

    result: dict[int, float] = {}
    seen_dates: set[int] = set()
    for raw_date, raw_close in zip(records["date"], records["close"], strict=True):
        date = int(raw_date)
        compact_date_to_iso(date)
        if date in seen_dates:
            raise ValueError(f"{label} 出现重复交易日: {compact_date_to_iso(date)}")
        seen_dates.add(date)
        close = float(raw_close) / 100
        if not math.isfinite(close):
            raise ValueError(f"{label} 出现非有限收盘价: {compact_date_to_iso(date)}")
        if close > 0:
            result[date] = close
    if not result:
        raise ValueError(f"{label} 没有有效收盘价")
    return result


def build_denominator_rows(
    denominator_data: dict[str, dict[int, float]], start_date: int
) -> tuple[list[DenominatorRow], list[dict[str, str]]]:
    full = denominator_data["sh880008"]
    rows: list[DenominatorRow] = []
    omitted: list[dict[str, str]] = []

    for date in sorted(date for date in full if date >= start_date):
        amount = full[date]
        if amount <= 0:
            omitted.append(
                {
                    "date": compact_date_to_iso(date),
                    "reason": "sh880008_not_positive",
                }
            )
            continue
        rows.append(DenominatorRow(date=date, amount_yuan=amount, source="sh880008"))

    rows.sort(key=lambda row: row.date)
    if not rows:
        raise ValueError("分母日历为空")
    if any(left.date >= right.date for left, right in zip(rows, rows[1:])):
        raise ValueError("分母日历日期不严格递增")
    return rows, omitted


def scan_active_amount_matrix(
    candidates: list[FileSnapshot], calendar_dates: np.ndarray
) -> tuple[np.ndarray, list[dict[str, str]]]:
    """把每只候选股票映射到分母日历；矩阵仅在内存中存在。"""

    matrix = np.zeros((calendar_dates.size, len(candidates)), dtype=np.float32)
    skipped: list[dict[str, str]] = []
    calendar_start = int(calendar_dates[0])
    calendar_end = int(calendar_dates[-1])

    for column, snapshot in enumerate(candidates):
        try:
            if snapshot.size == 0:
                raise ValueError("empty_day_file")
            if snapshot.size % DAY_RECORD_BYTES != 0:
                raise ValueError("invalid_day_record_length")
            records = np.fromfile(snapshot.path, dtype=DAY_DTYPE)
        except (OSError, ValueError) as exc:
            skipped.append({"path": str(snapshot.path), "reason": str(exc)})
            continue

        valid = (
            (records["date"] >= calendar_start)
            & (records["date"] <= calendar_end)
            & (records["close"] > 0)
            & (records["amount"] > 0)
            & np.isfinite(records["amount"])
            & (records["volume"] > 0)
        )
        if snapshot.market == "bj":
            valid &= records["date"] >= BEIJING_UNIVERSE_SWITCH_DATE
        if not bool(valid.any()):
            continue

        record_dates = records["date"][valid]
        positions = np.searchsorted(calendar_dates, record_dates)
        matches = positions < calendar_dates.size
        matched_indexes = np.nonzero(matches)[0]
        if matched_indexes.size:
            matches[matched_indexes] &= (
                calendar_dates[positions[matched_indexes]] == record_dates[matched_indexes]
            )
        if not bool(matches.any()):
            continue
        matrix[positions[matches], column] = records["amount"][valid][matches]

    return matrix, skipped


def rounded_yi(amount_yuan: float) -> float:
    # 保留 8 位小数，既满足网页展示精度，也保证极小合成样本可由输出字段反算 C5。
    return round(amount_yuan / 100_000_000, 8)


def build_ai_chain_series_records(
    denominator_rows: list[DenominatorRow],
    amount_matrix: np.ndarray,
    *,
    c5_output_dates: set[int],
) -> list[dict[str, object]]:
    """计算当前 AI 产业链工作簿快照的全池成交额占比分子。

    该序列独立于 C5：分子是工作簿中全部当日成交活跃成分的 AMOUNT 之和，
    而不是在 AI 股票池内再取前 5%。2025-01-01 前不回溯，避免把当前
    成分表伪装成历史逐日成分。输出日历严格跟随实际 C5 records；若全 A
    当日无有效样本而 C5 被记为 omitted，则 AI 也不额外产生孤立空值日。
    """

    if amount_matrix.shape[0] != len(denominator_rows):
        raise ValueError("AI 产业链分子矩阵和分母日历行数不一致")
    records: list[dict[str, object]] = []
    for row_index, denominator in enumerate(denominator_rows):
        if denominator.date < AI_CHAIN_START_DATE or denominator.date not in c5_output_dates:
            continue
        active_amounts = amount_matrix[row_index]
        active_amounts = active_amounts[active_amounts > 0]
        active_stock_count = int(active_amounts.size)
        if active_stock_count == 0:
            records.append(
                {
                    "date": compact_date_to_iso(denominator.date),
                    "ai_chain_amount_pct": None,
                    "ai_chain_amount_yi": None,
                    "ai_chain_active_stock_count": 0,
                }
            )
            continue
        amount_yuan = float(active_amounts.sum(dtype=np.float64))
        amount_pct = 100 * amount_yuan / denominator.amount_yuan
        if not math.isfinite(amount_pct) or amount_pct < 0:
            raise ValueError(f"{compact_date_to_iso(denominator.date)} 计算出无效 AI 产业链成交额占比")
        records.append(
            {
                "date": compact_date_to_iso(denominator.date),
                "ai_chain_amount_pct": round(amount_pct, 6),
                "ai_chain_amount_yi": rounded_yi(amount_yuan),
                "ai_chain_active_stock_count": active_stock_count,
            }
        )
    return records


def build_ai_chain_series(
    records: list[dict[str, object]], universe: AIChainUniverse
) -> dict[str, object]:
    return {
        "name": "AI产业链成交额占比",
        "field": "ai_chain_amount_pct",
        "start_date": compact_date_to_iso(AI_CHAIN_START_DATE),
        "definition": "AI产业链成交额占比 = 当前 AI产业链.xlsx 股票池中当日成交活跃成分的 AMOUNT 之和 / sh880008.day.amount × 100%。",
        "active_stock_rule": "close > 0 且 amount > 0 且 volume > 0；不插值。",
        "universe": {
            "workbook": str(AI_CHAIN_WORKBOOK_RELATIVE_PATH).replace("\\", "/"),
            "sheet": AI_CHAIN_SHEET_NAME,
            "code_column": AI_CHAIN_CODE_HEADER,
            "code_count": len(universe.resolved_codes),
            "codes_sha256": ai_chain_codes_sha256(universe.resolved_codes),
            "member_codes_sha256": ai_chain_member_codes_sha256(universe.resolved_codes),
        },
        "records": records,
    }


def build_ai_chain_manifest(
    series_records: list[dict[str, object]],
    universe: AIChainUniverse,
    candidates: Iterable[FileSnapshot],
) -> dict[str, object]:
    series_dates = [record["date"] for record in series_records]
    return {
        "name": "AI产业链成交额占比",
        "field": "ai_chain_amount_pct",
        "start_date": compact_date_to_iso(AI_CHAIN_START_DATE),
        "data_range": {
            "start": series_dates[0] if series_dates else None,
            "end": series_dates[-1] if series_dates else None,
        },
        "records": len(series_records),
        "missing_output_records": sum(
            record.get("ai_chain_amount_pct") is None for record in series_records
        ),
        "formula": "sum(AI产业链当前股票池当日有效 AMOUNT) / sh880008.day.amount × 100%。",
        "active_stock_rule": "close > 0 且 amount > 0 且 volume > 0；不插值。",
        "universe": {
            "workbook_path": str(universe.workbook_path),
            "workbook_sha256": universe.workbook_sha256,
            "sheet": AI_CHAIN_SHEET_NAME,
            "code_column": AI_CHAIN_CODE_HEADER,
            "input_code_count": len(universe.input_codes),
            "resolved_code_count": len(universe.resolved_codes),
            "resolved_code_sha256": ai_chain_codes_sha256(universe.resolved_codes),
            "member_codes_sha256": ai_chain_member_codes_sha256(universe.resolved_codes),
            "non_stock_code_rows_excluded": universe.non_stock_code_rows_excluded,
            "code_aliases": [],
            "tdx_candidate_file_count": sum(1 for _ in candidates),
        },
    }


def build_records(
    denominator_rows: list[DenominatorRow],
    amount_matrix: np.ndarray,
    chinext_close_by_date: dict[int, float],
) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    if amount_matrix.shape[0] != len(denominator_rows):
        raise ValueError("分子矩阵和分母日历行数不一致")
    records: list[dict[str, object]] = []
    omitted: list[dict[str, str]] = []

    for row_index, denominator in enumerate(denominator_rows):
        active_amounts = amount_matrix[row_index]
        active_amounts = active_amounts[active_amounts > 0]
        active_stock_count = int(active_amounts.size)
        if active_stock_count == 0:
            omitted.append(
                {"date": compact_date_to_iso(denominator.date), "reason": "no_active_candidate_stock"}
            )
            continue
        top5_stock_count = (active_stock_count + 19) // 20
        top_amount_yuan = float(
            np.partition(active_amounts, active_stock_count - top5_stock_count)[
                active_stock_count - top5_stock_count :
            ].sum(dtype=np.float64)
        )
        c5_pct = 100 * top_amount_yuan / denominator.amount_yuan
        if not math.isfinite(c5_pct) or c5_pct < 0:
            raise ValueError(f"{compact_date_to_iso(denominator.date)} 计算出无效 C5")
        chinext_close = chinext_close_by_date.get(denominator.date)
        records.append(
            {
                "date": compact_date_to_iso(denominator.date),
                "chinext_close": round(chinext_close, 2) if chinext_close is not None else None,
                "c5_pct": round(c5_pct, 6),
                "top5_amount_yi": rounded_yi(top_amount_yuan),
                "market_amount_yi": rounded_yi(denominator.amount_yuan),
                "active_stock_count": active_stock_count,
                "top5_stock_count": top5_stock_count,
                "denominator_source": denominator.source,
                "numerator_scope": (
                    "sh_sz_bj_active_a"
                    if denominator.date >= BEIJING_UNIVERSE_SWITCH_DATE
                    else "sh_sz_active_a"
                ),
            }
        )
    return records, omitted


def records_to_csv_bytes(records: list[dict[str, object]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=[
            "date",
            "chinext_close",
            "c5_pct",
            "top5_amount_yi",
            "market_amount_yi",
            "active_stock_count",
            "top5_stock_count",
            "denominator_source",
            "numerator_scope",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(records)
    return stream.getvalue().encode("utf-8")


def candidate_counts(candidates: Iterable[FileSnapshot]) -> dict[str, int]:
    result = {market: 0 for market in CANDIDATE_PREFIXES}
    for candidate in candidates:
        result[candidate.market] += 1
    return result


def build_payload(
    records: list[dict[str, object]], generated_at: str, ai_chain_series: dict[str, object]
) -> dict[str, object]:
    return {
        "schema_version": "1",
        "generated_at_beijing": generated_at,
        "records": records,
        "ai_chain_series": ai_chain_series,
        "provenance": {
            "evidence_level": "market_data_vendor",
            "source": "通达信本地盘后 .day 日线",
            "metric_name": "通达信全A等权 AMOUNT 口径 C5",
            "definition": "C5 = 当日成交活跃普通 A 股中，成交额前 5% 个股成交额之和 / sh880008.day.amount × 100%。",
            "active_stock_rule": "close > 0 且 amount > 0 且 volume > 0；K = ceil(0.05 × N)。",
            "comparison_index": {
                "code": "399006",
                "name": "创业板指",
                "field": "chinext_close",
                "value": "收盘价",
            },
            "raw_data_copied": False,
            "scope_warning": "该曲线以通达信全A等权品种的 AMOUNT 字段为分母，并以通达信厂商日线中的交易活跃 A 股为分子代理；不等同于官方逐日全市场成分清单。未设置覆盖率门槛，也不插值。",
        },
    }


def build_manifest(
    *,
    records: list[dict[str, object]],
    generated_at: str,
    tdx_root: Path,
    candidates: list[FileSnapshot],
    denominator_files: dict[str, FileSnapshot],
    comparison_index_file: FileSnapshot,
    comparison_index_close_by_date: dict[int, float],
    ai_chain_series_records: list[dict[str, object]],
    ai_chain_universe: AIChainUniverse,
    ai_chain_candidates: list[FileSnapshot],
    skipped_candidate_files: list[dict[str, str]],
    omitted_dates: list[dict[str, str]],
) -> dict[str, object]:
    candidate_file_count = candidate_counts(candidates)
    denominator_inputs = {
        name: {
            "path": str(snapshot.path),
            "bytes": snapshot.size,
            "sha256": sha256_file(snapshot.path),
            "last_write_time_utc": datetime.fromtimestamp(
                snapshot.mtime_ns / 1_000_000_000, tz=timezone.utc
            ).isoformat(timespec="seconds"),
        }
        for name, snapshot in denominator_files.items()
    }
    comparison_index_dates = sorted(comparison_index_close_by_date)
    comparison_index_input = {
        "code": "399006",
        "name": "创业板指",
        "field": "chinext_close",
        "value": "收盘价",
        "price_scale": "close / 100",
        "source": "通达信本地盘后 .day 日线",
        "path": str(comparison_index_file.path),
        "bytes": comparison_index_file.size,
        "sha256": sha256_file(comparison_index_file.path),
        "last_write_time_utc": datetime.fromtimestamp(
            comparison_index_file.mtime_ns / 1_000_000_000, tz=timezone.utc
        ).isoformat(timespec="seconds"),
        "data_range": {
            "start": compact_date_to_iso(comparison_index_dates[0]),
            "end": compact_date_to_iso(comparison_index_dates[-1]),
        },
        "missing_output_records": sum(
            record.get("chinext_close") is None for record in records
        ),
    }
    return {
        "schema_version": "1",
        "generated_at_beijing": generated_at,
        "payload_sha256": None,
        "csv_sha256": None,
        "payload_records": len(records),
        "data_range": {
            "start": records[0]["date"] if records else None,
            "end": records[-1]["date"] if records else None,
        },
        "evidence_level": "market_data_vendor",
        "source": "通达信本地盘后 .day 日线",
        "raw_data_copied": False,
        "source_paths": {
            "tdx_root": str(tdx_root),
            "sh_l_day": str(tdx_root / MARKET_DIRECTORIES["sh"]),
            "sz_l_day": str(tdx_root / MARKET_DIRECTORIES["sz"]),
            "bj_l_day": str(tdx_root / MARKET_DIRECTORIES["bj"]),
        },
        "denominator_inputs": denominator_inputs,
        "comparison_index_input": comparison_index_input,
        "ai_chain_series": build_ai_chain_manifest(
            ai_chain_series_records, ai_chain_universe, ai_chain_candidates
        ),
        "denominator_segments": [
            {
                "start": compact_date_to_iso(START_DATE),
                "end": records[-1]["date"] if records else None,
                "source": "sh880008",
                "formula": "sh880008.day.amount",
            },
        ],
        "numerator_segments": [
            {
                "start": compact_date_to_iso(START_DATE),
                "end": "2022-08-01",
                "scope": "sh_sz_active_a",
            },
            {
                "start": "2022-08-02",
                "end": records[-1]["date"] if records else None,
                "scope": "sh_sz_bj_active_a",
            },
        ],
        "candidate_prefix_rules": {
            market: list(prefixes) for market, prefixes in CANDIDATE_PREFIXES.items()
        },
        "candidate_file_count": candidate_file_count,
        "candidate_file_count_total": len(candidates),
        "candidate_total_bytes": sum(candidate.size for candidate in candidates),
        "skipped_candidate_files": skipped_candidate_files,
        "omitted_dates": omitted_dates,
        "scope_warning": "分母全期间使用 sh880008.day.amount；分子于 2022-08-02 起纳入北交所候选股。sh880008 的历史成分与纳入规则未作为本包的官方逐日成分清单使用。该包不设 coverage_ratio 门槛，也不插值。",
    }


def _strict_iso_date(value: object, label: str) -> str:
    if not isinstance(value, str) or DATE_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{label} 不是 YYYY-MM-DD")
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"{label} 不是有效日期") from exc
    return value


def _is_finite_nonnegative(value: object) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and float(value) >= 0


def verify_ai_chain_series(
    payload: dict[str, object], manifest: dict[str, object], records: list[dict[str, object]]
) -> None:
    payload_series = payload.get("ai_chain_series")
    manifest_series = manifest.get("ai_chain_series")
    if payload_series is None and manifest_series is None:
        return
    if not isinstance(payload_series, dict) or not isinstance(manifest_series, dict):
        raise ValueError("AI 产业链子序列 payload 与 manifest 必须同时存在")
    expected_start_date = compact_date_to_iso(AI_CHAIN_START_DATE)
    if (
        payload_series.get("name") != "AI产业链成交额占比"
        or payload_series.get("field") != "ai_chain_amount_pct"
        or payload_series.get("start_date") != expected_start_date
        or not isinstance(payload_series.get("definition"), str)
        or not payload_series["definition"].strip()
        or not isinstance(payload_series.get("active_stock_rule"), str)
        or not payload_series["active_stock_rule"].strip()
    ):
        raise ValueError("payload AI 产业链子序列说明不一致")
    payload_universe = payload_series.get("universe")
    if (
        not isinstance(payload_universe, dict)
        or payload_universe.get("workbook") != str(AI_CHAIN_WORKBOOK_RELATIVE_PATH).replace("\\", "/")
        or payload_universe.get("sheet") != AI_CHAIN_SHEET_NAME
        or payload_universe.get("code_column") != AI_CHAIN_CODE_HEADER
        or not isinstance(payload_universe.get("code_count"), int)
        or payload_universe["code_count"] <= 0
        or not isinstance(payload_universe.get("codes_sha256"), str)
        or re.fullmatch(r"[a-f0-9]{64}", payload_universe["codes_sha256"]) is None
    ):
        raise ValueError("payload AI 产业链股票池说明不一致")
    payload_has_member_fingerprint = "member_codes_sha256" in payload_universe
    if payload_has_member_fingerprint and (
        not isinstance(payload_universe.get("member_codes_sha256"), str)
        or re.fullmatch(r"[a-f0-9]{64}", payload_universe["member_codes_sha256"]) is None
    ):
        raise ValueError("payload AI 产业链成员集合指纹无效")

    series_records = payload_series.get("records")
    if not isinstance(series_records, list):
        raise ValueError("payload AI 产业链 records 必须是数组")
    expected_dates = [record["date"] for record in records if record["date"] >= expected_start_date]
    if len(series_records) != len(expected_dates):
        raise ValueError("AI 产业链子序列记录数与 C5 日历不一致")
    c5_by_date = {record["date"]: record for record in records}
    for index, (series_record, expected_date) in enumerate(zip(series_records, expected_dates, strict=True)):
        if not isinstance(series_record, dict):
            raise ValueError(f"ai_chain_series.records[{index}] 不是对象")
        date = _strict_iso_date(series_record.get("date"), f"ai_chain_series.records[{index}].date")
        if date != expected_date:
            raise ValueError("AI 产业链子序列日期必须与 C5 交易日历一致")
        amount_pct = series_record.get("ai_chain_amount_pct")
        amount_yi = series_record.get("ai_chain_amount_yi")
        active_count = series_record.get("ai_chain_active_stock_count")
        if not isinstance(active_count, int) or active_count < 0:
            raise ValueError("AI 产业链活跃成分数必须是非负整数")
        if amount_pct is None or amount_yi is None:
            if amount_pct is not None or amount_yi is not None or active_count != 0:
                raise ValueError("AI 产业链空值记录必须同时为空且活跃成分数为 0")
            continue
        if not _is_finite_nonnegative(amount_pct) or not _is_finite_nonnegative(amount_yi):
            raise ValueError("AI 产业链成交额或占比必须是非负有限数")
        if active_count <= 0:
            raise ValueError("AI 产业链有成交额记录时活跃成分数必须为正")
        c5_record = c5_by_date[date]
        recomputed = 100 * float(amount_yi) / float(c5_record["market_amount_yi"])
        if abs(recomputed - float(amount_pct)) > 0.0002:
            raise ValueError("AI 产业链成交额占比与统一分母不一致")

    expected_data_range = {
        "start": expected_dates[0] if expected_dates else None,
        "end": expected_dates[-1] if expected_dates else None,
    }
    if (
        manifest_series.get("name") != "AI产业链成交额占比"
        or manifest_series.get("field") != "ai_chain_amount_pct"
        or manifest_series.get("start_date") != expected_start_date
        or manifest_series.get("data_range") != expected_data_range
        or manifest_series.get("records") != len(series_records)
        or manifest_series.get("missing_output_records")
        != sum(record.get("ai_chain_amount_pct") is None for record in series_records)
        or not isinstance(manifest_series.get("formula"), str)
        or not manifest_series["formula"].strip()
        or not isinstance(manifest_series.get("active_stock_rule"), str)
        or not manifest_series["active_stock_rule"].strip()
    ):
        raise ValueError("manifest AI 产业链子序列说明不一致")
    manifest_universe = manifest_series.get("universe")
    if (
        not isinstance(manifest_universe, dict)
        or not isinstance(manifest_universe.get("workbook_path"), str)
        or not isinstance(manifest_universe.get("workbook_sha256"), str)
        or re.fullmatch(r"[a-f0-9]{64}", manifest_universe["workbook_sha256"]) is None
        or manifest_universe.get("sheet") != AI_CHAIN_SHEET_NAME
        or manifest_universe.get("code_column") != AI_CHAIN_CODE_HEADER
        or not isinstance(manifest_universe.get("input_code_count"), int)
        or not isinstance(manifest_universe.get("resolved_code_count"), int)
        or manifest_universe["input_code_count"] <= 0
        or manifest_universe["resolved_code_count"] <= 0
        or manifest_universe["input_code_count"] != payload_universe["code_count"]
        or manifest_universe["resolved_code_count"] != payload_universe["code_count"]
        or manifest_universe.get("resolved_code_sha256") != payload_universe["codes_sha256"]
        or not isinstance(manifest_universe.get("non_stock_code_rows_excluded"), int)
        or manifest_universe["non_stock_code_rows_excluded"] < 0
        or not isinstance(manifest_universe.get("tdx_candidate_file_count"), int)
        or manifest_universe["tdx_candidate_file_count"] != payload_universe["code_count"]
        or not isinstance(manifest_universe.get("code_aliases"), list)
    ):
        raise ValueError("manifest AI 产业链股票池说明不一致")
    manifest_has_member_fingerprint = "member_codes_sha256" in manifest_universe
    if manifest_has_member_fingerprint and (
        not isinstance(manifest_universe.get("member_codes_sha256"), str)
        or re.fullmatch(r"[a-f0-9]{64}", manifest_universe["member_codes_sha256"]) is None
    ):
        raise ValueError("manifest AI 产业链成员集合指纹无效")
    if payload_has_member_fingerprint != manifest_has_member_fingerprint or (
        payload_has_member_fingerprint
        and payload_universe["member_codes_sha256"] != manifest_universe["member_codes_sha256"]
    ):
        raise ValueError("AI 产业链成员集合指纹不一致")


def verify_artifact_bundle(payload_path: Path, manifest_path: Path, csv_path: Path) -> dict[str, object]:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(manifest, dict):
        raise ValueError("发布包 JSON 根节点必须为对象")
    if payload.get("schema_version") != "1" or manifest.get("schema_version") != "1":
        raise ValueError("发布包 schema_version 不受支持")
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("payload provenance 必须为对象")
    comparison_index = provenance.get("comparison_index")
    if not isinstance(comparison_index, dict):
        raise ValueError("payload 缺少创业板指说明")
    if (
        comparison_index.get("code") != "399006"
        or comparison_index.get("field") != "chinext_close"
        or comparison_index.get("value") != "收盘价"
    ):
        raise ValueError("payload 创业板指字段说明不一致")
    if manifest.get("payload_sha256") != sha256_file(payload_path):
        raise ValueError("payload SHA-256 自检失败")
    if manifest.get("csv_sha256") != sha256_file(csv_path):
        raise ValueError("CSV SHA-256 自检失败")
    records = payload.get("records")
    if not isinstance(records, list) or manifest.get("payload_records") != len(records):
        raise ValueError("payload_records 自检失败")
    previous_date: str | None = None
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"records[{index}] 不是对象")
        date = _strict_iso_date(record.get("date"), f"records[{index}].date")
        if previous_date is not None and date <= previous_date:
            raise ValueError("records 日期必须严格递增")
        previous_date = date
        active_count = record.get("active_stock_count")
        top_count = record.get("top5_stock_count")
        if not isinstance(active_count, int) or active_count <= 0:
            raise ValueError("active_stock_count 必须是正整数")
        if top_count != (active_count + 19) // 20:
            raise ValueError("top5_stock_count 必须为 ceil(5% × active_stock_count)")
        values = (record.get("c5_pct"), record.get("top5_amount_yi"), record.get("market_amount_yi"))
        if not all(isinstance(value, (int, float)) and math.isfinite(value) and value >= 0 for value in values):
            raise ValueError("C5 和成交额字段必须是非负有限数")
        if float(record["market_amount_yi"]) <= 0:
            raise ValueError("market_amount_yi 必须为正")
        if "chinext_close" not in record:
            raise ValueError("chinext_close 字段缺失")
        chinext_close = record["chinext_close"]
        if chinext_close is not None and (
            not isinstance(chinext_close, (int, float))
            or not math.isfinite(chinext_close)
            or float(chinext_close) <= 0
        ):
            raise ValueError("chinext_close 必须为 null 或正有限数")
        recomputed = 100 * float(record["top5_amount_yi"]) / float(record["market_amount_yi"])
        if abs(recomputed - float(record["c5_pct"])) > 0.0002:
            raise ValueError("C5 与成交额字段不一致")
        if record.get("denominator_source") != "sh880008":
            raise ValueError("分母来源不一致")
        expected_scope = "sh_sz_active_a" if date < "2022-08-02" else "sh_sz_bj_active_a"
        if record.get("numerator_scope") != expected_scope:
            raise ValueError("分子分段不一致")
    expected_range = {
        "start": records[0]["date"] if records else None,
        "end": records[-1]["date"] if records else None,
    }
    if manifest.get("data_range") != expected_range:
        raise ValueError("manifest data_range 不一致")
    if manifest.get("raw_data_copied") is not False:
        raise ValueError("manifest 必须明确 raw_data_copied=false")
    comparison_index = manifest.get("comparison_index_input")
    if not isinstance(comparison_index, dict):
        raise ValueError("manifest 缺少创业板指输入说明")
    if comparison_index.get("code") != "399006" or comparison_index.get("field") != "chinext_close":
        raise ValueError("manifest 创业板指字段说明不一致")
    if comparison_index.get("source") != "通达信本地盘后 .day 日线":
        raise ValueError("manifest 创业板指来源说明不一致")
    missing_chinext = sum(record.get("chinext_close") is None for record in records)
    if comparison_index.get("missing_output_records") != missing_chinext:
        raise ValueError("manifest 创业板指缺口统计不一致")
    verify_ai_chain_series(payload, manifest, records)
    return manifest


def write_bundle(
    output_directory: Path,
    payload: dict[str, object],
    manifest: dict[str, object],
    records: list[dict[str, object]],
) -> tuple[Path, Path, Path]:
    payload_path = output_directory / PAYLOAD_FILENAME
    manifest_path = output_directory / MANIFEST_FILENAME
    csv_path = output_directory / CSV_FILENAME
    atomic_write_bytes(json_bytes(payload), payload_path)
    atomic_write_bytes(records_to_csv_bytes(records), csv_path)
    completed_manifest = dict(manifest)
    completed_manifest["payload_sha256"] = sha256_file(payload_path)
    completed_manifest["csv_sha256"] = sha256_file(csv_path)
    atomic_write_bytes(json_bytes(completed_manifest), manifest_path)
    verify_artifact_bundle(payload_path, manifest_path, csv_path)
    return payload_path, manifest_path, csv_path


def read_published_snapshot(payload_target: Path, manifest_target: Path) -> tuple[bytes, bytes] | None:
    payload_exists = payload_target.exists()
    manifest_exists = manifest_target.exists()
    if payload_exists != manifest_exists:
        raise ValueError("发布目录已有不完整 JSON 对，拒绝覆盖")
    if not payload_exists:
        return None
    return payload_target.read_bytes(), manifest_target.read_bytes()


def restore_published_snapshot(
    snapshot: tuple[bytes, bytes] | None, payload_target: Path, manifest_target: Path
) -> None:
    if snapshot is None:
        for target in (payload_target, manifest_target):
            if target.exists():
                target.unlink()
        return
    atomic_write_bytes(snapshot[0], payload_target)
    atomic_write_bytes(snapshot[1], manifest_target)


def publish_bundle_atomically(payload_path: Path, manifest_path: Path, publish_directory: Path) -> None:
    if publish_directory.resolve() != PUBLISH_DIRECTORY.resolve():
        raise ValueError(f"publish-dir 必须是已授权静态数据目录: {PUBLISH_DIRECTORY}")
    artifact_csv = payload_path.parent / CSV_FILENAME
    verify_artifact_bundle(payload_path, manifest_path, artifact_csv)
    payload_target = publish_directory / payload_path.name
    manifest_target = publish_directory / manifest_path.name
    snapshot = read_published_snapshot(payload_target, manifest_target)
    try:
        # manifest 是提交标记：旧 manifest 会拒绝读取新 payload，直到新 manifest 到位。
        atomic_write_bytes(payload_path.read_bytes(), payload_target)
        atomic_write_bytes(manifest_path.read_bytes(), manifest_target)
        if sha256_file(payload_target) != sha256_file(payload_path):
            raise ValueError("发布后 payload SHA-256 不一致")
        if sha256_file(manifest_target) != sha256_file(manifest_path):
            raise ValueError("发布后 manifest SHA-256 不一致")
    except Exception:
        restore_published_snapshot(snapshot, payload_target, manifest_target)
        raise


def resolve_project_root(value: str | None) -> Path:
    root = Path(value).resolve() if value else Path(__file__).resolve().parents[1]
    if not (root / "AGENTS.md").is_file():
        raise FileNotFoundError(f"无法确认产业链投研项目根目录: {root}")
    return root


def main() -> None:
    parser = argparse.ArgumentParser(description="构建通达信全A等权 AMOUNT 口径 C5 交易集中度发布包")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--tdx-root", default=r"D:\HT")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--publish-dir", default=None)
    parser.add_argument("--start-date", default=str(START_DATE), help="YYYYMMDD，默认 20130101")
    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root)
    tdx_root = Path(args.tdx_root).resolve()
    start_date = parse_compact_date(args.start_date)
    output_directory = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else (project_root / DEFAULT_OUTPUT_DIRECTORY).resolve()
    )

    candidates = discover_candidate_files(tdx_root)
    ai_chain_universe = load_ai_chain_universe(project_root)
    ai_chain_candidates = ai_chain_candidate_snapshots(ai_chain_universe, candidates)
    ai_chain_indexes = candidate_column_indexes(candidates, ai_chain_candidates)
    denominator_files = denominator_snapshots(tdx_root)
    comparison_index_file = comparison_index_snapshot(tdx_root)
    denominator_data = {
        name: amount_by_date(read_day_array(snapshot.path, label=name), label=name)
        for name, snapshot in denominator_files.items()
    }
    chinext_close_by_date = close_by_date(
        read_day_array(comparison_index_file.path, label="sz399006"), label="sz399006"
    )
    denominator_rows, denominator_omitted = build_denominator_rows(denominator_data, start_date)
    calendar_dates = np.asarray([row.date for row in denominator_rows], dtype=np.uint32)
    amount_matrix, skipped_candidate_files = scan_active_amount_matrix(candidates, calendar_dates)
    records, numerator_omitted = build_records(
        denominator_rows, amount_matrix, chinext_close_by_date
    )
    ai_chain_series_records = build_ai_chain_series_records(
        denominator_rows,
        amount_matrix[:, ai_chain_indexes],
        c5_output_dates={int(record["date"].replace("-", "")) for record in records},
    )
    ai_chain_series = build_ai_chain_series(ai_chain_series_records, ai_chain_universe)
    del amount_matrix

    # 拒绝用 TDX 刷新中的混合快照生成产物；不复制任何原始文件。
    assert_ai_chain_universe_unchanged(ai_chain_universe)
    assert_snapshots_unchanged(
        [*candidates, *denominator_files.values(), comparison_index_file]
    )
    generated_at = beijing_now()
    payload = build_payload(records, generated_at, ai_chain_series)
    manifest = build_manifest(
        records=records,
        generated_at=generated_at,
        tdx_root=tdx_root,
        candidates=candidates,
        denominator_files=denominator_files,
        comparison_index_file=comparison_index_file,
        comparison_index_close_by_date=chinext_close_by_date,
        ai_chain_series_records=ai_chain_series_records,
        ai_chain_universe=ai_chain_universe,
        ai_chain_candidates=ai_chain_candidates,
        skipped_candidate_files=skipped_candidate_files,
        omitted_dates=[*denominator_omitted, *numerator_omitted],
    )
    payload_path, manifest_path, csv_path = write_bundle(output_directory, payload, manifest, records)
    if args.publish_dir:
        publish_bundle_atomically(payload_path, manifest_path, Path(args.publish_dir).resolve())
    verified_manifest = verify_artifact_bundle(payload_path, manifest_path, csv_path)
    print(
        json.dumps(
            {
                "payload": str(payload_path),
                "manifest": str(manifest_path),
                "csv": str(csv_path),
                "records": verified_manifest["payload_records"],
                "data_range": verified_manifest["data_range"],
                "published": bool(args.publish_dir),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

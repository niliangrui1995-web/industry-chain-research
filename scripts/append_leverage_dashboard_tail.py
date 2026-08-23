from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
import hashlib
import json
import os
from pathlib import Path
import struct
from typing import Any
from zoneinfo import ZoneInfo


PROJECT_ROOT_DEFAULT = Path(r"D:\vcp_hunter\产业链投研")
PUBLISH_DIRECTORY_DEFAULT = Path(r"D:\vcp_hunter\基金持仓\public\data")
DFCF_DIRECTORY = Path("artifacts/leverage_capitulation/dfcf_daily")
POST2017_DIRECTORY = Path(
    "artifacts/leverage_capitulation/eastmoney_post2017_market_cap_vendor"
)
DASHBOARD_DIRECTORY = Path("artifacts/leverage_capitulation/dashboard_bundle")
PAYLOAD_FILENAME = "leverage-dashboard.json"
MANIFEST_FILENAME = "leverage-dashboard.manifest.json"
DAY_STRUCT = struct.Struct("<IIIIIfII")
RATIO_QUANTUM = Decimal("0.00000001")
INDEX_PATHS = {
    "000001": Path(r"D:\HT\vipdoc\sh\lday\sh000001.day"),
    "399106": Path(r"D:\HT\vipdoc\sz\lday\sz399106.day"),
    "399006": Path(r"D:\HT\vipdoc\sz\lday\sz399006.day"),
}


class TailAppendBlocked(RuntimeError):
    """本轮新增记录无法安全追加到既有网页包。"""


def _parse_date(value: object, label: str) -> date:
    if not isinstance(value, str):
        raise TailAppendBlocked(f"{label} 缺少 YYYY-MM-DD 日期")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise TailAppendBlocked(f"{label} 不是 YYYY-MM-DD 日期") from exc


def _positive_decimal(value: object, label: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise TailAppendBlocked(f"{label} 不是数值") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise TailAppendBlocked(f"{label} 必须为正数")
    return parsed


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TailAppendBlocked(f"{label} 无法读取: {path}") from exc
    if not isinstance(decoded, dict):
        raise TailAppendBlocked(f"{label} 必须是 JSON 对象")
    return decoded


def _tail_date_from_payload(payload: dict[str, Any]) -> date:
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise TailAppendBlocked("既有网页包没有可复用记录")
    last = records[-1]
    if not isinstance(last, dict):
        raise TailAppendBlocked("既有网页包最后记录无效")
    return _parse_date(last.get("date"), "既有网页包最后记录")


def _read_new_dfcf_rows(path: Path, after: date, cutoff: date) -> dict[date, dict[str, Decimal]]:
    values: dict[date, dict[str, Decimal]] = {}
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                raw_date = row.get("date")
                try:
                    current = date.fromisoformat(raw_date or "")
                except ValueError:
                    continue
                if not after < current <= cutoff:
                    continue
                if current in values:
                    raise TailAppendBlocked(f"新增 DFCF 日期重复: {current.isoformat()}")
                values[current] = {
                    "sh_margin_y": _positive_decimal(
                        row.get("sh_margin_y"), f"DFCF {current} 沪市融资余额"
                    ),
                    "sz_margin_y": _positive_decimal(
                        row.get("sz_margin_y"), f"DFCF {current} 深市融资余额"
                    ),
                    "total_margin_y": _positive_decimal(
                        row.get("total_margin_y"), f"DFCF {current} 两市融资余额"
                    ),
                }
                if (
                    values[current]["sh_margin_y"] + values[current]["sz_margin_y"]
                    != values[current]["total_margin_y"]
                ):
                    raise TailAppendBlocked(
                        f"新增 DFCF 两市合计不一致: {current.isoformat()}"
                    )
    except OSError as exc:
        raise TailAppendBlocked(f"DFCF 合并表无法读取: {path}") from exc
    return values


def _read_new_market_caps(path: Path, after: date, cutoff: date) -> dict[date, Decimal]:
    values: dict[date, Decimal] = {}
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                raw_date = row.get("date")
                try:
                    current = date.fromisoformat(raw_date or "")
                except ValueError:
                    continue
                if not after < current <= cutoff:
                    continue
                if current in values:
                    raise TailAppendBlocked(f"新增市值日期重复: {current.isoformat()}")
                values[current] = _positive_decimal(
                    row.get("market_cap_yi"), f"市值 {current}"
                )
    except OSError as exc:
        raise TailAppendBlocked(f"后2017市值表无法读取: {path}") from exc
    return values


def _read_new_index_values(path: Path, after: date, cutoff: date) -> dict[date, Decimal]:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise TailAppendBlocked(f"TDX 指数无法读取: {path}") from exc
    if not payload or len(payload) % DAY_STRUCT.size:
        raise TailAppendBlocked(f"TDX 指数格式无效: {path}")
    values: dict[date, Decimal] = {}
    for offset in range(0, len(payload), DAY_STRUCT.size):
        raw_day, _, _, _, raw_close, _, _, _ = DAY_STRUCT.unpack_from(payload, offset)
        try:
            current = datetime.strptime(str(raw_day), "%Y%m%d").date()
        except ValueError:
            continue
        if not after < current <= cutoff:
            continue
        if current in values:
            raise TailAppendBlocked(f"新增指数日期重复: {current.isoformat()}")
        values[current] = _positive_decimal(
            Decimal(raw_close) / Decimal("100"), f"TDX 指数 {current} 收盘价"
        )
    return values


def _ratio(numerator: Decimal, denominator: Decimal) -> float:
    with localcontext() as context:
        context.prec = 50
        value = (numerator / denominator * Decimal("100")).quantize(
            RATIO_QUANTUM, rounding=ROUND_HALF_UP
        )
    return float(value)


def _build_tail_records(
    margin_rows: dict[date, dict[str, Decimal]],
    market_caps: dict[date, Decimal],
    index_values: dict[str, dict[date, Decimal]],
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for current in sorted(margin_rows):
        if current not in market_caps:
            raise TailAppendBlocked(f"新增日期缺少同日市值: {current.isoformat()}")
        missing_indices = [
            code for code, values in index_values.items() if current not in values
        ]
        if missing_indices:
            raise TailAppendBlocked(
                f"新增日期缺少指数收盘价: {current.isoformat()} ({', '.join(missing_indices)})"
            )
        margin = margin_rows[current]
        market_cap = market_caps[current]
        records.append(
            {
                "date": current.isoformat(),
                "denominator_market_cap_yi": float(market_cap),
                "index_000001_close": float(index_values["000001"][current]),
                "index_399006_close": float(index_values["399006"][current]),
                "index_399106_close": float(index_values["399106"][current]),
                "market_cap_review_status": "eastmoney_vendor_unverified",
                "market_cap_source": "eastmoney_post2017_vendor_unverified",
                "ratio_pct": _ratio(margin["total_margin_y"], market_cap),
                "sh_margin_yi": float(margin["sh_margin_y"]),
                "sz_margin_yi": float(margin["sz_margin_y"]),
                "total_margin_yi": float(margin["total_margin_y"]),
            }
        )
    return records


def _beijing_now() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")


def _json_bytes(payload: object) -> bytes:
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


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _atomic_write_bytes(payload: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _snapshot(paths: list[Path]) -> dict[Path, bytes | None]:
    return {path: path.read_bytes() if path.exists() else None for path in paths}


def _restore_snapshot(snapshot: dict[Path, bytes | None]) -> None:
    for path, previous in snapshot.items():
        if previous is None:
            if path.exists():
                path.unlink()
        else:
            _atomic_write_bytes(previous, path)


def _publish_tail_atomically(
    *,
    payload_bytes: bytes,
    manifest_bytes: bytes,
    artifact_payload: Path,
    artifact_manifest: Path,
    publish_payload: Path,
    publish_manifest: Path,
) -> None:
    targets = [artifact_payload, artifact_manifest, publish_payload, publish_manifest]
    snapshot = _snapshot(targets)
    try:
        _atomic_write_bytes(payload_bytes, artifact_payload)
        _atomic_write_bytes(manifest_bytes, artifact_manifest)
        _atomic_write_bytes(payload_bytes, publish_payload)
        _atomic_write_bytes(manifest_bytes, publish_manifest)
    except Exception:
        _restore_snapshot(snapshot)
        raise


def _update_metadata(
    payload: dict[str, Any], manifest: dict[str, Any], records: list[dict[str, object]]
) -> None:
    last_date = str(records[-1]["date"])
    payload["generated_at_beijing"] = _beijing_now()
    provenance = payload.get("provenance")
    if isinstance(provenance, dict):
        ratio_range = provenance.get("ratio_data_range")
        if isinstance(ratio_range, dict) and provenance.get("ratio_available") is True:
            ratio_range["end"] = last_date

    data_range = manifest.get("data_range")
    if isinstance(data_range, dict):
        data_range["end"] = last_date
    manifest["payload_records"] = len(records)
    market_cap = manifest.get("market_cap")
    if isinstance(market_cap, dict):
        ratio_range = market_cap.get("ratio_data_range")
        if isinstance(ratio_range, dict) and market_cap.get("ratio_available") is True:
            ratio_range["end"] = last_date
        segments = market_cap.get("source_segments")
        if isinstance(segments, list):
            for segment in reversed(segments):
                if isinstance(segment, dict) and segment.get("start") == "2017-01-03":
                    segment["end"] = last_date
                    break


def append_tail(
    project_root: Path,
    publish_dir: Path,
    *,
    cutoff: date | None = None,
) -> dict[str, object]:
    output_directory = project_root / DASHBOARD_DIRECTORY
    payload_path = output_directory / PAYLOAD_FILENAME
    manifest_path = output_directory / MANIFEST_FILENAME
    published_payload_path = publish_dir / PAYLOAD_FILENAME
    published_manifest_path = publish_dir / MANIFEST_FILENAME
    payload = _read_json(published_payload_path, "既有发布网页包")
    manifest = _read_json(published_manifest_path, "既有发布网页清单")
    base_payload_sha256 = manifest.get("payload_sha256")
    baseline_date = _tail_date_from_payload(payload)
    end_date = cutoff or date.today()

    margin_rows = _read_new_dfcf_rows(
        project_root / DFCF_DIRECTORY / "dfcf_margin_balances.csv",
        baseline_date,
        end_date,
    )
    if not margin_rows:
        return {
            "status": "no_changes",
            "historical_data_policy": "reuse_without_full_validation",
            "appended_dates": [],
        }
    market_caps = _read_new_market_caps(
        project_root / POST2017_DIRECTORY / "eastmoney_post2017_market_cap_vendor.csv",
        baseline_date,
        end_date,
    )
    index_values = {
        code: _read_new_index_values(path, baseline_date, end_date)
        for code, path in INDEX_PATHS.items()
    }
    tail_records = _build_tail_records(margin_rows, market_caps, index_values)

    existing_records = payload.get("records")
    if not isinstance(existing_records, list):
        raise TailAppendBlocked("既有网页包 records 无效")
    existing_records.extend(tail_records)
    _update_metadata(payload, manifest, existing_records)
    payload_bytes = _json_bytes(payload)
    manifest["payload_sha256"] = _sha256(payload_bytes)
    manifest["incremental_tail"] = {
        "base_payload_sha256": base_payload_sha256,
        "base_last_date": baseline_date.isoformat(),
        "appended_dates": [record["date"] for record in tail_records],
    }
    manifest_bytes = _json_bytes(manifest)

    _publish_tail_atomically(
        payload_bytes=payload_bytes,
        manifest_bytes=manifest_bytes,
        artifact_payload=payload_path,
        artifact_manifest=manifest_path,
        publish_payload=published_payload_path,
        publish_manifest=published_manifest_path,
    )
    return {
        "status": "updated",
        "historical_data_policy": "reuse_without_full_validation",
        "appended_dates": [record["date"] for record in tail_records],
        "payload_sha256": manifest["payload_sha256"],
    }


def _resolve_root(value: str | None, default: Path, marker: str) -> Path:
    root = Path(value).expanduser().resolve() if value else default
    if not (root / marker).exists():
        raise TailAppendBlocked(f"无法确认目录: {root}")
    return root


def _resolve_directory(value: str | None, default: Path) -> Path:
    directory = Path(value).expanduser().resolve() if value else default
    if not directory.is_dir():
        raise TailAppendBlocked(f"无法确认发布目录: {directory}")
    return directory


def main() -> None:
    parser = argparse.ArgumentParser(description="将两融新增尾部直接追加到既有网页包")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--publish-dir", default=None)
    parser.add_argument("--end-date", default=None)
    args = parser.parse_args()
    try:
        project_root = _resolve_root(args.project_root, PROJECT_ROOT_DEFAULT, "AGENTS.md")
        publish_dir = _resolve_directory(args.publish_dir, PUBLISH_DIRECTORY_DEFAULT)
        cutoff = _parse_date(args.end_date, "--end-date") if args.end_date else None
        result = append_tail(project_root, publish_dir, cutoff=cutoff)
    except TailAppendBlocked as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(2) from exc
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

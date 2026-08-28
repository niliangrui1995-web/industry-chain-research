from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timedelta
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
INDEX_VALUE_FIELDS = {
    "000001": "index_000001_close",
    "399106": "index_399106_close",
    "399006": "index_399006_close",
}
INDEX_SOURCE = "本地 TDX 厂商日线（用于三指数收盘价；未做交易所或指数编制方原始链复核）"
INDEX_SNAPSHOT_HASH_RECORDED = "recorded"
INDEX_SNAPSHOT_HASH_TAIL_EVIDENCE_ABSENT = "tail_snapshot_evidence_absent"
MANIFEST_DESCRIPTION = (
    "DFCF 两融余额与三指数静态数据包；"
    "三指数收盘价来自本地 TDX 厂商日线，未做交易所或指数编制方原始链复核；"
    "两融余额下降仅为去杠杆压力代理，不证明强平、底部或反弹。"
)
HISTORICAL_TAIL_HASH_GAP = "本包新增尾部输入的完整文件哈希未留存（本地 TDX 厂商日线）。"


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


def _read_new_index_values(
    path: Path, after: date, cutoff: date
) -> tuple[dict[date, Decimal], dict[str, object]]:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise TailAppendBlocked(f"TDX 指数无法读取: {path}") from exc
    if not payload or len(payload) % DAY_STRUCT.size:
        raise TailAppendBlocked(f"TDX 指数格式无效: {path}")
    values: dict[date, Decimal] = {}
    source_dates: list[date] = []
    for offset in range(0, len(payload), DAY_STRUCT.size):
        raw_day, _, _, _, raw_close, _, _, _ = DAY_STRUCT.unpack_from(payload, offset)
        try:
            current = datetime.strptime(str(raw_day), "%Y%m%d").date()
        except ValueError:
            continue
        source_dates.append(current)
        if not after < current <= cutoff:
            continue
        if current in values:
            raise TailAppendBlocked(f"新增指数日期重复: {current.isoformat()}")
        values[current] = _positive_decimal(
            Decimal(raw_close) / Decimal("100"), f"TDX 指数 {current} 收盘价"
        )
    if not source_dates:
        raise TailAppendBlocked(f"TDX 指数没有有效交易日期: {path}")
    return values, {
        "source": INDEX_SOURCE,
        "path": str(path),
        "sha256": _sha256(payload),
        "sha256_covers_through": max(source_dates).isoformat(),
        "source_snapshot_hash_status": INDEX_SNAPSHOT_HASH_RECORDED,
        "first_date": min(source_dates).isoformat(),
        "last_date": max(source_dates).isoformat(),
    }


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


def _publish_manifest_atomically(
    *, manifest_bytes: bytes, artifact_manifest: Path, publish_manifest: Path
) -> None:
    targets = [artifact_manifest, publish_manifest]
    snapshot = _snapshot(targets)
    try:
        _atomic_write_bytes(manifest_bytes, artifact_manifest)
        _atomic_write_bytes(manifest_bytes, publish_manifest)
    except Exception:
        _restore_snapshot(snapshot)
        raise


def _update_metadata(
    payload: dict[str, Any],
    manifest: dict[str, Any],
    records: list[dict[str, object]],
    index_metadata: dict[str, dict[str, object]],
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
    manifest["indices"] = index_metadata
    manifest["description"] = MANIFEST_DESCRIPTION
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
    index_inputs = {
        code: _read_new_index_values(path, baseline_date, end_date)
        for code, path in INDEX_PATHS.items()
    }
    index_values = {
        code: values for code, (values, _) in index_inputs.items()
    }
    index_metadata = {
        code: metadata for code, (_, metadata) in index_inputs.items()
    }
    tail_records = _build_tail_records(margin_rows, market_caps, index_values)

    existing_records = payload.get("records")
    if not isinstance(existing_records, list):
        raise TailAppendBlocked("既有网页包 records 无效")
    existing_records.extend(tail_records)
    _update_metadata(payload, manifest, existing_records, index_metadata)
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


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _effective_index_tail(
    payload: dict[str, Any],
) -> dict[str, tuple[date, Decimal]]:
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise TailAppendBlocked("既有网页包没有可核对的指数记录")

    effective: dict[str, tuple[date, Decimal]] = {}
    for record_number, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise TailAppendBlocked(f"既有网页包第 {record_number} 条记录无效")
        current = _parse_date(record.get("date"), f"既有网页包第 {record_number} 条记录")
        for code, field in INDEX_VALUE_FIELDS.items():
            value = record.get(field)
            if value is None:
                continue
            close = _positive_decimal(
                value, f"既有网页包 {current.isoformat()} {code} 收盘价"
            )
            previous = effective.get(code)
            if previous is None or current > previous[0]:
                effective[code] = (current, close)

    missing = [code for code in INDEX_VALUE_FIELDS if code not in effective]
    if missing:
        raise TailAppendBlocked(f"既有网页包缺少有效指数收盘价: {', '.join(missing)}")
    return effective


def _assert_current_index_tail_matches(
    code: str, target_date: date, expected_close: Decimal
) -> None:
    values, _ = _read_new_index_values(
        INDEX_PATHS[code], target_date - timedelta(days=1), target_date
    )
    actual_close = values.get(target_date)
    if actual_close is None:
        raise TailAppendBlocked(
            f"本地 TDX 指数缺少既有网页包尾部日期: {code} {target_date.isoformat()}"
        )
    if actual_close != expected_close:
        raise TailAppendBlocked(
            f"本地 TDX 指数与既有网页包尾部收盘价不一致: {code} {target_date.isoformat()}"
        )


def reconcile_index_metadata(
    project_root: Path, publish_dir: Path
) -> dict[str, object]:
    """仅修复既有尾部的指数来源元数据，不刷新或改写 payload 记录。"""

    output_directory = project_root / DASHBOARD_DIRECTORY
    artifact_payload_path = output_directory / PAYLOAD_FILENAME
    artifact_manifest_path = output_directory / MANIFEST_FILENAME
    published_payload_path = publish_dir / PAYLOAD_FILENAME
    published_manifest_path = publish_dir / MANIFEST_FILENAME
    payload = _read_json(published_payload_path, "既有发布网页包")
    manifest = _read_json(published_manifest_path, "既有发布网页清单")
    try:
        payload_bytes = published_payload_path.read_bytes()
        artifact_payload_bytes = artifact_payload_path.read_bytes()
        published_manifest_bytes = published_manifest_path.read_bytes()
        artifact_manifest_bytes = artifact_manifest_path.read_bytes()
    except OSError as exc:
        raise TailAppendBlocked("既有网页包产物无法读取") from exc
    payload_sha256 = _sha256(payload_bytes)
    if manifest.get("payload_sha256") != payload_sha256:
        raise TailAppendBlocked("既有发布网页包 SHA-256 与清单不一致")
    if artifact_payload_bytes != payload_bytes:
        raise TailAppendBlocked("研究仓产物与既有发布网页包 payload 不一致")
    if artifact_manifest_bytes != published_manifest_bytes:
        raise TailAppendBlocked("研究仓产物与既有发布网页包 manifest 不一致")
    artifact_manifest = _read_json(artifact_manifest_path, "研究仓既有网页清单")
    if artifact_manifest.get("payload_sha256") != payload_sha256:
        raise TailAppendBlocked("研究仓既有网页清单与 payload SHA-256 不一致")

    effective = _effective_index_tail(payload)
    indices = manifest.get("indices")
    if not isinstance(indices, dict):
        raise TailAppendBlocked("既有发布网页清单指数元数据无效")

    stale_codes: list[str] = []
    prior_dates: dict[str, date] = {}
    for code, (effective_date, _) in effective.items():
        entry = indices.get(code)
        if not isinstance(entry, dict):
            raise TailAppendBlocked(f"既有发布网页清单缺少指数元数据: {code}")
        first_date = _parse_date(entry.get("first_date"), f"既有清单指数 {code} 首日")
        prior_date = _parse_date(entry.get("last_date"), f"既有清单指数 {code} 末日")
        if first_date > prior_date or first_date > effective_date:
            raise TailAppendBlocked(f"既有清单指数日期范围无效: {code}")
        if not _is_sha256(entry.get("sha256")):
            raise TailAppendBlocked(f"既有清单指数 SHA-256 无效: {code}")
        if not isinstance(entry.get("path"), str) or not entry["path"].strip():
            raise TailAppendBlocked(f"既有清单指数路径无效: {code}")
        prior_dates[code] = prior_date
        if prior_date < effective_date:
            stale_codes.append(code)

    reconciled_dates = {
        code: effective[code][0].isoformat() for code in INDEX_VALUE_FIELDS
    }
    if not stale_codes:
        return {
            "status": "no_changes",
            "historical_data_policy": "reuse_without_full_validation",
            "reconciled_index_last_dates": reconciled_dates,
        }
    if len(stale_codes) != len(INDEX_VALUE_FIELDS):
        raise TailAppendBlocked("指数来源日期仅部分落后，拒绝混合修复历史快照证据")

    for code in stale_codes:
        effective_date, effective_close = effective[code]
        _assert_current_index_tail_matches(code, effective_date, effective_close)
        entry = indices[code]
        assert isinstance(entry, dict)
        entry["source"] = INDEX_SOURCE
        entry["sha256_covers_through"] = prior_dates[code].isoformat()
        entry["source_snapshot_hash_status"] = (
            INDEX_SNAPSHOT_HASH_TAIL_EVIDENCE_ABSENT
        )
        entry["last_date"] = effective_date.isoformat()

    manifest["description"] = f"{MANIFEST_DESCRIPTION}{HISTORICAL_TAIL_HASH_GAP}"
    manifest_bytes = _json_bytes(manifest)
    _publish_manifest_atomically(
        manifest_bytes=manifest_bytes,
        artifact_manifest=artifact_manifest_path,
        publish_manifest=published_manifest_path,
    )
    return {
        "status": "metadata_repaired",
        "historical_data_policy": "reuse_without_full_validation",
        "reconciled_index_last_dates": reconciled_dates,
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
    parser = argparse.ArgumentParser(description="维护两融网页包的新增尾部或指数元数据")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--publish-dir", default=None)
    parser.add_argument("--end-date", default=None)
    parser.add_argument(
        "--reconcile-index-metadata",
        action="store_true",
        help="只修复既有网页包指数来源元数据，不刷新或改写 payload 记录",
    )
    args = parser.parse_args()
    try:
        project_root = _resolve_root(args.project_root, PROJECT_ROOT_DEFAULT, "AGENTS.md")
        publish_dir = _resolve_directory(args.publish_dir, PUBLISH_DIRECTORY_DEFAULT)
        if args.reconcile_index_metadata:
            if args.end_date:
                raise TailAppendBlocked("--reconcile-index-metadata 不接受 --end-date")
            result = reconcile_index_metadata(project_root, publish_dir)
        else:
            cutoff = _parse_date(args.end_date, "--end-date") if args.end_date else None
            result = append_tail(project_root, publish_dir, cutoff=cutoff)
    except TailAppendBlocked as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, ensure_ascii=False))
        raise SystemExit(2) from exc
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

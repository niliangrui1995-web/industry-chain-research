#!/usr/bin/env python3
"""Snapshot explicit public PIT sources without weakening their evidence boundary."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import shutil
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from uuid import uuid4


SOURCE_SCHEMA = "kronos-public-pit-sources-v1"
BAOSTOCK_SCHEMA = "kronos-baostock-trade-status-v1"
NORMALIZATION_SCHEMA_V1 = "kronos-a-share-pit-normalization-v1"
NORMALIZATION_SCHEMA_V2 = "kronos-a-share-pit-normalization-v2"
NORMALIZATION_SCHEMA = NORMALIZATION_SCHEMA_V1
PUBLICATION_SCHEMA_V1 = "kronos-a-share-pit-publication-v1"
PUBLICATION_SCHEMA_V2 = "kronos-a-share-pit-publication-v2"
PUBLICATION_SCHEMA = PUBLICATION_SCHEMA_V1
REVIEWED_OVERLAY_SCHEMA = "kronos-a-share-reviewed-overlay-v1"
ROW_AUDIT_SCHEMA = "kronos-a-share-row-audit-v1"
CSI_MEMBERSHIP_RECEIPT_SCHEMA = "kronos-a-share-csi-membership-receipt-v1"
CNINFO_PAGINATION_RECEIPT_SCHEMA = "kronos-a-share-cninfo-pagination-receipt-v1"
TRADING_CALENDAR_DATASET = "trading_calendar"
TRADING_CALENDAR_ARTIFACT_ROLE = "trading_calendar"
TRADING_CALENDAR_ARTIFACT_SCHEMA = "kronos-a-share-trading-calendar-v1"
INDEX_MEMBERSHIP_ARTIFACT_ROLE = "index_membership_anchor_and_adjustments"
INDEX_MEMBERSHIP_ARTIFACT_SCHEMA = "kronos-a-share-index-membership-evidence-v1"
CORPORATE_ACTIONS_ARTIFACT_ROLE = "cninfo_complete_pagination_receipt"
CORPORATE_ACTIONS_ARTIFACT_SCHEMA = "kronos-a-share-corporate-actions-evidence-v1"
BAOSTOCK_FIELDS = "date,code,tradestatus,isST"
SYMBOL_PATTERN = re.compile(r"^(?:sh|sz|bj)\.\d{6}$")
SOURCE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")
SOURCE_PRIORITY = (
    "official_primary",
    "public_secondary",
    "tdx_mechanical",
)
SOURCE_PRIORITY_VALUE = {
    source_class: len(SOURCE_PRIORITY) - index
    for index, source_class in enumerate(SOURCE_PRIORITY)
}
NORMALIZED_DATASETS = (
    "security_master",
    "st_status",
    "suspensions",
    "price_limits",
    "index_membership",
    "corporate_actions",
    TRADING_CALENDAR_DATASET,
)
DATASET_KEYS = {
    "security_master": ("ticker", "list_date"),
    "st_status": ("ticker", "effective_from"),
    "suspensions": ("ticker", "trade_date"),
    "price_limits": ("ticker", "trade_date"),
    "index_membership": ("index_code", "ticker", "effective_from"),
    "corporate_actions": ("ticker", "announcement_date", "ex_date"),
    TRADING_CALENDAR_DATASET: ("trade_date",),
}
EVIDENCE_ARTIFACT_SCHEMAS = {
    TRADING_CALENDAR_ARTIFACT_ROLE: TRADING_CALENDAR_ARTIFACT_SCHEMA,
    INDEX_MEMBERSHIP_ARTIFACT_ROLE: INDEX_MEMBERSHIP_ARTIFACT_SCHEMA,
    CORPORATE_ACTIONS_ARTIFACT_ROLE: CORPORATE_ACTIONS_ARTIFACT_SCHEMA,
}
SOURCE_BOUND_ARTIFACTS = {
    "index_membership": (
        INDEX_MEMBERSHIP_ARTIFACT_ROLE,
        INDEX_MEMBERSHIP_ARTIFACT_SCHEMA,
    ),
    "corporate_actions": (
        CORPORATE_ACTIONS_ARTIFACT_ROLE,
        CORPORATE_ACTIONS_ARTIFACT_SCHEMA,
    ),
    TRADING_CALENDAR_DATASET: (
        TRADING_CALENDAR_ARTIFACT_ROLE,
        TRADING_CALENDAR_ARTIFACT_SCHEMA,
    ),
}
V2_COVERAGE_KEY_CONTRACTS = {
    "security_master": "derived",
    "st_status": "derived",
    "suspensions": "derived",
    "price_limits": "derived",
    "index_membership": "source_bound",
    "corporate_actions": "source_bound",
    TRADING_CALENDAR_DATASET: "source_bound",
}
EXTRACTOR_BY_FORMAT = {
    "csv": ("csv-table-v1", "1"),
    "json": ("json-records-v1", "1"),
    "html": ("html-table-v1", "1"),
    "pdf": ("pdf-table-v1", "1"),
}
SUPPORTED_ENCODINGS = {"utf-8", "utf-8-sig", "gb18030"}
SOURCE_CLASS_DOMAIN_ALLOWLIST = {
    "official_primary": (
        "sse.com.cn",
        "szse.cn",
        "csindex.com.cn",
        "cninfo.com.cn",
        "bse.cn",
    ),
    "public_secondary": ("baostock.com",),
}
OFFICIAL_DATASET_DOMAIN_ALLOWLIST = {
    "security_master": ("sse.com.cn", "szse.cn", "bse.cn"),
    "st_status": ("sse.com.cn", "szse.cn", "bse.cn"),
    "suspensions": ("sse.com.cn", "szse.cn", "bse.cn"),
    "price_limits": ("sse.com.cn", "szse.cn", "bse.cn"),
    "index_membership": ("csindex.com.cn",),
    "corporate_actions": ("cninfo.com.cn",),
    TRADING_CALENDAR_DATASET: ("sse.com.cn", "szse.cn", "bse.cn"),
}


class PublicDataError(RuntimeError):
    """Raised when a public-source snapshot is incomplete or unsafe."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_within(path: Path, root: Path) -> Path:
    candidate = path.resolve()
    boundary = root.resolve()
    try:
        candidate.relative_to(boundary)
    except ValueError as exc:
        raise PublicDataError(f"path_outside_training_root: {candidate}") from exc
    return candidate


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(f".{path.name}.pending-{os.getpid()}")
    with pending.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, path)


def _parse_iso_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise PublicDataError(f"{field_name} 必须为 YYYY-MM-DD") from exc


def _https_host(url: str) -> str:
    try:
        parsed = urllib.parse.urlsplit(url)
        port = parsed.port
    except (TypeError, ValueError) as exc:
        raise PublicDataError("公开PIT URL 无效") from exc
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise PublicDataError("公开PIT下载只允许显式 HTTPS URL")
    if parsed.username is not None or parsed.password is not None:
        raise PublicDataError("公开PIT URL 不允许包含认证信息")
    if port not in (None, 443):
        raise PublicDataError("公开PIT HTTPS URL 只允许默认 443 端口")
    return parsed.hostname.lower().rstrip(".")


def _fixed_source_domains(
    source_class: str,
    *,
    dataset: str | None = None,
) -> tuple[str, ...]:
    fixed = SOURCE_CLASS_DOMAIN_ALLOWLIST.get(source_class)
    if fixed is None:
        raise PublicDataError("source_class 不属于代码固定来源等级")
    if source_class == "official_primary" and dataset is not None:
        fixed = OFFICIAL_DATASET_DOMAIN_ALLOWLIST.get(dataset)
        if fixed is None:
            raise PublicDataError(f"{dataset}: 缺少代码固定官方域名合同")
    return tuple(fixed)


def _validate_fixed_source_identity(
    url: str,
    *,
    source_class: str,
    dataset: str | None = None,
) -> str:
    host = _https_host(url)
    fixed = _fixed_source_domains(source_class, dataset=dataset)
    if not _host_is_allowed(host, fixed):
        scope = f"dataset={dataset}, " if dataset is not None else ""
        raise PublicDataError(
            f"来源域名不在代码固定白名单：{scope}source_class={source_class}, "
            f"host={host}, fixed={list(fixed)}"
        )
    return host


def _normalize_allowed_domains(item: dict[str, Any], request_host: str) -> tuple[str, ...]:
    source_class = str(item.get("source_class", ""))
    fixed = _fixed_source_domains(source_class)
    if not _host_is_allowed(request_host, fixed):
        raise PublicDataError(
            f"原始 URL 域名不在代码固定白名单：host={request_host}, fixed={list(fixed)}"
        )
    configured = item.get("allowed_domains")
    if configured is None:
        return (request_host,)
    if not isinstance(configured, list) or not configured:
        raise PublicDataError("allowed_domains 必须为非空字符串数组")
    normalized: list[str] = []
    for raw_domain in configured:
        if not isinstance(raw_domain, str) or not raw_domain.strip():
            raise PublicDataError("allowed_domains 必须为非空字符串数组")
        domain = raw_domain.strip().lower().rstrip(".")
        if any(character in domain for character in (":", "/", "@", "*")):
            raise PublicDataError(f"allowed_domains 包含无效域名：{raw_domain!r}")
        if _https_host(f"https://{domain}") != domain:
            raise PublicDataError(f"allowed_domains 包含无效域名：{raw_domain!r}")
        if not _host_is_allowed(domain, fixed):
            raise PublicDataError(
                f"allowed_domains 只能收窄代码固定白名单：domain={domain}, "
                f"fixed={list(fixed)}"
            )
        normalized.append(domain)
    return tuple(sorted(set(normalized)))


def _host_is_allowed(host: str, allowed_domains: tuple[str, ...]) -> bool:
    return any(host == domain or host.endswith(f".{domain}") for domain in allowed_domains)


def _validate_resolved_url(url: str, allowed_domains: tuple[str, ...]) -> str:
    host = _https_host(url)
    if not _host_is_allowed(host, allowed_domains):
        raise PublicDataError(
            f"重定向后的域名不在允许列表：host={host}, allowed={list(allowed_domains)}"
        )
    return host


def _validate_source(item: dict[str, Any]) -> tuple[str, ...]:
    allowed = {
        "source_id",
        "source_class",
        "url",
        "valid_from",
        "valid_to",
        "sha256",
        "allowed_domains",
        "artifact_role",
        "artifact_schema_version",
    }
    unknown = sorted(set(item) - allowed)
    if unknown:
        raise PublicDataError(f"公开源配置包含未知字段：{unknown}")
    for required in ("source_id", "source_class", "url"):
        if not item.get(required):
            raise PublicDataError(f"公开源缺少 {required}")
    if item["source_class"] not in {"official_primary", "public_secondary"}:
        raise PublicDataError("source_class 必须为 official_primary 或 public_secondary")
    if not SOURCE_ID_PATTERN.fullmatch(str(item["source_id"])):
        raise PublicDataError("source_id 只能包含字母、数字、点、下划线和连字符")
    request_host = _https_host(str(item["url"]))
    _validate_fixed_source_identity(
        str(item["url"]), source_class=str(item["source_class"])
    )
    allowed_domains = _normalize_allowed_domains(item, request_host)
    if not _host_is_allowed(request_host, allowed_domains):
        raise PublicDataError("原始 URL 域名不在 allowed_domains 中")
    expected_hash = item.get("sha256")
    if expected_hash is not None and not SHA256_PATTERN.fullmatch(str(expected_hash)):
        raise PublicDataError("公开源 sha256 必须为64位十六进制")
    _evidence_artifact_metadata(item, label=f"sources.{item['source_id']}")
    return allowed_domains


def _evidence_artifact_metadata(
    source: Mapping[str, Any],
    *,
    label: str,
    required_role: str | None = None,
) -> dict[str, str]:
    artifact_role = source.get("artifact_role")
    artifact_schema = source.get("artifact_schema_version")
    if artifact_role is None and artifact_schema is None and required_role is None:
        return {}
    role = required_role if required_role is not None else artifact_role
    expected_schema = EVIDENCE_ARTIFACT_SCHEMAS.get(str(role))
    if (
        expected_schema is None
        or artifact_role != role
        or artifact_schema != expected_schema
    ):
        raise PublicDataError(
            f"{label} 证据工件身份无效：artifact_role={artifact_role!r}, "
            f"artifact_schema_version={artifact_schema!r}"
        )
    if source.get("source_class") != "official_primary":
        raise PublicDataError(f"{label} 证据工件必须为 official_primary")
    return {
        "artifact_role": str(role),
        "artifact_schema_version": expected_schema,
    }


def _calendar_artifact_metadata(
    source: Mapping[str, Any],
    *,
    label: str,
    required: bool = False,
) -> dict[str, str]:
    if (
        source.get("artifact_role") is None
        and source.get("artifact_schema_version") is None
        and not required
    ):
        return {}
    try:
        return _evidence_artifact_metadata(
            source,
            label=label,
            required_role=TRADING_CALENDAR_ARTIFACT_ROLE,
        )
    except PublicDataError as exc:
        raise PublicDataError(
            f"{label} 日历工件必须固定为 artifact_role="
            f"{TRADING_CALENDAR_ARTIFACT_ROLE!r}, artifact_schema_version="
            f"{TRADING_CALENDAR_ARTIFACT_SCHEMA!r}，且为 official_primary"
        ) from exc


def _new_staging_directory(output: Path, training_root: Path) -> Path:
    output = ensure_within(output, training_root)
    root = training_root.resolve()
    if output == root:
        raise PublicDataError("公开数据输出目录不能等于 training_root")
    parent = ensure_within(output.parent, training_root)
    parent.mkdir(parents=True, exist_ok=True)
    staging = ensure_within(
        parent / f".{output.name}.pending-{os.getpid()}-{uuid4().hex}", training_root
    )
    staging.mkdir(exist_ok=False)
    return staging


def _promote_directory(staging: Path, output: Path, training_root: Path) -> None:
    """Publish a complete tree without ever merging it into the previous tree."""

    staging = ensure_within(staging, training_root)
    output = ensure_within(output, training_root)
    if not staging.is_dir():
        raise PublicDataError("公开数据 staging 目录不存在")
    if output.exists() and not output.is_dir():
        raise PublicDataError(f"公开数据输出路径不是目录：{output}")
    backup: Path | None = None
    if output.exists():
        backup = ensure_within(
            output.parent / f".{output.name}.backup-{os.getpid()}-{uuid4().hex}",
            training_root,
        )
        os.replace(output, backup)
    try:
        os.replace(staging, output)
    except Exception as promotion_error:
        if backup is not None and backup.exists() and not output.exists():
            try:
                os.replace(backup, output)
            except Exception as rollback_error:
                raise PublicDataError(
                    f"公开数据发布失败且回滚失败：publish={promotion_error}; "
                    f"rollback={rollback_error}"
                ) from rollback_error
        raise PublicDataError(f"公开数据目录原子发布失败：{promotion_error}") from promotion_error
    if backup is not None and backup.exists():
        shutil.rmtree(backup)


def _cleanup_staging(staging: Path | None) -> None:
    if staging is not None and staging.exists():
        shutil.rmtree(staging)


def snapshot_url_manifest(
    manifest_path: Path,
    output_directory: Path,
    training_root: Path,
    *,
    timeout: int = 60,
) -> dict[str, Any]:
    """Download exact URLs from a reviewed manifest and preserve their raw bytes."""

    output = ensure_within(output_directory, training_root)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != SOURCE_SCHEMA:
        raise PublicDataError(f"schema_version 必须为 {SOURCE_SCHEMA}")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise PublicDataError("公开源 manifest 必须包含非空 sources")
    validated_sources: list[tuple[dict[str, Any], tuple[str, ...]]] = []
    source_ids: set[str] = set()
    for item in sources:
        if not isinstance(item, dict):
            raise PublicDataError("sources 每项必须是对象")
        allowed_domains = _validate_source(item)
        source_id = str(item["source_id"])
        if source_id in source_ids:
            raise PublicDataError(f"source_id 重复：{source_id}")
        source_ids.add(source_id)
        validated_sources.append((item, allowed_domains))

    staging: Path | None = _new_staging_directory(output, training_root)
    records: list[dict[str, Any]] = []
    try:
        for item, allowed_domains in validated_sources:
            request = urllib.request.Request(
                item["url"],
                headers={"User-Agent": "KronosAsharePIT/1.0 (+local research snapshot)"},
            )
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    final_url = response.geturl()
                    _validate_resolved_url(final_url, allowed_domains)
                    content = response.read()
                    content_type = response.headers.get("Content-Type")
            except PublicDataError:
                raise
            except Exception as exc:
                raise PublicDataError(f"{item['source_id']} 下载失败：{exc}") from exc
            if not content:
                raise PublicDataError(f"{item['source_id']} 下载结果为空")
            actual_hash = hashlib.sha256(content).hexdigest()
            expected_hash = item.get("sha256")
            if expected_hash and actual_hash != str(expected_hash).lower():
                raise PublicDataError(
                    f"{item['source_id']} SHA256 不匹配：expected={expected_hash}, "
                    f"actual={actual_hash}"
                )
            suffix = Path(urllib.parse.urlsplit(str(item["url"])).path).suffix or ".bin"
            filename = f"{item['source_id']}{suffix}"
            staging_destination = ensure_within(staging / filename, training_root)
            final_destination = ensure_within(output / filename, training_root)
            atomic_write(staging_destination, content)
            records.append(
                {
                    **item,
                    "resolved_url": final_url,
                    "content_type": content_type,
                    "local_path": str(final_destination),
                    "bytes": len(content),
                    "sha256": actual_hash,
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        result = {
            "schema_version": SOURCE_SCHEMA,
            "status": "ok",
            "source_count": len(records),
            "sources": records,
        }
        atomic_write(
            ensure_within(staging / "snapshot_manifest.json", training_root),
            (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        _promote_directory(staging, output, training_root)
        staging = None
        return result
    finally:
        _cleanup_staging(staging)


def _inspect_baostock_shard(
    path: Path,
    *,
    symbol: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    lower = _parse_iso_date(start_date, "start_date")
    upper = _parse_iso_date(end_date, "end_date")
    row_count = 0
    first_date: date | None = None
    previous_date: date | None = None
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise PublicDataError(f"Baostock shard 为空：{path}") from exc
        expected_fields = BAOSTOCK_FIELDS.split(",")
        if header != expected_fields:
            raise PublicDataError(f"Baostock shard schema 不匹配：{path}")
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(expected_fields) or any(value == "" for value in row):
                raise PublicDataError(f"Baostock shard 第{line_number}行字段不完整：{path}")
            row_date = _parse_iso_date(row[0], f"{path.name}:{line_number}:date")
            if not lower <= row_date <= upper:
                raise PublicDataError(f"Baostock shard 日期越界：{path}:{line_number}")
            if previous_date is not None and row_date <= previous_date:
                raise PublicDataError(f"Baostock shard 日期未严格递增：{path}:{line_number}")
            if row[1] != symbol:
                raise PublicDataError(f"Baostock shard ticker 不匹配：{path}:{line_number}")
            if row[2] not in {"0", "1"} or row[3] not in {"0", "1"}:
                raise PublicDataError(f"Baostock shard 状态字段无效：{path}:{line_number}")
            if first_date is None:
                first_date = row_date
            previous_date = row_date
            row_count += 1
    if row_count == 0 or first_date is None or previous_date is None:
        raise PublicDataError(f"Baostock shard 没有有效记录：{path}")
    return {
        "row_count": row_count,
        "min_date": first_date.isoformat(),
        "max_date": previous_date.isoformat(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _load_reusable_baostock_shards(
    output: Path,
    *,
    start_date: str,
    end_date: str,
    training_root: Path,
) -> dict[str, dict[str, Any]]:
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        return {}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    shards = manifest.get("shards")
    manifest_symbols = manifest.get("symbols")
    if (
        not isinstance(shards, list)
        or not all(isinstance(item, dict) for item in shards)
        or not isinstance(manifest_symbols, list)
        or not all(isinstance(symbol, str) for symbol in manifest_symbols)
    ):
        return {}
    shard_symbols = [item.get("symbol") for item in shards]
    if (
        manifest.get("schema_version") != BAOSTOCK_SCHEMA
        or manifest.get("status") != "ok"
        or manifest.get("fields") != BAOSTOCK_FIELDS.split(",")
        or manifest.get("start_date") != start_date
        or manifest.get("end_date") != end_date
        or manifest.get("symbol_count") != len(shards)
        or manifest_symbols != sorted(manifest_symbols)
        or len(set(manifest_symbols)) != len(manifest_symbols)
        or shard_symbols != manifest_symbols
    ):
        return {}
    expected_symbol_hash = hashlib.sha256(
        ("\n".join(manifest_symbols) + "\n").encode("utf-8")
    ).hexdigest()
    if manifest.get("symbols_sha256") != expected_symbol_hash:
        return {}
    reusable: dict[str, dict[str, Any]] = {}
    for contract in shards:
        if not isinstance(contract, dict):
            return {}
        symbol = contract.get("symbol")
        if not isinstance(symbol, str) or symbol in reusable or not SYMBOL_PATTERN.fullmatch(symbol):
            return {}
        expected_path = ensure_within(output / f"{symbol}.csv", training_root)
        try:
            configured_path = ensure_within(Path(str(contract.get("path", ""))), training_root)
        except PublicDataError:
            continue
        if configured_path != expected_path or not expected_path.is_file():
            continue
        if (
            contract.get("query_start_date") != start_date
            or contract.get("query_end_date") != end_date
            or not SHA256_PATTERN.fullmatch(str(contract.get("sha256", "")))
        ):
            continue
        try:
            observed = _inspect_baostock_shard(
                expected_path,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
        except (OSError, UnicodeError, PublicDataError):
            continue
        if any(observed.get(key) != contract.get(key) for key in observed):
            continue
        reusable[symbol] = {**contract, **observed}
    return reusable


def _write_baostock_query_result(
    result: Any,
    destination: Path,
    *,
    symbol: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    try:
        returned_fields = list(result.fields)
    except (AttributeError, TypeError) as exc:
        raise PublicDataError(f"Baostock {symbol} 返回 schema 无效") from exc
    if returned_fields != BAOSTOCK_FIELDS.split(","):
        raise PublicDataError(f"Baostock {symbol} 返回 schema 不匹配")
    rows: list[list[str]] = []
    while result.next():
        rows.append(result.get_row_data())
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(returned_fields)
    writer.writerows(rows)
    atomic_write(destination, buffer.getvalue().encode("utf-8"))
    return _inspect_baostock_shard(
        destination,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )


def fetch_baostock_trade_status_shards(
    symbols: Iterable[str],
    start_date: str,
    end_date: str,
    output_directory: Path,
    training_root: Path,
) -> dict[str, Any]:
    """Fetch public secondary daily ST/trade status into resumable symbol shards."""

    output = ensure_within(output_directory, training_root)
    lower = _parse_iso_date(start_date, "start_date")
    upper = _parse_iso_date(end_date, "end_date")
    if lower > upper:
        raise PublicDataError("start_date 不得晚于 end_date")
    raw_symbols = list(symbols)
    invalid = [symbol for symbol in raw_symbols if not isinstance(symbol, str)]
    if invalid:
        raise PublicDataError("Baostock ticker 必须为字符串")
    normalized = sorted(set(raw_symbols))
    if not normalized:
        raise PublicDataError("Baostock ticker 列表不能为空")
    invalid = [symbol for symbol in normalized if not SYMBOL_PATTERN.fullmatch(symbol)]
    if invalid:
        raise PublicDataError(f"Baostock ticker 格式无效：{invalid[:10]}")
    reusable = _load_reusable_baostock_shards(
        output,
        start_date=start_date,
        end_date=end_date,
        training_root=training_root,
    )
    staging: Path | None = _new_staging_directory(output, training_root)
    records: list[dict[str, Any]] = []
    try:
        for symbol in normalized:
            if symbol in reusable:
                source_path = ensure_within(output / f"{symbol}.csv", training_root)
                staging_path = ensure_within(staging / f"{symbol}.csv", training_root)
                shutil.copyfile(source_path, staging_path)
                observed = _inspect_baostock_shard(
                    staging_path,
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                )
                if observed["sha256"] != reusable[symbol]["sha256"]:
                    raise PublicDataError(f"Baostock {symbol} 复用复制后 SHA256 漂移")
                records.append(
                    {
                        "symbol": symbol,
                        "path": str(ensure_within(output / f"{symbol}.csv", training_root)),
                        "query_start_date": start_date,
                        "query_end_date": end_date,
                        **observed,
                        "resumed": True,
                    }
                )
        missing = [symbol for symbol in normalized if symbol not in reusable]
        if missing:
            try:
                import baostock as bs
            except ImportError as exc:
                raise PublicDataError("缺少 baostock；请先安装训练锁定依赖") from exc
            login = bs.login()
            if login.error_code != "0":
                raise PublicDataError(f"Baostock 登录失败：{login.error_code} {login.error_msg}")
            try:
                for symbol in missing:
                    result = bs.query_history_k_data_plus(
                        symbol,
                        BAOSTOCK_FIELDS,
                        start_date=start_date,
                        end_date=end_date,
                        frequency="d",
                        adjustflag="3",
                    )
                    if result.error_code != "0":
                        raise PublicDataError(
                            f"Baostock {symbol} 查询失败：{result.error_code} {result.error_msg}"
                        )
                    staging_path = ensure_within(staging / f"{symbol}.csv", training_root)
                    observed = _write_baostock_query_result(
                        result,
                        staging_path,
                        symbol=symbol,
                        start_date=start_date,
                        end_date=end_date,
                    )
                    records.append(
                        {
                            "symbol": symbol,
                            "path": str(
                                ensure_within(output / f"{symbol}.csv", training_root)
                            ),
                            "query_start_date": start_date,
                            "query_end_date": end_date,
                            **observed,
                            "resumed": False,
                        }
                    )
            finally:
                bs.logout()
        records.sort(key=lambda item: item["symbol"])
        symbol_hash = hashlib.sha256(
            ("\n".join(normalized) + "\n").encode("utf-8")
        ).hexdigest()
        report = {
            "schema_version": BAOSTOCK_SCHEMA,
            "status": "ok",
            "source_class": "public_secondary",
            "fields": BAOSTOCK_FIELDS.split(","),
            "start_date": start_date,
            "end_date": end_date,
            "symbol_count": len(records),
            "symbols": normalized,
            "symbols_sha256": symbol_hash,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "shards": records,
        }
        atomic_write(
            ensure_within(staging / "manifest.json", training_root),
            (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        _promote_directory(staging, output, training_root)
        staging = None
        return report
    finally:
        _cleanup_staging(staging)


def _load_data_contract() -> Any:
    """Load the canonical PIT validator without duplicating its schema."""

    import importlib.util
    import sys

    module_name = "kronos_a_share_data"
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing
    module_path = Path(__file__).resolve().with_name(f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise PublicDataError("无法加载 PIT 规范合同")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _strict_keys(payload: Mapping[str, Any], allowed: set[str], *, label: str) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise PublicDataError(f"{label} 包含未知字段：{unknown}")


def _parse_aware_timestamp(value: Any, *, field: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise PublicDataError(f"{field} 必须为带时区 ISO-8601") from exc
    if parsed.tzinfo is None:
        raise PublicDataError(f"{field} 必须带时区")
    return parsed.isoformat()


def _normalization_manifest(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PublicDataError(f"归一化 manifest 无法读取：{path}") from exc
    if not isinstance(payload, dict):
        raise PublicDataError("归一化 manifest 必须是 JSON object")
    schema_version = payload.get("schema_version")
    if schema_version == NORMALIZATION_SCHEMA_V1:
        _strict_keys(
            payload,
            {
                "schema_version",
                "coverage_start",
                "coverage_end",
                "source_priority",
                "datasets",
            },
            label="normalization manifest",
        )
        lower = _parse_iso_date(payload.get("coverage_start"), "coverage_start")
        upper = _parse_iso_date(payload.get("coverage_end"), "coverage_end")
    elif schema_version == NORMALIZATION_SCHEMA_V2:
        _strict_keys(
            payload,
            {
                "schema_version",
                "model_coverage_start",
                "model_coverage_end",
                "evidence_lookback_start",
                "source_priority",
                "datasets",
            },
            label="normalization manifest",
        )
        lower = _parse_iso_date(
            payload.get("model_coverage_start"), "model_coverage_start"
        )
        upper = _parse_iso_date(
            payload.get("model_coverage_end"), "model_coverage_end"
        )
        evidence_start = _parse_iso_date(
            payload.get("evidence_lookback_start"), "evidence_lookback_start"
        )
        if lower != date(2018, 1, 2) or upper != date(2026, 7, 31):
            raise PublicDataError(
                "v2 model_coverage_start/end 固定为 2018-01-02—2026-07-31"
            )
        if evidence_start >= lower:
            raise PublicDataError("evidence_lookback_start 必须早于 model_coverage_start")
    else:
        raise PublicDataError(
            f"schema_version 必须为 {NORMALIZATION_SCHEMA_V1} 或 {NORMALIZATION_SCHEMA_V2}"
        )
    if payload.get("source_priority") != list(SOURCE_PRIORITY):
        raise PublicDataError(
            "source_priority 必须固定为 official_primary > "
            "public_secondary > tdx_mechanical"
        )
    if lower > upper:
        raise PublicDataError("model/coverage start 不得晚于 end")
    datasets = payload.get("datasets")
    if not isinstance(datasets, dict) or set(datasets) != set(NORMALIZED_DATASETS):
        raise PublicDataError(
            f"datasets 必须精确包含七张业务表：{list(NORMALIZED_DATASETS)}"
        )
    return payload, hashlib.sha256(raw).hexdigest()


def _resolve_snapshot_source(
    source: Mapping[str, Any],
    *,
    training_root: Path,
    output: Path,
    label: str,
    dataset: str | None = None,
) -> dict[str, Any]:
    manifest_reference = source.get("snapshot_manifest")
    if not isinstance(manifest_reference, str) or not manifest_reference.strip():
        raise PublicDataError(f"{label}.snapshot_manifest 不得为空")
    manifest_path = ensure_within(Path(manifest_reference), training_root)
    if not manifest_path.is_file():
        raise PublicDataError(f"{label}.snapshot_manifest 不存在：{manifest_path}")
    if manifest_path == output or output in manifest_path.parents:
        raise PublicDataError(f"{label}.snapshot_manifest 不得位于待发布目录内")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PublicDataError(f"{label}.snapshot_manifest 无法解析") from exc
    records = manifest.get("sources") if isinstance(manifest, dict) else None
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") != SOURCE_SCHEMA
        or manifest.get("status") != "ok"
        or not isinstance(records, list)
    ):
        raise PublicDataError(f"{label}.snapshot_manifest 不是受控 URL 原始快照")
    source_id = str(source.get("source_id", ""))
    matches = [item for item in records if isinstance(item, dict) and item.get("source_id") == source_id]
    if len(matches) != 1:
        raise PublicDataError(f"{label}.source_id 在原始快照中必须唯一：{source_id!r}")
    record = matches[0]
    source_class = str(source.get("source_class", ""))
    if source_class not in {"official_primary", "public_secondary"}:
        raise PublicDataError(f"{label}.source_class 不可作为规范表供值源")
    if record.get("source_class") != source_class:
        raise PublicDataError(f"{label}.source_class 与已抓取 manifest 不一致")
    configured_artifact = _evidence_artifact_metadata(source, label=label)
    recorded_artifact = _evidence_artifact_metadata(
        record, label=f"{label}.snapshot_record"
    )
    if configured_artifact and configured_artifact != recorded_artifact:
        raise PublicDataError(f"{label} 日历工件元数据与已抓取 manifest 不一致")
    raw_reference = record.get("local_path")
    if not isinstance(raw_reference, str) or not raw_reference.strip():
        raise PublicDataError(f"{label} 原始快照缺少 local_path")
    raw_path = Path(raw_reference)
    if not raw_path.is_absolute():
        raw_path = manifest_path.parent / raw_path
    raw_path = ensure_within(raw_path, training_root)
    if not raw_path.is_file() or raw_path == output or output in raw_path.parents:
        raise PublicDataError(f"{label} 原始响应不存在或位于待发布目录内")
    expected_hash = str(record.get("sha256", "")).lower()
    if not SHA256_PATTERN.fullmatch(expected_hash) or sha256_file(raw_path) != expected_hash:
        raise PublicDataError(f"{label} 原始响应 SHA256 不匹配")
    if record.get("bytes") is not None and int(record["bytes"]) != raw_path.stat().st_size:
        raise PublicDataError(f"{label} 原始响应字节数不匹配")
    valid_from = _parse_iso_date(record.get("valid_from"), f"{label}.valid_from")
    valid_to = _parse_iso_date(record.get("valid_to"), f"{label}.valid_to")
    if valid_to < valid_from:
        raise PublicDataError(f"{label}.valid_to 早于 valid_from")
    url = str(record.get("resolved_url") or record.get("url") or "")
    _validate_fixed_source_identity(
        url,
        source_class=source_class,
        dataset=dataset,
    )
    return {
        "source_id": source_id,
        "source_class": source_class,
        "url": url,
        "retrieved_at": _parse_aware_timestamp(
            record.get("retrieved_at"), field=f"{label}.retrieved_at"
        ),
        "valid_from": valid_from,
        "valid_to": valid_to,
        "raw_path": raw_path,
        "sha256": expected_hash,
        "bytes": raw_path.stat().st_size,
        "snapshot_manifest": manifest_path,
        "snapshot_manifest_sha256": sha256_file(manifest_path),
        **recorded_artifact,
    }


def _resolve_mechanical_source(
    source: Mapping[str, Any],
    *,
    training_root: Path,
    output: Path,
    label: str,
) -> dict[str, Any]:
    if source.get("source_class") != "tdx_mechanical":
        raise PublicDataError(f"{label} 机械核验源必须为 tdx_mechanical")
    raw_reference = source.get("raw_path")
    if not isinstance(raw_reference, str) or not raw_reference.strip():
        raise PublicDataError(f"{label}.raw_path 不得为空")
    raw_path = ensure_within(Path(raw_reference), training_root)
    if not raw_path.is_file() or raw_path == output or output in raw_path.parents:
        raise PublicDataError(f"{label}.raw_path 不存在或位于待发布目录内")
    expected_hash = str(source.get("sha256", "")).lower()
    if not SHA256_PATTERN.fullmatch(expected_hash) or sha256_file(raw_path) != expected_hash:
        raise PublicDataError(f"{label} TDX 机械核验文件 SHA256 不匹配")
    valid_from = _parse_iso_date(source.get("valid_from"), f"{label}.valid_from")
    valid_to = _parse_iso_date(source.get("valid_to"), f"{label}.valid_to")
    if valid_to < valid_from:
        raise PublicDataError(f"{label}.valid_to 早于 valid_from")
    return {
        "source_id": str(source.get("source_id", "")),
        "source_class": "tdx_mechanical",
        "retrieved_at": _parse_aware_timestamp(
            source.get("retrieved_at"), field=f"{label}.retrieved_at"
        ),
        "valid_from": valid_from,
        "valid_to": valid_to,
        "raw_path": raw_path,
        "sha256": expected_hash,
        "bytes": raw_path.stat().st_size,
    }


def _canonical_json_sha256(payload: Mapping[str, Any]) -> str:
    try:
        raw = json.dumps(
            dict(payload),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise PublicDataError("extractor_config 必须可确定性 JSON 序列化") from exc
    return hashlib.sha256(raw).hexdigest()


def _validate_extractor_config(
    source: Mapping[str, Any],
    *,
    label: str,
) -> dict[str, Any]:
    source_format = str(source.get("format", ""))
    expected = EXTRACTOR_BY_FORMAT.get(source_format)
    if expected is None:
        raise PublicDataError(f"{label}.format 必须为 csv/json/html/pdf")
    extractor_id = source.get("extractor_id")
    extractor_version = str(source.get("extractor_version", ""))
    if (extractor_id, extractor_version) != expected:
        raise PublicDataError(
            f"{label} extractor 固定为 id={expected[0]!r}, version={expected[1]!r}"
        )
    config = source.get("extractor_config")
    if not isinstance(config, dict):
        raise PublicDataError(f"{label}.extractor_config 必须是 object")
    if source_format == "csv":
        _strict_keys(config, {"encoding", "delimiter"}, label=f"{label}.extractor_config")
        encoding = str(config.get("encoding", "utf-8-sig")).lower().replace("_", "-")
        delimiter = str(config.get("delimiter", ","))
        if encoding not in SUPPORTED_ENCODINGS:
            raise PublicDataError(f"{label}.extractor_config.encoding 不在允许列表")
        if len(delimiter) != 1 or delimiter in {"\r", "\n", "\0"}:
            raise PublicDataError(f"{label}.extractor_config.delimiter 必须是单个可见字符")
        normalized_config: dict[str, Any] = {
            "encoding": encoding,
            "delimiter": delimiter,
        }
    elif source_format == "json":
        _strict_keys(
            config,
            {"encoding", "records_path", "pagination_metadata"},
            label=f"{label}.extractor_config",
        )
        encoding = str(config.get("encoding", "utf-8")).lower().replace("_", "-")
        records_path = config.get("records_path", [])
        if encoding not in SUPPORTED_ENCODINGS:
            raise PublicDataError(f"{label}.extractor_config.encoding 不在允许列表")
        if not isinstance(records_path, list) or any(
            not isinstance(item, (str, int)) or isinstance(item, bool)
            for item in records_path
        ):
            raise PublicDataError(f"{label}.extractor_config.records_path 必须为字符串/整数数组")
        normalized_config = {"encoding": encoding, "records_path": records_path}
        pagination_metadata = config.get("pagination_metadata")
        if pagination_metadata is not None:
            if not isinstance(pagination_metadata, Mapping):
                raise PublicDataError(
                    f"{label}.extractor_config.pagination_metadata 必须是 object"
                )
            _strict_keys(
                pagination_metadata,
                {"total_records_path", "total_pages_path", "page_number_path"},
                label=f"{label}.extractor_config.pagination_metadata",
            )
            normalized_metadata: dict[str, list[str | int]] = {}
            for field in (
                "total_records_path",
                "total_pages_path",
                "page_number_path",
            ):
                path_components = pagination_metadata.get(field)
                if (
                    not isinstance(path_components, list)
                    or not path_components
                    or any(
                        not isinstance(component, (str, int))
                        or isinstance(component, bool)
                        for component in path_components
                    )
                ):
                    raise PublicDataError(
                        f"{label}.extractor_config.pagination_metadata.{field} 无效"
                    )
                normalized_metadata[field] = list(path_components)
            normalized_config["pagination_metadata"] = normalized_metadata
    elif source_format == "html":
        _strict_keys(config, {"encoding", "table_index"}, label=f"{label}.extractor_config")
        encoding = str(config.get("encoding", "utf-8")).lower().replace("_", "-")
        table_index = config.get("table_index", 0)
        if encoding not in SUPPORTED_ENCODINGS:
            raise PublicDataError(f"{label}.extractor_config.encoding 不在允许列表")
        if not isinstance(table_index, int) or isinstance(table_index, bool) or table_index < 0:
            raise PublicDataError(f"{label}.extractor_config.table_index 必须为非负整数")
        normalized_config = {"encoding": encoding, "table_index": table_index}
    else:
        _strict_keys(config, {"pages", "table_index"}, label=f"{label}.extractor_config")
        pages = config.get("pages")
        table_index = config.get("table_index", 0)
        if (
            not isinstance(pages, list)
            or not pages
            or any(not isinstance(item, int) or isinstance(item, bool) or item < 0 for item in pages)
            or pages != sorted(set(pages))
        ):
            raise PublicDataError(f"{label}.extractor_config.pages 必须为递增、唯一的非负整数数组")
        if not isinstance(table_index, int) or isinstance(table_index, bool) or table_index < 0:
            raise PublicDataError(f"{label}.extractor_config.table_index 必须为非负整数")
        normalized_config = {"pages": pages, "table_index": table_index}

    configured_hash = str(source.get("extractor_config_sha256", "")).lower()
    observed_hash = _canonical_json_sha256(normalized_config)
    if not SHA256_PATTERN.fullmatch(configured_hash) or configured_hash != observed_hash:
        raise PublicDataError(f"{label}.extractor_config_sha256 不匹配")
    extracted_hash = str(source.get("extracted_sha256", "")).lower()
    if not SHA256_PATTERN.fullmatch(extracted_hash):
        raise PublicDataError(f"{label}.extracted_sha256 必须为小写 SHA256")
    row_count = source.get("extracted_row_count")
    if not isinstance(row_count, int) or isinstance(row_count, bool) or row_count < 1:
        raise PublicDataError(f"{label}.extracted_row_count 必须为正整数")
    if source.get("row_audit_status") not in (None, "passed"):
        raise PublicDataError(f"{label}.row_audit_status 只能作为 passed 冗余声明")
    row_audit = source.get("row_audit")
    if not isinstance(row_audit, dict):
        raise PublicDataError(
            f"{label}.row_audit 必须提供逐行审计工件；不接受 row_audit_status 标量自证"
        )
    _strict_keys(
        row_audit,
        {
            "schema_version",
            "path",
            "sha256",
            "bytes",
            "row_count",
            "source_sha256",
            "extracted_sha256",
            "audit_status",
            "audited_at",
            "auditor",
        },
        label=f"{label}.row_audit",
    )
    if row_audit.get("schema_version") != ROW_AUDIT_SCHEMA:
        raise PublicDataError(f"{label}.row_audit.schema_version 无效")
    if row_audit.get("audit_status") != "passed":
        raise PublicDataError(f"{label}.row_audit.audit_status 必须为 passed")
    for field in ("sha256", "source_sha256", "extracted_sha256"):
        if not SHA256_PATTERN.fullmatch(str(row_audit.get(field, ""))):
            raise PublicDataError(f"{label}.row_audit.{field} 必须为 SHA256")
    for field in ("bytes", "row_count"):
        value = row_audit.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise PublicDataError(f"{label}.row_audit.{field} 必须为正整数")
    _parse_aware_timestamp(row_audit.get("audited_at"), field=f"{label}.row_audit.audited_at")
    if not isinstance(row_audit.get("auditor"), str) or not row_audit["auditor"].strip():
        raise PublicDataError(f"{label}.row_audit.auditor 不得为空")
    return {
        "source_format": source_format,
        "extractor_id": expected[0],
        "extractor_version": expected[1],
        "extractor_config": normalized_config,
        "extractor_config_sha256": observed_hash,
        "extracted_sha256": extracted_hash,
        "extracted_row_count": row_count,
        "row_audit_status": "passed",
        "row_audit": dict(row_audit),
    }


def _source_contract(
    source: Any,
    *,
    training_root: Path,
    output: Path,
    label: str,
    expected_role: str | None = None,
    normalization_schema: str = NORMALIZATION_SCHEMA_V1,
    dataset: str | None = None,
) -> dict[str, Any]:
    if not isinstance(source, dict):
        raise PublicDataError(f"{label} 必须是 object")
    allowed = {
        "source_id",
        "source_class",
        "role",
        "snapshot_manifest",
        "raw_path",
        "sha256",
        "valid_from",
        "valid_to",
        "retrieved_at",
        "format",
        "encoding",
        "delimiter",
        "mapping",
        "constants",
        "artifact_role",
        "artifact_schema_version",
    }
    if normalization_schema == NORMALIZATION_SCHEMA_V2:
        allowed |= {
            "extractor_id",
            "extractor_version",
            "extractor_config",
            "extractor_config_sha256",
            "extracted_sha256",
            "extracted_row_count",
            "row_audit_status",
            "row_audit",
            "reviewed_overlay",
        }
    _strict_keys(source, allowed, label=label)
    source_id = str(source.get("source_id", ""))
    if not SOURCE_ID_PATTERN.fullmatch(source_id):
        raise PublicDataError(f"{label}.source_id 格式无效")
    role = str(source.get("role", "authoritative"))
    if expected_role is not None:
        if source.get("role") not in (None, expected_role):
            raise PublicDataError(f"{label}.role 与所在位置不一致")
        role = expected_role
    if role not in {"authoritative", "mechanical_cross_check", "expected_keys"}:
        raise PublicDataError(f"{label}.role 无效")
    if normalization_schema == NORMALIZATION_SCHEMA_V1:
        if source.get("format") != "csv":
            raise PublicDataError(f"{label}.format 当前只允许显式 csv")
        encoding = str(source.get("encoding", "utf-8-sig"))
        if encoding.lower().replace("_", "-") not in SUPPORTED_ENCODINGS:
            raise PublicDataError(f"{label}.encoding 不在允许列表")
        delimiter = str(source.get("delimiter", ","))
        if len(delimiter) != 1 or delimiter in {"\r", "\n", "\0"}:
            raise PublicDataError(f"{label}.delimiter 必须是单个可见分隔符")
        extraction: dict[str, Any] = {}
    elif normalization_schema == NORMALIZATION_SCHEMA_V2:
        if source.get("encoding") is not None or source.get("delimiter") is not None:
            raise PublicDataError(
                f"{label} v2 的 encoding/delimiter 必须只写入 extractor_config"
            )
        extraction = _validate_extractor_config(source, label=label)
        encoding = str(extraction["extractor_config"].get("encoding", "utf-8"))
        delimiter = str(extraction["extractor_config"].get("delimiter", ","))
    else:
        raise PublicDataError(f"{label} normalization_schema 无效")
    mapping = source.get("mapping")
    constants = source.get("constants", {})
    if not isinstance(mapping, dict) or not mapping:
        raise PublicDataError(f"{label}.mapping 必须是非空 object")
    if not isinstance(constants, dict):
        raise PublicDataError(f"{label}.constants 必须是 object")
    if set(mapping) & set(constants):
        raise PublicDataError(f"{label} 同一目标列不得同时 mapping/constants")
    if role == "mechanical_cross_check":
        if source.get("snapshot_manifest") is not None:
            raise PublicDataError(f"{label} TDX 机械核验不得伪装成 URL 快照")
        resolved = _resolve_mechanical_source(
            source, training_root=training_root, output=output, label=label
        )
    else:
        if source.get("source_class") == "tdx_mechanical":
            raise PublicDataError("TDX 机械核验源不得作为供值或 expected_keys")
        forbidden_direct = {
            field
            for field in ("raw_path", "sha256", "valid_from", "valid_to", "retrieved_at")
            if source.get(field) is not None
        }
        if forbidden_direct:
            raise PublicDataError(
                f"{label} official/public 元数据只能来自已抓取 snapshot_manifest："
                f"{sorted(forbidden_direct)}"
            )
        resolved = _resolve_snapshot_source(
            source,
            training_root=training_root,
            output=output,
            label=label,
            dataset=dataset,
        )
    return {
        **resolved,
        "role": role,
        "format": "csv",
        "encoding": encoding,
        "delimiter": delimiter,
        "mapping": mapping,
        "constants": constants,
        "normalization_schema": normalization_schema,
        "reviewed_overlay": source.get("reviewed_overlay"),
        "_training_root": training_root.resolve(),
        "_output": output.resolve(),
        **extraction,
    }


def _normalize_ticker(value: Any) -> str:
    raw = str(value).strip()
    prefixed = re.fullmatch(r"(?i)(sh|sz|bj)[.]?(\d{6})", raw)
    if prefixed:
        return f"{prefixed.group(2)}.{prefixed.group(1).upper()}"
    suffixed = re.fullmatch(r"(?i)(\d{6})[.](SH|SZ|BJ)", raw)
    if suffixed:
        return f"{suffixed.group(1)}.{suffixed.group(2).upper()}"
    raise PublicDataError(f"ticker 无法归一化：{value!r}")


def _mapping_value(series: Any, spec: Any, *, label: str) -> Any:
    import pandas as pd

    if isinstance(spec, str):
        column, transform, value_map = spec, "identity", None
    elif isinstance(spec, dict):
        _strict_keys(spec, {"column", "transform", "value_map"}, label=label)
        column = spec.get("column")
        transform = str(spec.get("transform", "identity"))
        value_map = spec.get("value_map")
    else:
        raise PublicDataError(f"{label} 必须是源列名或 mapping object")
    if not isinstance(column, str) or column not in series.columns:
        raise PublicDataError(f"{label}.column 不存在：{column!r}")
    values = series[column].map(lambda value: value.strip() if isinstance(value, str) else value)
    if value_map is not None:
        if not isinstance(value_map, dict) or not value_map:
            raise PublicDataError(f"{label}.value_map 必须是非空 object")
        unknown = sorted({str(value) for value in values.dropna()} - set(value_map))
        if unknown:
            raise PublicDataError(f"{label}.value_map 缺少原值：{unknown[:10]}")
        values = values.map(lambda value: value_map.get(str(value)) if pd.notna(value) else value)
    transforms = {
        "identity": lambda value: value,
        "ticker": _normalize_ticker,
        "upper": lambda value: str(value).strip().upper(),
        "lower": lambda value: str(value).strip().lower(),
        "bool_01": lambda value: {
            "0": False,
            "1": True,
            "false": False,
            "true": True,
        }[str(value).strip().lower()],
    }
    if transform not in transforms:
        raise PublicDataError(f"{label}.transform 不受支持：{transform}")
    try:
        return values.map(
            lambda value: transforms[transform](value) if pd.notna(value) else value
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise PublicDataError(f"{label} 转换失败：{exc}") from exc


def _canonical_extracted_bytes(frame: Any) -> bytes:
    return frame.to_csv(index=False, lineterminator="\n", na_rep="").encode("utf-8")


def _canonical_extracted_row_sha256(row: Mapping[str, Any], columns: Sequence[str]) -> str:
    import pandas as pd

    payload = [
        [str(column), "" if pd.isna(row[column]) else str(row[column])]
        for column in columns
    ]
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _json_pointer_component(value: Any) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def _extract_tabular_source(contract: Mapping[str, Any]) -> tuple[Any, bytes]:
    import pandas as pd

    raw_path = Path(contract["raw_path"])
    source_format = contract.get("source_format")
    config = contract.get("extractor_config")
    try:
        if source_format == "csv":
            frame = pd.read_csv(
                raw_path,
                dtype=str,
                encoding=config["encoding"],
                sep=config["delimiter"],
                keep_default_na=False,
            )
            raw_locators = [f"csv:data-row:{index}" for index in range(1, len(frame) + 1)]
        elif source_format == "json":
            payload = json.loads(raw_path.read_text(encoding=config["encoding"]))
            pagination_values = None
            if config.get("pagination_metadata") is not None:
                pagination_values = {}
                for field, path_components in config["pagination_metadata"].items():
                    current: Any = payload
                    for component in path_components:
                        if isinstance(component, int):
                            if not isinstance(current, list) or not 0 <= component < len(current):
                                raise PublicDataError(
                                    f"JSON pagination_metadata.{field} 越界"
                                )
                        elif not isinstance(current, Mapping) or component not in current:
                            raise PublicDataError(
                                f"JSON pagination_metadata.{field} 不存在"
                            )
                        current = current[component]
                    if isinstance(current, bool) or not str(current).strip().isdigit():
                        raise PublicDataError(
                            f"JSON pagination_metadata.{field} 必须为非负整数"
                        )
                    pagination_values[field] = int(current)
            records: Any = payload
            for component in config["records_path"]:
                if isinstance(component, int):
                    if not isinstance(records, list) or component >= len(records):
                        raise PublicDataError("JSON records_path 越界")
                elif not isinstance(records, Mapping) or component not in records:
                    raise PublicDataError("JSON records_path 不存在")
                records = records[component]
            if not isinstance(records, list) or not records or not all(
                isinstance(row, Mapping) for row in records
            ):
                raise PublicDataError("JSON extractor 结果必须为非空 object 数组")
            frame = pd.DataFrame([dict(row) for row in records])
            if pagination_values is not None:
                frame.attrs["pagination_metadata"] = pagination_values
            pointer_prefix = "".join(
                f"/{_json_pointer_component(component)}"
                for component in config["records_path"]
            )
            raw_locators = [
                f"json:{pointer_prefix}/{index}" for index in range(len(frame))
            ]
        elif source_format == "html":
            try:
                from bs4 import BeautifulSoup
            except ImportError as exc:
                raise PublicDataError("missing_dependency:beautifulsoup4") from exc
            document = BeautifulSoup(
                raw_path.read_text(encoding=config["encoding"]), "html.parser"
            )
            tables = document.find_all("table")
            table_index = config["table_index"]
            if table_index >= len(tables):
                raise PublicDataError("HTML table_index 越界")
            rows: list[list[str]] = []
            for tr in tables[table_index].find_all("tr"):
                cells = tr.find_all(["th", "td"])
                if not cells:
                    continue
                if any(
                    str(cell.get("rowspan", "1")) != "1"
                    or str(cell.get("colspan", "1")) != "1"
                    for cell in cells
                ):
                    raise PublicDataError("HTML extractor 不允许 rowspan/colspan")
                rows.append([cell.get_text(" ", strip=True) for cell in cells])
            if len(rows) < 2:
                raise PublicDataError("HTML table 必须包含表头和至少一条记录")
            header = rows[0]
            if any(not value for value in header) or len(header) != len(set(header)):
                raise PublicDataError("HTML table 表头必须非空且唯一")
            if any(len(row) != len(header) for row in rows[1:]):
                raise PublicDataError("HTML table 行列数不一致")
            frame = pd.DataFrame(rows[1:], columns=header)
            raw_locators = [
                f"html:table:{table_index}:data-row:{index}"
                for index in range(1, len(frame) + 1)
            ]
        elif source_format == "pdf":
            try:
                import pdfplumber
            except ImportError as exc:
                raise PublicDataError("missing_dependency:pdfplumber") from exc
            extracted_rows: list[list[Any]] = []
            raw_locators = []
            header: list[str] | None = None
            with pdfplumber.open(io.BytesIO(raw_path.read_bytes())) as document:
                for page_number in config["pages"]:
                    if page_number >= len(document.pages):
                        raise PublicDataError("PDF pages 越界")
                    tables = document.pages[page_number].extract_tables()
                    if config["table_index"] >= len(tables):
                        raise PublicDataError("PDF table_index 越界")
                    table = tables[config["table_index"]]
                    if not table or len(table) < 2:
                        raise PublicDataError("PDF table 必须包含表头和记录")
                    current_header = [str(value or "").strip() for value in table[0]]
                    if any(not value for value in current_header) or len(current_header) != len(
                        set(current_header)
                    ):
                        raise PublicDataError("PDF table 表头必须非空且唯一")
                    if header is None:
                        header = current_header
                    elif current_header != header:
                        raise PublicDataError("PDF 跨页表头不一致")
                    for row_number, row in enumerate(table[1:], start=1):
                        if len(row) != len(header):
                            raise PublicDataError("PDF table 行列数不一致")
                        extracted_rows.append([str(value or "").strip() for value in row])
                        raw_locators.append(
                            f"pdf:page:{page_number}:table:{config['table_index']}:data-row:{row_number}"
                        )
            if header is None or not extracted_rows:
                raise PublicDataError("PDF extractor 未产生记录")
            frame = pd.DataFrame(extracted_rows, columns=header)
        else:
            raise PublicDataError(f"不支持的 extractor format：{source_format!r}")
    except PublicDataError:
        raise
    except Exception as exc:
        raise PublicDataError(
            f"{contract['source_id']} {source_format} 确定性抽取失败：{exc}"
        ) from exc
    if frame.empty:
        raise PublicDataError(f"{contract['source_id']} 抽取结果为空")
    frame.columns = [str(column).strip() for column in frame.columns]
    if any(not column for column in frame.columns) or len(frame.columns) != len(set(frame.columns)):
        raise PublicDataError(f"{contract['source_id']} 抽取结果列名必须非空且唯一")
    if len(raw_locators) != len(frame) or len(set(raw_locators)) != len(raw_locators):
        raise PublicDataError(f"{contract['source_id']} 原始行定位无法闭合")
    frame.attrs["raw_locators"] = tuple(raw_locators)
    extracted = _canonical_extracted_bytes(frame)
    observed_hash = hashlib.sha256(extracted).hexdigest()
    if observed_hash != contract["extracted_sha256"]:
        raise PublicDataError(f"{contract['source_id']} extracted SHA256 不匹配")
    if len(frame) != contract["extracted_row_count"]:
        raise PublicDataError(f"{contract['source_id']} extracted_row_count 不匹配")
    return frame, extracted


def _validate_row_audit_artifact(
    frame: Any,
    contract: Mapping[str, Any],
    *,
    label: str,
) -> dict[str, Any]:
    import pandas as pd

    audit = contract.get("row_audit")
    if not isinstance(audit, Mapping):
        raise PublicDataError(f"{label}.row_audit 缺失")
    if audit.get("source_sha256") != contract.get("sha256"):
        raise PublicDataError(f"{label}.row_audit.source_sha256 绑定不匹配")
    if audit.get("extracted_sha256") != contract.get("extracted_sha256"):
        raise PublicDataError(f"{label}.row_audit.extracted_sha256 绑定不匹配")
    if int(audit.get("row_count", -1)) != len(frame):
        raise PublicDataError(f"{label}.row_audit.row_count 与抽取行数不匹配")
    reference = audit.get("path")
    if not isinstance(reference, str) or not Path(reference).is_absolute():
        raise PublicDataError(f"{label}.row_audit.path 必须是 training_root 内绝对路径")
    audit_path = ensure_within(Path(reference), Path(contract["_training_root"]))
    if (
        not audit_path.is_file()
        or audit_path == contract["_output"]
        or contract["_output"] in audit_path.parents
    ):
        raise PublicDataError(f"{label}.row_audit.path 不存在或位于待发布目录内")
    if sha256_file(audit_path) != str(audit.get("sha256", "")).lower():
        raise PublicDataError(f"{label}.row_audit.sha256 漂移")
    if audit_path.stat().st_size != int(audit.get("bytes", -1)):
        raise PublicDataError(f"{label}.row_audit.bytes 漂移")
    try:
        rows = pd.read_csv(
            audit_path,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
        )
    except Exception as exc:
        raise PublicDataError(f"{label}.row_audit 无法读取：{exc}") from exc
    required = {
        "source_row_number",
        "raw_locator",
        "extracted_row_sha256",
        "audit_status",
    }
    if set(rows.columns) != required:
        raise PublicDataError(f"{label}.row_audit 列合同无效")
    expected_numbers = [str(index) for index in range(1, len(frame) + 1)]
    if rows["source_row_number"].tolist() != expected_numbers:
        raise PublicDataError(f"{label}.row_audit.source_row_number 必须逐行连续闭合")
    expected_locators = list(frame.attrs.get("raw_locators", ()))
    if rows["raw_locator"].tolist() != expected_locators:
        raise PublicDataError(f"{label}.row_audit.raw_locator 与确定性抽取定位不匹配")
    expected_hashes = [
        _canonical_extracted_row_sha256(row, list(frame.columns))
        for row in frame.to_dict(orient="records")
    ]
    if rows["extracted_row_sha256"].tolist() != expected_hashes:
        raise PublicDataError(f"{label}.row_audit.extracted_row_sha256 不匹配")
    if not rows["audit_status"].eq("passed").all():
        raise PublicDataError(f"{label}.row_audit 存在未通过行")
    return {
        "schema_version": ROW_AUDIT_SCHEMA,
        "path": audit_path,
        "sha256": str(audit["sha256"]).lower(),
        "bytes": audit_path.stat().st_size,
        "row_count": len(rows),
        "source_sha256": str(contract["sha256"]),
        "extracted_sha256": str(contract["extracted_sha256"]),
        "audit_status": "passed",
        "audited_at": _parse_aware_timestamp(
            audit.get("audited_at"), field=f"{label}.row_audit.audited_at"
        ),
        "auditor": str(audit["auditor"]).strip(),
    }


def _apply_reviewed_overlay(
    frame: Any,
    contract: dict[str, Any],
    *,
    dataset: str,
) -> Any:
    import pandas as pd

    overlay = contract.get("reviewed_overlay")
    if overlay is None:
        return frame
    if contract.get("normalization_schema") != NORMALIZATION_SCHEMA_V2:
        raise PublicDataError("reviewed_overlay 只允许用于 v2")
    if not isinstance(overlay, dict):
        raise PublicDataError(f"{dataset}/{contract['source_id']}.reviewed_overlay 必须是 object")
    allowed = {
        "schema_version",
        "path",
        "sha256",
        "row_count",
        "raw_sha256",
        "extracted_sha256",
        "extractor_id",
        "extractor_version",
        "extractor_config_sha256",
        "review_status",
        "reviewed_at",
        "reviewer",
        "reason",
    }
    label = f"{dataset}/{contract['source_id']}.reviewed_overlay"
    _strict_keys(overlay, allowed, label=label)
    if overlay.get("schema_version") != REVIEWED_OVERLAY_SCHEMA:
        raise PublicDataError(f"{label}.schema_version 无效")
    for key, expected in (
        ("raw_sha256", contract["sha256"]),
        ("extracted_sha256", contract["extracted_sha256"]),
        ("extractor_id", contract["extractor_id"]),
        ("extractor_version", contract["extractor_version"]),
        ("extractor_config_sha256", contract["extractor_config_sha256"]),
    ):
        if overlay.get(key) != expected:
            raise PublicDataError(f"{label}.{key} 与原始抽取合同不匹配")
    if overlay.get("review_status") != "approved":
        raise PublicDataError(f"{label}.review_status 必须为 approved")
    _parse_aware_timestamp(overlay.get("reviewed_at"), field=f"{label}.reviewed_at")
    for field in ("reviewer", "reason"):
        if not isinstance(overlay.get(field), str) or not overlay[field].strip():
            raise PublicDataError(f"{label}.{field} 不得为空")
    overlay_reference = overlay.get("path")
    if not isinstance(overlay_reference, str) or not Path(overlay_reference).is_absolute():
        raise PublicDataError(f"{label}.path 必须是 training_root 内绝对路径")
    overlay_path = ensure_within(Path(overlay_reference), contract["_training_root"])
    if (
        not overlay_path.is_file()
        or overlay_path == contract["_output"]
        or contract["_output"] in overlay_path.parents
    ):
        raise PublicDataError(f"{label}.path 不存在或位于待发布目录内")
    expected_hash = str(overlay.get("sha256", "")).lower()
    if not SHA256_PATTERN.fullmatch(expected_hash) or sha256_file(overlay_path) != expected_hash:
        raise PublicDataError(f"{label}.sha256 不匹配")
    try:
        corrections = pd.read_csv(
            overlay_path, dtype=str, keep_default_na=False, encoding="utf-8-sig"
        )
    except Exception as exc:
        raise PublicDataError(f"{label} 无法读取：{exc}") from exc
    row_count = overlay.get("row_count")
    if not isinstance(row_count, int) or isinstance(row_count, bool) or row_count < 1:
        raise PublicDataError(f"{label}.row_count 必须为正整数")
    if len(corrections) != row_count:
        raise PublicDataError(f"{label}.row_count 不匹配")
    required = {"source_row_number", "correction_reason", *frame.columns}
    if set(corrections.columns) != required:
        raise PublicDataError(f"{label} 列必须精确包含 source_row_number/correction_reason 和规范列")
    numbers = pd.to_numeric(corrections["source_row_number"], errors="coerce")
    if (
        numbers.isna().any()
        or (numbers % 1 != 0).any()
        or (numbers < 1).any()
        or (numbers > len(frame)).any()
        or numbers.duplicated().any()
    ):
        raise PublicDataError(f"{label}.source_row_number 必须唯一且位于抽取行范围")
    if corrections["correction_reason"].astype(str).str.strip().eq("").any():
        raise PublicDataError(f"{label}.correction_reason 不得为空")
    corrected = frame.copy()
    for row in corrections.itertuples(index=False):
        target_index = int(row.source_row_number) - 1
        for column in frame.columns:
            corrected.at[target_index, column] = getattr(row, column)
    contract["_overlay_report"] = {
        "schema_version": REVIEWED_OVERLAY_SCHEMA,
        "path": overlay_path,
        "sha256": expected_hash,
        "bytes": overlay_path.stat().st_size,
        "row_count": row_count,
        "raw_sha256": contract["sha256"],
        "extracted_sha256": contract["extracted_sha256"],
        "extractor_id": contract["extractor_id"],
        "extractor_version": contract["extractor_version"],
        "extractor_config_sha256": contract["extractor_config_sha256"],
        "review_status": "approved",
        "reviewed_at": _parse_aware_timestamp(
            overlay["reviewed_at"], field=f"{label}.reviewed_at"
        ),
        "reviewer": overlay["reviewer"].strip(),
        "reason": overlay["reason"].strip(),
    }
    return corrected


def _read_mapped_source(
    contract: Mapping[str, Any],
    *,
    dataset: str,
    keys_only: bool,
) -> Any:
    import pandas as pd

    data_contract = _load_data_contract()
    spec = data_contract.PIT_TABLE_SPECS[dataset]
    allowed_targets = set(spec.required_columns) | set(spec.optional_columns)
    configured_targets = set(contract["mapping"]) | set(contract["constants"])
    unknown = sorted(configured_targets - allowed_targets)
    if unknown:
        raise PublicDataError(f"{dataset}/{contract['source_id']} 映射了未知目标列：{unknown}")
    required = set(DATASET_KEYS[dataset]) if keys_only else set(spec.required_columns)
    missing = sorted(required - configured_targets)
    if missing:
        raise PublicDataError(f"{dataset}/{contract['source_id']} 缺少显式目标映射：{missing}")
    if contract.get("normalization_schema") == NORMALIZATION_SCHEMA_V2:
        source_frame, extracted_bytes = _extract_tabular_source(contract)
        row_audit_report = _validate_row_audit_artifact(
            source_frame,
            contract,
            label=f"{dataset}/{contract['source_id']}",
        )
        binding_payload = {
            "raw_sha256": contract["sha256"],
            "extractor_id": contract["extractor_id"],
            "extractor_version": contract["extractor_version"],
            "extractor_config_sha256": contract["extractor_config_sha256"],
            "extracted_sha256": contract["extracted_sha256"],
            "extracted_row_count": contract["extracted_row_count"],
            "row_audit_status": contract["row_audit_status"],
            "row_audit_sha256": row_audit_report["sha256"],
        }
        contract["_extracted_bytes"] = extracted_bytes
        contract["_row_audit_report"] = row_audit_report
        contract["_extraction_report"] = {
            **binding_payload,
            "binding_sha256": _canonical_json_sha256(binding_payload),
            "bytes": len(extracted_bytes),
            "extractor_config": dict(contract["extractor_config"]),
        }
        if source_frame.attrs.get("pagination_metadata") is not None:
            contract["_extraction_report"]["pagination_metadata"] = dict(
                source_frame.attrs["pagination_metadata"]
            )
    else:
        try:
            source_frame = pd.read_csv(
                contract["raw_path"],
                dtype=str,
                encoding=contract["encoding"],
                sep=contract["delimiter"],
                keep_default_na=False,
            )
        except Exception as exc:
            raise PublicDataError(
                f"{dataset}/{contract['source_id']} 原始 CSV 无法读取：{exc}"
            ) from exc
    if source_frame.empty:
        raise PublicDataError(f"{dataset}/{contract['source_id']} 原始 CSV 无记录")
    if isinstance(contract, dict):
        contract["_source_frame"] = source_frame.copy()
    output = pd.DataFrame(index=source_frame.index)
    for target, mapping in contract["mapping"].items():
        output[target] = _mapping_value(
            source_frame,
            mapping,
            label=f"{dataset}/{contract['source_id']}.mapping.{target}",
        )
    for target, value in contract["constants"].items():
        if value is None:
            raise PublicDataError(f"{dataset}/{contract['source_id']}.constants.{target} 不得为 null")
        output[target] = value
    output = _apply_reviewed_overlay(output, contract, dataset=dataset)
    if contract.get("normalization_schema") == NORMALIZATION_SCHEMA_V2:
        canonical_source_bytes = _canonical_extracted_bytes(output)
        canonical_source_sha256 = hashlib.sha256(canonical_source_bytes).hexdigest()
        contract["_canonical_source_bytes"] = canonical_source_bytes
        contract["_extraction_report"]["canonical_source_sha256"] = (
            canonical_source_sha256
        )
        contract["_extraction_report"]["canonical_source_row_count"] = len(output)
        contract["_extraction_report"]["canonical_source_bytes"] = len(
            canonical_source_bytes
        )
        binding_payload = {
            key: contract["_extraction_report"][key]
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
        if contract["_extraction_report"].get("pagination_metadata") is not None:
            binding_payload["pagination_metadata"] = contract["_extraction_report"][
                "pagination_metadata"
            ]
        contract["_extraction_report"]["binding_sha256"] = _canonical_json_sha256(
            binding_payload
        )
    if keys_only:
        key_columns = list(DATASET_KEYS[dataset])
        if output[key_columns].isna().any().any() or (
            output[key_columns].astype(str).apply(lambda column: column.str.strip().eq(""))
        ).any().any():
            raise PublicDataError(f"{dataset}/{contract['source_id']} expected_keys 存在空键")
        if contract["role"] == "expected_keys":
            return output[key_columns].drop_duplicates().reset_index(drop=True)
        return output.reset_index(drop=True)
    try:
        return data_contract.validate_pit_table(dataset, output)
    except Exception as exc:
        raise PublicDataError(
            f"{dataset}/{contract['source_id']} 映射后不符合规范表：{exc}"
        ) from exc


def _canonical_cell(value: Any) -> str:
    import pandas as pd

    if pd.isna(value):
        return "<NA>"
    if isinstance(value, (datetime, date, pd.Timestamp)):
        return pd.Timestamp(value).date().isoformat()
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value).strip()


def _key_tuple(row: Any, columns: Sequence[str]) -> tuple[str, ...]:
    return tuple(_canonical_cell(row[column]) for column in columns)


def _merge_authoritative_sources(
    dataset: str,
    frames: Sequence[tuple[Mapping[str, Any], Any]],
) -> tuple[Any, set[tuple[str, ...]], int]:
    import pandas as pd

    keys = DATASET_KEYS[dataset]
    candidates: dict[tuple[str, ...], list[tuple[Mapping[str, Any], dict[str, Any]]]] = {}
    for contract, frame in frames:
        for row in frame.to_dict(orient="records"):
            candidates.setdefault(_key_tuple(row, keys), []).append((contract, row))
    selected: list[dict[str, Any]] = []
    conflicts: set[tuple[str, ...]] = set()
    lower_priority_disagreements = 0
    for key, group in sorted(candidates.items()):
        highest = max(SOURCE_PRIORITY_VALUE[str(contract["source_class"])] for contract, _ in group)
        top = [(contract, row) for contract, row in group if SOURCE_PRIORITY_VALUE[str(contract["source_class"])] == highest]
        signatures: dict[tuple[tuple[str, str], ...], list[tuple[Mapping[str, Any], dict[str, Any]]]] = {}
        for contract, row in top:
            signature = tuple(sorted((column, _canonical_cell(value)) for column, value in row.items()))
            signatures.setdefault(signature, []).append((contract, row))
        if len(signatures) != 1:
            conflicts.add(key)
            continue
        chosen_group = next(iter(signatures.values()))
        chosen_contract, chosen_row = min(chosen_group, key=lambda item: str(item[0]["source_id"]))
        chosen_signature = tuple(sorted((column, _canonical_cell(value)) for column, value in chosen_row.items()))
        lower_priority_disagreements += sum(
            tuple(sorted((column, _canonical_cell(value)) for column, value in row.items())) != chosen_signature
            for contract, row in group
            if SOURCE_PRIORITY_VALUE[str(contract["source_class"])] < highest
        )
        selected.append(chosen_row)
    if not selected:
        raise PublicDataError(f"{dataset}: 所有记录均因同优先级冲突被排除")
    merged = pd.DataFrame(selected)
    data_contract = _load_data_contract()
    try:
        merged = data_contract.validate_pit_table(dataset, merged)
    except Exception as exc:
        raise PublicDataError(f"{dataset}: 优先级合并后合同无效：{exc}") from exc
    return merged, conflicts, lower_priority_disagreements


def _apply_mechanical_cross_checks(
    dataset: str,
    selected: Any,
    checks: Sequence[tuple[Mapping[str, Any], Any]],
) -> tuple[Any, set[tuple[str, ...]]]:
    keys = DATASET_KEYS[dataset]
    selected_records = {
        _key_tuple(row, keys): row for row in selected.to_dict(orient="records")
    }
    conflicts: set[tuple[str, ...]] = set()
    for _, frame in checks:
        seen: dict[tuple[str, ...], tuple[tuple[str, str], ...]] = {}
        for row in frame.to_dict(orient="records"):
            key = _key_tuple(row, keys)
            comparable = tuple(
                sorted(
                    (column, _canonical_cell(value))
                    for column, value in row.items()
                    if column not in keys
                )
            )
            if key in seen and seen[key] != comparable:
                conflicts.add(key)
                continue
            seen[key] = comparable
            target = selected_records.get(key)
            if target is None:
                continue
            missing_columns = [column for column, _ in comparable if column not in target]
            if missing_columns:
                raise PublicDataError(
                    f"{dataset}: TDX 机械核验列未由 authoritative 源供值："
                    f"{missing_columns}"
                )
            if any(_canonical_cell(target[column]) != value for column, value in comparable):
                conflicts.add(key)
    if conflicts:
        selected = selected[
            ~selected.apply(lambda row: _key_tuple(row, keys) in conflicts, axis=1)
        ].reset_index(drop=True)
    if selected.empty:
        raise PublicDataError(f"{dataset}: TDX 机械核验冲突导致规范表为空")
    return selected, conflicts


def _intervals_cover(intervals: Sequence[tuple[date, date]], start: date, end: date) -> bool:
    cursor = start.toordinal()
    for lower, upper in sorted(intervals):
        lower_ordinal = lower.toordinal()
        upper_ordinal = upper.toordinal()
        if upper_ordinal < cursor:
            continue
        if lower_ordinal > cursor:
            return False
        cursor = max(cursor, upper_ordinal + 1)
        if cursor > end.toordinal():
            return True
    return cursor > end.toordinal()


def _write_normalized_csv(path: Path, frame: Any, training_root: Path) -> None:
    payload = frame.to_csv(index=False, lineterminator="\n", date_format="%Y-%m-%d").encode(
        "utf-8"
    )
    atomic_write(ensure_within(path, training_root), payload)


def _active_member_dates(
    membership: Any,
    calendar: Any,
    *,
    start: date,
    end: date,
) -> set[tuple[str, str]]:
    import pandas as pd

    events: dict[date, list[tuple[str, int]]] = {}
    for row in membership.itertuples(index=False):
        if str(row.index_code) not in {"000300.SH", "000905.SH"}:
            continue
        lower = max(row.effective_from.date(), start)
        upper = min(row.effective_to.date(), end) if not pd.isna(row.effective_to) else end
        if lower > upper:
            continue
        events.setdefault(lower, []).append((str(row.ticker), 1))
        if upper < end:
            events.setdefault(upper + timedelta(days=1), []).append(
                (str(row.ticker), -1)
            )
    open_dates = sorted(
        row.trade_date.date()
        for row in calendar.itertuples(index=False)
        if bool(row.is_open) and start <= row.trade_date.date() <= end
    )
    event_dates = sorted(events)
    event_index = 0
    active_counts: dict[str, int] = {}
    keys: set[tuple[str, str]] = set()
    for trade_date in open_dates:
        while event_index < len(event_dates) and event_dates[event_index] <= trade_date:
            for ticker, delta in events[event_dates[event_index]]:
                value = active_counts.get(ticker, 0) + delta
                if value <= 0:
                    active_counts.pop(ticker, None)
                else:
                    active_counts[ticker] = value
            event_index += 1
        keys.update((ticker, trade_date.isoformat()) for ticker in active_counts)
    return keys


def _derive_key_contract(
    dataset: str,
    frames: Mapping[str, Any],
    *,
    start: date,
    end: date,
) -> tuple[set[tuple[str, ...]], bool, list[str]]:
    import pandas as pd

    membership = frames["index_membership"]
    member_tickers = set(
        membership.loc[
            membership["index_code"].astype(str).isin({"000300.SH", "000905.SH"}),
            "ticker",
        ].astype(str)
    )
    selected = frames[dataset]
    issues: list[str] = []
    if dataset == "security_master":
        expected: set[tuple[str, ...]] = set()
        rows_by_ticker = {
            ticker: group for ticker, group in selected.groupby(selected["ticker"].astype(str))
        }
        for ticker in sorted(member_tickers):
            rows = rows_by_ticker.get(ticker)
            if rows is None:
                expected.add((ticker, "<MISSING>"))
                issues.append(f"missing_security_master:{ticker}")
            else:
                expected.update(
                    _key_tuple(row, DATASET_KEYS[dataset])
                    for row in rows.to_dict(orient="records")
                )
        return expected, not issues, issues
    if dataset == "st_status":
        expected = {
            _key_tuple(row, DATASET_KEYS[dataset])
            for row in selected[
                selected["ticker"].astype(str).isin(member_tickers)
            ].to_dict(orient="records")
        }
        status_ok = _load_data_contract()._status_intervals_cover_membership(
            selected,
            membership,
            start=start,
            end=end,
        )
        if not status_ok:
            issues.append("st_intervals_do_not_cover_active_membership")
        return expected, bool(status_ok), issues
    if dataset in {"suspensions", "price_limits"}:
        expected = _active_member_dates(
            membership,
            frames[TRADING_CALENDAR_DATASET],
            start=start,
            end=end,
        )
        if not expected:
            issues.append("active_membership_x_open_calendar_empty")
        return expected, bool(expected), issues
    raise PublicDataError(f"{dataset}: 不支持 derived coverage_key_contract")


def _receipt_file(
    config: Any,
    *,
    training_root: Path,
    output: Path,
    label: str,
) -> tuple[dict[str, Any], Path, str]:
    if not isinstance(config, Mapping):
        raise PublicDataError(f"{label} 必须是 object")
    _strict_keys(config, {"path", "sha256", "bytes"}, label=label)
    reference = config.get("path")
    if not isinstance(reference, str) or not Path(reference).is_absolute():
        raise PublicDataError(f"{label}.path 必须是 training_root 内绝对路径")
    path = ensure_within(Path(reference), training_root)
    if not path.is_file() or path == output or output in path.parents:
        raise PublicDataError(f"{label}.path 不存在或位于待发布目录内")
    expected_hash = str(config.get("sha256", "")).lower()
    if not SHA256_PATTERN.fullmatch(expected_hash) or sha256_file(path) != expected_hash:
        raise PublicDataError(f"{label}.sha256 漂移")
    expected_bytes = config.get("bytes")
    if (
        not isinstance(expected_bytes, int)
        or isinstance(expected_bytes, bool)
        or expected_bytes < 1
        or path.stat().st_size != expected_bytes
    ):
        raise PublicDataError(f"{label}.bytes 漂移")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PublicDataError(f"{label} 无法读取") from exc
    if not isinstance(payload, dict):
        raise PublicDataError(f"{label} 必须是 JSON object")
    return payload, path, expected_hash


def _membership_expected_events(
    frame: Any,
    *,
    index_code: str,
    start: date,
    end: date,
) -> tuple[set[str], dict[date, tuple[set[str], set[str]]]]:
    import pandas as pd

    subset = frame[frame["index_code"].astype(str) == index_code].copy()
    subset["effective_from"] = pd.to_datetime(
        subset["effective_from"], errors="coerce"
    ).dt.normalize()
    if "effective_to" not in subset.columns:
        subset["effective_to"] = pd.NaT
    else:
        subset["effective_to"] = pd.to_datetime(
            subset["effective_to"], errors="coerce"
        ).dt.normalize()
    if subset["effective_from"].isna().any():
        raise PublicDataError(f"{index_code}: expected_keys effective_from 无效")
    anchor = {
        str(row.ticker)
        for row in subset.itertuples(index=False)
        if row.effective_from.date() <= start
        and (pd.isna(row.effective_to) or row.effective_to.date() >= start)
    }
    mutable: dict[date, dict[str, set[str]]] = {}
    for row in subset.itertuples(index=False):
        effective_from = row.effective_from.date()
        if start < effective_from <= end:
            mutable.setdefault(effective_from, {"added": set(), "removed": set()})[
                "added"
            ].add(str(row.ticker))
        if pd.notna(row.effective_to):
            removal_date = row.effective_to.date() + timedelta(days=1)
            if start < removal_date <= end:
                mutable.setdefault(removal_date, {"added": set(), "removed": set()})[
                    "removed"
                ].add(str(row.ticker))
    return anchor, {
        event_date: (values["added"], values["removed"])
        for event_date, values in mutable.items()
    }


def _validate_csi_membership_receipt(
    payload: Mapping[str, Any],
    expected_frame: Any,
    *,
    start: date,
    end: date,
    authoritative_sha256s: set[str],
    source_frames: Mapping[str, Any] | None = None,
) -> None:
    _strict_keys(
        payload,
        {
            "schema_version",
            "dataset",
            "coverage_start",
            "coverage_end",
            "status",
            "indexes",
        },
        label="index_membership.completeness_receipt",
    )
    if (
        payload.get("schema_version") != CSI_MEMBERSHIP_RECEIPT_SCHEMA
        or payload.get("dataset") != "index_membership"
        or payload.get("status") != "passed"
        or _parse_iso_date(payload.get("coverage_start"), "receipt.coverage_start") != start
        or _parse_iso_date(payload.get("coverage_end"), "receipt.coverage_end") != end
    ):
        raise PublicDataError("index_membership completeness receipt 顶层合同无效")
    indexes = payload.get("indexes")
    expected_codes = set(expected_frame["index_code"].astype(str))
    if not isinstance(indexes, list) or {
        str(item.get("index_code")) for item in indexes if isinstance(item, Mapping)
    } != expected_codes:
        raise PublicDataError("index_membership receipt 未精确覆盖全部 index_code")
    referenced_hashes: set[str] = set()
    for item in indexes:
        if not isinstance(item, Mapping):
            raise PublicDataError("index_membership receipt index item 无效")
        _strict_keys(
            item,
            {
                "index_code",
                "anchor_date",
                "anchor_members",
                "anchor_source_sha256",
                "adjustments",
                "final_members_sha256",
            },
            label=f"index_membership.receipt.{item.get('index_code')}",
        )
        index_code = str(item["index_code"])
        if _parse_iso_date(item.get("anchor_date"), "receipt.anchor_date") != start:
            raise PublicDataError(f"{index_code}: anchor_date 必须等于 model_coverage_start")
        anchor_members = item.get("anchor_members")
        if (
            not isinstance(anchor_members, list)
            or anchor_members != sorted(set(map(str, anchor_members)))
            or any(not re.fullmatch(r"\d{6}\.(?:SH|SZ|BJ)", value) for value in anchor_members)
        ):
            raise PublicDataError(f"{index_code}: anchor_members 必须排序、唯一且 ticker 合法")
        expected_anchor, expected_events = _membership_expected_events(
            expected_frame,
            index_code=index_code,
            start=start,
            end=end,
        )
        if set(anchor_members) != expected_anchor:
            raise PublicDataError(f"{index_code}: anchor_members 与 expected_keys 不闭合")
        anchor_source = str(item.get("anchor_source_sha256", ""))
        if anchor_source not in authoritative_sha256s:
            raise PublicDataError(f"{index_code}: anchor_source_sha256 未绑定 authoritative 原文")
        referenced_hashes.add(anchor_source)
        if source_frames is not None:
            source_anchor, _ = _membership_expected_events(
                source_frames[anchor_source],
                index_code=index_code,
                start=start,
                end=end,
            )
            if not set(anchor_members).issubset(source_anchor):
                raise PublicDataError(f"{index_code}: anchor 事件不在所称原文中")
        active = set(anchor_members)
        previous_hash = _canonical_json_sha256(
            {
                "index_code": index_code,
                "anchor_date": start.isoformat(),
                "anchor_members": anchor_members,
                "source_sha256": anchor_source,
            }
        )
        adjustments = item.get("adjustments")
        if not isinstance(adjustments, list):
            raise PublicDataError(f"{index_code}: adjustments 必须是数组")
        observed_events: dict[date, tuple[set[str], set[str]]] = {}
        for expected_sequence, adjustment in enumerate(adjustments, start=1):
            if not isinstance(adjustment, Mapping):
                raise PublicDataError(f"{index_code}: adjustment 无效")
            allowed = {
                "sequence",
                "effective_date",
                "added",
                "removed",
                "source_sha256",
                "previous_receipt_sha256",
                "receipt_sha256",
            }
            _strict_keys(adjustment, allowed, label=f"{index_code}.adjustment")
            if adjustment.get("sequence") != expected_sequence:
                raise PublicDataError(f"{index_code}: adjustment sequence 断链")
            event_date = _parse_iso_date(
                adjustment.get("effective_date"), "receipt.adjustment.effective_date"
            )
            if not start < event_date <= end or event_date in observed_events:
                raise PublicDataError(f"{index_code}: adjustment 日期越界或重复")
            added = adjustment.get("added")
            removed = adjustment.get("removed")
            if (
                not isinstance(added, list)
                or not isinstance(removed, list)
                or added != sorted(set(map(str, added)))
                or removed != sorted(set(map(str, removed)))
                or set(added) & set(removed)
            ):
                raise PublicDataError(f"{index_code}: adjustment added/removed 不闭合")
            source_hash = str(adjustment.get("source_sha256", ""))
            if source_hash not in authoritative_sha256s:
                raise PublicDataError(f"{index_code}: adjustment 未绑定 authoritative 原文")
            if source_frames is not None:
                _, source_events = _membership_expected_events(
                    source_frames[source_hash],
                    index_code=index_code,
                    start=start,
                    end=end,
                )
                if source_events.get(event_date) != (set(added), set(removed)):
                    raise PublicDataError(f"{index_code}: adjustment 事件不在所称原文中")
            if adjustment.get("previous_receipt_sha256") != previous_hash:
                raise PublicDataError(f"{index_code}: adjustment previous_receipt_sha256 断链")
            receipt_payload = {key: adjustment[key] for key in sorted(allowed - {"receipt_sha256"})}
            observed_hash = _canonical_json_sha256(receipt_payload)
            if adjustment.get("receipt_sha256") != observed_hash:
                raise PublicDataError(f"{index_code}: adjustment receipt_sha256 漂移")
            if not set(removed).issubset(active) or set(added) & active:
                raise PublicDataError(f"{index_code}: adjustment 无法从前态应用")
            active.difference_update(removed)
            active.update(added)
            observed_events[event_date] = (set(added), set(removed))
            referenced_hashes.add(source_hash)
            previous_hash = observed_hash
        if observed_events != expected_events:
            raise PublicDataError(f"{index_code}: receipt 未覆盖 expected_keys 全部调样事件")
        final_hash = _canonical_json_sha256({"members": sorted(active)})
        if item.get("final_members_sha256") != final_hash:
            raise PublicDataError(f"{index_code}: final_members_sha256 不匹配")
    if referenced_hashes != authoritative_sha256s:
        raise PublicDataError("index_membership receipt 未闭合全部 authoritative 原文")


def _validate_cninfo_pagination_receipt(
    payload: Mapping[str, Any],
    expected_frame: Any,
    *,
    start: date,
    end: date,
    authoritative_sha256s: set[str],
    source_frames: Mapping[str, Any] | None = None,
    raw_source_frames: Mapping[str, Any] | None = None,
) -> bool:
    _strict_keys(
        payload,
        {
            "schema_version",
            "dataset",
            "coverage_start",
            "coverage_end",
            "status",
            "page_size",
            "total_records",
            "total_pages",
            "pages",
        },
        label="corporate_actions.completeness_receipt",
    )
    if (
        payload.get("schema_version") != CNINFO_PAGINATION_RECEIPT_SCHEMA
        or payload.get("dataset") != "corporate_actions"
        or payload.get("status") != "passed"
        or _parse_iso_date(payload.get("coverage_start"), "receipt.coverage_start") != start
        or _parse_iso_date(payload.get("coverage_end"), "receipt.coverage_end") != end
    ):
        raise PublicDataError("corporate_actions pagination receipt 顶层合同无效")
    page_size = payload.get("page_size")
    total_records = payload.get("total_records")
    total_pages = payload.get("total_pages")
    pages = payload.get("pages")
    if (
        not isinstance(page_size, int)
        or isinstance(page_size, bool)
        or page_size < 1
        or not isinstance(total_records, int)
        or isinstance(total_records, bool)
        or total_records != len(expected_frame)
        or not isinstance(total_pages, int)
        or isinstance(total_pages, bool)
        or total_pages < 1
        or not isinstance(pages, list)
        or len(pages) != total_pages
    ):
        raise PublicDataError("corporate_actions pagination 数量合同无效")
    expected_keys = {
        _key_tuple(row, DATASET_KEYS["corporate_actions"])
        for row in expected_frame.to_dict(orient="records")
    }
    observed_keys: set[tuple[str, ...]] = set()
    referenced_hashes: set[str] = set()
    official_totals_verified = source_frames is not None and raw_source_frames is not None
    for page_number, page in enumerate(pages, start=1):
        if not isinstance(page, Mapping):
            raise PublicDataError("corporate_actions pagination page 无效")
        _strict_keys(
            page,
            {"page_number", "row_count", "source_sha256", "keys_sha256"},
            label=f"corporate_actions.pages[{page_number}]",
        )
        row_count = page.get("row_count")
        if (
            page.get("page_number") != page_number
            or not isinstance(row_count, int)
            or isinstance(row_count, bool)
            or row_count < 1
            or (page_number < total_pages and row_count != page_size)
            or (page_number == total_pages and row_count > page_size)
        ):
            raise PublicDataError("corporate_actions pagination 缺页或页大小不闭合")
        source_hash = str(page.get("source_sha256", ""))
        if source_hash not in authoritative_sha256s:
            raise PublicDataError("corporate_actions page 未绑定 authoritative 原文")
        if source_hash in referenced_hashes:
            raise PublicDataError("corporate_actions pagination 同一页原文重复使用")
        if source_frames is None:
            page_keys = []
            official_totals_verified = False
        else:
            page_keys = sorted(
                {
                    _key_tuple(row, DATASET_KEYS["corporate_actions"])
                    for row in source_frames[source_hash].to_dict(orient="records")
                }
            )
        if len(page_keys) != row_count:
            raise PublicDataError("corporate_actions page row_count 与所称原文不匹配")
        if page.get("keys_sha256") != _canonical_json_sha256(
            {"keys": [list(key) for key in page_keys]}
        ):
            raise PublicDataError("corporate_actions pagination keys_sha256 漂移")
        if observed_keys & set(page_keys):
            raise PublicDataError("corporate_actions pagination 跨页键重复")
        observed_keys.update(page_keys)
        referenced_hashes.add(source_hash)
        raw_frame = raw_source_frames.get(source_hash) if raw_source_frames is not None else None
        bound_metadata = (
            raw_frame.attrs.get("pagination_metadata")
            if raw_frame is not None
            else None
        )
        if isinstance(bound_metadata, Mapping):
            if dict(bound_metadata) != {
                "total_records_path": total_records,
                "total_pages_path": total_pages,
                "page_number_path": page_number,
            }:
                raise PublicDataError("corporate_actions receipt 与官方 JSON 分页元数据不一致")
            continue
        required_meta = {
            "receipt_total_records",
            "receipt_total_pages",
            "receipt_page_number",
        }
        if raw_frame is None or not required_meta.issubset(raw_frame.columns):
            official_totals_verified = False
        else:
            values = {}
            for column in required_meta:
                unique = {
                    str(value).strip()
                    for value in raw_frame[column]
                    if str(value).strip()
                }
                if len(unique) != 1 or not next(iter(unique)).isdigit():
                    raise PublicDataError("corporate_actions 官方分页元数据不闭合")
                values[column] = int(next(iter(unique)))
            if values != {
                "receipt_total_records": total_records,
                "receipt_total_pages": total_pages,
                "receipt_page_number": page_number,
            }:
                raise PublicDataError("corporate_actions receipt 与官方分页元数据不一致")
    if observed_keys != expected_keys or referenced_hashes != authoritative_sha256s:
        raise PublicDataError("corporate_actions pagination 未闭合全部页或 authoritative 原文")
    return bool(official_totals_verified)


def _validate_completeness_receipt(
    dataset: str,
    config: Any,
    expected_frame: Any,
    authoritative: Sequence[tuple[Mapping[str, Any], Any]],
    *,
    training_root: Path,
    output: Path,
    start: date,
    end: date,
) -> dict[str, Any]:
    payload, path, receipt_sha256 = _receipt_file(
        config,
        training_root=training_root,
        output=output,
        label=f"datasets.{dataset}.completeness_receipt",
    )
    source_hashes = {str(contract["sha256"]) for contract, _ in authoritative}
    source_frames = {
        str(contract["sha256"]): frame for contract, frame in authoritative
    }
    raw_source_frames = {
        str(contract["sha256"]): contract.get("_source_frame")
        for contract, _ in authoritative
    }
    if dataset == "index_membership":
        _validate_csi_membership_receipt(
            payload,
            expected_frame,
            start=start,
            end=end,
            authoritative_sha256s=source_hashes,
            source_frames=source_frames,
        )
        schema = CSI_MEMBERSHIP_RECEIPT_SCHEMA
        formal_complete = True
    elif dataset == "corporate_actions":
        formal_complete = _validate_cninfo_pagination_receipt(
            payload,
            expected_frame,
            start=start,
            end=end,
            authoritative_sha256s=source_hashes,
            source_frames=source_frames,
            raw_source_frames=raw_source_frames,
        )
        schema = CNINFO_PAGINATION_RECEIPT_SCHEMA
    else:
        raise PublicDataError(f"{dataset}: 不支持 completeness_receipt")
    return {
        "schema_version": schema,
        "path": path,
        "sha256": receipt_sha256,
        "bytes": path.stat().st_size,
        "status": "passed",
        "formal_complete": formal_complete,
    }


def publish_normalized_pit_bundle(
    manifest_path: Path,
    output_directory: Path,
    training_root: Path,
) -> dict[str, Any]:
    """Publish reviewed raw responses as a canonical, hash-bound PIT bundle.

    The publisher never downloads, fills, votes, or guesses.  Equal-priority
    disagreements and TDX cross-check disagreements are removed from the
    normalized table; coverage can only be complete when a source-bound
    expected-key set proves that no requested key is missing.
    """

    import pandas as pd

    output = ensure_within(output_directory, training_root)
    if output == training_root.resolve():
        raise PublicDataError("PIT 发布目录不能等于 training_root")
    if output.exists():
        raise PublicDataError("目标 PIT version_root 已存在；请使用新版本目录")
    payload, normalization_sha256 = _normalization_manifest(manifest_path)
    normalization_schema = str(payload["schema_version"])
    if normalization_schema == NORMALIZATION_SCHEMA_V2:
        model_start = _parse_iso_date(payload["model_coverage_start"], "model_coverage_start")
        model_end = _parse_iso_date(payload["model_coverage_end"], "model_coverage_end")
        evidence_start = _parse_iso_date(
            payload["evidence_lookback_start"], "evidence_lookback_start"
        )
    else:
        model_start = _parse_iso_date(payload["coverage_start"], "coverage_start")
        model_end = _parse_iso_date(payload["coverage_end"], "coverage_end")
        evidence_start = model_start
    data_contract = _load_data_contract()
    staging: Path | None = _new_staging_directory(output, training_root)
    table_reports: dict[str, dict[str, Any]] = {}
    coverage_rows: list[dict[str, Any]] = []
    prepared: dict[str, dict[str, Any]] = {}
    try:
        for dataset in NORMALIZED_DATASETS:
            config = payload["datasets"][dataset]
            if not isinstance(config, dict):
                raise PublicDataError(f"datasets.{dataset} 必须是 object")
            allowed_config = {"sources", "expected_keys"}
            if normalization_schema == NORMALIZATION_SCHEMA_V2:
                allowed_config |= {"coverage_key_contract", "completeness_receipt"}
            _strict_keys(config, allowed_config, label=f"datasets.{dataset}")
            coverage_key_contract = (
                str(config.get("coverage_key_contract", ""))
                if normalization_schema == NORMALIZATION_SCHEMA_V2
                else "source_bound"
            )
            if normalization_schema == NORMALIZATION_SCHEMA_V2:
                expected_contract_type = V2_COVERAGE_KEY_CONTRACTS[dataset]
                if coverage_key_contract != expected_contract_type:
                    raise PublicDataError(
                        f"datasets.{dataset}.coverage_key_contract 固定为 "
                        f"{expected_contract_type!r}"
                    )
            configured_sources = config.get("sources")
            if not isinstance(configured_sources, list) or not configured_sources:
                raise PublicDataError(f"datasets.{dataset}.sources 必须是非空数组")
            contracts: list[dict[str, Any]] = []
            ids: set[str] = set()
            for index, source in enumerate(configured_sources):
                contract = _source_contract(
                    source,
                    training_root=training_root,
                    output=output,
                    label=f"datasets.{dataset}.sources[{index}]",
                    normalization_schema=normalization_schema,
                    dataset=dataset,
                )
                if contract["source_id"] in ids:
                    raise PublicDataError(f"{dataset}: source_id 重复：{contract['source_id']}")
                ids.add(contract["source_id"])
                contracts.append(contract)
            if dataset == TRADING_CALENDAR_DATASET:
                for index, contract in enumerate(contracts):
                    if contract["role"] != "authoritative":
                        raise PublicDataError(
                            "trading_calendar 只允许带固定工件身份的官方 authoritative 源"
                        )
                    _calendar_artifact_metadata(
                        contract,
                        label=f"datasets.{dataset}.sources[{index}]",
                        required=True,
                    )
            else:
                for index, contract in enumerate(contracts):
                    if contract.get("artifact_role") is None:
                        continue
                    allowed_artifact = SOURCE_BOUND_ARTIFACTS.get(dataset)
                    if (
                        normalization_schema != NORMALIZATION_SCHEMA_V2
                        or allowed_artifact is None
                    ):
                        raise PublicDataError(f"{dataset}: 不允许此证据工件元数据")
                    _evidence_artifact_metadata(
                        contract,
                        label=f"datasets.{dataset}.sources[{index}]",
                        required_role=allowed_artifact[0],
                    )

            expected_config = config.get("expected_keys")
            if normalization_schema == NORMALIZATION_SCHEMA_V2:
                if coverage_key_contract == "source_bound" and expected_config is None:
                    raise PublicDataError(f"datasets.{dataset}.expected_keys 不得为空")
                if coverage_key_contract == "derived" and expected_config is not None:
                    raise PublicDataError(
                        f"datasets.{dataset}.expected_keys 在 derived 合同下必须为 null"
                    )
                if dataset in {"index_membership", "corporate_actions"}:
                    if not isinstance(config.get("completeness_receipt"), Mapping):
                        raise PublicDataError(
                            f"datasets.{dataset}.completeness_receipt 缺失"
                        )
                elif config.get("completeness_receipt") is not None:
                    raise PublicDataError(
                        f"datasets.{dataset} 不允许 completeness_receipt"
                    )
            expected_contract: dict[str, Any] | None = None
            expected_frame = None
            if expected_config is not None:
                expected_contract = _source_contract(
                    expected_config,
                    training_root=training_root,
                    output=output,
                    label=f"datasets.{dataset}.expected_keys",
                    expected_role="expected_keys",
                    normalization_schema=normalization_schema,
                    dataset=dataset,
                )
                if normalization_schema == NORMALIZATION_SCHEMA_V2:
                    required_artifact = SOURCE_BOUND_ARTIFACTS[dataset]
                    _evidence_artifact_metadata(
                        expected_contract,
                        label=f"datasets.{dataset}.expected_keys",
                        required_role=required_artifact[0],
                    )
                elif dataset == TRADING_CALENDAR_DATASET:
                    _calendar_artifact_metadata(
                        expected_contract,
                        label=f"datasets.{dataset}.expected_keys",
                        required=True,
                    )
                elif expected_contract.get("artifact_role") is not None:
                    raise PublicDataError(f"{dataset}: 不允许证据工件元数据")
                expected_frame = _read_mapped_source(
                    expected_contract, dataset=dataset, keys_only=True
                )

            authoritative: list[tuple[Mapping[str, Any], Any]] = []
            mechanical: list[tuple[Mapping[str, Any], Any]] = []
            for contract in contracts:
                keys_only = contract["role"] == "mechanical_cross_check"
                frame = _read_mapped_source(contract, dataset=dataset, keys_only=keys_only)
                if keys_only:
                    if set(contract["mapping"]) | set(contract["constants"]) <= set(
                        DATASET_KEYS[dataset]
                    ):
                        raise PublicDataError(f"{dataset}/{contract['source_id']} 机械核验缺少值列")
                    mechanical.append((contract, frame))
                else:
                    authoritative.append((contract, frame))
            if not authoritative:
                raise PublicDataError(f"{dataset}: 缺少 official/public 规范表供值源")
            merged, equal_priority_conflicts, lower_disagreements = (
                _merge_authoritative_sources(dataset, authoritative)
            )
            merged, mechanical_conflicts = _apply_mechanical_cross_checks(
                dataset, merged, mechanical
            )
            completeness_receipt = None
            if (
                normalization_schema == NORMALIZATION_SCHEMA_V2
                and dataset in {"index_membership", "corporate_actions"}
            ):
                completeness_receipt = _validate_completeness_receipt(
                    dataset,
                    config.get("completeness_receipt"),
                    merged,
                    authoritative,
                    training_root=training_root,
                    output=output,
                    start=model_start,
                    end=model_end,
                )
            prepared[dataset] = {
                "config": config,
                "coverage_key_contract": coverage_key_contract,
                "contracts": contracts,
                "expected_contract": expected_contract,
                "expected_frame": expected_frame,
                "authoritative": authoritative,
                "merged": data_contract.validate_pit_table(dataset, merged),
                "equal_priority_conflicts": equal_priority_conflicts,
                "mechanical_conflicts": mechanical_conflicts,
                "lower_disagreements": lower_disagreements,
                "completeness_receipt": completeness_receipt,
            }

        frames = {dataset: item["merged"] for dataset, item in prepared.items()}
        if normalization_schema == NORMALIZATION_SCHEMA_V2:
            earlier_open_dates = sorted(
                row.trade_date.date()
                for row in frames[TRADING_CALENDAR_DATASET].itertuples(index=False)
                if bool(row.is_open) and row.trade_date.date() < model_start
            )
            if not earlier_open_dates or earlier_open_dates[-1] != evidence_start:
                raise PublicDataError(
                    "evidence_lookback_start 必须等于官方日历中 model_coverage_start 的前一开放交易日"
                )

        for dataset in NORMALIZED_DATASETS:
            item = prepared[dataset]
            merged = item["merged"]
            selected_keys = {
                _key_tuple(row, DATASET_KEYS[dataset])
                for row in merged.to_dict(orient="records")
            }
            derived_complete = True
            derived_issues: list[str] = []
            if item["coverage_key_contract"] == "derived":
                expected_keys, derived_complete, derived_issues = _derive_key_contract(
                    dataset,
                    frames,
                    start=model_start,
                    end=model_end,
                )
            else:
                expected_frame = item["expected_frame"]
                expected_keys = (
                    {
                        _key_tuple(row, DATASET_KEYS[dataset])
                        for row in expected_frame.to_dict(orient="records")
                    }
                    if expected_frame is not None
                    else set()
                )
            missing_expected = expected_keys - selected_keys
            outside_key_space: set[tuple[str, ...]] = set()
            if normalization_schema == NORMALIZATION_SCHEMA_V2:
                outside_key_space = selected_keys - expected_keys
                if outside_key_space:
                    merged = merged[
                        ~merged.apply(
                            lambda row: _key_tuple(row, DATASET_KEYS[dataset])
                            in outside_key_space,
                            axis=1,
                        )
                    ].reset_index(drop=True)
                    if merged.empty:
                        raise PublicDataError(f"{dataset}: 固定 coverage key space 过滤后为空")
                    merged = data_contract.validate_pit_table(dataset, merged)
                    frames[dataset] = merged
            exclusion_rows = [
                {**dict(zip(DATASET_KEYS[dataset], key)), "reason": reason}
                for reason, keys in (
                    ("equal_priority_conflict", item["equal_priority_conflicts"]),
                    ("tdx_mechanical_conflict", item["mechanical_conflicts"]),
                    ("missing_expected_key", missing_expected),
                    ("outside_fixed_key_space", outside_key_space),
                )
                for key in sorted(keys)
            ]
            exclusions = pd.DataFrame(
                exclusion_rows, columns=[*DATASET_KEYS[dataset], "reason"]
            )
            exclusion_relative = Path("exclusions") / f"{dataset}.csv"
            exclusion_path = ensure_within(staging / exclusion_relative, training_root)
            _write_normalized_csv(exclusion_path, exclusions, training_root)
            exclusion_sha256 = sha256_file(exclusion_path)
            required_start = (
                evidence_start
                if normalization_schema == NORMALIZATION_SCHEMA_V2
                and dataset in {"price_limits", TRADING_CALENDAR_DATASET}
                else model_start
            )
            authoritative_intervals = [
                (contract["valid_from"], contract["valid_to"])
                for contract, _ in item["authoritative"]
            ]
            source_period_complete = _intervals_cover(
                authoritative_intervals, required_start, model_end
            )
            expected_evidence_present = (
                item["expected_contract"] is not None
                if item["coverage_key_contract"] == "source_bound"
                else derived_complete
            )
            is_complete = bool(
                expected_evidence_present
                and source_period_complete
                and not missing_expected
                and not item["equal_priority_conflicts"]
                and not item["mechanical_conflicts"]
                and (
                    item.get("completeness_receipt") is None
                    or item["completeness_receipt"].get("formal_complete") is True
                )
            )

            table_path = ensure_within(staging / f"{dataset}.csv", training_root)
            _write_normalized_csv(table_path, merged, training_root)
            copied_sources: list[dict[str, Any]] = []
            cross_checks: list[dict[str, Any]] = []
            copy_contracts = [*item["contracts"]]
            if item["expected_contract"] is not None:
                copy_contracts.append(item["expected_contract"])
            copied_by_id: dict[str, tuple[str, ...]] = {}
            for contract in copy_contracts:
                extraction_hash = str(contract.get("extracted_sha256", ""))
                identity = (
                    contract["sha256"],
                    contract["source_class"],
                    extraction_hash,
                    str(contract.get("_row_audit_report", {}).get("sha256", "")),
                )
                previous = copied_by_id.get(contract["source_id"])
                if previous is not None:
                    if previous != identity:
                        raise PublicDataError(
                            f"{dataset}: source_id {contract['source_id']} 绑定多个原始/抽取文件"
                        )
                    continue
                copied_by_id[contract["source_id"]] = identity
                suffix = contract["raw_path"].suffix or ".bin"
                relative_raw = Path("raw") / dataset / f"{contract['source_id']}{suffix}"
                copied_path = ensure_within(staging / relative_raw, training_root)
                atomic_write(copied_path, contract["raw_path"].read_bytes())
                if sha256_file(copied_path) != contract["sha256"]:
                    raise PublicDataError(
                        f"{dataset}/{contract['source_id']} 原始响应复制后 SHA256 漂移"
                    )
                record: dict[str, Any] = {
                    "source_id": contract["source_id"],
                    "source_class": contract["source_class"],
                    "retrieved_at": contract["retrieved_at"],
                    "valid_from": contract["valid_from"].isoformat(),
                    "valid_to": contract["valid_to"].isoformat(),
                    "path": relative_raw.as_posix(),
                    "sha256": contract["sha256"],
                    "bytes": contract["bytes"],
                    "role": contract["role"],
                }
                for field in ("artifact_role", "artifact_schema_version"):
                    if contract.get(field) is not None:
                        record[field] = contract[field]
                if normalization_schema == NORMALIZATION_SCHEMA_V2:
                    extracted_relative = (
                        Path("extracted") / dataset / f"{contract['source_id']}.csv"
                    )
                    extracted_path = ensure_within(
                        staging / extracted_relative, training_root
                    )
                    atomic_write(extracted_path, contract["_extracted_bytes"])
                    extraction = {
                        **contract["_extraction_report"],
                        "source_format": contract["source_format"],
                        "path": extracted_relative.as_posix(),
                        "sha256": sha256_file(extracted_path),
                    }
                    canonical_relative = (
                        Path("canonical_sources")
                        / dataset
                        / f"{contract['source_id']}.csv"
                    )
                    canonical_path = ensure_within(
                        staging / canonical_relative, training_root
                    )
                    atomic_write(canonical_path, contract["_canonical_source_bytes"])
                    extraction["canonical_source_path"] = canonical_relative.as_posix()
                    record["extraction"] = extraction
                    row_audit_report = contract["_row_audit_report"]
                    row_audit_relative = (
                        Path("row_audits") / dataset / f"{contract['source_id']}.csv"
                    )
                    row_audit_path = ensure_within(
                        staging / row_audit_relative, training_root
                    )
                    atomic_write(
                        row_audit_path,
                        Path(row_audit_report["path"]).read_bytes(),
                    )
                    record["row_audit"] = {
                        **{
                            key: value
                            for key, value in row_audit_report.items()
                            if key != "path"
                        },
                        "path": row_audit_relative.as_posix(),
                    }
                    overlay_report = contract.get("_overlay_report")
                    if overlay_report is not None:
                        overlay_relative = (
                            Path("overlays") / dataset / f"{contract['source_id']}.csv"
                        )
                        overlay_path = ensure_within(
                            staging / overlay_relative, training_root
                        )
                        atomic_write(overlay_path, overlay_report["path"].read_bytes())
                        record["reviewed_overlay"] = {
                            **{
                                key: value
                                for key, value in overlay_report.items()
                                if key != "path"
                            },
                            "path": overlay_relative.as_posix(),
                        }
                if contract["source_class"] == "tdx_mechanical":
                    cross_checks.append(record)
                else:
                    copied_sources.append({**record, "url": contract["url"]})
            copied_sources.sort(key=lambda value: (value["source_id"], value["role"]))
            cross_checks.sort(key=lambda value: value["source_id"])
            observed_start = max(
                required_start,
                min(contract["valid_from"] for contract, _ in item["authoritative"]),
            )
            observed_end = min(
                model_end,
                max(contract["valid_to"] for contract, _ in item["authoritative"]),
            )
            if observed_end < observed_start:
                raise PublicDataError(f"{dataset}: 实际来源与请求 coverage 无交集")
            declared_start = required_start if is_complete else observed_start
            declared_end = model_end if is_complete else observed_end
            published_receipt = None
            receipt_report = item.get("completeness_receipt")
            if receipt_report is not None:
                receipt_relative = Path("receipts") / f"{dataset}.json"
                receipt_path = ensure_within(staging / receipt_relative, training_root)
                atomic_write(receipt_path, Path(receipt_report["path"]).read_bytes())
                if sha256_file(receipt_path) != receipt_report["sha256"]:
                    raise PublicDataError(f"{dataset}: completeness receipt 复制后漂移")
                published_receipt = {
                    **{
                        key: value
                        for key, value in receipt_report.items()
                        if key != "path"
                    },
                    "path": receipt_relative.as_posix(),
                }
            normalization_record: dict[str, Any] = {
                "schema_version": normalization_schema,
                "manifest_sha256": normalization_sha256,
                "source_priority": list(SOURCE_PRIORITY),
                "coverage_key_contract": item["coverage_key_contract"],
                "equal_priority_conflict_keys_excluded": len(
                    item["equal_priority_conflicts"]
                ),
                "mechanical_conflict_keys_excluded": len(item["mechanical_conflicts"]),
                "lower_priority_disagreements": item["lower_disagreements"],
                "expected_key_count": len(expected_keys),
                "missing_expected_key_count": len(missing_expected),
                "outside_fixed_key_space_count": len(outside_key_space),
                "derived_contract_issues": derived_issues,
                "exclusion_report": exclusion_relative.as_posix(),
                "exclusion_report_sha256": exclusion_sha256,
            }
            if published_receipt is not None:
                normalization_record["completeness_receipt"] = published_receipt
            if normalization_schema == NORMALIZATION_SCHEMA_V2:
                normalization_record.update(
                    {
                        "model_coverage_start": model_start.isoformat(),
                        "model_coverage_end": model_end.isoformat(),
                        "evidence_lookback_start": evidence_start.isoformat(),
                    }
                )
            provenance = {
                "schema_version": data_contract.PIT_PROVENANCE_SCHEMA,
                "dataset": dataset,
                "coverage_start": declared_start.isoformat(),
                "coverage_end": declared_end.isoformat(),
                "sources": copied_sources,
                "cross_checks": cross_checks,
                "normalization": normalization_record,
            }
            provenance_relative = Path("provenance") / f"{dataset}.json"
            provenance_path = ensure_within(staging / provenance_relative, training_root)
            atomic_write(
                provenance_path,
                (json.dumps(provenance, ensure_ascii=False, indent=2) + "\n").encode(
                    "utf-8"
                ),
            )
            file_hash = sha256_file(table_path)
            schema_hash = data_contract.pit_table_schema_sha256(dataset, merged)
            provenance_hash = sha256_file(provenance_path)
            coverage_rows.append(
                {
                    "dataset": dataset,
                    "coverage_start": declared_start.isoformat(),
                    "coverage_end": declared_end.isoformat(),
                    "is_complete": is_complete,
                    "binding_schema": (
                        data_contract.PIT_COVERAGE_BINDING_SCHEMA if is_complete else ""
                    ),
                    "file_sha256": file_hash if is_complete else "",
                    "schema_sha256": schema_hash if is_complete else "",
                    "row_count": len(merged) if is_complete else "",
                    "file_bytes": table_path.stat().st_size if is_complete else "",
                    "source_manifest": provenance_relative.as_posix() if is_complete else "",
                    "source_manifest_sha256": provenance_hash if is_complete else "",
                }
            )
            table_reports[dataset] = {
                "rows": len(merged),
                "sha256": file_hash,
                "schema_sha256": schema_hash,
                "is_complete": is_complete,
                "coverage_key_contract": item["coverage_key_contract"],
                "source_count": len(item["authoritative"]),
                "expected_key_count": len(expected_keys),
                "missing_expected_key_count": len(missing_expected),
                "outside_fixed_key_space_count": len(outside_key_space),
                "derived_contract_issues": derived_issues,
                "equal_priority_conflict_keys_excluded": len(
                    item["equal_priority_conflicts"]
                ),
                "mechanical_conflict_keys_excluded": len(item["mechanical_conflicts"]),
                "lower_priority_disagreements": item["lower_disagreements"],
                "exclusion_count": len(exclusions),
                "exclusion_report": exclusion_relative.as_posix(),
                "exclusion_report_sha256": exclusion_sha256,
            }

        coverage = data_contract.validate_pit_table("coverage", pd.DataFrame(coverage_rows))
        _write_normalized_csv(staging / "coverage.csv", coverage, training_root)
        validation = data_contract.validate_pit_bundle(
            staging,
            coverage_start=model_start,
            coverage_end=model_end,
            allow_unpublished_staging=True,
        )
        if validation.missing_tables or validation.errors:
            raise PublicDataError(
                "规范 PIT bundle 未通过结构/哈希合同："
                + "; ".join([*validation.missing_tables, *validation.errors])
            )
        formal_release_allowed = normalization_schema == NORMALIZATION_SCHEMA_V2
        staging_candidate_ready = bool(
            validation.table_reports.get("normalization_release_contract", {}).get(
                "staging_candidate_ready"
            )
        )
        status = (
            "production_ready"
            if formal_release_allowed and staging_candidate_ready
            else "local_provisional"
        )
        publication_validation = validation.to_report()
        publication_validation["production_ready"] = status == "production_ready"
        artifact_inventory = [
            {
                "path": artifact.relative_to(staging).as_posix(),
                "bytes": artifact.stat().st_size,
                "sha256": sha256_file(artifact),
            }
            for artifact in sorted(
                (path for path in staging.rglob("*") if path.is_file()),
                key=lambda path: path.relative_to(staging).as_posix(),
            )
        ]
        publication: dict[str, Any] = {
            "schema_version": (
                PUBLICATION_SCHEMA_V2
                if normalization_schema == NORMALIZATION_SCHEMA_V2
                else PUBLICATION_SCHEMA_V1
            ),
            "status": status,
            "formal_release_allowed": formal_release_allowed,
            "normalization_schema_version": normalization_schema,
            "normalization_manifest": str(manifest_path.resolve()),
            "normalization_manifest_sha256": normalization_sha256,
            "source_priority": list(SOURCE_PRIORITY),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tables": table_reports,
            "artifact_inventory": artifact_inventory,
            "pit_validation": publication_validation,
        }
        if normalization_schema == NORMALIZATION_SCHEMA_V2:
            publication.update(
                {
                    "model_coverage_start": model_start.isoformat(),
                    "model_coverage_end": model_end.isoformat(),
                    "evidence_lookback_start": evidence_start.isoformat(),
                }
            )
        else:
            publication.update(
                {
                    "coverage_start": model_start.isoformat(),
                    "coverage_end": model_end.isoformat(),
                    "release_cap_reason": "normalization_v1_local_provisional_only",
                }
            )
        publication_path = ensure_within(
            staging / "publication_manifest.json", training_root
        )
        atomic_write(
            publication_path,
            (json.dumps(publication, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        publication_sha256 = sha256_file(publication_path)
        atomic_write(
            ensure_within(staging / "publication_manifest.sha256", training_root),
            f"{publication_sha256}  publication_manifest.json\n".encode("ascii"),
        )
        final_validation = data_contract.validate_pit_bundle(
            staging,
            coverage_start=model_start,
            coverage_end=model_end,
        )
        if status == "production_ready" and not final_validation.production_ready:
            raise PublicDataError(
                "PIT publication 写入后未通过正式准出复验："
                + "; ".join(
                    [
                        *final_validation.missing_tables,
                        *final_validation.errors,
                        *final_validation.warnings,
                    ]
                )
            )
        if status != "production_ready" and final_validation.production_ready:
            raise PublicDataError("local_provisional publication 不得复验为 production_ready")
        _promote_directory(staging, output, training_root)
        staging = None
        return {**publication, "publication_manifest_sha256": publication_sha256}
    finally:
        _cleanup_staging(staging)

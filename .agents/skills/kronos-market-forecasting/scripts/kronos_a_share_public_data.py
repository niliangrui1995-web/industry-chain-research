#!/usr/bin/env python3
"""Snapshot explicit public PIT sources without weakening their evidence boundary."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from uuid import uuid4


SOURCE_SCHEMA = "kronos-public-pit-sources-v1"
BAOSTOCK_SCHEMA = "kronos-baostock-trade-status-v1"
NORMALIZATION_SCHEMA = "kronos-a-share-pit-normalization-v1"
PUBLICATION_SCHEMA = "kronos-a-share-pit-publication-v1"
TRADING_CALENDAR_DATASET = "trading_calendar"
TRADING_CALENDAR_ARTIFACT_ROLE = "trading_calendar"
TRADING_CALENDAR_ARTIFACT_SCHEMA = "kronos-a-share-trading-calendar-v1"
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


def _normalize_allowed_domains(item: dict[str, Any], request_host: str) -> tuple[str, ...]:
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
    allowed_domains = _normalize_allowed_domains(item, request_host)
    if not _host_is_allowed(request_host, allowed_domains):
        raise PublicDataError("原始 URL 域名不在 allowed_domains 中")
    expected_hash = item.get("sha256")
    if expected_hash is not None and not SHA256_PATTERN.fullmatch(str(expected_hash)):
        raise PublicDataError("公开源 sha256 必须为64位十六进制")
    _calendar_artifact_metadata(item, label=f"sources.{item['source_id']}")
    return allowed_domains


def _calendar_artifact_metadata(
    source: Mapping[str, Any],
    *,
    label: str,
    required: bool = False,
) -> dict[str, str]:
    artifact_role = source.get("artifact_role")
    artifact_schema = source.get("artifact_schema_version")
    if artifact_role is None and artifact_schema is None and not required:
        return {}
    if (
        artifact_role != TRADING_CALENDAR_ARTIFACT_ROLE
        or artifact_schema != TRADING_CALENDAR_ARTIFACT_SCHEMA
    ):
        raise PublicDataError(
            f"{label} 日历工件必须固定为 artifact_role="
            f"{TRADING_CALENDAR_ARTIFACT_ROLE!r}, artifact_schema_version="
            f"{TRADING_CALENDAR_ARTIFACT_SCHEMA!r}"
        )
    if source.get("source_class") != "official_primary":
        raise PublicDataError(f"{label} trading_calendar 必须为 official_primary")
    return {
        "artifact_role": TRADING_CALENDAR_ARTIFACT_ROLE,
        "artifact_schema_version": TRADING_CALENDAR_ARTIFACT_SCHEMA,
    }


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
    if payload.get("schema_version") != NORMALIZATION_SCHEMA:
        raise PublicDataError(f"schema_version 必须为 {NORMALIZATION_SCHEMA}")
    if payload.get("source_priority") != list(SOURCE_PRIORITY):
        raise PublicDataError(
            "source_priority 必须固定为 official_primary > "
            "public_secondary > tdx_mechanical"
        )
    lower = _parse_iso_date(payload.get("coverage_start"), "coverage_start")
    upper = _parse_iso_date(payload.get("coverage_end"), "coverage_end")
    if lower > upper:
        raise PublicDataError("coverage_start 不得晚于 coverage_end")
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
    configured_artifact = _calendar_artifact_metadata(source, label=label)
    recorded_artifact = _calendar_artifact_metadata(record, label=f"{label}.snapshot_record")
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
    _https_host(url)
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


def _source_contract(
    source: Any,
    *,
    training_root: Path,
    output: Path,
    label: str,
    expected_role: str | None = None,
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
    if source.get("format") != "csv":
        raise PublicDataError(f"{label}.format 当前只允许显式 csv")
    encoding = str(source.get("encoding", "utf-8-sig"))
    if encoding.lower().replace("_", "-") not in {"utf-8", "utf-8-sig", "gb18030"}:
        raise PublicDataError(f"{label}.encoding 不在允许列表")
    delimiter = str(source.get("delimiter", ","))
    if len(delimiter) != 1 or delimiter in {"\r", "\n", "\0"}:
        raise PublicDataError(f"{label}.delimiter 必须是单个可见分隔符")
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
            source, training_root=training_root, output=output, label=label
        )
    return {
        **resolved,
        "role": role,
        "format": "csv",
        "encoding": encoding,
        "delimiter": delimiter,
        "mapping": mapping,
        "constants": constants,
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
    coverage_start = _parse_iso_date(payload["coverage_start"], "coverage_start")
    coverage_end = _parse_iso_date(payload["coverage_end"], "coverage_end")
    data_contract = _load_data_contract()
    staging: Path | None = _new_staging_directory(output, training_root)
    table_reports: dict[str, dict[str, Any]] = {}
    coverage_rows: list[dict[str, Any]] = []
    try:
        for dataset in NORMALIZED_DATASETS:
            config = payload["datasets"][dataset]
            if not isinstance(config, dict):
                raise PublicDataError(f"datasets.{dataset} 必须是 object")
            _strict_keys(config, {"sources", "expected_keys"}, label=f"datasets.{dataset}")
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
            elif any(
                contract.get("artifact_role") is not None
                or contract.get("artifact_schema_version") is not None
                for contract in contracts
            ):
                raise PublicDataError(
                    f"{dataset}: trading_calendar 工件元数据不得用于其他数据集"
                )
            expected_config = config.get("expected_keys")
            expected_contract: dict[str, Any] | None = None
            expected_frame = None
            if expected_config is not None:
                expected_contract = _source_contract(
                    expected_config,
                    training_root=training_root,
                    output=output,
                    label=f"datasets.{dataset}.expected_keys",
                    expected_role="expected_keys",
                )
                if dataset == TRADING_CALENDAR_DATASET:
                    _calendar_artifact_metadata(
                        expected_contract,
                        label=f"datasets.{dataset}.expected_keys",
                        required=True,
                    )
                elif (
                    expected_contract.get("artifact_role") is not None
                    or expected_contract.get("artifact_schema_version") is not None
                ):
                    raise PublicDataError(
                        f"{dataset}: trading_calendar 工件元数据不得用于其他数据集"
                    )
                expected_frame = _read_mapped_source(
                    expected_contract, dataset=dataset, keys_only=True
                )

            authoritative: list[tuple[Mapping[str, Any], Any]] = []
            mechanical: list[tuple[Mapping[str, Any], Any]] = []
            for contract in contracts:
                keys_only = contract["role"] == "mechanical_cross_check"
                frame = _read_mapped_source(contract, dataset=dataset, keys_only=keys_only)
                if keys_only:
                    # A cross-check containing only keys cannot verify a value and is rejected.
                    if set(contract["mapping"]) | set(contract["constants"]) <= set(DATASET_KEYS[dataset]):
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
            merged = data_contract.validate_pit_table(dataset, merged)
            selected_keys = {
                _key_tuple(row, DATASET_KEYS[dataset])
                for row in merged.to_dict(orient="records")
            }
            expected_keys = (
                {
                    _key_tuple(row, DATASET_KEYS[dataset])
                    for row in expected_frame.to_dict(orient="records")
                }
                if expected_frame is not None
                else set()
            )
            missing_expected = expected_keys - selected_keys
            exclusion_rows = [
                {**dict(zip(DATASET_KEYS[dataset], key)), "reason": reason}
                for reason, keys in (
                    ("equal_priority_conflict", equal_priority_conflicts),
                    ("tdx_mechanical_conflict", mechanical_conflicts),
                    ("missing_expected_key", missing_expected),
                )
                for key in sorted(keys)
            ]
            exclusions = pd.DataFrame(
                exclusion_rows,
                columns=[*DATASET_KEYS[dataset], "reason"],
            )
            exclusion_relative = Path("exclusions") / f"{dataset}.csv"
            exclusion_path = ensure_within(staging / exclusion_relative, training_root)
            _write_normalized_csv(exclusion_path, exclusions, training_root)
            exclusion_sha256 = sha256_file(exclusion_path)
            authoritative_intervals = [
                (contract["valid_from"], contract["valid_to"])
                for contract, _ in authoritative
            ]
            source_period_complete = _intervals_cover(
                authoritative_intervals, coverage_start, coverage_end
            )
            is_complete = bool(
                expected_contract is not None
                and source_period_complete
                and not missing_expected
                and not equal_priority_conflicts
                and not mechanical_conflicts
            )

            table_path = ensure_within(staging / f"{dataset}.csv", training_root)
            _write_normalized_csv(table_path, merged, training_root)
            copied_sources: list[dict[str, Any]] = []
            cross_checks: list[dict[str, Any]] = []
            copy_contracts = [*contracts]
            if expected_contract is not None:
                copy_contracts.append(expected_contract)
            copied_by_id: dict[str, tuple[str, str]] = {}
            for contract in copy_contracts:
                previous = copied_by_id.get(contract["source_id"])
                identity = (contract["sha256"], contract["source_class"])
                if previous is not None:
                    if previous != identity:
                        raise PublicDataError(
                            f"{dataset}: source_id {contract['source_id']} 绑定多个原始文件"
                        )
                    continue
                copied_by_id[contract["source_id"]] = identity
                suffix = contract["raw_path"].suffix or ".bin"
                relative_raw = Path("raw") / dataset / f"{contract['source_id']}{suffix}"
                copied_path = ensure_within(staging / relative_raw, training_root)
                atomic_write(copied_path, contract["raw_path"].read_bytes())
                if sha256_file(copied_path) != contract["sha256"]:
                    raise PublicDataError(f"{dataset}/{contract['source_id']} 原始响应复制后 SHA256 漂移")
                record = {
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
                if contract["source_class"] == "tdx_mechanical":
                    cross_checks.append(record)
                else:
                    copied_sources.append({**record, "url": contract["url"]})
            copied_sources.sort(key=lambda item: (item["source_id"], item["role"]))
            cross_checks.sort(key=lambda item: item["source_id"])
            observed_start = max(
                coverage_start, min(contract["valid_from"] for contract, _ in authoritative)
            )
            observed_end = min(
                coverage_end, max(contract["valid_to"] for contract, _ in authoritative)
            )
            if observed_end < observed_start:
                raise PublicDataError(f"{dataset}: 实际来源与请求 coverage 无交集")
            declared_start = coverage_start if is_complete else observed_start
            declared_end = coverage_end if is_complete else observed_end
            provenance = {
                "schema_version": data_contract.PIT_PROVENANCE_SCHEMA,
                "dataset": dataset,
                "coverage_start": declared_start.isoformat(),
                "coverage_end": declared_end.isoformat(),
                "sources": copied_sources,
                "cross_checks": cross_checks,
                "normalization": {
                    "schema_version": NORMALIZATION_SCHEMA,
                    "manifest_sha256": normalization_sha256,
                    "source_priority": list(SOURCE_PRIORITY),
                    "equal_priority_conflict_keys_excluded": len(equal_priority_conflicts),
                    "mechanical_conflict_keys_excluded": len(mechanical_conflicts),
                    "lower_priority_disagreements": lower_disagreements,
                    "expected_key_count": len(expected_keys),
                    "missing_expected_key_count": len(missing_expected),
                    "exclusion_report": exclusion_relative.as_posix(),
                    "exclusion_report_sha256": exclusion_sha256,
                },
            }
            provenance_relative = Path("provenance") / f"{dataset}.json"
            provenance_path = ensure_within(staging / provenance_relative, training_root)
            atomic_write(
                provenance_path,
                (json.dumps(provenance, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
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
                "source_count": len(authoritative),
                "expected_key_count": len(expected_keys),
                "missing_expected_key_count": len(missing_expected),
                "equal_priority_conflict_keys_excluded": len(equal_priority_conflicts),
                "mechanical_conflict_keys_excluded": len(mechanical_conflicts),
                "lower_priority_disagreements": lower_disagreements,
                "exclusion_count": len(exclusions),
                "exclusion_report": exclusion_relative.as_posix(),
                "exclusion_report_sha256": exclusion_sha256,
            }

        coverage = data_contract.validate_pit_table(
            "coverage", pd.DataFrame(coverage_rows)
        )
        _write_normalized_csv(staging / "coverage.csv", coverage, training_root)
        validation = data_contract.validate_pit_bundle(
            staging, coverage_start=coverage_start, coverage_end=coverage_end
        )
        if validation.missing_tables or validation.errors:
            raise PublicDataError(
                "规范 PIT bundle 未通过结构/哈希合同："
                + "; ".join([*validation.missing_tables, *validation.errors])
            )
        status = "production_ready" if validation.production_ready else "local_provisional"
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
        publication = {
            "schema_version": PUBLICATION_SCHEMA,
            "status": status,
            "normalization_manifest": str(manifest_path.resolve()),
            "normalization_manifest_sha256": normalization_sha256,
            "coverage_start": coverage_start.isoformat(),
            "coverage_end": coverage_end.isoformat(),
            "source_priority": list(SOURCE_PRIORITY),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tables": table_reports,
            "artifact_inventory": artifact_inventory,
            "pit_validation": validation.to_report(),
        }
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
        _promote_directory(staging, output, training_root)
        staging = None
        return {**publication, "publication_manifest_sha256": publication_sha256}
    finally:
        _cleanup_staging(staging)

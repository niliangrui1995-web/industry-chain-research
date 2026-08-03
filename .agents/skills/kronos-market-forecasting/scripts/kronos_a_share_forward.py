#!/usr/bin/env python3
"""Immutable forward-observation ledger for explicit Kronos A-share scoring runs."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit

import pandas as pd

from kronos_a_share_data import verify_inference_snapshot
from kronos_a_share_runtime import atomic_write_json, resolve_under, sha256_file
from kronos_a_share_training import CheckpointFileLock


FORWARD_BATCH_SCHEMA = "kronos-a-share-forward-batch-v4"
FORWARD_SUMMARY_SCHEMA = "kronos-a-share-forward-summary-v2"
FORWARD_REGISTRY_ROOT_SCHEMA = "kronos-a-share-forward-registry-root-v1"
RELEASE_RECEIPT_BINDING_SCHEMA = "kronos-a-share-gate-receipt-binding-v2"
GATE_RECEIPT_SCHEMA = "kronos-a-share-gate-receipt-v2"
GATE_HEAD_SCHEMA = "kronos-a-share-gate-head-v1"
FORWARD_START = pd.Timestamp("2026-08-03")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
INFERENCE_SNAPSHOT_SCHEMA = "kronos-a-share-inference-snapshot-v1"
FORECAST_PATH_COLUMNS = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
)
PIT_PROVENANCE_SCHEMA = "kronos-a-share-pit-provenance-v1"
TRADING_CALENDAR_ARTIFACT_SCHEMA = "kronos-a-share-trading-calendar-v1"
TRADING_CALENDAR_OFFICIAL_DOMAINS = (
    "sse.com.cn",
    "szse.cn",
    "bse.cn",
    "csindex.com.cn",
)


class ForwardRegistryError(RuntimeError):
    """Raised when a forward record is unsafe, ambiguous, or has drifted."""


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _payload_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp(value: Any, *, field: str) -> pd.Timestamp:
    try:
        result = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ForwardRegistryError(f"{field} 不是有效时间") from exc
    if result.tzinfo is None:
        raise ForwardRegistryError(f"{field} 必须包含时区")
    return result


def _validate_hash(value: Any, *, field: str) -> str:
    text = str(value).lower()
    if SHA256_PATTERN.fullmatch(text) is None:
        raise ForwardRegistryError(f"{field} 必须是64位 SHA256")
    return text


def _inference_project_root(training_root: Path) -> Path:
    root = training_root.resolve()
    if root.name != "kronos_ashare" or root.parent.name != "_training":
        raise ForwardRegistryError(
            "inference snapshot 复验要求 training_root=<project>/_training/kronos_ashare"
        )
    return root.parent.parent


def _manifest_inventory(
    manifest_path: Path,
    manifest: Mapping[str, Any],
) -> None:
    snapshot_root = manifest_path.parent.resolve()
    expected_files = {"inference_manifest.json"}
    for collection_name in ("market_files", "pit_files"):
        collection = manifest.get(collection_name)
        if not isinstance(collection, list):
            raise ForwardRegistryError(
                f"inference manifest {collection_name} 必须是数组"
            )
        for item in collection:
            if not isinstance(item, Mapping):
                raise ForwardRegistryError("inference manifest 文件行必须是对象")
            relative_text = str(item.get("relative_path", ""))
            relative = Path(relative_text)
            if (
                not relative_text
                or relative.is_absolute()
                or ".." in relative.parts
            ):
                raise ForwardRegistryError("inference manifest relative_path 越界")
            try:
                candidate = (snapshot_root / relative).resolve(strict=True)
            except OSError as exc:
                raise ForwardRegistryError(
                    f"inference snapshot 文件缺失：{relative_text}"
                ) from exc
            if snapshot_root not in candidate.parents or not candidate.is_file():
                raise ForwardRegistryError(
                    f"inference snapshot 文件缺失或越界：{relative_text}"
                )
            try:
                declared_bytes = int(item.get("bytes", -1))
            except (TypeError, ValueError) as exc:
                raise ForwardRegistryError(
                    f"inference snapshot 文件 bytes 无效：{relative_text}"
                ) from exc
            if (
                candidate.stat().st_size != declared_bytes
                or sha256_file(candidate) != item.get("sha256")
            ):
                raise ForwardRegistryError(
                    f"inference snapshot 文件哈希漂移：{relative_text}"
                )
            expected_files.add(relative.as_posix())
    actual_files = {
        item.relative_to(snapshot_root).as_posix()
        for item in snapshot_root.rglob("*")
        if item.is_file()
    }
    if actual_files != expected_files:
        raise ForwardRegistryError("inference snapshot 文件集合漂移")


def _validate_inference_snapshot(
    *,
    training_root: Path,
    manifest_reference: Any,
    manifest_sha256: Any,
    snapshot_id: str,
    input_binding: Mapping[str, Any],
    input_sha256: str,
    as_of: pd.Timestamp,
) -> tuple[str, Path, Mapping[str, Any]]:
    try:
        manifest_path = resolve_under(
            training_root,
            str(manifest_reference or ""),
            must_exist=True,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise ForwardRegistryError(
            "inference manifest 路径越界或不存在"
        ) from exc
    if not manifest_path.is_file() or manifest_path.name != "inference_manifest.json":
        raise ForwardRegistryError("inference manifest 路径无效")
    normalized_reference = manifest_path.relative_to(training_root.resolve()).as_posix()
    declared_hash = _validate_hash(
        manifest_sha256,
        field="inference_manifest_sha256",
    )
    if sha256_file(manifest_path) != declared_hash:
        raise ForwardRegistryError("inference manifest 文件 SHA256 不匹配")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ForwardRegistryError("inference manifest 无法解析") from exc
    if not isinstance(manifest, Mapping):
        raise ForwardRegistryError("inference manifest 必须是对象")
    unsigned = dict(manifest)
    declared_payload = unsigned.pop("payload_sha256", None)
    if (
        manifest.get("schema_version") != INFERENCE_SNAPSHOT_SCHEMA
        or declared_payload != _payload_hash(unsigned)
    ):
        raise ForwardRegistryError("inference manifest schema/payload SHA256 漂移")
    if (
        manifest.get("snapshot_id") != snapshot_id
        or manifest.get("input_sha256") != input_sha256
        or manifest.get("input_binding") != dict(input_binding)
    ):
        raise ForwardRegistryError(
            "inference manifest 与 snapshot_id/input binding 不一致"
        )
    try:
        manifest_as_of = _timestamp(manifest.get("as_of"), field="inference.as_of")
    except ForwardRegistryError:
        raise
    if manifest_as_of != as_of:
        raise ForwardRegistryError("inference manifest as_of 与前瞻批次不一致")
    _manifest_inventory(manifest_path, manifest)
    try:
        verified = verify_inference_snapshot(
            manifest_path,
            training_root=training_root,
            project_root=_inference_project_root(training_root),
            expected_as_of=as_of,
        )
    except Exception as exc:
        raise ForwardRegistryError(f"inference snapshot 完整复验失败：{exc}") from exc
    if (
        not isinstance(verified, Mapping)
        or verified.get("snapshot_id") != snapshot_id
        or verified.get("input_sha256") != input_sha256
        or verified.get("input_binding") != dict(input_binding)
    ):
        raise ForwardRegistryError("inference snapshot 完整复验返回绑定漂移")
    if sha256_file(manifest_path) != declared_hash:
        raise ForwardRegistryError("inference manifest 在复验期间发生变化")
    _manifest_inventory(manifest_path, manifest)
    return normalized_reference, manifest_path, manifest


def _validate_future_calendar(
    *,
    training_root: Path,
    manifest_path: Path,
    manifest: Mapping[str, Any],
    calendar_reference: Any,
    authoritative_dates: Sequence[str],
    as_of: pd.Timestamp,
) -> tuple[str, str]:
    try:
        calendar_path = resolve_under(
            training_root,
            str(calendar_reference or ""),
            must_exist=True,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise ForwardRegistryError(
            "future trading calendar 路径越界或不存在"
        ) from exc
    snapshot_root = manifest_path.parent.resolve()
    if snapshot_root not in calendar_path.parents or not calendar_path.is_file():
        raise ForwardRegistryError(
            "future trading calendar 必须位于绑定的 inference snapshot"
        )
    relative_to_snapshot = calendar_path.relative_to(snapshot_root).as_posix()
    raw_matches = [
        item
        for item in manifest.get("pit_files", [])
        if isinstance(item, Mapping)
        and item.get("relative_path") == relative_to_snapshot
        and item.get("role") == "raw_response"
    ]
    calendar_hash = sha256_file(calendar_path)
    if (
        len(raw_matches) != 1
        or raw_matches[0].get("sha256") != calendar_hash
        or raw_matches[0].get("bytes") != calendar_path.stat().st_size
    ):
        raise ForwardRegistryError(
            "future trading calendar 未绑定到 inference raw_response"
        )
    pit_relative = relative_to_snapshot.removeprefix("pit/")
    provenance_matches: list[Mapping[str, Any]] = []
    for item in manifest.get("pit_files", []):
        if not isinstance(item, Mapping) or item.get("role") != "provenance_manifest":
            continue
        provenance_path = snapshot_root / str(item.get("relative_path", ""))
        try:
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ForwardRegistryError(
                "future trading calendar provenance 无法解析"
            ) from exc
        if (
            not isinstance(provenance, Mapping)
            or provenance.get("schema_version") != PIT_PROVENANCE_SCHEMA
        ):
            raise ForwardRegistryError(
                "future trading calendar provenance schema 无效"
            )
        for source in provenance.get("sources", []):
            if isinstance(source, Mapping) and source.get("path") == pit_relative:
                provenance_matches.append(source)
    if len(provenance_matches) != 1:
        raise ForwardRegistryError(
            "future trading calendar 必须唯一绑定专用 provenance"
        )
    source = provenance_matches[0]
    parsed_url = urlsplit(str(source.get("url", "")))
    host = (parsed_url.hostname or "").lower().rstrip(".")
    if (
        source.get("source_class") != "official_primary"
        or source.get("role") != "authoritative"
        or source.get("artifact_role") != "trading_calendar"
        or source.get("artifact_schema_version")
        != TRADING_CALENDAR_ARTIFACT_SCHEMA
        or source.get("sha256") != calendar_hash
        or parsed_url.scheme.lower() != "https"
        or not any(
            host == domain or host.endswith(f".{domain}")
            for domain in TRADING_CALENDAR_OFFICIAL_DOMAINS
        )
    ):
        raise ForwardRegistryError(
            "future trading calendar 官方来源、artifact role 或 schema 无效"
        )
    try:
        frame = pd.read_csv(calendar_path)
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        raise ForwardRegistryError("future trading calendar CSV 无法解析") from exc
    if list(frame.columns) != ["timestamps"]:
        raise ForwardRegistryError(
            "future trading calendar CSV 必须精确包含 timestamps"
        )
    values = pd.DatetimeIndex(pd.to_datetime(frame["timestamps"], errors="coerce"))
    if values.isna().any():
        raise ForwardRegistryError("future trading calendar 包含无效日期")
    if values.tz is not None:
        values = values.tz_convert(as_of.tzinfo).tz_localize(None)
    if not values.equals(values.normalize()):
        raise ForwardRegistryError("future trading calendar 不是日频日期")
    if values.has_duplicates or not values.is_monotonic_increasing:
        raise ForwardRegistryError("future trading calendar 日期未严格递增")
    future = values[values > as_of.tz_localize(None).normalize()]
    if len(future) < len(authoritative_dates):
        raise ForwardRegistryError("future trading calendar 未来日期不足")
    observed_dates = [item.date().isoformat() for item in future[: len(authoritative_dates)]]
    if observed_dates != list(authoritative_dates):
        raise ForwardRegistryError(
            "前瞻 authoritative future dates 与绑定交易日历不一致"
        )
    return (
        calendar_path.relative_to(training_root.resolve()).as_posix(),
        calendar_hash,
    )


def _authoritative_future_dates(
    values: Sequence[Any],
    as_of: pd.Timestamp,
) -> list[str]:
    try:
        value_count = len(values)
    except TypeError as exc:
        raise ForwardRegistryError("权威 future trading dates 必须是10个日期的序列") from exc
    if isinstance(values, (str, bytes)) or value_count != 10:
        raise ForwardRegistryError("权威 future trading dates 必须恰好10个")
    local_as_of = as_of.tz_localize(None).normalize()
    result: list[str] = []
    for index, value in enumerate(values):
        try:
            stamp = pd.Timestamp(value)
        except (TypeError, ValueError) as exc:
            raise ForwardRegistryError(
                f"future trading dates[{index}] 无效"
            ) from exc
        if stamp.tzinfo is not None:
            stamp = stamp.tz_convert(as_of.tzinfo).tz_localize(None)
        if stamp != stamp.normalize():
            raise ForwardRegistryError("future trading dates 必须是日频日期，不接受时分秒")
        if stamp <= local_as_of:
            raise ForwardRegistryError("future trading dates 必须晚于 as_of 交易日")
        if stamp.weekday() >= 5:
            raise ForwardRegistryError("future trading dates 含周末，不能作为权威交易日历")
        result.append(stamp.date().isoformat())
    if result != sorted(set(result)):
        raise ForwardRegistryError("future trading dates 必须严格递增且不重复")
    return result


def _validate_record(
    record: Mapping[str, Any],
    as_of: pd.Timestamp,
    *,
    allow_research: bool,
    authoritative_future_trading_dates: Sequence[str],
) -> dict[str, Any]:
    required = {
        "as_of",
        "ticker",
        "horizon",
        "raw_score",
        "percentile",
        "forecast_path",
        "path_dispersion",
        "dataset_id",
        "run_id",
        "adapter_hash",
        "inference_snapshot_id",
        "inference_input_sha256",
        "gate_status",
        "constraint_flags",
        "evidence_class",
        "output_type",
    }
    missing = sorted(required - set(record))
    if missing:
        raise ForwardRegistryError(f"forward record 缺少字段：{missing}")
    observed_as_of = _timestamp(record["as_of"], field="record.as_of")
    if observed_as_of != as_of:
        raise ForwardRegistryError("forward record.as_of 与批次不一致")
    if record["horizon"] != 10:
        raise ForwardRegistryError("forward horizon 必须为10")
    expected_gate_status = "blocked" if allow_research else "passed"
    if record["gate_status"] != expected_gate_status or record["output_type"] != "model_output":
        raise ForwardRegistryError("前瞻内部记录的 gate/output_type 合同无效")
    if record["evidence_class"] != "model_output":
        raise ForwardRegistryError("forward evidence_class 必须为 model_output")
    ticker = str(record["ticker"]).upper()
    if re.fullmatch(r"\d{6}\.(?:SH|SZ|BJ)", ticker) is None:
        raise ForwardRegistryError(f"forward ticker 无效：{ticker}")
    score = float(record["raw_score"])
    percentile = float(record["percentile"])
    dispersion = float(record["path_dispersion"])
    if not all(math.isfinite(value) for value in (score, percentile, dispersion)):
        raise ForwardRegistryError("forward score/percentile/dispersion 包含 NaN/Inf")
    if not 0 <= percentile <= 1 or dispersion < 0:
        raise ForwardRegistryError("forward percentile/dispersion 越界")
    path = record["forecast_path"]
    if not isinstance(path, list) or len(path) != 10:
        raise ForwardRegistryError("forward forecast_path 必须恰好10行")
    timestamps: list[str] = []
    normalized_path: list[dict[str, Any]] = []
    for index, row in enumerate(path):
        if not isinstance(row, Mapping) or set(row) != set(FORECAST_PATH_COLUMNS):
            raise ForwardRegistryError(
                f"forecast_path[{index}] 必须精确包含固定 OHLCVA 列"
            )
        try:
            stamp = pd.Timestamp(row["timestamp"])
        except (TypeError, ValueError) as exc:
            raise ForwardRegistryError(
                f"forecast_path[{index}].timestamp 无效"
            ) from exc
        if stamp.tzinfo is not None:
            stamp = stamp.tz_convert(as_of.tzinfo).tz_localize(None)
        if stamp != stamp.normalize():
            raise ForwardRegistryError("forecast_path 必须是日频交易日，不接受分钟时点")
        timestamps.append(stamp.date().isoformat())
        values: dict[str, float] = {}
        for field in FORECAST_PATH_COLUMNS[1:]:
            raw_value = row[field]
            if isinstance(raw_value, bool):
                raise ForwardRegistryError(
                    f"forecast_path[{index}].{field} 不是有限数值"
                )
            try:
                value = float(raw_value)
            except (TypeError, ValueError) as exc:
                raise ForwardRegistryError(
                    f"forecast_path[{index}].{field} 不是有限数值"
                ) from exc
            if not math.isfinite(value):
                raise ForwardRegistryError(
                    f"forecast_path[{index}].{field} 包含 NaN/Inf"
                )
            values[field] = value
        if any(values[field] <= 0 for field in ("open", "high", "low", "close")):
            raise ForwardRegistryError("forecast_path OHLC 必须为正数")
        if (
            values["high"] < max(values["open"], values["close"])
            or values["low"] > min(values["open"], values["close"])
            or values["high"] < values["low"]
        ):
            raise ForwardRegistryError("forecast_path OHLC 关系无效")
        if values["volume"] < 0 or values["amount"] < 0:
            raise ForwardRegistryError("forecast_path volume/amount 不得为负")
        normalized_row = {"timestamp": timestamps[-1], **values}
        normalized_path.append(normalized_row)
    if timestamps != list(authoritative_future_trading_dates):
        raise ForwardRegistryError("forecast_path 与权威 future trading dates 不一致")
    normalized = dict(record)
    normalized["ticker"] = ticker
    normalized["as_of"] = as_of.isoformat()
    normalized["forecast_path"] = normalized_path
    normalized["adapter_hash"] = _validate_hash(
        record["adapter_hash"], field="record.adapter_hash"
    )
    normalized["inference_input_sha256"] = _validate_hash(
        record["inference_input_sha256"],
        field="record.inference_input_sha256",
    )
    snapshot_id = str(record["inference_snapshot_id"])
    if re.fullmatch(r"\d{8}-[0-9a-f]{16}", snapshot_id) is None:
        raise ForwardRegistryError("record.inference_snapshot_id 无效")
    if snapshot_id[:8] != as_of.strftime("%Y%m%d"):
        raise ForwardRegistryError("record inference snapshot 日期与 as_of 不一致")
    if snapshot_id[9:] != normalized["inference_input_sha256"][:16]:
        raise ForwardRegistryError("record inference snapshot 与 input hash 不一致")
    normalized["inference_snapshot_id"] = snapshot_id
    return normalized


def _validate_release_receipt(
    binding: Mapping[str, Any],
    training_root: Path,
    *,
    gate_status: str,
    gate_binding: Any,
    adapter_hash: str,
    scorer_checkpoint_hash: str,
    evaluated_checkpoint: str,
    run_id: str,
) -> dict[str, Any]:
    if binding.get("schema_version") != RELEASE_RECEIPT_BINDING_SCHEMA:
        raise ForwardRegistryError("release receipt binding schema 无效")
    gate_hash = _validate_hash(binding.get("gate_sha256"), field="gate_sha256")
    receipt_hash = _validate_hash(
        binding.get("gate_receipt_sha256"), field="gate_receipt_sha256"
    )
    if binding.get("gate_receipt_schema_version") != GATE_RECEIPT_SCHEMA:
        raise ForwardRegistryError("release receipt 声明 schema 无效")
    gate_sequence = binding.get("gate_sequence")
    if isinstance(gate_sequence, bool) or not isinstance(gate_sequence, int) or gate_sequence < 1:
        raise ForwardRegistryError("release receipt gate_sequence 必须是正整数")
    try:
        receipt_path = resolve_under(
            training_root,
            str(binding.get("gate_receipt_path", "")),
            must_exist=True,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise ForwardRegistryError("release receipt 路径越界或不存在") from exc
    if not receipt_path.is_file() or receipt_path.name != f"{gate_hash}.json":
        raise ForwardRegistryError("release receipt 路径与 gate SHA256 不一致")
    if sha256_file(receipt_path) != receipt_hash:
        raise ForwardRegistryError("release receipt 文件 SHA256 不匹配")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ForwardRegistryError("release receipt 无法解析") from exc
    expected = {
        "schema_version": GATE_RECEIPT_SCHEMA,
        "gate_sha256": gate_hash,
        "gate_status": gate_status,
        "binding": gate_binding,
        "adapter_hash": adapter_hash,
        "scorer_checkpoint_hash": scorer_checkpoint_hash,
        "evaluated_checkpoint": evaluated_checkpoint,
        "run_id": run_id,
        "gate_sequence": gate_sequence,
    }
    if not isinstance(receipt, Mapping) or any(
        receipt.get(key) != value for key, value in expected.items()
    ):
        raise ForwardRegistryError("release receipt 内容与 gate/批次绑定不一致")
    _validate_gate_lineage(
        receipt_path,
        gate_sha256=gate_hash,
        gate_receipt_sha256=receipt_hash,
        gate_sequence=int(binding["gate_sequence"]),
    )
    normalized = dict(binding)
    normalized["gate_receipt_path"] = receipt_path.relative_to(
        Path(training_root).resolve()
    ).as_posix()
    return normalized


def _validate_gate_lineage(
    receipt_path: Path,
    *,
    gate_sha256: str,
    gate_receipt_sha256: str,
    gate_sequence: int,
) -> None:
    checkpoint_dir = receipt_path.parent.parent
    if receipt_path.parent.name != "gate-receipts" or checkpoint_dir.name != "checkpoints":
        raise ForwardRegistryError("release receipt 不位于受控 checkpoints/gate-receipts")
    lineage_dir = checkpoint_dir / "gate-lineage"
    head_path = checkpoint_dir / "gate-head.json"
    files = sorted(lineage_dir.glob("*.json")) if lineage_dir.is_dir() else []
    if not files or not head_path.is_file():
        raise ForwardRegistryError("release receipt 缺少 active gate lineage/head")
    core_fields = (
        "schema_version",
        "sequence",
        "gate_sha256",
        "gate_receipt_sha256",
        "previous_event_sha256",
        "created_at",
    )
    expected_fields = {*core_fields, "event_sha256"}
    previous_hash: str | None = None
    events: list[dict[str, Any]] = []
    for expected_sequence, event_path in enumerate(files, start=1):
        try:
            event = json.loads(event_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ForwardRegistryError("gate lineage event 无法解析") from exc
        if not isinstance(event, dict) or set(event) != expected_fields:
            raise ForwardRegistryError("gate lineage event 字段不匹配")
        sequence = event.get("sequence")
        if (
            isinstance(sequence, bool)
            or not isinstance(sequence, int)
            or sequence != expected_sequence
        ):
            raise ForwardRegistryError("gate lineage sequence 不连续")
        core = {field: event[field] for field in core_fields}
        event_hash = _payload_hash(core)
        if (
            event.get("schema_version") != GATE_HEAD_SCHEMA
            or event.get("previous_event_sha256") != previous_hash
            or event.get("event_sha256") != event_hash
            or event_path.name != f"{expected_sequence:08d}-{event_hash}.json"
        ):
            raise ForwardRegistryError("gate lineage 链或 event hash 不匹配")
        event_gate_hash = _validate_hash(
            event.get("gate_sha256"), field="lineage.gate_sha256"
        )
        event_receipt_hash = _validate_hash(
            event.get("gate_receipt_sha256"),
            field="lineage.gate_receipt_sha256",
        )
        historical_receipt_path = (
            checkpoint_dir / "gate-receipts" / f"{event_gate_hash}.json"
        )
        if (
            not historical_receipt_path.is_file()
            or sha256_file(historical_receipt_path) != event_receipt_hash
        ):
            raise ForwardRegistryError("gate lineage 历史 receipt 缺失或漂移")
        try:
            historical_receipt = json.loads(
                historical_receipt_path.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ForwardRegistryError("gate lineage 历史 receipt 无法解析") from exc
        if (
            not isinstance(historical_receipt, Mapping)
            or historical_receipt.get("schema_version") != GATE_RECEIPT_SCHEMA
            or historical_receipt.get("gate_sha256") != event_gate_hash
            or historical_receipt.get("gate_sequence") != expected_sequence
        ):
            raise ForwardRegistryError("gate lineage 历史 receipt 语义不匹配")
        events.append(event)
        previous_hash = event_hash
    try:
        active_head = json.loads(head_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ForwardRegistryError("active gate head 无法解析") from exc
    if active_head != events[-1]:
        raise ForwardRegistryError("active gate head 不是最新 lineage event")
    if gate_sequence > len(events):
        raise ForwardRegistryError("release receipt gate_sequence 超出 lineage")
    target = events[gate_sequence - 1]
    if (
        target.get("gate_sha256") != gate_sha256
        or target.get("gate_receipt_sha256") != gate_receipt_sha256
    ):
        raise ForwardRegistryError("release receipt 不属于声明的 gate lineage event")


def _registry_root_sha256(commitments: Sequence[Mapping[str, Any]]) -> str:
    return _payload_hash(
        {
            "schema_version": FORWARD_REGISTRY_ROOT_SCHEMA,
            "batch_commitments": [dict(item) for item in commitments],
        }
    )


def _batch_files(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.glob("*.json")
        if path.name != "summary.json" and not path.name.startswith(".")
    )


def _inspect_batch(path: Path, training_root: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ForwardRegistryError(f"前瞻批次不可解析：{path}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != FORWARD_BATCH_SCHEMA:
        raise ForwardRegistryError(f"前瞻批次 schema 无效：{path}")
    declared = payload.get("payload_sha256")
    unsigned = dict(payload)
    unsigned.pop("payload_sha256", None)
    if declared != _payload_hash(unsigned):
        raise ForwardRegistryError(f"前瞻批次 SHA256 漂移：{path}")
    semantic = dict(payload)
    semantic.pop("payload_sha256", None)
    declared_content = semantic.pop("content_sha256", None)
    semantic.pop("recorded_at", None)
    if declared_content != _payload_hash(semantic):
        raise ForwardRegistryError(f"前瞻批次 content SHA256 漂移：{path}")
    as_of = _timestamp(payload.get("as_of"), field="batch.as_of")
    if path.name[:8] != as_of.strftime("%Y%m%d"):
        raise ForwardRegistryError(f"前瞻批次文件名与 as_of 不一致：{path}")
    recorded_at = _timestamp(payload.get("recorded_at"), field="batch.recorded_at")
    local_recorded_at = recorded_at.tz_convert(as_of.tzinfo)
    if local_recorded_at.date() != as_of.date() or local_recorded_at < as_of:
        raise ForwardRegistryError(f"前瞻批次 recorded_at/as_of 时点无效：{path}")
    future_dates = _authoritative_future_dates(
        payload.get("authoritative_future_trading_dates", []),
        as_of,
    )
    if payload.get("target_date") != future_dates[-1]:
        raise ForwardRegistryError(f"前瞻 target_date 与权威交易日不一致：{path}")
    release_gate_status = payload.get("release_gate_status")
    allow_research = (
        release_gate_status == "blocked"
        and payload.get("research_scoring_allowed") is True
    )
    if release_gate_status != "passed" and not allow_research:
        raise ForwardRegistryError(f"前瞻批次 release gate 语义无效：{path}")
    if release_gate_status == "passed" and payload.get("research_scoring_allowed") is not False:
        raise ForwardRegistryError(f"passed 前瞻批次不得标记 research scoring：{path}")
    if payload.get("evidence_class") != "model_output":
        raise ForwardRegistryError(f"前瞻批次 evidence_class 无效：{path}")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ForwardRegistryError(f"前瞻批次 records 为空：{path}")
    normalized_records = [
        _validate_record(
            item,
            as_of,
            allow_research=allow_research,
            authoritative_future_trading_dates=future_dates,
        )
        for item in records
    ]
    if normalized_records != records:
        raise ForwardRegistryError(f"前瞻 records 未使用规范日频日期：{path}")
    universe = payload.get("universe_scores")
    if not isinstance(universe, list) or len(universe) < 2:
        raise ForwardRegistryError(f"前瞻批次缺少完整 universe_scores：{path}")
    normalized_universe: list[dict[str, Any]] = []
    for item in universe:
        if not isinstance(item, Mapping):
            raise ForwardRegistryError(f"前瞻 universe_scores 行无效：{path}")
        ticker = str(item.get("ticker", "")).upper()
        if re.fullmatch(r"\d{6}\.(?:SH|SZ|BJ)", ticker) is None:
            raise ForwardRegistryError(f"前瞻 universe_scores ticker 无效：{path}")
        try:
            score = float(item.get("raw_score"))
            percentile = float(item.get("percentile"))
        except (TypeError, ValueError) as exc:
            raise ForwardRegistryError(f"前瞻 universe_scores 数值无效：{path}") from exc
        if (
            not math.isfinite(score)
            or not math.isfinite(percentile)
            or not 0 <= percentile <= 1
        ):
            raise ForwardRegistryError(f"前瞻 universe_scores 数值越界：{path}")
        normalized_universe.append(
            {"ticker": ticker, "raw_score": score, "percentile": percentile}
        )
    if normalized_universe != universe:
        raise ForwardRegistryError(f"前瞻 universe_scores 未规范化：{path}")
    tickers = [item["ticker"] for item in normalized_universe]
    if (
        len(tickers) != len(universe)
        or len(tickers) != len(set(tickers))
        or payload.get("eligible_universe_count") != len(universe)
    ):
        raise ForwardRegistryError(f"前瞻批次 universe_scores 合同无效：{path}")
    inference_input_sha256 = _validate_hash(
        payload.get("inference_input_sha256"),
        field="inference_input_sha256",
    )
    inference_binding = payload.get("inference_input_binding")
    if not isinstance(inference_binding, Mapping):
        raise ForwardRegistryError(f"前瞻批次缺少 inference input binding：{path}")
    if _payload_hash(inference_binding) != inference_input_sha256:
        raise ForwardRegistryError(f"前瞻批次 inference input SHA256 不匹配：{path}")
    snapshot_id = str(payload.get("inference_snapshot_id", ""))
    if re.fullmatch(r"\d{8}-[0-9a-f]{16}", snapshot_id) is None:
        raise ForwardRegistryError(f"前瞻批次 inference snapshot id 无效：{path}")
    if snapshot_id[:8] != _timestamp(payload.get("as_of"), field="batch.as_of").strftime(
        "%Y%m%d"
    ):
        raise ForwardRegistryError(f"前瞻批次 inference snapshot 日期漂移：{path}")
    if snapshot_id[9:] != inference_input_sha256[:16]:
        raise ForwardRegistryError(f"前瞻批次 inference snapshot/hash 漂移：{path}")
    (
        normalized_manifest_reference,
        manifest_path,
        inference_manifest,
    ) = _validate_inference_snapshot(
        training_root=training_root,
        manifest_reference=payload.get("inference_manifest_path"),
        manifest_sha256=payload.get("inference_manifest_sha256"),
        snapshot_id=snapshot_id,
        input_binding=inference_binding,
        input_sha256=inference_input_sha256,
        as_of=as_of,
    )
    if normalized_manifest_reference != payload.get("inference_manifest_path"):
        raise ForwardRegistryError(f"前瞻批次 inference manifest 路径未规范化：{path}")
    normalized_calendar_reference, calendar_hash = _validate_future_calendar(
        training_root=training_root,
        manifest_path=manifest_path,
        manifest=inference_manifest,
        calendar_reference=payload.get("future_calendar_path"),
        authoritative_dates=future_dates,
        as_of=as_of,
    )
    if (
        normalized_calendar_reference != payload.get("future_calendar_path")
        or calendar_hash != payload.get("future_calendar_sha256")
    ):
        raise ForwardRegistryError(
            f"前瞻批次 future calendar 路径/hash 未规范化：{path}"
        )
    release_receipt = payload.get("release_receipt_binding")
    if not isinstance(release_receipt, Mapping):
        raise ForwardRegistryError(f"前瞻批次缺少 release receipt binding：{path}")
    normalized_receipt = _validate_release_receipt(
        release_receipt,
        training_root,
        gate_status=str(release_gate_status),
        gate_binding=payload.get("gate_binding"),
        adapter_hash=_validate_hash(payload.get("adapter_hash"), field="adapter_hash"),
        scorer_checkpoint_hash=_validate_hash(
            payload.get("scorer_checkpoint_hash"),
            field="scorer_checkpoint_hash",
        ),
        evaluated_checkpoint=str(payload.get("evaluated_checkpoint", "")),
        run_id=str(payload.get("run_id", "")),
    )
    if normalized_receipt != release_receipt:
        raise ForwardRegistryError(f"前瞻批次 receipt 路径未规范化：{path}")
    record_hashes = {
        str(item.get("inference_input_sha256"))
        for item in payload.get("records", [])
        if isinstance(item, Mapping)
    }
    record_snapshots = {
        str(item.get("inference_snapshot_id"))
        for item in payload.get("records", [])
        if isinstance(item, Mapping)
    }
    if record_hashes != {inference_input_sha256} or record_snapshots != {snapshot_id}:
        raise ForwardRegistryError(f"前瞻 records 与 inference input 绑定不一致：{path}")
    if {str(item.get("adapter_hash")) for item in normalized_records} != {
        str(payload.get("adapter_hash"))
    }:
        raise ForwardRegistryError(f"前瞻 records 与 adapter 绑定不一致：{path}")
    if len({str(item.get("run_id")) for item in normalized_records}) != 1 or str(
        normalized_records[0].get("run_id")
    ) != str(payload.get("run_id")):
        raise ForwardRegistryError(f"前瞻 records 与 run_id 绑定不一致：{path}")
    if len({str(item.get("dataset_id")) for item in normalized_records}) != 1 or str(
        normalized_records[0].get("dataset_id")
    ) != str(payload.get("dataset_id")):
        raise ForwardRegistryError(f"前瞻 records 与 dataset_id 绑定不一致：{path}")
    universe_tickers = set(tickers)
    if not {str(item.get("ticker")) for item in normalized_records}.issubset(
        universe_tickers
    ):
        raise ForwardRegistryError(f"前瞻 records 超出 universe_scores：{path}")
    return payload


def inspect_forward_registry(
    registry_directory: Path,
    training_root: Path,
    *,
    minimum_days: int,
    recommended_days: int,
    expected_adapter_hash: str | None = None,
    expected_scorer_checkpoint_hash: str | None = None,
    expected_gate_binding: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = resolve_under(training_root, registry_directory)
    if minimum_days < 60 or recommended_days < 120 or recommended_days < minimum_days:
        raise ForwardRegistryError("前瞻观察阈值不得弱于60/120日")
    if not root.is_dir():
        commitments: list[dict[str, Any]] = []
        return {
            "schema_version": FORWARD_SUMMARY_SCHEMA,
            "status": "empty",
            "observation_days": 0,
            "pending_observation_days": 0,
            "minimum_days": minimum_days,
            "recommended_days": recommended_days,
            "minimum_met": False,
            "recommended_met": False,
            "first_as_of": None,
            "last_as_of": None,
            "batch_count": 0,
            "batch_commitments": commitments,
            "registry_root_sha256": _registry_root_sha256(commitments),
        }
    inspected: list[tuple[Path, dict[str, Any], str]] = []
    for path in _batch_files(root):
        before_hash = sha256_file(path)
        payload = _inspect_batch(path, Path(training_root).resolve())
        after_hash = sha256_file(path)
        if before_hash != after_hash:
            raise ForwardRegistryError(f"前瞻批次在检查期间发生变化：{path}")
        inspected.append((path, payload, after_hash))
    batches = [payload for _, payload, _ in inspected]
    batch_commitments = sorted(
        [
            {
                "date": _timestamp(payload.get("as_of"), field="batch.as_of")
                .tz_localize(None)
                .date()
                .isoformat(),
                "path": path.relative_to(root).as_posix(),
                "file_sha256": file_sha256,
                "content_sha256": _validate_hash(
                    payload.get("content_sha256"), field="content_sha256"
                ),
                "payload_sha256": _validate_hash(
                    payload.get("payload_sha256"), field="payload_sha256"
                ),
                "gate_sha256": _validate_hash(
                    payload.get("release_receipt_binding", {}).get("gate_sha256"),
                    field="gate_sha256",
                ),
                "gate_receipt_sha256": _validate_hash(
                    payload.get("release_receipt_binding", {}).get(
                        "gate_receipt_sha256"
                    ),
                    field="gate_receipt_sha256",
                ),
                "gate_sequence": int(
                    payload.get("release_receipt_binding", {}).get("gate_sequence")
                ),
            }
            for path, payload, file_sha256 in inspected
        ],
        key=lambda item: (item["date"], item["path"]),
    )
    dates: list[pd.Timestamp] = []
    pending_dates: list[pd.Timestamp] = []
    adapter_hashes: set[str] = set()
    scorer_hashes: set[str] = set()
    bindings: set[str] = set()
    evaluated_checkpoints: set[str] = set()
    now = pd.Timestamp(_utc_now())
    seen_batch_dates: set[object] = set()
    for batch in batches:
        as_of = _timestamp(batch.get("as_of"), field="batch.as_of")
        if as_of.tz_localize(None).normalize() < FORWARD_START:
            raise ForwardRegistryError("前瞻批次早于2026-08-03")
        batch_date = as_of.tz_localize(None).date()
        if batch_date in seen_batch_dates:
            raise ForwardRegistryError("同一前瞻目录存在重复批次日")
        seen_batch_dates.add(batch_date)
        target_date = pd.Timestamp(str(batch.get("target_date")))
        if target_date.tzinfo is not None or target_date != target_date.normalize():
            raise ForwardRegistryError("前瞻 target_date 必须是日频日期")
        if target_date.date() <= batch_date:
            raise ForwardRegistryError("前瞻 target_date 必须晚于 as_of 交易日")
        if now.tz_convert(as_of.tzinfo).date() > target_date.date():
            dates.append(as_of.normalize())
        else:
            pending_dates.append(as_of.normalize())
        adapter_hashes.add(_validate_hash(batch.get("adapter_hash"), field="adapter_hash"))
        scorer_hashes.add(
            _validate_hash(
                batch.get("scorer_checkpoint_hash"),
                field="scorer_checkpoint_hash",
            )
        )
        bindings.add(_payload_hash({"binding": batch.get("gate_binding")}))
        evaluated_checkpoints.add(str(batch.get("evaluated_checkpoint", "")))
    if len(adapter_hashes) > 1:
        raise ForwardRegistryError("同一前瞻目录混入多个 adapter_hash")
    if (
        len(scorer_hashes) > 1
        or len(bindings) > 1
        or len(evaluated_checkpoints) > 1
        or "" in evaluated_checkpoints
    ):
        raise ForwardRegistryError("同一前瞻目录混入多个 scorer 或 gate binding")
    if expected_adapter_hash is not None and adapter_hashes not in (
        set(),
        {_validate_hash(expected_adapter_hash, field="expected_adapter_hash")},
    ):
        raise ForwardRegistryError("前瞻账本 adapter_hash 与当前 gate 不一致")
    if expected_scorer_checkpoint_hash is not None and scorer_hashes not in (
        set(),
        {
            _validate_hash(
                expected_scorer_checkpoint_hash,
                field="expected_scorer_checkpoint_hash",
            )
        },
    ):
        raise ForwardRegistryError("前瞻账本 scorer_checkpoint_hash 与当前 gate 不一致")
    if expected_gate_binding is not None and bindings not in (
        set(),
        {_payload_hash({"binding": dict(expected_gate_binding)})},
    ):
        raise ForwardRegistryError("前瞻账本 binding 与当前 gate 不一致")
    unique_dates = sorted(set(dates))
    unique_pending_dates = sorted(set(pending_dates))
    return {
        "schema_version": FORWARD_SUMMARY_SCHEMA,
        "status": "ok" if batches else "empty",
        "adapter_hash": next(iter(adapter_hashes), None),
        "scorer_checkpoint_hash": next(iter(scorer_hashes), None),
        "observation_days": len(unique_dates),
        "pending_observation_days": len(unique_pending_dates),
        "minimum_days": minimum_days,
        "recommended_days": recommended_days,
        "minimum_met": len(unique_dates) >= minimum_days,
        "recommended_met": len(unique_dates) >= recommended_days,
        "first_as_of": (
            sorted(set(unique_dates + unique_pending_dates))[0].isoformat()
            if unique_dates or unique_pending_dates
            else None
        ),
        "last_as_of": (
            sorted(set(unique_dates + unique_pending_dates))[-1].isoformat()
            if unique_dates or unique_pending_dates
            else None
        ),
        "batch_count": len(batches),
        "batch_commitments": batch_commitments,
        "registry_root_sha256": _registry_root_sha256(batch_commitments),
    }


def record_forward_batch(
    *,
    training_root: Path,
    registry_root: Path,
    as_of: Any,
    records: Sequence[Mapping[str, Any]],
    universe_scores: Sequence[Mapping[str, Any]],
    gate: Mapping[str, Any],
    inference_input_binding: Mapping[str, Any],
    inference_input_sha256: str,
    inference_snapshot_id: str,
    inference_manifest_path: Path,
    inference_manifest_sha256: str,
    future_calendar_path: Path,
    release_receipt_binding: Mapping[str, Any],
    authoritative_future_trading_dates: Sequence[Any],
    minimum_days: int,
    recommended_days: int,
) -> dict[str, Any]:
    """Atomically add one explicit scoring batch; duplicate dates fail closed."""

    root = resolve_under(training_root, registry_root)
    observed_at = _timestamp(as_of, field="as_of")
    if observed_at.tz_localize(None).normalize() < FORWARD_START:
        raise ForwardRegistryError("真正前瞻记录只接受2026-08-03及以后")
    allow_research = (
        gate.get("gate_status") == "blocked"
        and gate.get("research_scoring_allowed") is True
    )
    if gate.get("gate_status") != "passed" and not allow_research:
        raise ForwardRegistryError("只有 passed 或前瞻观察专用 gate 可以追加记录")
    future_dates = _authoritative_future_dates(
        authoritative_future_trading_dates,
        observed_at,
    )
    adapter_hash = _validate_hash(gate.get("adapter_hash"), field="gate.adapter_hash")
    scorer_checkpoint_hash = _validate_hash(
        gate.get("scorer_checkpoint_hash"), field="gate.scorer_checkpoint_hash"
    )
    evaluated_checkpoint = str(gate.get("evaluated_checkpoint", ""))
    if not evaluated_checkpoint:
        raise ForwardRegistryError("gate 缺少 evaluated_checkpoint")
    inference_hash = _validate_hash(
        inference_input_sha256,
        field="inference_input_sha256",
    )
    if not isinstance(inference_input_binding, Mapping):
        raise ForwardRegistryError("inference_input_binding 必须是对象")
    normalized_inference_binding = dict(inference_input_binding)
    if _payload_hash(normalized_inference_binding) != inference_hash:
        raise ForwardRegistryError("inference_input_binding 与 SHA256 不一致")
    snapshot_id = str(inference_snapshot_id)
    if re.fullmatch(r"\d{8}-[0-9a-f]{16}", snapshot_id) is None:
        raise ForwardRegistryError("inference_snapshot_id 无效")
    if snapshot_id[:8] != observed_at.strftime("%Y%m%d"):
        raise ForwardRegistryError("inference_snapshot_id 日期与 as_of 不一致")
    if snapshot_id[9:] != inference_hash[:16]:
        raise ForwardRegistryError("inference_snapshot_id 与 input hash 不一致")
    manifest_hash = _validate_hash(
        inference_manifest_sha256,
        field="inference_manifest_sha256",
    )
    (
        normalized_manifest_reference,
        manifest_path,
        inference_manifest,
    ) = _validate_inference_snapshot(
        training_root=Path(training_root).resolve(),
        manifest_reference=inference_manifest_path,
        manifest_sha256=manifest_hash,
        snapshot_id=snapshot_id,
        input_binding=normalized_inference_binding,
        input_sha256=inference_hash,
        as_of=observed_at,
    )
    normalized_calendar_reference, calendar_hash = _validate_future_calendar(
        training_root=Path(training_root).resolve(),
        manifest_path=manifest_path,
        manifest=inference_manifest,
        calendar_reference=future_calendar_path,
        authoritative_dates=future_dates,
        as_of=observed_at,
    )
    normalized_records = [
        _validate_record(
            item,
            observed_at,
            allow_research=allow_research,
            authoritative_future_trading_dates=future_dates,
        )
        for item in records
    ]
    if not normalized_records:
        raise ForwardRegistryError("前瞻批次不得为空")
    tickers = [item["ticker"] for item in normalized_records]
    if len(tickers) != len(set(tickers)):
        raise ForwardRegistryError("前瞻批次 ticker 重复")
    if {item["adapter_hash"] for item in normalized_records} != {adapter_hash}:
        raise ForwardRegistryError("record adapter_hash 与 gate 不一致")
    if {item["inference_input_sha256"] for item in normalized_records} != {
        inference_hash
    } or {item["inference_snapshot_id"] for item in normalized_records} != {
        snapshot_id
    }:
        raise ForwardRegistryError("record 与 inference input binding 不一致")
    if len({item["run_id"] for item in normalized_records}) != 1:
        raise ForwardRegistryError("前瞻批次混入多个 run_id")
    if not isinstance(release_receipt_binding, Mapping):
        raise ForwardRegistryError("release_receipt_binding 必须是对象")
    normalized_receipt_binding = _validate_release_receipt(
        release_receipt_binding,
        Path(training_root).resolve(),
        gate_status=str(gate.get("gate_status")),
        gate_binding=gate.get("binding"),
        adapter_hash=adapter_hash,
        scorer_checkpoint_hash=scorer_checkpoint_hash,
        evaluated_checkpoint=evaluated_checkpoint,
        run_id=str(normalized_records[0]["run_id"]),
    )
    normalized_universe: list[dict[str, Any]] = []
    for item in universe_scores:
        if not isinstance(item, Mapping):
            raise ForwardRegistryError("universe_scores 行必须是对象")
        ticker = str(item.get("ticker", "")).upper()
        if re.fullmatch(r"\d{6}\.(?:SH|SZ|BJ)", ticker) is None:
            raise ForwardRegistryError(f"universe_scores ticker 无效：{ticker}")
        score = float(item.get("raw_score"))
        percentile = float(item.get("percentile"))
        if not math.isfinite(score) or not math.isfinite(percentile) or not 0 <= percentile <= 1:
            raise ForwardRegistryError("universe_scores 数值无效")
        normalized_universe.append(
            {"ticker": ticker, "raw_score": score, "percentile": percentile}
        )
    normalized_universe.sort(key=lambda item: item["ticker"])
    universe_tickers = [item["ticker"] for item in normalized_universe]
    if len(normalized_universe) < 2 or len(universe_tickers) != len(set(universe_tickers)):
        raise ForwardRegistryError("universe_scores 必须覆盖至少2只不重复证券")
    if not {item["ticker"] for item in normalized_records}.issubset(
        set(universe_tickers)
    ):
        raise ForwardRegistryError("records 必须属于 universe_scores")
    recorded_at = pd.Timestamp(_utc_now())
    local_recorded_at = recorded_at.tz_convert(observed_at.tzinfo)
    if (
        local_recorded_at.date() != observed_at.date()
        or local_recorded_at < observed_at
    ):
        raise ForwardRegistryError("禁止事后回填前瞻记录；as_of 必须是当前本地日期")
    batch = {
        "schema_version": FORWARD_BATCH_SCHEMA,
        "recorded_at": recorded_at.isoformat(),
        "as_of": observed_at.isoformat(),
        "target_date": future_dates[-1],
        "authoritative_future_trading_dates": future_dates,
        "adapter_hash": adapter_hash,
        "scorer_checkpoint_hash": scorer_checkpoint_hash,
        "evaluated_checkpoint": evaluated_checkpoint,
        "run_id": normalized_records[0]["run_id"],
        "dataset_id": normalized_records[0]["dataset_id"],
        "gate_binding": gate.get("binding"),
        "inference_snapshot_id": snapshot_id,
        "inference_manifest_path": normalized_manifest_reference,
        "inference_manifest_sha256": manifest_hash,
        "future_calendar_path": normalized_calendar_reference,
        "future_calendar_sha256": calendar_hash,
        "inference_input_binding": normalized_inference_binding,
        "inference_input_sha256": inference_hash,
        "release_receipt_binding": normalized_receipt_binding,
        "release_gate_status": gate.get("gate_status"),
        "research_scoring_allowed": allow_research,
        "evidence_class": "model_output",
        "records": normalized_records,
        "eligible_universe_count": len(normalized_universe),
        "universe_scores": normalized_universe,
    }
    semantic_batch = dict(batch)
    semantic_batch.pop("recorded_at")
    batch["content_sha256"] = _payload_hash(semantic_batch)
    batch["payload_sha256"] = _payload_hash(batch)
    model_directory = resolve_under(root, scorer_checkpoint_hash)
    lock_path = resolve_under(root, ".forward-observations.lock")
    model_directory.mkdir(parents=True, exist_ok=True)
    date_key = observed_at.strftime("%Y%m%d")
    destination = resolve_under(
        model_directory,
        f"{date_key}-{batch['content_sha256'][:16]}.json",
    )
    with CheckpointFileLock(lock_path):
        same_date = list(model_directory.glob(f"{date_key}-*.json"))
        if same_date:
            if len(same_date) != 1:
                raise ForwardRegistryError("同一 adapter/as_of 存在多个前瞻批次")
            existing = _inspect_batch(same_date[0], Path(training_root).resolve())
            if existing.get("content_sha256") != batch["content_sha256"]:
                raise ForwardRegistryError("同一 adapter/as_of 已存在不同前瞻批次")
            reused = True
            destination = same_date[0]
            batch = existing
        else:
            atomic_write_json(destination, batch, allowed_root=training_root)
            reused = False
        summary = inspect_forward_registry(
            model_directory,
            training_root,
            minimum_days=minimum_days,
            recommended_days=recommended_days,
            expected_adapter_hash=adapter_hash,
            expected_scorer_checkpoint_hash=scorer_checkpoint_hash,
            expected_gate_binding=gate.get("binding"),
        )
        summary.update(
            {
                "generated_at": _utc_now().isoformat(),
                "registry_directory": str(model_directory),
            }
        )
        atomic_write_json(
            model_directory / "summary.json",
            summary,
            allowed_root=training_root,
        )
    return {
        "status": "reused" if reused else "recorded",
        "batch_path": str(destination),
        "payload_sha256": batch["payload_sha256"],
        "summary": summary,
    }

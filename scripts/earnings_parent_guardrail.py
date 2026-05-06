# -*- coding: utf-8 -*-
"""Guardrail helper for the 22-30-2 earnings-call parent automation.

This script deliberately handles deterministic mechanics only:
- preflight local paths and imports
- load the Zijin earnings calendar without network refresh
- compute the strict future window and child run times
- validate ticker/company/market identity for candidate events
- scan child automation TOMLs, detect duplicates, stale tasks, and rrule drift
- optionally apply mechanical child TOML create/update/pause changes

It does not decide whether a web page is sufficient official evidence and it
does not perform official call-time writeback. Ambiguous source situations are
reported as review items for the parent agent to judge.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import tomllib
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


BEIJING_TZ = ZoneInfo("Asia/Shanghai")
WEEKDAYS = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
RRULE_PATTERN = re.compile(
    r"^DTSTART:\d{8}T\d{6}\n"
    r"RRULE:FREQ=WEEKLY;BYDAY=(SU|MO|TU|WE|TH|FR|SA);"
    r"BYHOUR=\d{1,2};BYMINUTE=\d{1,2};COUNT=1$"
)
OFFICIAL_CALL_SOURCE_TYPES = {
    "official_ir_event",
    "official_ir_press_release",
    "official_ir_calendar",
    "official_ir_webcast",
    "official_ir_page",
    "sec_filing",
    "exchange_announcement",
}
OFFICIAL_CALENDAR_SOURCES = {
    "Company IR",
    "JPX",
    "TDnet",
    "DART",
    "KIND",
    "MOPS",
    "SEC EDGAR 6-K",
    "confirmed",
}
SOURCE_CONFIDENCE_RANK = {
    "unknown": 0,
    "third_party_calendar_estimate": 1,
    "non_official_estimate": 1,
    "conflict_requires_official_verification": 2,
    "official_date_mismatch": 2,
    "official_disclosure": 3,
    "official_confirmed": 4,
}
EU_MARKETS = {"DE", "FR", "UK", "NL", "IT", "SE"}
DEFAULT_CODEX_HOME = Path.home() / ".codex"
DEFAULT_PROJECT_ROOT = Path("D:/vcp_hunter") / "\u4ea7\u4e1a\u94fe\u6295\u7814"
DEFAULT_ZIJIN_ROOT = Path("D:/vcp_hunter") / "\u7d2b\u91d1\u7814\u9009"
CHILD_NAME_PREFIX = "\u8d22\u62a5\u7535\u8bdd\u4f1a\u6df1\u6316"


@dataclass(frozen=True)
class PlannedEvent:
    company: str
    ticker: str
    sector: str
    market: str
    report_date: str
    fiscal_period: str
    time_label: str
    event_status: str
    event_source: str
    source_type: str
    planned_child_start_beijing: str
    schedule_basis: str
    official_call_beijing: str
    original_call_time_text: str
    original_timezone: str
    call_time_source_url: str
    call_time_source_type: str
    calendar_source: str
    source_confidence: str
    official_source_url: str
    calendar_caveat: str
    task_key: str


@dataclass
class ChildRecord:
    path: Path
    data: dict[str, Any]
    task_key: str
    ticker: str
    company: str
    report_date: str
    fiscal_period: str
    planned_child_start_beijing: str
    schedule_basis: str
    planned_dt: dt.datetime | None
    has_memory: bool
    rrule_ok: bool


def _json_string(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _dump_toml(data: dict[str, Any]) -> str:
    order = [
        "version",
        "id",
        "kind",
        "name",
        "prompt",
        "status",
        "rrule",
        "model",
        "reasoning_effort",
        "execution_environment",
        "cwds",
        "created_at",
        "updated_at",
    ]
    lines: list[str] = []
    keys = [key for key in order if key in data] + [key for key in data if key not in order]
    for key in keys:
        value = data[key]
        if isinstance(value, bool):
            lines.append(f"{key} = {str(value).lower()}")
        elif isinstance(value, int):
            lines.append(f"{key} = {value}")
        elif isinstance(value, list):
            lines.append(f"{key} = [{', '.join(_json_string(str(item)) for item in value)}]")
        else:
            lines.append(f"{key} = {_json_string(str(value))}")
    return "\n".join(lines) + "\n"


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def _write_toml(path: Path, data: dict[str, Any], *, backup_tag: str) -> str | None:
    backup_path: str | None = None
    if path.exists():
        backup = path.with_name(f"{path.name}.bak-guardrail-{backup_tag}")
        if not backup.exists():
            shutil.copy2(path, backup)
        backup_path = str(backup)
    path.write_text(_dump_toml(data), encoding="utf-8")
    return backup_path


def _prompt_field(prompt: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*([^\n]+)", prompt or "", re.M)
    return match.group(1).strip() if match else ""


def _normalize_period(value: str) -> str:
    text = str(value or "").strip()
    return "" if text.upper() == "N/A" else text


def _task_key(ticker: str, report_date: str, fiscal_period: str) -> str:
    return f"{ticker.strip().upper()}|{report_date[:10]}|{_normalize_period(fiscal_period)}"


def _parse_beijing_time(value: str) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.strptime(value.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=BEIJING_TZ)
    except ValueError:
        return None


def _format_beijing_time(value: dt.datetime) -> str:
    return value.astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")


def _make_one_shot_rrule(start: dt.datetime) -> str:
    local = start.astimezone(BEIJING_TZ)
    return (
        f"DTSTART:{local.strftime('%Y%m%dT%H%M%S')}\n"
        f"RRULE:FREQ=WEEKLY;BYDAY={WEEKDAYS[local.weekday()]};"
        f"BYHOUR={local.hour};BYMINUTE={local.minute};COUNT=1"
    )


def _slug_ticker(ticker: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", ticker.lower()).strip("-")


def _child_id_for(event: PlannedEvent) -> str:
    digest = hashlib.sha1(event.task_key.encode("utf-8")).hexdigest()[:6]
    return f"ec-{_slug_ticker(event.ticker)}-{event.report_date.replace('-', '')}-{digest}"


def _load_service(zijin_root: Path):
    sys.path.insert(0, str(zijin_root))
    from domains.global_earnings_calendar.service import (  # type: ignore
        EarningsCalendarEvent,
        GlobalEarningsCalendarService,
        build_oligarch_universe,
        market_from_ticker,
    )

    return EarningsCalendarEvent, GlobalEarningsCalendarService, build_oligarch_universe, market_from_ticker


def _is_official_call_event(event: Any) -> bool:
    source_type = str(getattr(event, "call_time_source_type", "") or "").strip()
    if source_type not in OFFICIAL_CALL_SOURCE_TYPES and not source_type.startswith("official_ir_"):
        return False
    if str(getattr(event, "status", "") or "").strip() != "confirmed":
        return False
    if not (
        str(getattr(event, "conference_url", "") or "").strip()
        or str(getattr(event, "call_time_source_url", "") or "").strip()
    ):
        return False
    return _parse_beijing_time(str(getattr(event, "beijing_time", "") or "")) is not None


def _default_proxy_start(event: Any, market_from_ticker) -> dt.datetime:
    report_date = dt.date.fromisoformat(str(event.report_date)[:10])
    market = str(event.market or market_from_ticker(event.ticker)).strip().upper()
    label = str(event.time_label or "").lower()
    if market == "US":
        if "盘前" in str(event.time_label or "") or "before" in label or "pre" in label:
            return dt.datetime.combine(report_date, dt.time(23, 30), tzinfo=BEIJING_TZ)
        return dt.datetime.combine(report_date + dt.timedelta(days=1), dt.time(8, 0), tzinfo=BEIJING_TZ)
    if market in {"TW", "HK", "JP", "KR"}:
        return dt.datetime.combine(report_date, dt.time(20, 0), tzinfo=BEIJING_TZ)
    if market in EU_MARKETS:
        return dt.datetime.combine(report_date + dt.timedelta(days=1), dt.time(2, 30), tzinfo=BEIJING_TZ)
    return dt.datetime.combine(report_date + dt.timedelta(days=1), dt.time(8, 0), tzinfo=BEIJING_TZ)


def _calendar_source_fields(event: Any, schedule_basis: str, official_url: str) -> tuple[str, str, str, str, str]:
    source = str(event.source or "").strip() or "not_found_in_current_calendar"
    status = str(event.status or "").strip() or "unknown"
    source_type = str(event.call_time_source_type or "").strip()
    final_official_url = "N/A"
    confidence = "unknown"
    caveat = "No official calendar source was found in the current event."

    if schedule_basis == "official_call_plus_3h":
        final_official_url = official_url
        confidence = "official_confirmed"
        caveat = "Official call/webcast time confirmed; child is scheduled at official call time plus 3 hours."
    elif source_type == "mops_material_information" or source == "MOPS":
        source = "MOPS"
        final_official_url = str(event.call_time_source_url or "N/A")
        confidence = "official_disclosure"
        caveat = "MOPS confirms an earnings/report disclosure event, not a call/webcast time; scheduled by default proxy."
    elif source in OFFICIAL_CALENDAR_SOURCES:
        final_official_url = str(event.call_time_source_url or event.conference_url or "N/A")
        confidence = "official_disclosure"
        caveat = "Official date/disclosure source found, but no credible call/webcast time was available; scheduled by default proxy."
    elif source == "Yahoo Finance":
        confidence = "non_official_estimate"
        caveat = "Yahoo Finance estimate only; no credible official call/webcast time found; scheduled by default proxy."
    elif source in {"Nasdaq", "Alpha Vantage"}:
        confidence = "third_party_calendar_estimate"
        caveat = f"{source} is a third-party calendar lead only; no credible official call/webcast time found; scheduled by default proxy."
    else:
        confidence = "unknown"
        caveat = "Source type is not enough for official call-time writeback; scheduled by default proxy."

    return source, status, confidence, final_official_url, caveat


def _plan_event(event: Any, market_from_ticker) -> PlannedEvent:
    fiscal_period = _normalize_period(str(event.fiscal_period or ""))
    if _is_official_call_event(event):
        call_dt = _parse_beijing_time(str(event.beijing_time or ""))
        if call_dt is None:
            raise ValueError(f"official event has unparsable beijing_time: {event.ticker}")
        planned = call_dt + dt.timedelta(hours=3)
        basis = "official_call_plus_3h"
        official_call = _format_beijing_time(call_dt)
        original_text = str(event.original_call_time_text or "N/A")
        original_tz = str(event.original_timezone or "N/A")
        call_url = str(event.call_time_source_url or event.conference_url or "N/A")
        call_type = str(event.call_time_source_type or "official_ir_event")
    else:
        planned = _default_proxy_start(event, market_from_ticker)
        basis = "default_proxy_not_call_time"
        official_call = "not_found"
        original_text = "not_found"
        original_tz = "N/A"
        call_url = "N/A"
        call_type = "default_proxy_not_call_time"

    calendar_source, event_status, confidence, official_url, caveat = _calendar_source_fields(
        event, basis, call_url
    )
    ticker = str(event.ticker or "").strip().upper()
    report_date = str(event.report_date or "")[:10]
    return PlannedEvent(
        company=str(event.company or "").strip(),
        ticker=ticker,
        sector=str(event.sector or "").strip(),
        market=str(event.market or market_from_ticker(ticker)).strip(),
        report_date=report_date,
        fiscal_period=fiscal_period,
        time_label=str(event.time_label or "").strip(),
        event_status=event_status,
        event_source=calendar_source,
        source_type=str(event.call_time_source_type or "").strip(),
        planned_child_start_beijing=_format_beijing_time(planned),
        schedule_basis=basis,
        official_call_beijing=official_call,
        original_call_time_text=original_text,
        original_timezone=original_tz,
        call_time_source_url=call_url,
        call_time_source_type=call_type,
        calendar_source=calendar_source,
        source_confidence=confidence,
        official_source_url=official_url,
        calendar_caveat=caveat,
        task_key=_task_key(ticker, report_date, fiscal_period),
    )


def _scan_children(automations_root: Path) -> tuple[list[ChildRecord], list[dict[str, Any]]]:
    children: list[ChildRecord] = []
    problems: list[dict[str, Any]] = []
    for path in sorted(automations_root.glob("*/automation.toml")):
        try:
            data = _read_toml(path)
        except Exception as exc:  # noqa: BLE001
            problems.append({"path": str(path), "problem": "toml_parse_failed", "detail": str(exc)})
            continue
        prompt = str(data.get("prompt", "") or "")
        if not (prompt.startswith("TASK_KEY:") and "CHILD TASK SKILL HARD GATE" in prompt):
            continue
        planned_text = _prompt_field(prompt, "Planned child start Beijing")
        record = ChildRecord(
            path=path,
            data=data,
            task_key=_prompt_field(prompt, "TASK_KEY"),
            ticker=_prompt_field(prompt, "Ticker").upper(),
            company=_prompt_field(prompt, "Company"),
            report_date=_prompt_field(prompt, "Report date")[:10],
            fiscal_period=_normalize_period(_prompt_field(prompt, "Fiscal period")),
            planned_child_start_beijing=planned_text,
            schedule_basis=_prompt_field(prompt, "Schedule basis"),
            planned_dt=_parse_beijing_time(planned_text),
            has_memory=(path.parent / "memory.md").exists(),
            rrule_ok=bool(RRULE_PATTERN.match(str(data.get("rrule", "")))),
        )
        children.append(record)
    return children, problems


def _template_body(children: list[ChildRecord]) -> str | None:
    marker = "\n\nCHILD TASK SKILL HARD GATE:"
    for child in children:
        prompt = str(child.data.get("prompt", "") or "")
        index = prompt.find(marker)
        if index >= 0 and "Company Fundamental Baseline" in prompt:
            return prompt[index:]
    return None


def _child_prompt(event: PlannedEvent, template_body: str) -> str:
    fiscal_period = event.fiscal_period or "N/A"
    header = "\n".join(
        [
            f"TASK_KEY: {event.task_key}",
            "Automation parent: 22-30-2",
            f"Company: {event.company}",
            f"Ticker: {event.ticker}",
            f"Report date: {event.report_date}",
            f"Fiscal period: {fiscal_period}",
            f"Sector: {event.sector}",
            f"Market: {event.market}",
            f"Planned child start Beijing: {event.planned_child_start_beijing}",
            f"Schedule basis: {event.schedule_basis}",
            f"Official call Beijing time: {event.official_call_beijing}",
            f"Original call time text: {event.original_call_time_text}",
            f"Original timezone: {event.original_timezone}",
            f"Call time source URL: {event.call_time_source_url}",
            f"Call time source type: {event.call_time_source_type}",
            f"Calendar source: {event.calendar_source}",
            f"Event status: {event.event_status}",
            f"Source confidence: {event.source_confidence}",
            f"Official source URL: {event.official_source_url}",
            f"Calendar caveat: {event.calendar_caveat}",
        ]
    )
    return header + template_body


def _event_with_preserved_source(event: PlannedEvent, existing_prompt: str) -> PlannedEvent:
    existing = {
        "calendar_source": _prompt_field(existing_prompt, "Calendar source"),
        "event_status": _prompt_field(existing_prompt, "Event status"),
        "source_confidence": _prompt_field(existing_prompt, "Source confidence"),
        "official_source_url": _prompt_field(existing_prompt, "Official source URL"),
        "calendar_caveat": _prompt_field(existing_prompt, "Calendar caveat"),
    }
    if not all(existing.values()):
        return event
    existing_rank = SOURCE_CONFIDENCE_RANK.get(existing["source_confidence"], 0)
    event_rank = SOURCE_CONFIDENCE_RANK.get(event.source_confidence, 0)
    if existing_rank <= event_rank:
        return event
    return replace(
        event,
        calendar_source=existing["calendar_source"],
        event_status=existing["event_status"],
        source_confidence=existing["source_confidence"],
        official_source_url=existing["official_source_url"],
        calendar_caveat=existing["calendar_caveat"],
    )


def _validate_candidate_mapping(
    events: list[PlannedEvent],
    universe: dict[str, Any],
    market_from_ticker,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    seen_tickers: dict[str, str] = {}
    for event in events:
        if not event.company or not event.ticker:
            errors.append({"ticker": event.ticker, "problem": "empty_company_or_ticker"})
            continue
        if event.ticker in seen_tickers and seen_tickers[event.ticker] != event.company:
            errors.append(
                {
                    "ticker": event.ticker,
                    "problem": "same_ticker_multiple_companies",
                    "companies": [seen_tickers[event.ticker], event.company],
                }
            )
        seen_tickers[event.ticker] = event.company
        suffix_market = market_from_ticker(event.ticker)
        if suffix_market != event.market:
            errors.append(
                {
                    "ticker": event.ticker,
                    "problem": "market_suffix_mismatch",
                    "event_market": event.market,
                    "market_from_ticker": suffix_market,
                }
            )
        company = universe.get(event.ticker)
        if not company:
            errors.append({"ticker": event.ticker, "problem": "ticker_missing_from_universe"})
            continue
        if str(company.market).upper() != event.market.upper():
            errors.append(
                {
                    "ticker": event.ticker,
                    "problem": "universe_market_mismatch",
                    "universe_market": company.market,
                    "event_market": event.market,
                }
            )
        normalized_universe = re.sub(r"[^a-z0-9]+", "", str(company.company).lower())
        normalized_event = re.sub(r"[^a-z0-9]+", "", event.company.lower())
        if not (
            normalized_universe == normalized_event
            or normalized_universe in normalized_event
            or normalized_event in normalized_universe
        ):
            errors.append(
                {
                    "ticker": event.ticker,
                    "problem": "universe_company_mismatch",
                    "universe_company": company.company,
                    "event_company": event.company,
                }
            )

    if any(event.ticker in {"2316.TW", "2313.TW", "3044.TW"} for event in events):
        pcb_gate = {
            ticker: universe.get(ticker).company if universe.get(ticker) else None
            for ticker in ["2316.TW", "2313.TW", "3044.TW"]
        }
        expected = {"2316.TW": "Wus", "2313.TW": "Compeq", "3044.TW": "Tripod"}
        if pcb_gate != expected:
            errors.append({"problem": "taiwan_pcb_gate_failed", "mapping": pcb_gate})
    return errors


def _match_child(event: PlannedEvent, children: list[ChildRecord]) -> tuple[ChildRecord | None, str | None]:
    key_matches = [child for child in children if child.task_key == event.task_key]
    if len(key_matches) > 1:
        return None, "duplicate_key_ambiguous"
    if len(key_matches) == 1:
        return key_matches[0], None

    fallback = [
        child
        for child in children
        if child.ticker == event.ticker and child.report_date == event.report_date
    ]
    if len(fallback) > 1:
        return None, "duplicate_ticker_date_ambiguous"
    if len(fallback) == 1:
        return fallback[0], None
    return None, None


def _child_matches_event(child: ChildRecord, event: PlannedEvent) -> tuple[bool, list[str]]:
    prompt = str(child.data.get("prompt", "") or "")
    expected_rrule_dt = _parse_beijing_time(event.planned_child_start_beijing)
    expected_rrule = _make_one_shot_rrule(expected_rrule_dt) if expected_rrule_dt else ""
    existing_source_fields = {
        "calendar_source": _prompt_field(prompt, "Calendar source"),
        "event_status": _prompt_field(prompt, "Event status"),
        "source_confidence": _prompt_field(prompt, "Source confidence"),
        "official_source_url": _prompt_field(prompt, "Official source URL"),
        "calendar_caveat": _prompt_field(prompt, "Calendar caveat"),
    }
    source_header_present = all(existing_source_fields.values())
    existing_source_rank = SOURCE_CONFIDENCE_RANK.get(existing_source_fields["source_confidence"], 0)
    event_source_rank = SOURCE_CONFIDENCE_RANK.get(event.source_confidence, 0)
    # Preserve stronger agent-reviewed source fields. The service cache can lag a
    # manual official-source check, so the guardrail may upgrade but not downgrade.
    source_ok = source_header_present and existing_source_rank >= event_source_rank
    checks = {
        "status": str(child.data.get("status")) == "ACTIVE",
        "task_key": child.task_key == event.task_key,
        "ticker": child.ticker == event.ticker,
        "company": child.company == event.company,
        "report_date": child.report_date == event.report_date,
        "planned_child_start_beijing": child.planned_child_start_beijing == event.planned_child_start_beijing,
        "schedule_basis": child.schedule_basis == event.schedule_basis,
        "official_call_beijing": _prompt_field(prompt, "Official call Beijing time") == event.official_call_beijing,
        "source_header": source_ok,
        "rrule": str(child.data.get("rrule", "")) == expected_rrule,
        "model": child.data.get("model") == "gpt-5.5",
        "reasoning_effort": child.data.get("reasoning_effort") == "xhigh",
        "execution_environment": child.data.get("execution_environment") == "local",
    }
    failed = [name for name, ok in checks.items() if not ok]
    return not failed, failed


def _review_items(events: list[PlannedEvent]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for event in events:
        if event.schedule_basis == "official_call_plus_3h":
            continue
        status = "needs_agent_review"
        if event.source_confidence == "non_official_estimate":
            reason = "third_party_estimate_no_official_call_time"
        elif event.source_confidence == "official_disclosure":
            reason = "official_date_or_disclosure_without_precise_call_time"
        elif event.source_confidence == "third_party_calendar_estimate":
            reason = "third_party_calendar_without_official_confirmation"
        else:
            reason = "call_time_not_found"
        items.append(
            {
                "ticker": event.ticker,
                "company": event.company,
                "report_date": event.report_date,
                "status": status,
                "reason": reason,
                "calendar_source": event.calendar_source,
                "calendar_caveat": event.calendar_caveat,
            }
        )
    return items


def _build_action_plan(
    events: list[PlannedEvent],
    children: list[ChildRecord],
    now: dt.datetime,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    actions: dict[str, list[dict[str, Any]]] = {
        "create": [],
        "update": [],
        "pause": [],
        "validate_pending": [],
        "repair_rrule": [],
    }
    blockers: list[dict[str, Any]] = []
    current_ticker_dates = {(event.ticker, event.report_date) for event in events}
    current_dates_by_ticker = {event.ticker: event.report_date for event in events}
    validated_child_ids: set[str] = set()

    for event in events:
        child, problem = _match_child(event, children)
        if problem:
            blockers.append({"ticker": event.ticker, "report_date": event.report_date, "problem": problem})
            continue
        payload = {
            "ticker": event.ticker,
            "company": event.company,
            "report_date": event.report_date,
            "task_key": event.task_key,
            "planned_child_start_beijing": event.planned_child_start_beijing,
            "schedule_basis": event.schedule_basis,
        }
        if child:
            child_id = str(child.data.get("id"))
            matches, failed = _child_matches_event(child, event)
            if matches:
                actions["validate_pending"].append({"child_id": child_id, **payload})
                validated_child_ids.add(child_id)
            else:
                actions["update"].append({"child_id": child_id, "update_reasons": failed, **payload})
        else:
            actions["create"].append({"child_id": _child_id_for(event), **payload})

    for child in children:
        if str(child.data.get("status")) != "ACTIVE":
            continue
        reason: str | None = None
        if child.has_memory:
            reason = "executed_child_paused"
        if child.planned_dt and child.planned_dt < now:
            reason = "stale_child_paused"
        if (
            child.ticker in current_dates_by_ticker
            and (child.ticker, child.report_date) not in current_ticker_dates
        ):
            reason = "stale_child_paused_date_drift"
        if reason:
            actions["pause"].append(
                {
                    "child_id": child.data.get("id"),
                    "ticker": child.ticker,
                    "report_date": child.report_date,
                    "planned_child_start_beijing": child.planned_child_start_beijing,
                    "reason": reason,
                    "rrule_ok": child.rrule_ok,
                }
            )
            if not child.rrule_ok:
                actions["repair_rrule"].append(
                    {
                        "child_id": child.data.get("id"),
                        "ticker": child.ticker,
                        "report_date": child.report_date,
                        "planned_child_start_beijing": child.planned_child_start_beijing,
                    }
                )
        elif child.rrule_ok and child.planned_dt and child.planned_dt >= now:
            child_id = str(child.data.get("id"))
            if child_id in validated_child_ids:
                continue
            actions["validate_pending"].append(
                {
                    "child_id": child_id,
                    "ticker": child.ticker,
                    "report_date": child.report_date,
                    "planned_child_start_beijing": child.planned_child_start_beijing,
                }
            )
    return actions, blockers


def _apply_actions(
    actions: dict[str, list[dict[str, Any]]],
    events: list[PlannedEvent],
    children: list[ChildRecord],
    automations_root: Path,
    project_root: Path,
    run_ms: int,
    backup_tag: str,
) -> dict[str, Any]:
    template = _template_body(children)
    if not template:
        return {"applied": False, "problem": "child_template_body_not_found"}

    children_by_id = {str(child.data.get("id")): child for child in children}
    event_by_key = {event.task_key: event for event in events}
    backups: list[str] = []
    changed: list[str] = []

    for action in actions["pause"]:
        child = children_by_id.get(str(action["child_id"]))
        if not child:
            continue
        data = dict(child.data)
        if child.planned_dt and not child.rrule_ok:
            data["rrule"] = _make_one_shot_rrule(child.planned_dt)
        data["status"] = "PAUSED"
        data["cwds"] = [str(project_root)]
        data["updated_at"] = run_ms
        backup = _write_toml(child.path, data, backup_tag=backup_tag)
        if backup:
            backups.append(backup)
        changed.append(str(data.get("id")))

    for action in actions["update"]:
        child = children_by_id.get(str(action["child_id"]))
        event = event_by_key.get(str(action["task_key"]))
        if not child or not event:
            continue
        planned_dt = _parse_beijing_time(event.planned_child_start_beijing)
        if planned_dt is None:
            continue
        event = _event_with_preserved_source(event, str(child.data.get("prompt", "") or ""))
        data = dict(child.data)
        data.update(
            {
                "name": f"{CHILD_NAME_PREFIX} {event.ticker} {event.company} {event.report_date}",
                "prompt": _child_prompt(event, template),
                "status": "ACTIVE",
                "rrule": _make_one_shot_rrule(planned_dt),
                "model": "gpt-5.5",
                "reasoning_effort": "xhigh",
                "execution_environment": "local",
                "cwds": [str(project_root)],
                "updated_at": run_ms,
            }
        )
        backup = _write_toml(child.path, data, backup_tag=backup_tag)
        if backup:
            backups.append(backup)
        changed.append(str(data.get("id")))

    for action in actions["create"]:
        event = event_by_key.get(str(action["task_key"]))
        if not event:
            continue
        planned_dt = _parse_beijing_time(event.planned_child_start_beijing)
        if planned_dt is None:
            continue
        child_id = str(action["child_id"])
        child_dir = automations_root / child_id
        suffix = 1
        while child_dir.exists():
            child_dir = automations_root / f"{child_id}-{suffix}"
            suffix += 1
        child_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "version": 1,
            "id": child_dir.name,
            "kind": "cron",
            "name": f"{CHILD_NAME_PREFIX} {event.ticker} {event.company} {event.report_date}",
            "prompt": _child_prompt(event, template),
            "status": "ACTIVE",
            "rrule": _make_one_shot_rrule(planned_dt),
            "model": "gpt-5.5",
            "reasoning_effort": "xhigh",
            "execution_environment": "local",
            "cwds": [str(project_root)],
            "created_at": run_ms,
            "updated_at": run_ms,
        }
        _write_toml(child_dir / "automation.toml", data, backup_tag=backup_tag)
        changed.append(str(data["id"]))

    return {"applied": True, "changed": changed, "backups": backups}


def _preflight(project_root: Path, zijin_root: Path, automations_root: Path) -> list[dict[str, Any]]:
    problems: list[dict[str, Any]] = []
    required = {
        "project_root": project_root,
        "zijin_root": zijin_root,
        "earnings_skill": project_root / "skills" / "earnings-call-investment-analyst",
        "automations_root": automations_root,
    }
    for label, path in required.items():
        if not path.exists():
            problems.append({"problem": "missing_path", "label": label, "path": str(path)})
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic guardrail for earnings-call parent automation.")
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT_ROOT)
    parser.add_argument("--zijin-root", type=Path, default=DEFAULT_ZIJIN_ROOT)
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME") or DEFAULT_CODEX_HOME))
    parser.add_argument("--lookahead-days", type=int, default=5)
    parser.add_argument("--start-date-offset-days", type=int, default=-1)
    parser.add_argument("--window-hours", type=int, default=72)
    parser.add_argument("--now", help="Override Beijing now, format YYYY-MM-DD HH:MM")
    parser.add_argument("--apply-mechanical", action="store_true", help="Apply deterministic TOML create/update/pause actions.")
    parser.add_argument("--output", choices=["json", "text"], default="json")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    zijin_root = args.zijin_root.resolve()
    automations_root = (args.codex_home / "automations").resolve()
    now = _parse_beijing_time(args.now) if args.now else dt.datetime.now(BEIJING_TZ).replace(second=0, microsecond=0)
    if now is None:
        raise SystemExit("--now must use format YYYY-MM-DD HH:MM")
    window_end = now + dt.timedelta(hours=args.window_hours)
    run_ms = int(now.timestamp() * 1000)
    backup_tag = now.strftime("%Y%m%d-%H%M%S")

    preflight = _preflight(project_root, zijin_root, automations_root)
    if preflight:
        print(json.dumps({"status": "environment_preflight_failed", "problems": preflight}, ensure_ascii=False, indent=2))
        return 2

    try:
        _, GlobalEarningsCalendarService, build_oligarch_universe, market_from_ticker = _load_service(zijin_root)
        import requests  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {"status": "environment_preflight_failed", "problems": [{"problem": "import_failed", "detail": str(exc)}]},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    service = GlobalEarningsCalendarService()
    today = dt.date.today() + dt.timedelta(days=args.start_date_offset_days)
    raw_events = service.load_events(today=today, lookahead_days=args.lookahead_days, allow_network=False)
    planned_events = [_plan_event(event, market_from_ticker) for event in raw_events]
    future_events = [
        event
        for event in planned_events
        if (planned_dt := _parse_beijing_time(event.planned_child_start_beijing))
        and now <= planned_dt <= window_end
    ]
    past_events = [
        event
        for event in planned_events
        if (planned_dt := _parse_beijing_time(event.planned_child_start_beijing)) and planned_dt < now
    ]

    universe = build_oligarch_universe()
    mapping_errors = _validate_candidate_mapping(future_events, universe, market_from_ticker)
    children, child_scan_problems = _scan_children(automations_root)
    actions, blockers = _build_action_plan(future_events, children, now)
    review_items = _review_items(future_events)

    status = "ok"
    if mapping_errors:
        status = "candidate_mapping_failed"
    elif child_scan_problems or blockers:
        status = "mechanical_guardrail_blocked"

    apply_result: dict[str, Any] = {"applied": False}
    if args.apply_mechanical and status == "ok":
        apply_result = _apply_actions(actions, future_events, children, automations_root, project_root, run_ms, backup_tag)
        children, child_scan_problems = _scan_children(automations_root)
        actions, blockers = _build_action_plan(future_events, children, now)
        if child_scan_problems or blockers:
            status = "post_apply_validation_failed"

    duplicate_task_keys: dict[str, list[str]] = {}
    duplicate_ticker_dates: dict[str, list[str]] = {}
    key_index: dict[str, list[str]] = {}
    ticker_date_index: dict[str, list[str]] = {}
    active_with_memory: list[str] = []
    active_past: list[str] = []
    bad_rrules: list[str] = []
    for child in children:
        child_id = str(child.data.get("id"))
        key_index.setdefault(child.task_key, []).append(child_id)
        ticker_date_index.setdefault(f"{child.ticker}|{child.report_date}", []).append(child_id)
        if str(child.data.get("status")) == "ACTIVE" and child.has_memory:
            active_with_memory.append(child_id)
        if str(child.data.get("status")) == "ACTIVE" and child.planned_dt and child.planned_dt < now:
            active_past.append(child_id)
        if not child.rrule_ok:
            bad_rrules.append(child_id)
    duplicate_task_keys = {key: ids for key, ids in key_index.items() if key and len(ids) > 1}
    duplicate_ticker_dates = {key: ids for key, ids in ticker_date_index.items() if key and len(ids) > 1}

    report = {
        "status": status,
        "mode": "apply_mechanical" if args.apply_mechanical else "dry_run",
        "now_beijing": _format_beijing_time(now),
        "window_end_beijing": _format_beijing_time(window_end),
        "calendar_read": {
            "today_arg": str(today),
            "lookahead_days": args.lookahead_days,
            "allow_network": False,
            "event_count": len(raw_events),
            "future_candidate_count": len(future_events),
            "past_event_count": len(past_events),
        },
        "future_candidates": [asdict(event) for event in future_events],
        "review_items": review_items,
        "mapping_errors": mapping_errors,
        "child_scan_problems": child_scan_problems,
        "blockers": blockers,
        "actions": actions,
        "apply_result": apply_result,
        "final_validation": {
            "child_count": len(children),
            "bad_rrules": bad_rrules,
            "active_with_memory": active_with_memory,
            "active_past": active_past,
            "duplicate_task_keys": duplicate_task_keys,
            "duplicate_ticker_dates": duplicate_ticker_dates,
        },
        "touch_contract": {
            "refresh_events_called": False,
            "confirmed_event_writeback_attempted": False,
            "trade_dates_touched": False,
            "market_calendar_refresh_touched": False,
        },
    }

    if args.output == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"status: {report['status']}")
        print(f"window: {report['now_beijing']} -> {report['window_end_beijing']}")
        print(f"future candidates: {len(future_events)}")
        print(f"review items: {len(review_items)}")
        print(f"create/update/pause: {len(actions['create'])}/{len(actions['update'])}/{len(actions['pause'])}")
        print(f"bad rrules: {len(bad_rrules)}")
    return 0 if status == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())

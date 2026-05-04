#!/usr/bin/env python3
"""Build a standard earnings evidence pack.

The pack merges source discovery, webcast assets, transcript metadata, and
optional actuals/guidance/consensus JSON files into a single evidence layer.
It does not replace analyst judgment; it makes the source basis explicit.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import urllib.parse
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
OFFICIAL_EVENT_DOMAINS = {
    "events.q4inc.com",
    "q4cdn.com",
    "event.on24.com",
    "event.webcasts.com",
    "viavid.webcasts.com",
    "services.choruscall.com",
    "edge.media-server.com",
    "globalmeet.webcasts.com",
}
REGULATORY_DOMAINS = {
    "sec.gov",
    "www.sec.gov",
}
THIRD_PARTY_AUDIO_DOMAINS = {
    "files.quartr.com",
}
THIRD_PARTY_TRANSCRIPT_DOMAINS = {
    "stockanalysis.com",
    "www.stockanalysis.com",
    "fool.com",
    "www.fool.com",
    "seekingalpha.com",
    "www.seekingalpha.com",
    "benzinga.com",
    "www.benzinga.com",
    "alphaspread.com",
    "www.alphaspread.com",
    "earningscall.biz",
    "www.earningscall.biz",
}
REPLAY_ENTRY_DOMAINS = {
    "app.webinar.net",
    "events.q4inc.com",
    "attendees.events.q4inc.com",
}
RELEVANT_ASSET_CATEGORIES = {
    "audio",
    "video",
    "playlist",
    "subtitle",
    "transcript_or_subtitle",
    "document",
    "json",
    "video_or_replay",
}


def load_json(path: str | None) -> Any:
    if not path:
        return None
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(str(file_path))
    return json.loads(file_path.read_text(encoding="utf-8"))


def read_text(path: str | None, max_chars: int = 12000) -> str:
    if not path:
        return ""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(str(file_path))
    text = file_path.read_text(encoding="utf-8", errors="replace")
    return text[:max_chars]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def domain_of(url: str) -> str:
    if not url:
        return ""
    return urllib.parse.urlparse(url).netloc.lower()


def domain_matches(domain: str, domains: set[str]) -> bool:
    return domain in domains or any(domain.endswith(f".{known}") for known in domains)


def classify_source(url: str = "", title: str = "", company_domains: set[str] | None = None) -> str:
    company_domains = company_domains or set()
    domain = domain_of(url)
    lowered = f"{url} {title}".lower()

    if domain in REGULATORY_DOMAINS or domain.endswith(".sec.gov"):
        return "regulatory_filing"
    if domain in company_domains or any(domain.endswith(f".{d}") for d in company_domains):
        return "company_original"
    if domain_matches(domain, OFFICIAL_EVENT_DOMAINS):
        return "official_event_platform"
    if domain_matches(domain, THIRD_PARTY_AUDIO_DOMAINS) and any(
        token in lowered for token in ("audio-files", ".mp3", ".mpeg", ".m4a", ".wav")
    ):
        return "original_call_audio"
    if any(token in lowered for token in ("consensus", "estimate", "market data", "price", "volume")):
        return "market_data"
    if domain_matches(domain, THIRD_PARTY_TRANSCRIPT_DOMAINS) or any(
        token in lowered for token in ("transcript", "fool.com", "seekingalpha", "benzinga")
    ):
        return "third_party_transcript"
    if any(token in lowered for token in ("reuters", "bloomberg", "cnbc", "barron", "marketwatch")):
        return "media_or_analyst"
    return "unknown"


def infer_hosting_type(source_type: str, url: str = "", file_path: str = "") -> str:
    domain = domain_of(url)
    if source_type == "regulatory_filing":
        return "regulatory_hosted"
    if source_type == "company_original":
        return "company_hosted"
    if source_type == "official_event_platform":
        return "official_platform_hosted"
    if source_type in {"original_call_audio", "third_party_transcript", "media_or_analyst"}:
        return "third_party_hosted" if url else "local_derivative"
    if domain_matches(domain, THIRD_PARTY_AUDIO_DOMAINS | THIRD_PARTY_TRANSCRIPT_DOMAINS):
        return "third_party_hosted"
    if not url and file_path:
        return "local_derivative"
    return "unknown"


def is_relevant_webcast_asset(category: str, url: str) -> bool:
    if category in RELEVANT_ASSET_CATEGORIES:
        return True
    domain = domain_of(url)
    lowered = url.lower()
    if category == "other" and (domain_matches(domain, REPLAY_ENTRY_DOMAINS) or "webinar" in lowered):
        return True
    return False


def resolved_path_key(path: str) -> str:
    if not path:
        return ""
    try:
        return str(Path(path).expanduser().resolve()).casefold()
    except Exception:
        return path.replace("\\", "/").casefold()


def find_source_by_file_path(sources: list[dict[str, Any]], path: str) -> dict[str, Any] | None:
    target = resolved_path_key(path)
    if not target:
        return None
    for source in sources:
        file_path = source.get("file_path", "")
        if file_path and resolved_path_key(file_path) == target:
            return source
    return None


def source_id(index: int) -> str:
    return f"S{index:03d}"


def add_source(
    sources: list[dict[str, Any]],
    seen: dict[tuple[str, str], str],
    title: str,
    source_type: str,
    url: str = "",
    file_path: str = "",
    retrieved_at: str = "",
    publisher: str = "",
    notes: str = "",
    hosting_type: str = "",
    origin_source_id: str = "",
    content_origin: str = "",
) -> str:
    key = (url or "", file_path or "")
    if key in seen:
        return seen[key]

    sid = source_id(len(sources) + 1)
    item: dict[str, Any] = {
        "id": sid,
        "title": title,
        "source_type": source_type,
        "url": url,
        "file_path": file_path,
        "retrieved_at": retrieved_at,
        "publisher": publisher,
        "notes": notes,
        "hosting_type": hosting_type or infer_hosting_type(source_type, url, file_path),
    }
    if origin_source_id:
        item["origin_source_id"] = origin_source_id
    if content_origin:
        item["content_origin"] = content_origin
    if file_path:
        path = Path(file_path)
        if path.exists() and path.is_file():
            item["sha256"] = sha256_file(path)
            item["bytes"] = path.stat().st_size
    sources.append(item)
    seen[key] = sid
    return sid


def parse_kv(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Use key=value format.")
    key, val = value.split("=", 1)
    return key.strip(), val.strip()


def parse_domains(values: list[str]) -> set[str]:
    domains: set[str] = set()
    for value in values:
        for part in value.split(","):
            cleaned = part.strip().lower()
            if cleaned:
                domains.add(cleaned)
    return domains


def normalize_manual_sources(values: list[str]) -> list[dict[str, str]]:
    items = []
    for value in values:
        fields: dict[str, str] = {}
        for segment in value.split("|"):
            key, val = parse_kv(segment)
            fields[key] = val
        items.append(fields)
    return items


def build_sources(
    source_inventory: dict[str, Any] | None,
    webcast_assets: dict[str, Any] | None,
    transcript_manifest: dict[str, Any] | None,
    transcript_path: str | None,
    manual_sources: list[dict[str, str]],
    company_domains: set[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    sources: list[dict[str, Any]] = []
    seen: dict[tuple[str, str], str] = {}
    gaps: list[str] = []

    if source_inventory:
        retrieved_at = source_inventory.get("retrieved_at", "")
        if not source_inventory.get("sec_company"):
            gaps.append("SEC company mapping was not found or not applicable.")

        for filing in source_inventory.get("sec_filings", []):
            url = filing.get("url", "")
            title = " ".join(
                part for part in [
                    filing.get("form", ""),
                    filing.get("filingDate", ""),
                    filing.get("primaryDocDescription") or filing.get("primaryDocument") or "",
                ] if part
            )
            add_source(
                sources,
                seen,
                title=title or "SEC filing",
                source_type="regulatory_filing",
                url=url,
                retrieved_at=retrieved_at,
                publisher="SEC",
                notes="Relevant SEC filing from source inventory.",
            )

    if webcast_assets:
        input_url = webcast_assets.get("input_url", "")
        retrieved_at = webcast_assets.get("retrieved_at", "")
        if input_url:
            input_source_type = classify_source(input_url, "webcast replay transcript", company_domains)
            add_source(
                sources,
                seen,
                title="Inspected webcast or transcript page",
                source_type=input_source_type,
                url=input_url,
                file_path=webcast_assets.get("page_path", ""),
                retrieved_at=retrieved_at,
                publisher=domain_of(input_url),
                notes="Input webcast page inspected for replay assets.",
            )

        for asset in webcast_assets.get("assets", []):
            category = asset.get("category", "asset")
            url = asset.get("url", "")
            if not is_relevant_webcast_asset(str(category), str(url)):
                continue
            download = asset.get("download") or {}
            file_path = download.get("path", "") if isinstance(download, dict) else ""
            source_type = classify_source(url, category, company_domains)
            add_source(
                sources,
                seen,
                title=f"Webcast asset: {category}",
                source_type=source_type,
                url=url,
                file_path=file_path,
                retrieved_at=retrieved_at,
                publisher=domain_of(url),
                notes=f"Discovered from webcast page; category={category}.",
            )

    if transcript_manifest:
        origin_source = find_source_by_file_path(
            sources,
            transcript_manifest.get("media_path", "") or transcript_manifest.get("input", ""),
        )
        origin_source_type = (origin_source or {}).get("source_type") or classify_source(
            transcript_manifest.get("input", ""),
            "audio transcription input",
            company_domains,
        )
        if origin_source_type == "unknown":
            origin_source_type = "unknown"
        origin_source_id = (origin_source or {}).get("id", "")
        origin_hosting = (origin_source or {}).get("hosting_type", "")
        origin_note = f" Origin source: {origin_source_id}." if origin_source_id else ""
        transcript_file = transcript_manifest.get("transcript_path") or transcript_path or ""
        if transcript_file:
            add_source(
                sources,
                seen,
                title="Audio transcription output",
                source_type=origin_source_type,
                file_path=transcript_file,
                retrieved_at=transcript_manifest.get("created_at", ""),
                publisher=transcript_manifest.get("provider", ""),
                notes="Generated from replay audio or video; source type inherited from the input media." + origin_note,
                hosting_type="local_derivative",
                origin_source_id=origin_source_id,
                content_origin=(origin_source or {}).get("content_origin", "") or "call_audio",
            )
        audio_path = transcript_manifest.get("audio_path", "")
        if audio_path:
            add_source(
                sources,
                seen,
                title="Extracted 16 kHz mono call audio",
                source_type=origin_source_type,
                file_path=audio_path,
                retrieved_at=transcript_manifest.get("created_at", ""),
                publisher="local transcription pipeline",
                notes="Prepared audio file for transcription; source type inherited from the input media." + origin_note,
                hosting_type="local_derivative" if origin_hosting != "official_platform_hosted" else "official_platform_derivative",
                origin_source_id=origin_source_id,
                content_origin=(origin_source or {}).get("content_origin", "") or "call_audio",
            )
    elif transcript_path:
        add_source(
            sources,
            seen,
            title="Transcript file",
            source_type="unknown",
            file_path=transcript_path,
            notes="User-provided transcript path.",
        )

    for item in manual_sources:
        url = item.get("url", "")
        file_path = item.get("file", "") or item.get("file_path", "")
        title = item.get("title", "") or item.get("label", "") or url or file_path
        explicit_type = item.get("type", "")
        add_source(
            sources,
            seen,
            title=title,
            source_type=explicit_type or classify_source(url, title, company_domains),
            url=url,
            file_path=file_path,
            publisher=item.get("publisher", ""),
            notes=item.get("notes", "Manual source supplied to pack builder."),
            hosting_type=item.get("hosting_type", "") or item.get("hosting", ""),
            origin_source_id=item.get("origin_source_id", ""),
            content_origin=item.get("content_origin", ""),
        )

    return sources, gaps


def company_original_status(sources: list[dict[str, Any]], gaps: list[str]) -> str:
    has_company = any(source.get("source_type") == "company_original" for source in sources)
    has_official_event = any(source.get("source_type") == "official_event_platform" for source in sources)
    has_regulatory = any(source.get("source_type") == "regulatory_filing" for source in sources)
    if has_company and (has_official_event or has_regulatory):
        return "found"
    if has_company or has_official_event or has_regulatory:
        return "partial"
    if gaps:
        return "missing"
    return "unavailable"


def source_ids_by_type(sources: list[dict[str, Any]], source_type: str) -> list[str]:
    return [source["id"] for source in sources if source.get("source_type") == source_type]


def source_ids_by_hosting_type(sources: list[dict[str, Any]], hosting_type: str) -> list[str]:
    return [source["id"] for source in sources if source.get("hosting_type") == hosting_type]


def default_gaps(status: str, sources: list[dict[str, Any]], raw_gaps: list[str]) -> list[dict[str, str]]:
    gaps = [
        {
            "gap": gap,
            "impact": "Source discovery may be incomplete.",
            "severity": "medium",
            "next_step": "Verify manually.",
        }
        for gap in raw_gaps
    ]
    if status in {"missing", "unavailable"}:
        gaps.append(
            {
                "gap": "No company original source was identified.",
                "impact": "Reported facts should be treated as provisional until official company materials are checked.",
                "severity": "high",
                "next_step": "Search the company investor-relations site and official filing archive.",
            }
        )
    if not any(source.get("source_type") == "official_event_platform" for source in sources):
        gaps.append(
            {
                "gap": "No official webcast or replay source was identified.",
                "impact": "Conference-call takeaways may rely on third-party transcript or secondary sources.",
                "severity": "medium",
                "next_step": "Find the company-hosted webcast page or event platform replay.",
            }
        )
    if any(
        source.get("source_type") == "original_call_audio"
        and source.get("hosting_type") == "third_party_hosted"
        for source in sources
    ):
        gaps.append(
            {
                "gap": "Complete original call audio is third-party hosted.",
                "impact": "Call wording can be checked against the recording, but the hosting path is not company-hosted or official-event hosted.",
                "severity": "low",
                "next_step": "Use the official IR event page, release, or filing as the verification anchor and label the audio hosting path.",
            }
        )
    return gaps


def build_markdown(pack: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Earnings Evidence Pack")
    lines.append("")
    lines.append(f"- Company: {pack.get('company') or 'n/a'}")
    lines.append(f"- Ticker: {pack.get('ticker') or 'n/a'}")
    lines.append(f"- Quarter: {pack.get('quarter') or 'n/a'}")
    lines.append(f"- Fiscal year: {pack.get('fiscal_year') or 'n/a'}")
    lines.append(f"- Company original status: {pack.get('company_original_status')}")
    lines.append(f"- Created at: {pack.get('created_at')}")
    lines.append("")
    lines.append("## Source Policy")
    lines.append("")
    lines.append("Company-hosted original materials and official filings are the primary evidence layer. Third-party transcripts, media, and analyst notes are supporting evidence only.")
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    lines.append("| ID | Type | Hosting | Title | URL/File |")
    lines.append("|---|---|---|---|---|")
    for source in pack.get("sources", []):
        loc = source.get("url") or source.get("file_path") or ""
        lines.append(
            f"| {source.get('id')} | {source.get('source_type')} | {source.get('hosting_type', '')} | {source.get('title')} | {loc} |"
        )
    lines.append("")
    lines.append("## Gaps")
    lines.append("")
    gaps = pack.get("gaps", [])
    if gaps:
        for gap in gaps:
            lines.append(f"- [{gap.get('severity')}] {gap.get('gap')} Impact: {gap.get('impact')} Next: {gap.get('next_step')}")
    else:
        lines.append("- No material source gaps recorded.")
    lines.append("")
    lines.append("## Transcript Preview")
    lines.append("")
    preview = pack.get("transcript", {}).get("preview", "")
    lines.append(preview if preview else "No transcript preview available.")
    lines.append("")
    lines.append("## Analyst Fill-In Sections")
    lines.append("")
    lines.append("### Actuals")
    lines.append(json.dumps(pack.get("actuals", {}), indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("### Guidance")
    lines.append(json.dumps(pack.get("guidance", {}), indent=2, ensure_ascii=False))
    lines.append("")
    lines.append("### Consensus")
    lines.append(json.dumps(pack.get("consensus", {}), indent=2, ensure_ascii=False))
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a standard earnings evidence pack.")
    parser.add_argument("--ticker", default="", help="Ticker symbol.")
    parser.add_argument("--company", default="", help="Company name.")
    parser.add_argument("--quarter", default="", help="Quarter label.")
    parser.add_argument("--fiscal-year", default="", help="Fiscal year.")
    parser.add_argument("--company-domain", action="append", default=[], help="Company IR or corporate domain. May be repeated or comma-separated.")
    parser.add_argument("--source-inventory", default="", help="Path to source_inventory.json.")
    parser.add_argument("--webcast-assets", default="", help="Path to webcast_assets.json.")
    parser.add_argument("--transcript-manifest", default="", help="Path to transcript_manifest.json.")
    parser.add_argument("--transcript", default="", help="Path to raw transcript text.")
    parser.add_argument("--actuals-json", default="", help="Optional JSON file for reported actuals.")
    parser.add_argument("--guidance-json", default="", help="Optional JSON file for guidance.")
    parser.add_argument("--consensus-json", default="", help="Optional JSON file for consensus.")
    parser.add_argument("--manual-source", action="append", default=[], help="Manual source as key=value|key=value, for example title=release|url=https://...|type=company_original.")
    parser.add_argument("--out-dir", default="artifacts/earnings_pack", help="Output directory.")
    args = parser.parse_args()

    company_domains = parse_domains(args.company_domain)
    manual_sources = normalize_manual_sources(args.manual_source)
    source_inventory = load_json(args.source_inventory)
    webcast_assets = load_json(args.webcast_assets)
    transcript_manifest = load_json(args.transcript_manifest)
    actuals = load_json(args.actuals_json) or {}
    guidance = load_json(args.guidance_json) or {}
    consensus = load_json(args.consensus_json) or {}
    transcript_text = read_text(args.transcript or (transcript_manifest or {}).get("transcript_path", ""))

    sources, raw_gaps = build_sources(
        source_inventory=source_inventory,
        webcast_assets=webcast_assets,
        transcript_manifest=transcript_manifest,
        transcript_path=args.transcript,
        manual_sources=manual_sources,
        company_domains=company_domains,
    )
    status = company_original_status(sources, raw_gaps)

    pack = {
        "schema_version": SCHEMA_VERSION,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "company": args.company or (source_inventory or {}).get("company", ""),
        "ticker": args.ticker or (source_inventory or {}).get("ticker", ""),
        "quarter": args.quarter or (source_inventory or {}).get("quarter", ""),
        "fiscal_year": args.fiscal_year or (source_inventory or {}).get("fiscal_year", ""),
        "company_original_status": status,
        "source_policy": {
            "primary_rule": "Use company-hosted original materials and official filings as the primary evidence layer whenever possible.",
            "official_source_ids": source_ids_by_type(sources, "company_original") + source_ids_by_type(sources, "regulatory_filing") + source_ids_by_type(sources, "official_event_platform"),
            "original_call_audio_ids": source_ids_by_type(sources, "original_call_audio"),
            "third_party_source_ids": source_ids_by_type(sources, "third_party_transcript") + source_ids_by_type(sources, "media_or_analyst"),
            "third_party_hosted_source_ids": source_ids_by_hosting_type(sources, "third_party_hosted"),
        },
        "sources": sources,
        "discovery": {
            "source_inventory_path": args.source_inventory,
            "search_queries": (source_inventory or {}).get("search_queries", []),
        },
        "webcast": {
            "webcast_assets_path": args.webcast_assets,
            "asset_count": len((webcast_assets or {}).get("assets", [])),
        },
        "transcript": {
            "transcript_path": args.transcript or (transcript_manifest or {}).get("transcript_path", ""),
            "transcript_manifest_path": args.transcript_manifest,
            "preview": transcript_text[:3000],
        },
        "actuals": actuals,
        "guidance": guidance,
        "consensus": consensus,
        "call_takeaways": [],
        "risk_flags": [],
        "evidence_ledger": [],
        "gaps": default_gaps(status, sources, raw_gaps),
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "evidence_pack.json"
    md_path = out_dir / "evidence_pack.md"
    json_path.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(build_markdown(pack), encoding="utf-8")

    print(str(md_path))
    print(str(json_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Extract candidate media and data assets from an earnings webcast page.

The script saves the original page HTML, scans the page and selected linked
scripts, and writes an inventory of candidate audio, video, transcript,
subtitle, JSON, playlist, and script URLs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


DEFAULT_USER_AGENT = os.environ.get(
    "EARNINGS_FETCH_USER_AGENT",
    "earnings-call-investment-analyst/0.1",
)
URL_RE = re.compile(r"https?:\\?/\\?/[^\"'<>\s)]+", re.IGNORECASE)
ATTR_RE = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
ASSET_EXTENSIONS = {
    ".mp3": "audio",
    ".m4a": "audio",
    ".wav": "audio",
    ".aac": "audio",
    ".mp4": "video",
    ".mov": "video",
    ".webm": "video",
    ".m3u8": "playlist",
    ".mpd": "playlist",
    ".vtt": "subtitle",
    ".srt": "subtitle",
    ".ttml": "subtitle",
    ".json": "json",
    ".pdf": "document",
    ".html": "html",
    ".htm": "html",
    ".js": "script",
}
PLATFORM_HINTS = {
    "events.q4inc.com": "q4inc",
    "q4cdn.com": "q4inc",
    "event.on24.com": "on24",
    "event.webcasts.com": "notified",
    "viavid.webcasts.com": "notified",
    "edge.media-server.com": "intrado",
}
Q4INC_EVENT_ID_RE = re.compile(r"(?:attendee|event)/([0-9]{6,})", re.IGNORECASE)


def fetch_bytes(url: str, user_agent: str, timeout: int = 30) -> bytes:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def decode_text(data: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def clean_candidate_url(raw: str, base_url: str) -> str | None:
    value = html.unescape(raw).strip().strip("\"'`<>),;")
    value = value.replace("\\/", "/")
    if not value:
        return None
    if value.startswith("//"):
        parsed_base = urllib.parse.urlparse(base_url)
        value = f"{parsed_base.scheme}:{value}"
    if value.startswith(("http://", "https://")):
        return value
    if value.startswith(("/", "./", "../")):
        return urllib.parse.urljoin(base_url, value)
    return None


def iter_urls_from_text(text: str, base_url: str) -> Iterable[str]:
    for match in URL_RE.finditer(text):
        cleaned = clean_candidate_url(match.group(0), base_url)
        if cleaned:
            yield cleaned


def iter_urls_from_json_like(value: object, base_url: str) -> Iterable[str]:
    """Recursively extract URL-looking strings from decoded event JSON."""
    if isinstance(value, str):
        cleaned = clean_candidate_url(value, base_url)
        if cleaned:
            yield cleaned
        for url in iter_urls_from_text(value, base_url):
            if url != cleaned:
                yield url
        return
    if isinstance(value, list):
        for item in value:
            yield from iter_urls_from_json_like(item, base_url)
        return
    if isinstance(value, dict):
        for item in value.values():
            yield from iter_urls_from_json_like(item, base_url)
        return


def categorize_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.lower()
    ext = Path(path).suffix
    if ext in ASSET_EXTENSIONS:
        return ASSET_EXTENSIONS[ext]

    lowered = url.lower()
    if any(token in lowered for token in ("audio", "audio-files", "mp3", "m4a", ".mpeg")):
        return "audio"
    if any(token in lowered for token in ("video", "webcast", "replay", "mp4", "m3u8")):
        return "video_or_replay"
    if any(token in lowered for token in ("caption", "subtitle", "transcript", "vtt", "srt")):
        return "transcript_or_subtitle"
    if "event" in lowered and ("json" in lowered or "/api/" in lowered):
        return "json"
    return "other"


def detect_platform(url: str, text: str) -> str:
    domain = urllib.parse.urlparse(url).netloc.lower()
    for known_domain, platform in PLATFORM_HINTS.items():
        if domain == known_domain or domain.endswith(f".{known_domain}"):
            return platform

    lowered = text.lower()
    if "q4inc" in lowered or "q4cdn" in lowered:
        return "q4inc"
    if "on24" in lowered:
        return "on24"
    if "intrado" in lowered or "media-server.com" in lowered:
        return "intrado"
    return "generic"


def q4inc_candidate_urls(page_url: str, page_text: str) -> list[str]:
    candidates: list[str] = []
    event_ids = set(Q4INC_EVENT_ID_RE.findall(page_url))
    event_ids.update(Q4INC_EVENT_ID_RE.findall(page_text))
    for event_id in sorted(event_ids):
        candidates.extend(
            [
                f"https://events.q4inc.com/api/events/{event_id}",
                f"https://events.q4inc.com/attendee/api/events/{event_id}",
                f"https://events.q4inc.com/attendee/{event_id}/guest",
                f"https://attendees.events.q4inc.com/rest/v1/event/{event_id}",
            ]
        )
    return candidates


def safe_filename_from_url(url: str, fallback: str) -> str:
    parsed = urllib.parse.urlparse(url)
    name = Path(parsed.path).name or fallback
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name[:120] or fallback


def should_download(category: str, mode: str) -> bool:
    if mode == "all":
        return True
    if mode == "media":
        return category in {"audio", "video", "playlist", "subtitle", "transcript_or_subtitle", "video_or_replay"}
    return False


def download_asset(url: str, out_path: Path, user_agent: str, max_mb: int) -> dict[str, object]:
    data = fetch_bytes(url, user_agent, timeout=60)
    size_mb = len(data) / (1024 * 1024)
    if size_mb > max_mb:
        return {"downloaded": False, "reason": f"asset exceeds max size: {size_mb:.1f} MB"}
    out_path.write_bytes(data)
    return {"downloaded": True, "path": str(out_path), "bytes": len(data)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract candidate assets from an earnings webcast page.")
    parser.add_argument("--url", required=True, help="Official webcast or replay page URL.")
    parser.add_argument("--out-dir", default="artifacts/webcast_assets", help="Output directory.")
    parser.add_argument("--fetch-scripts", action="store_true", help="Fetch linked JavaScript files and scan them too.")
    parser.add_argument("--skip-adapter-fetch", action="store_true", help="Do not fetch platform-adapter candidate URLs.")
    parser.add_argument("--script-limit", type=int, default=25, help="Maximum linked scripts to fetch.")
    parser.add_argument("--download", choices=["none", "media", "all"], default="none", help="Download discovered assets.")
    parser.add_argument("--max-download-mb", type=int, default=500, help="Maximum single-asset download size.")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="HTTP User-Agent header.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    raw_dir = out_dir / "raw"
    download_dir = out_dir / "downloads"
    raw_dir.mkdir(parents=True, exist_ok=True)
    download_dir.mkdir(parents=True, exist_ok=True)

    page_bytes = fetch_bytes(args.url, args.user_agent)
    page_text = decode_text(page_bytes)
    platform = detect_platform(args.url, page_text)
    page_path = raw_dir / "webcast_page.html"
    page_path.write_text(page_text, encoding="utf-8")

    texts: list[tuple[str, str]] = [("page", page_text)]
    page_urls = sorted(set(iter_urls_from_text(page_text, args.url)))
    adapter_candidates: list[str] = []
    if platform == "q4inc":
        adapter_candidates = q4inc_candidate_urls(args.url, page_text)
        page_urls = sorted(set(page_urls + adapter_candidates))
    script_urls = [u for u in page_urls if categorize_url(u) == "script"]

    fetched_scripts: list[dict[str, object]] = []
    if args.fetch_scripts:
        for index, script_url in enumerate(script_urls[: args.script_limit]):
            try:
                script_text = decode_text(fetch_bytes(script_url, args.user_agent))
                script_name = safe_filename_from_url(script_url, f"script_{index:03d}.js")
                script_path = raw_dir / script_name
                script_path.write_text(script_text, encoding="utf-8")
                texts.append((script_url, script_text))
                fetched_scripts.append({"url": script_url, "path": str(script_path)})
            except Exception as exc:
                fetched_scripts.append({"url": script_url, "error": repr(exc)})

    fetched_adapter_candidates: list[dict[str, object]] = []
    json_discovered_urls: list[str] = []
    if adapter_candidates and not args.skip_adapter_fetch:
        for index, adapter_url in enumerate(adapter_candidates):
            try:
                adapter_text = decode_text(fetch_bytes(adapter_url, args.user_agent))
                adapter_name = safe_filename_from_url(adapter_url, f"{platform}_adapter_{index:03d}.json")
                if "." not in adapter_name:
                    adapter_name = f"{adapter_name}.json"
                adapter_name = f"{index:03d}_{adapter_name}"
                adapter_path = raw_dir / adapter_name
                adapter_path.write_text(adapter_text, encoding="utf-8")
                texts.append((adapter_url, adapter_text))
                try:
                    adapter_json = json.loads(adapter_text)
                    for found_url in iter_urls_from_json_like(adapter_json, args.url):
                        json_discovered_urls.append(found_url)
                except json.JSONDecodeError:
                    pass
                fetched_adapter_candidates.append({"url": adapter_url, "path": str(adapter_path)})
            except Exception as exc:
                fetched_adapter_candidates.append({"url": adapter_url, "error": repr(exc)})

    discovered: dict[str, dict[str, object]] = {}
    for source, text in texts:
        for url in iter_urls_from_text(text, args.url):
            category = categorize_url(url)
            item = discovered.setdefault(
                url,
                {"url": url, "category": category, "sources": [], "download": None},
            )
            item["sources"].append(source)

    for url in adapter_candidates:
        category = categorize_url(url)
        item = discovered.setdefault(
            url,
            {"url": url, "category": category, "sources": [], "download": None},
        )
        item["sources"].append(f"{platform}_adapter")

    for url in json_discovered_urls:
        category = categorize_url(url)
        item = discovered.setdefault(
            url,
            {"url": url, "category": category, "sources": [], "download": None},
        )
        item["sources"].append(f"{platform}_event_json")

    for item in discovered.values():
        category = str(item["category"])
        if should_download(category, args.download):
            digest = hashlib.sha1(str(item["url"]).encode("utf-8")).hexdigest()[:8]
            name = f"{digest}_{safe_filename_from_url(str(item['url']), 'asset.bin')}"
            try:
                item["download"] = download_asset(str(item["url"]), download_dir / name, args.user_agent, args.max_download_mb)
            except Exception as exc:
                item["download"] = {"downloaded": False, "error": repr(exc)}

    assets = sorted(discovered.values(), key=lambda x: (str(x["category"]), str(x["url"])))
    inventory = {
        "input_url": args.url,
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "platform": platform,
        "adapter_candidates": adapter_candidates,
        "fetched_adapter_candidates": fetched_adapter_candidates,
        "page_path": str(page_path),
        "fetched_scripts": fetched_scripts,
        "assets": assets,
    }

    json_path = out_dir / "webcast_assets.json"
    json_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = ["# Webcast Asset Inventory", "", f"- URL: {args.url}", f"- Platform: {platform}", f"- Page: {page_path}", ""]
    md_lines.append("| Category | URL | Sources | Download |")
    md_lines.append("|---|---|---|---|")
    for item in assets:
        download = item.get("download") or {}
        if isinstance(download, dict) and download.get("path"):
            download_text = str(download["path"])
        elif isinstance(download, dict) and download.get("error"):
            download_text = "error"
        else:
            download_text = ""
        md_lines.append(
            f"| {item['category']} | {item['url']} | {', '.join(item['sources'])} | {download_text} |"
        )
    md_path = out_dir / "webcast_assets.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(str(md_path))
    print(str(json_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())

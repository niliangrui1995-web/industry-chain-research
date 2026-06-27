#!/usr/bin/env python3
"""Download and merge VTT caption segments from an HLS subtitle playlist."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_USER_AGENT = "earnings-call-investment-analyst/0.1"
MAX_PLAYLIST_BYTES = 5 * 1024 * 1024
MAX_SEGMENT_BYTES = 5 * 1024 * 1024
MAX_TOTAL_SEGMENT_BYTES = 100 * 1024 * 1024
MAX_SEGMENTS = 5000


class CaptionSizeError(ValueError):
    """Raised when caption downloads exceed local safety limits."""


def fetch_text(url: str, user_agent: str, max_bytes: int) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"unsupported URL scheme: {parsed.scheme or 'none'}")
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(request, timeout=60) as response:
                length = response.headers.get("Content-Length")
                if length and int(length) > max_bytes:
                    raise ValueError(f"response exceeds max size: {int(length)} bytes")
                data = bytearray()
                while True:
                    chunk = response.read(256 * 1024)
                    if not chunk:
                        return bytes(data).decode("utf-8", errors="replace")
                    data.extend(chunk)
                    if len(data) > max_bytes:
                        raise ValueError(f"response exceeds max size: {max_bytes} bytes")
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def playlist_segments(playlist_text: str, playlist_url: str) -> list[str]:
    urls: list[str] = []
    for raw_line in playlist_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(urllib.parse.urljoin(playlist_url, line))
    return urls


def playlist_duration_seconds(playlist_text: str) -> float:
    duration = 0.0
    for raw_line in playlist_text.splitlines():
        line = raw_line.strip()
        if not line.startswith("#EXTINF:"):
            continue
        value = line.split(":", 1)[1].split(",", 1)[0]
        try:
            duration += float(value)
        except ValueError:
            continue
    return duration


def checked_segment_size(current_total_bytes: int, segment_text: str) -> tuple[int, int]:
    segment_bytes = len(segment_text.encode("utf-8"))
    new_total = current_total_bytes + segment_bytes
    if new_total > MAX_TOTAL_SEGMENT_BYTES:
        raise CaptionSizeError(f"caption segments exceed total size limit: {MAX_TOTAL_SEGMENT_BYTES} bytes")
    return new_total, segment_bytes


def normalize_vtt_segment(text: str) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line == "WEBVTT" or line.startswith("X-TIMESTAMP-MAP="):
            continue
        lines.append(line)
    return lines


def vtt_to_plain_text(vtt_text: str) -> str:
    cleaned: list[str] = []
    seen: set[str] = set()
    for line in vtt_text.splitlines():
        value = line.strip()
        if not value or value == "WEBVTT":
            continue
        if "-->" in value:
            continue
        if re.fullmatch(r"\d+", value):
            continue
        if value in seen:
            continue
        seen.add(value)
        cleaned.append(value)
    return "\n".join(cleaned) + ("\n" if cleaned else "")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch and merge VTT captions from an HLS subtitle playlist.")
    parser.add_argument("--playlist-url", required=True, help="HLS subtitle playlist URL, usually subtitles.m3u8.")
    parser.add_argument("--out-dir", default="artifacts/earnings_captions", help="Output directory.")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="HTTP User-Agent header.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    playlist_text = fetch_text(args.playlist_url, args.user_agent, MAX_PLAYLIST_BYTES)
    playlist_path = raw_dir / "subtitles.m3u8"
    playlist_path.write_text(playlist_text, encoding="utf-8")

    segments = playlist_segments(playlist_text, args.playlist_url)
    if len(segments) > MAX_SEGMENTS:
        raise ValueError(f"playlist has too many segments: {len(segments)}")
    is_complete_playlist = "#EXT-X-ENDLIST" in playlist_text
    duration_seconds = playlist_duration_seconds(playlist_text)
    merged_lines = ["WEBVTT", ""]
    segment_records = []
    total_segment_bytes = 0
    for index, segment_url in enumerate(segments):
        try:
            segment_text = fetch_text(segment_url, args.user_agent, MAX_SEGMENT_BYTES)
            total_segment_bytes, segment_bytes = checked_segment_size(total_segment_bytes, segment_text)
            segment_path = raw_dir / f"segment_{index:04d}.vtt"
            segment_path.write_text(segment_text, encoding="utf-8")
            merged_lines.extend(normalize_vtt_segment(segment_text))
            merged_lines.append("")
            segment_records.append({"url": segment_url, "path": str(segment_path), "status": "ok", "bytes": segment_bytes})
        except Exception as exc:
            segment_records.append({"url": segment_url, "status": "error", "error": repr(exc)})
            if isinstance(exc, CaptionSizeError):
                break

    merged_vtt = "\n".join(merged_lines).strip() + "\n"
    merged_vtt_path = out_dir / "captions_merged.vtt"
    plain_text_path = out_dir / "captions_plain.txt"
    manifest_path = out_dir / "captions_manifest.json"
    merged_vtt_path.write_text(merged_vtt, encoding="utf-8")
    plain_text_path.write_text(vtt_to_plain_text(merged_vtt), encoding="utf-8")

    manifest = {
        "playlist_url": args.playlist_url,
        "playlist_path": str(playlist_path),
        "merged_vtt_path": str(merged_vtt_path),
        "plain_text_path": str(plain_text_path),
        "playlist_complete": is_complete_playlist,
        "warning": "" if is_complete_playlist else "Playlist has no EXT-X-ENDLIST; it may be a sliding live/DVR window rather than the full call captions.",
        "playlist_duration_seconds": duration_seconds,
        "segment_count": len(segments),
        "downloaded_count": sum(1 for item in segment_records if item["status"] == "ok"),
        "segment_bytes_total": total_segment_bytes,
        "segments": segment_records,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(str(manifest_path))
    print(str(merged_vtt_path))
    print(str(plain_text_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())

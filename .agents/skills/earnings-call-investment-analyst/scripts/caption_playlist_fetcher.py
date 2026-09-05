#!/usr/bin/env python3
"""Download and merge VTT caption segments from an HLS subtitle playlist."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
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
    lines = playlist_text.splitlines()
    if not lines or lines[0].strip() != "#EXTM3U":
        raise ValueError("播放列表缺少 EXTM3U 文件头。")
    duration = 0.0
    pending_segment = False
    ended = False
    for raw_line in lines[1:]:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("#EXT-X-GAP", "#EXT-X-BYTERANGE", "#EXT-X-KEY:", "#EXT-X-MAP:", "#EXT-X-STREAM-INF:", "#EXT-X-PART:")):
            raise ValueError("播放列表存在缺段标记或不支持的分段格式。")
        if line.startswith("#EXTINF:"):
            if pending_segment or ended:
                raise ValueError("播放列表的 EXTINF 与分段地址顺序无效。")
            value = float(line.split(":", 1)[1].split(",", 1)[0])
            if not math.isfinite(value) or value < 0:
                raise ValueError("播放列表的 EXTINF 时长必须为有限非负数。")
            duration += value
            pending_segment = True
        elif line == "#EXT-X-ENDLIST":
            ended = True
        elif not line.startswith("#"):
            if not pending_segment or ended:
                raise ValueError("字幕分段缺少 EXTINF 或位于 ENDLIST 之后。")
            pending_segment = False
    if pending_segment or not math.isfinite(duration):
        raise ValueError("播放列表存在悬空 EXTINF 或非法总时长。")
    return duration


def checked_segment_size(current_total_bytes: int, segment_text: str) -> tuple[int, int]:
    segment_bytes = len(segment_text.encode("utf-8"))
    new_total = current_total_bytes + segment_bytes
    if new_total > MAX_TOTAL_SEGMENT_BYTES:
        raise CaptionSizeError(f"caption segments exceed total size limit: {MAX_TOTAL_SEGMENT_BYTES} bytes")
    return new_total, segment_bytes


def normalize_vtt_segment(text: str) -> list[str]:
    lines = []
    for index, raw_line in enumerate(text.lstrip("\ufeff").splitlines()):
        line = raw_line.rstrip()
        if not line or index == 0 or line.startswith("X-TIMESTAMP-MAP="):
            continue
        lines.append(line)
    return lines


def validate_vtt_segment(text: str) -> None:
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or not re.fullmatch(r"WEBVTT(?:[ \t].*)?", lines[0]) or "-->" in lines[0]:
        raise ValueError("分段响应不是有效的 WEBVTT 字幕，可能返回了错误页。")
    index = 1
    while index < len(lines) and lines[index].startswith("X-TIMESTAMP-MAP="):
        index += 1
    if index < len(lines) and lines[index].strip():
        raise ValueError("WEBVTT 文件头与字幕正文缺少空行。")
    timestamp = r"(?:\d{2,}:)?[0-5]\d:[0-5]\d\.\d{3}"
    timing = re.compile(rf"({timestamp})[ \t]+-->[ \t]+({timestamp})(?:[ \t]+.*)?")

    def seconds(value: str) -> float:
        parts = [float(part) for part in value.split(":")]
        return sum(part * 60 ** power for power, part in enumerate(reversed(parts)))

    for block in re.split(r"\n[ \t]*\n", "\n".join(lines[index:]).strip()):
        if not block:
            continue
        cue = block.splitlines()
        if re.fullmatch(r"NOTE(?:[ \t].*)?", cue[0]) or cue[0] in {"STYLE", "REGION"}:
            continue
        time_index = 0 if "-->" in cue[0] else 1
        match = timing.fullmatch(cue[time_index]) if time_index < len(cue) else None
        if match is None or seconds(match[1]) >= seconds(match[2]):
            raise ValueError("WEBVTT 字幕块缺少有效时间轴，不能确认为已下载字幕。")


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
    playlist_ended = any(line.strip() == "#EXT-X-ENDLIST" for line in playlist_text.splitlines())
    warnings = []
    try:
        duration_seconds = playlist_duration_seconds(playlist_text)
    except ValueError as exc:
        duration_seconds = None
        warnings.append(f"播放列表格式校验失败：{exc}")
    playlist_valid = duration_seconds is not None
    merged_lines = ["WEBVTT", ""]
    segment_records = []
    total_segment_bytes = 0
    for index, segment_url in enumerate(segments if playlist_valid else []):
        try:
            segment_text = fetch_text(segment_url, args.user_agent, MAX_SEGMENT_BYTES)
            validate_vtt_segment(segment_text)
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

    downloaded_count = sum(1 for item in segment_records if item["status"] == "ok")
    download_complete = playlist_valid and bool(segments) and downloaded_count == len(segments)
    playlist_complete = playlist_ended and download_complete
    if not playlist_ended:
        warnings.append("播放列表缺少 EXT-X-ENDLIST，可能仅为直播或回看滑动窗口。")
    if not segments:
        warnings.append("播放列表不含字幕分段。")
    elif not download_complete:
        warnings.append(f"字幕分段下载不完整：{downloaded_count}/{len(segments)}，合并结果仅供诊断。")

    manifest = {
        "playlist_url": args.playlist_url,
        "playlist_path": str(playlist_path),
        "merged_vtt_path": str(merged_vtt_path),
        "plain_text_path": str(plain_text_path),
        "playlist_ended": playlist_ended,
        "playlist_valid": playlist_valid,
        "download_complete": download_complete,
        "playlist_complete": playlist_complete,
        "warning": " ".join(warnings),
        "playlist_duration_seconds": duration_seconds,
        "segment_count": len(segments),
        "downloaded_count": downloaded_count,
        "segment_bytes_total": total_segment_bytes,
        "segments": segment_records,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")

    print(str(manifest_path))
    print(str(merged_vtt_path))
    print(str(plain_text_path))
    return 0 if playlist_complete else 1


if __name__ == "__main__":
    sys.exit(main())

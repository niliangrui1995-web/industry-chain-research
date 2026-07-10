#!/usr/bin/env python3
"""Prepare and transcribe earnings-call audio or video.

The script can download a URL, extract 16 kHz mono WAV audio with ffmpeg, and
transcribe it with either a local Whisper CLI or the OpenAI Python SDK.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_USER_AGENT = os.environ.get(
    "EARNINGS_FETCH_USER_AGENT",
    "earnings-call-investment-analyst/0.1",
)
DEFAULT_MAX_DOWNLOAD_MB = 2048
DEFAULT_FFMPEG_TIMEOUT_SECONDS = 1800


def is_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def safe_name_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    name = Path(parsed.path).name or "downloaded_media"
    cleaned = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in name)
    return cleaned or "downloaded_media"


def executable_candidates(name: str) -> list[Path]:
    candidates: list[Path] = []
    exe_name = name if name.lower().endswith(".exe") else f"{name}.exe"

    if name.lower().startswith("ffmpeg"):
        for env_name in ("FFMPEG", "FFMPEG_PATH"):
            value = os.environ.get(env_name)
            if value:
                candidates.append(Path(value))
        ffmpeg_bin = os.environ.get("FFMPEG_BIN")
        if ffmpeg_bin:
            candidates.append(Path(ffmpeg_bin) / exe_name)

        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            roots = [
                Path(local_appdata) / "Programs" / "ffmpeg",
                Path(local_appdata) / "Microsoft" / "WinGet" / "Packages",
            ]
            for root in roots:
                if root.exists():
                    candidates.extend(root.glob(f"**/{exe_name}"))

    scripts_dir = Path(sys.executable).resolve().parent
    candidates.append(scripts_dir / exe_name)
    candidates.append(scripts_dir / name)
    return candidates


def resolve_executable(name: str) -> str | None:
    configured = Path(name)
    if configured.exists():
        return str(configured)

    found = shutil.which(name)
    if found:
        return found

    for candidate in executable_candidates(name):
        if candidate.exists() and candidate.is_file():
            return str(candidate)
    return None


def download_url(url: str, out_dir: Path, user_agent: str, max_mb: int) -> Path:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"unsupported URL scheme: {parsed.scheme or 'none'}")
    target = out_dir / safe_name_from_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    max_bytes = max_mb * 1024 * 1024
    with urllib.request.urlopen(request, timeout=120) as response:
        length = response.headers.get("Content-Length")
        if length and int(length) > max_bytes:
            raise ValueError(f"download exceeds max size: {int(length)} bytes")
        total = 0
        with target.open("wb") as fh:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError(f"download exceeds max size: {max_bytes} bytes")
                fh.write(chunk)
    return target


def run_command(command: list[str], timeout: int | None = None) -> None:
    subprocess.run(command, check=True, timeout=timeout)


def extract_audio(ffmpeg: str, input_path: Path, output_path: Path, timeout: int) -> None:
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ]
    run_command(command, timeout=timeout)


def split_audio(
    ffmpeg: str,
    audio_path: Path,
    chunk_dir: Path,
    chunk_seconds: int,
    timeout: int,
) -> list[Path]:
    chunk_dir.mkdir(parents=True, exist_ok=True)
    pattern = chunk_dir / "chunk_%03d.wav"
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(audio_path),
        "-f",
        "segment",
        "-segment_time",
        str(chunk_seconds),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(pattern),
    ]
    run_command(command, timeout=timeout)
    return sorted(chunk_dir.glob("chunk_*.wav"))


def transcribe_with_whisper_cli(audio_path: Path, out_dir: Path, model: str, language: str | None) -> Path:
    whisper = resolve_executable("whisper")
    if not whisper:
        raise RuntimeError("The 'whisper' CLI was not found on PATH.")
    command = [
        whisper,
        str(audio_path),
        "--model",
        model,
        "--output_dir",
        str(out_dir),
        "--output_format",
        "all",
        "--task",
        "transcribe",
    ]
    if language:
        command.extend(["--language", language])
    run_command(command)
    txt_candidates = sorted(out_dir.glob("*.txt"))
    if not txt_candidates:
        raise RuntimeError("Whisper CLI finished but no .txt transcript was found.")
    return txt_candidates[0]


def transcribe_with_openai(chunks: list[Path], out_dir: Path, model: str, language: str | None) -> Path:
    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError("The OpenAI Python package is required for --provider openai.") from exc

    client = OpenAI()
    transcript_path = out_dir / "transcript_raw.txt"
    lines: list[str] = []
    for index, chunk in enumerate(chunks):
        with chunk.open("rb") as audio_file:
            kwargs = {
                "model": model,
                "file": audio_file,
                "response_format": "text",
            }
            if language:
                kwargs["language"] = language
            text = client.audio.transcriptions.create(**kwargs)
        lines.append(f"[chunk {index:03d} | file={chunk.name}]")
        lines.append(str(text).strip())
        lines.append("")
    transcript_path.write_text("\n".join(lines), encoding="utf-8")
    return transcript_path


def fmt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    sec, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}.{ms:03d}"


def fmt_vtt_time(seconds: float) -> str:
    return fmt_time(seconds)


def transcribe_with_faster_whisper(
    media_path: Path,
    out_dir: Path,
    model: str,
    language: str | None,
    initial_prompt: str,
    clip_timestamps: str,
    device: str,
    compute_type: str,
) -> Path:
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:
        raise RuntimeError(
            "The faster-whisper package is required for --provider faster-whisper. "
            "Install it in a Python 3.10/3.11 environment with: python -m pip install faster-whisper"
        ) from exc

    transcript_json = out_dir / "transcript_segments.json"
    transcript_txt = out_dir / "transcript_raw.txt"
    transcript_vtt = out_dir / "transcript_timestamped.vtt"

    requested_device = device
    requested_compute_type = compute_type
    if device == "auto":
        try:
            import ctranslate2

            device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        except Exception:
            device = "cpu"
    if compute_type == "auto":
        compute_type = "int8" if device == "cuda" else "int8"

    fallback_reason = ""
    try:
        whisper_model = WhisperModel(model, device=device, compute_type=compute_type)
    except Exception as exc:
        fallback_reason = repr(exc)
        if requested_device != "auto" and requested_compute_type != "auto":
            raise
        device = "cpu"
        compute_type = "int8"
        whisper_model = WhisperModel(model, device=device, compute_type=compute_type)
    kwargs: dict[str, Any] = {
        "task": "transcribe",
        "beam_size": 5,
        "best_of": 5,
        "vad_filter": True,
        "vad_parameters": {"min_silence_duration_ms": 500},
        "condition_on_previous_text": True,
    }
    if language:
        kwargs["language"] = language
    if initial_prompt:
        kwargs["initial_prompt"] = initial_prompt
    if clip_timestamps:
        kwargs["clip_timestamps"] = clip_timestamps

    def collect_segments(active_model: WhisperModel) -> tuple[Any, list[dict[str, Any]], list[str], list[str]]:
        segments_iter, info = active_model.transcribe(str(media_path), **kwargs)
        segments: list[dict[str, Any]] = []
        txt_lines: list[str] = []
        vtt_lines: list[str] = ["WEBVTT", ""]
        for index, segment in enumerate(segments_iter, start=1):
            text = segment.text.strip()
            item = {
                "id": index,
                "start": segment.start,
                "end": segment.end,
                "start_text": fmt_time(segment.start),
                "end_text": fmt_time(segment.end),
                "text": text,
            }
            segments.append(item)
            txt_lines.append(f"[{item['start_text']} - {item['end_text']}] {text}")
            vtt_lines.append(str(index))
            vtt_lines.append(f"{fmt_vtt_time(segment.start)} --> {fmt_vtt_time(segment.end)}")
            vtt_lines.append(text)
            vtt_lines.append("")
        return info, segments, txt_lines, vtt_lines

    try:
        info, segments, txt_lines, vtt_lines = collect_segments(whisper_model)
    except Exception as exc:
        if requested_device != "auto" or device != "cuda":
            raise
        fallback_reason = fallback_reason or repr(exc)
        device = "cpu"
        compute_type = "int8"
        whisper_model = WhisperModel(model, device=device, compute_type=compute_type)
        info, segments, txt_lines, vtt_lines = collect_segments(whisper_model)

    metadata = {
        "media_path": str(media_path),
        "model": model,
        "device": device,
        "compute_type": compute_type,
        "requested_device": requested_device,
        "requested_compute_type": requested_compute_type,
        "fallback_reason": fallback_reason,
        "language": getattr(info, "language", None),
        "language_probability": getattr(info, "language_probability", None),
        "duration": getattr(info, "duration", None),
        "segment_count": len(segments),
    }
    transcript_json.write_text(
        json.dumps({"metadata": metadata, "segments": segments}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    transcript_txt.write_text("\n".join(txt_lines) + ("\n" if txt_lines else ""), encoding="utf-8")
    transcript_vtt.write_text("\n".join(vtt_lines), encoding="utf-8")
    return transcript_txt


def print_dependency_check() -> int:
    checks: dict[str, Any] = {
        "ffmpeg": resolve_executable("ffmpeg"),
        "whisper_cli": resolve_executable("whisper"),
        "openai_package": False,
        "openai_api_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        "faster_whisper_package": False,
        "faster_whisper_cuda_devices": None,
    }
    try:
        import openai  # noqa: F401

        checks["openai_package"] = True
    except Exception:
        pass
    try:
        import faster_whisper  # noqa: F401

        checks["faster_whisper_package"] = True
        try:
            import ctranslate2

            checks["faster_whisper_cuda_devices"] = ctranslate2.get_cuda_device_count()
        except Exception:
            pass
    except Exception:
        pass
    print(json.dumps(checks, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and transcribe earnings-call audio or video.")
    parser.add_argument("input", nargs="?", help="Audio/video file path or URL.")
    parser.add_argument("--out-dir", default="artifacts/earnings_transcripts", help="Output directory.")
    parser.add_argument("--provider", choices=["none", "whisper-cli", "openai", "faster-whisper"], default="none", help="Transcription provider.")
    parser.add_argument("--model", default="", help="Provider model. Defaults to base for whisper-cli, small.en for faster-whisper, and gpt-4o-transcribe for openai.")
    parser.add_argument("--language", default="", help="Optional language code, for example en.")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable path.")
    parser.add_argument("--no-ffmpeg", action="store_true", help="For faster-whisper, transcribe the input media directly without extracting WAV.")
    parser.add_argument("--chunk-seconds", type=int, default=900, help="Chunk size for OpenAI transcription.")
    parser.add_argument("--keep-chunks", action="store_true", help="Keep split audio chunks.")
    parser.add_argument("--initial-prompt", default="", help="Optional domain vocabulary prompt for faster-whisper.")
    parser.add_argument("--clip-timestamps", default="", help="Optional faster-whisper clip timestamps, for example 0,120 for a smoke test.")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"], help="Device for faster-whisper.")
    parser.add_argument("--compute-type", default="auto", help="Compute type for faster-whisper, for example auto, int8, float16, or int8_float16.")
    parser.add_argument("--check-deps", action="store_true", help="Print transcription dependency status and exit.")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="HTTP User-Agent header for URL input.")
    parser.add_argument("--max-download-mb", type=int, default=DEFAULT_MAX_DOWNLOAD_MB, help="Maximum HTTP media download size.")
    parser.add_argument("--ffmpeg-timeout-seconds", type=int, default=DEFAULT_FFMPEG_TIMEOUT_SECONDS, help="Maximum seconds for each ffmpeg command.")
    args = parser.parse_args()

    if args.check_deps:
        return print_dependency_check()
    if not args.input:
        parser.error("Provide input unless --check-deps is used.")

    out_dir = Path(args.out_dir)
    raw_dir = out_dir / "raw"
    chunk_dir = out_dir / "chunks"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    source = args.input
    if is_url(source):
        media_path = download_url(source, raw_dir, args.user_agent, args.max_download_mb)
    else:
        media_path = Path(source).expanduser().resolve()
        if not media_path.exists():
            raise FileNotFoundError(str(media_path))

    audio_path = out_dir / "audio_16k_mono.wav"
    ffmpeg_path = resolve_executable(args.ffmpeg)
    if args.provider == "faster-whisper" and args.no_ffmpeg:
        audio_path = media_path
    else:
        if not ffmpeg_path:
            raise RuntimeError(
                "ffmpeg was not found. Install ffmpeg, pass --ffmpeg, or use --provider faster-whisper --no-ffmpeg."
            )
        extract_audio(ffmpeg_path, media_path, audio_path, args.ffmpeg_timeout_seconds)

    provider = args.provider
    if provider == "whisper-cli":
        model = args.model or "base"
    elif provider == "faster-whisper":
        model = args.model or "small.en"
    else:
        model = args.model or "gpt-4o-transcribe"
    language = args.language or None
    transcript_path: Path | None = None

    if provider == "whisper-cli":
        transcript_path = transcribe_with_whisper_cli(audio_path, out_dir, model, language)
    elif provider == "faster-whisper":
        transcript_path = transcribe_with_faster_whisper(
            audio_path,
            out_dir,
            model,
            language,
            args.initial_prompt,
            args.clip_timestamps,
            args.device,
            args.compute_type,
        )
    elif provider == "openai":
        if not ffmpeg_path:
            raise RuntimeError("ffmpeg is required for OpenAI chunking.")
        chunks = split_audio(
            ffmpeg_path,
            audio_path,
            chunk_dir,
            args.chunk_seconds,
            args.ffmpeg_timeout_seconds,
        )
        transcript_path = transcribe_with_openai(chunks, out_dir, model, language)
        if not args.keep_chunks:
            for chunk in chunks:
                chunk.unlink(missing_ok=True)
            try:
                chunk_dir.rmdir()
            except OSError:
                pass

    manifest = {
        "input": source,
        "media_path": str(media_path),
        "audio_path": str(audio_path),
        "ffmpeg_path": ffmpeg_path,
        "provider": provider,
        "model": model,
        "language": language,
        "device": args.device,
        "compute_type": args.compute_type,
        "transcript_path": str(transcript_path) if transcript_path else None,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    manifest_path = out_dir / "transcript_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(str(manifest_path))
    if transcript_path:
        print(str(transcript_path))
    else:
        print(str(audio_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())

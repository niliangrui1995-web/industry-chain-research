#!/usr/bin/env python3
"""Read-only inspector for a local HT/TongdaXin data folder."""

from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys
import time
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


DAY_STRUCT = struct.Struct("<IIIIIfII")
LC1_STRUCT = struct.Struct("<HHfffffII")
SKIPPED_TOP_DIRS = {
    "htlog",
    "T0001",
    "lct",
    "funcs_jy",
    "chrome",
    "chrome49",
    "华泰证券网上交易委托系统",
}
REQUIRED_DATA_DIRS = (
    Path("vipdoc") / "sh" / "lday",
    Path("vipdoc") / "sz" / "lday",
    Path("T0002") / "hq_cache",
)
REQUIRED_DAY_FILES = (
    Path("vipdoc") / "sh" / "lday" / "sh000001.day",
    Path("vipdoc") / "sz" / "lday" / "sz399001.day",
)
HQ_CACHE_FILES = [
    "base.dbf",
    "sh.tcu",
    "sz.tcu",
    "bj.tcu",
    "sh.tfz",
    "sz.tfz",
    "tdxhy.cfg",
    "tdxbk.cfg",
    "tdxchain.cfg",
    "fundinfo.dat",
    "fundstk.dat",
    "gbbq",
]


def fmt_time(ts: float | int | None) -> str | None:
    if not ts:
        return None
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def decode_text(data: bytes) -> tuple[str, str]:
    for enc in ("gb18030", "gbk", "utf-8-sig", "utf-8"):
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return data.decode("latin1", errors="replace"), "latin1"


def safe_stat(path: Path) -> dict[str, Any]:
    st = path.stat()
    return {
        "path": str(path),
        "size": st.st_size,
        "mtime": fmt_time(st.st_mtime),
    }


def summarize_top_dirs(root: Path) -> dict[str, Any]:
    dirs: dict[str, Any] = {}
    for top in sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        if top.name in SKIPPED_TOP_DIRS:
            dirs[top.name] = {"skipped": True, "reason": "software/account/log/runtime boundary"}
            continue
        count = 0
        size = 0
        latest = 0.0
        exts: Counter[str] = Counter()
        for dirpath, dirnames, filenames in os.walk(top):
            dirnames[:] = [d for d in dirnames if d not in SKIPPED_TOP_DIRS]
            for name in filenames:
                fp = Path(dirpath) / name
                try:
                    st = fp.stat()
                except OSError:
                    continue
                count += 1
                size += st.st_size
                latest = max(latest, st.st_mtime)
                exts[fp.suffix.lower() or "<noext>"] += 1
        dirs[top.name] = {
            "files": count,
            "size_mb": round(size / 1024 / 1024, 2),
            "latest_mtime": fmt_time(latest),
            "top_extensions": exts.most_common(10),
        }
    return dirs


def parse_day_tail(path: Path, rows: int = 5) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if len(data) % DAY_STRUCT.size != 0:
        raise ValueError(f"unexpected .day size {len(data)}")
    out: list[dict[str, Any]] = []
    start = max(0, len(data) - rows * DAY_STRUCT.size)
    for offset in range(start, len(data), DAY_STRUCT.size):
        date, open_, high, low, close, amount, volume, reserved = DAY_STRUCT.unpack(
            data[offset : offset + DAY_STRUCT.size]
        )
        out.append(
            {
                "date": date,
                "open": open_ / 100,
                "high": high / 100,
                "low": low / 100,
                "close": close / 100,
                "amount": round(float(amount), 2),
                "volume": volume,
            }
        )
    return out


def summarize_day(root: Path, codes: list[str]) -> dict[str, Any]:
    latest: Counter[str] = Counter()
    record_buckets: Counter[str] = Counter()
    market_counts: Counter[str] = Counter()
    bad: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []

    for market in ("sh", "sz", "bj", "ds"):
        day_dir = root / "vipdoc" / market / "lday"
        if not day_dir.exists():
            continue
        for path in day_dir.glob("*.day"):
            st = path.stat()
            if st.st_size == 0 or st.st_size % DAY_STRUCT.size:
                bad.append({"file": rel(path, root), "size": st.st_size})
                continue
            try:
                last = parse_day_tail(path, 1)[0]
            except Exception as exc:  # pragma: no cover - diagnostic path
                bad.append({"file": rel(path, root), "error": str(exc)})
                continue
            latest[str(last["date"])] += 1
            market_counts[market] += 1
            n = st.st_size // DAY_STRUCT.size
            if n < 50:
                bucket = "<50"
            elif n < 250:
                bucket = "50-249"
            elif n < 1000:
                bucket = "250-999"
            elif n < 3000:
                bucket = "1000-2999"
            else:
                bucket = ">=3000"
            record_buckets[bucket] += 1

    for code in codes:
        code_l = code.lower()
        path = root / "vipdoc" / code_l[:2] / "lday" / f"{code_l}.day"
        if not path.exists():
            samples.append({"code": code, "exists": False})
            continue
        st = path.stat()
        samples.append(
            {
                "code": code_l,
                "file": rel(path, root),
                "records": st.st_size // DAY_STRUCT.size,
                "mtime": fmt_time(st.st_mtime),
                "tail": parse_day_tail(path, 5),
            }
        )

    return {
        "files": sum(market_counts.values()),
        "market_counts": market_counts,
        "bad_count": len(bad),
        "bad_sample": bad[:20],
        "latest_date_distribution": latest.most_common(20),
        "record_count_buckets": record_buckets,
        "samples": samples,
    }


def decode_lc1_date(raw: int) -> int | None:
    year = raw // 2048 + 2004
    rem = raw % 2048
    month = rem // 100
    day = rem % 100
    if 1990 <= year <= 2035 and 1 <= month <= 12 and 1 <= day <= 31:
        return year * 10000 + month * 100 + day
    return None


def summarize_lc1(root: Path, codes: list[str]) -> dict[str, Any]:
    latest: Counter[str] = Counter()
    bad: list[dict[str, Any]] = []
    total = 0
    samples: list[dict[str, Any]] = []

    for market in ("sh", "sz", "bj"):
        min_dir = root / "vipdoc" / market / "minline"
        if not min_dir.exists():
            continue
        for path in min_dir.glob("*.lc1"):
            total += 1
            st = path.stat()
            if st.st_size == 0 or st.st_size % LC1_STRUCT.size:
                bad.append({"file": rel(path, root), "size": st.st_size})
                continue
            with path.open("rb") as fh:
                fh.seek(-LC1_STRUCT.size, os.SEEK_END)
                raw = LC1_STRUCT.unpack(fh.read(LC1_STRUCT.size))
            date = decode_lc1_date(raw[0])
            if date is None:
                bad.append({"file": rel(path, root), "raw_date": raw[0]})
                continue
            latest[str(date)] += 1

    for code in codes:
        code_l = code.lower()
        path = root / "vipdoc" / code_l[:2] / "minline" / f"{code_l}.lc1"
        if not path.exists():
            continue
        st = path.stat()
        with path.open("rb") as fh:
            fh.seek(-LC1_STRUCT.size, os.SEEK_END)
            raw_date, minute, open_, high, low, close, amount, volume, reserved = LC1_STRUCT.unpack(
                fh.read(LC1_STRUCT.size)
            )
        samples.append(
            {
                "code": code_l,
                "file": rel(path, root),
                "records": st.st_size // LC1_STRUCT.size,
                "mtime": fmt_time(st.st_mtime),
                "last": {
                    "date": decode_lc1_date(raw_date),
                    "minute": minute,
                    "time": f"{minute // 60:02d}:{minute % 60:02d}",
                    "open": round(float(open_), 4),
                    "high": round(float(high), 4),
                    "low": round(float(low), 4),
                    "close": round(float(close), 4),
                    "amount": round(float(amount), 2),
                    "volume": volume,
                },
            }
        )

    return {
        "files": total,
        "bad_count": len(bad),
        "bad_sample": bad[:20],
        "latest_date_distribution": latest.most_common(20),
        "samples": samples,
    }


def summarize_cw(root: Path) -> dict[str, Any]:
    cw_dir = root / "vipdoc" / "cw"
    if not cw_dir.exists():
        return {"exists": False}

    zip_files = sorted(cw_dir.glob("*.zip"))
    zero_zip: list[str] = []
    bad_zip: list[dict[str, Any]] = []
    checked = 0
    latest = 0.0
    tail: list[dict[str, Any]] = []

    for path in zip_files:
        st = path.stat()
        latest = max(latest, st.st_mtime)
        if st.st_size == 0:
            zero_zip.append(path.name)
            continue
        try:
            with zipfile.ZipFile(path) as zf:
                err = zf.testzip()
                if err:
                    bad_zip.append({"file": path.name, "first_bad_member": err})
                checked += 1
        except Exception as exc:
            bad_zip.append({"file": path.name, "error": str(exc)})

    for path in zip_files[-10:]:
        st = path.stat()
        tail.append({"file": path.name, "size": st.st_size, "mtime": fmt_time(st.st_mtime)})

    return {
        "exists": True,
        "zip_count": len(zip_files),
        "zip_checked_nonzero": checked,
        "zero_zip_count": len(zero_zip),
        "zero_zip_sample": zero_zip[:20],
        "bad_zip_count": len(bad_zip),
        "bad_zip_sample": bad_zip[:20],
        "latest_mtime": fmt_time(latest),
        "latest_zip_sample": tail,
        "per_stock_dat_count": len(list(cw_dir.glob("gp*.dat"))),
    }


def normalize_blk_code(line: str) -> str | None:
    token = line.strip()
    if len(token) < 7:
        return None
    token = re.sub(r"\D.*$", "", token)
    if len(token) < 7 or not token[:7].isdigit():
        return None
    market_flag = token[0]
    code = token[1:7]
    prefix = {"0": "sz", "1": "sh", "2": "bj"}.get(market_flag)
    if prefix is None:
        return None
    return f"{prefix}{code}"


def summarize_blocknew(root: Path, include_samples: bool) -> dict[str, Any]:
    block_dir = root / "T0002" / "blocknew"
    if not block_dir.exists():
        return {"exists": False}

    blocks: list[dict[str, Any]] = []
    for path in sorted(block_dir.glob("*.blk")):
        data = path.read_bytes()
        text, enc = decode_text(data)
        codes = [code for code in (normalize_blk_code(line) for line in text.splitlines()) if code]
        item: dict[str, Any] = {
            "file": path.name,
            "size": path.stat().st_size,
            "mtime": fmt_time(path.stat().st_mtime),
            "encoding": enc,
            "code_count": len(codes),
        }
        if include_samples:
            item["sample_codes"] = codes[:12]
        blocks.append(item)

    cfg = block_dir / "blocknew.cfg"
    cfg_tokens: list[str] = []
    if cfg.exists() and include_samples:
        text, enc = decode_text(cfg.read_bytes())
        cfg_tokens = [token.strip() for token in re.split(r"\x00+", text) if token.strip()][:40]

    return {
        "exists": True,
        "block_count": len(blocks),
        "nonempty_block_count": sum(1 for item in blocks if item["size"] > 0),
        "latest_blocks": sorted(blocks, key=lambda item: item["mtime"] or "", reverse=True)[:20],
        "largest_blocks": sorted(blocks, key=lambda item: item["size"], reverse=True)[:10],
        "cfg_tokens_sample": cfg_tokens,
    }


def summarize_hq_cache(root: Path) -> dict[str, Any]:
    hq_dir = root / "T0002" / "hq_cache"
    if not hq_dir.exists():
        return {"exists": False}
    files = []
    for name in HQ_CACHE_FILES:
        path = hq_dir / name
        if path.exists():
            st = path.stat()
            files.append({"file": name, "size": st.st_size, "mtime": fmt_time(st.st_mtime)})
    return {"exists": True, "selected_files": files}


def inspect(root: Path, codes: list[str], include_block_samples: bool) -> dict[str, Any]:
    if not root.is_dir():
        raise FileNotFoundError(root)
    missing = [path for path in REQUIRED_DATA_DIRS if not (root / path).is_dir()]
    if missing:
        expected = ", ".join(str(path) for path in REQUIRED_DATA_DIRS)
        raise FileNotFoundError(f"{root} does not contain the required market-data directories: {expected}")
    invalid_day_files = []
    for relative in REQUIRED_DAY_FILES:
        path = root / relative
        try:
            tail = parse_day_tail(path, 1)
        except (OSError, ValueError, struct.error):
            invalid_day_files.append(relative)
            continue
        if not tail or not 19900101 <= int(tail[0]["date"]) <= 21001231:
            invalid_day_files.append(relative)
    if invalid_day_files:
        expected = ", ".join(str(path) for path in REQUIRED_DAY_FILES)
        raise FileNotFoundError(f"{root} does not contain valid .day sentinel files: {expected}")
    hq_dir = root / "T0002" / "hq_cache"
    if not any((hq_dir / name).is_file() and (hq_dir / name).stat().st_size > 0 for name in HQ_CACHE_FILES):
        raise FileNotFoundError(f"{root} does not contain a nonempty core hq_cache file")
    return {
        "root": str(root),
        "generated_at": fmt_time(time.time()),
        "top_dirs": summarize_top_dirs(root),
        "daily_day": summarize_day(root, codes),
        "minute_lc1": summarize_lc1(root, codes),
        "financial_cw": summarize_cw(root),
        "blocknew": summarize_blocknew(root, include_block_samples),
        "hq_cache": summarize_hq_cache(root),
        "evidence_boundary": {
            "daily_day": "market_data_vendor",
            "minute_lc1": "market_data_vendor when present; unavailable if absent",
            "blocknew": "secondary_trading_context",
            "financial_cw": "market_data_vendor, not official filings",
        },
        "privacy_boundary": "Skipped account/trading/log/runtime directories unless explicitly inspected outside this helper.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Inspect local HT/TongdaXin data read-only.")
    parser.add_argument(
        "--root",
        default=r"D:\HT",
        help="HT/TongdaXin installation/data root (default: %(default)s).",
    )
    parser.add_argument(
        "--codes",
        nargs="*",
        default=["sh000001", "sz399001", "sz000001", "sh600000", "sz300750", "sh688981", "bj899050"],
        help="Market-prefixed codes to sample.",
    )
    parser.add_argument("--skip-block-samples", action="store_true", help="Do not include block sample codes/names.")
    parser.add_argument("--json", action="store_true", help="Emit JSON. Text output is not implemented.")
    args = parser.parse_args(argv)

    result = inspect(Path(args.root), args.codes, not args.skip_block_samples)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=dict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

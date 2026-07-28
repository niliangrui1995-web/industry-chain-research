from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(r"D:\vcp_hunter\产业链投研\artifacts\earnings\300308\latest_call\transcript")
DRAFT = ROOT / "draft_fast_beam1" / "transcript_segments.json"
TURBO_FIRST = ROOT / "chunks_asr" / "chunk_000" / "transcript_segments.json"
SPOT = ROOT / "spotcheck_turbo"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_time(seconds: float, comma: bool = False) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    separator = "," if comma else "."
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{milliseconds:03d}"


def normalized(items: list[dict], source: str, offset: float = 0.0) -> list[dict]:
    result = []
    for item in items:
        start = float(item["start"]) + offset
        end = float(item["end"]) + offset
        result.append(
            {
                **item,
                "start": start,
                "end": end,
                "start_text": fmt_time(start),
                "end_text": fmt_time(end),
                "source": source,
            }
        )
    return result


def replace_range(
    segments: list[dict], start: float, end: float, replacements: list[dict]
) -> list[dict]:
    kept = [
        item
        for item in segments
        if float(item["end"]) <= start or float(item["start"]) >= end
    ]
    kept.extend(
        item
        for item in replacements
        if float(item["start"]) >= start and float(item["start"]) < end
    )
    return sorted(kept, key=lambda item: (float(item["start"]), float(item["end"])))


def correct_text(text: str, start: float) -> tuple[str, list[str]]:
    corrections = [
        ("EWT的FORMACOR", "1.6T光模块"),
        ("EWT的这个", "1.6T的"),
        ("EWT", "1.6T"),
        ("一流气", "1.6T"),
        ("一周期", "1.6T"),
        ("1流器", "1.6T"),
        ("1.67", "1.6T"),
        ("16T", "1.6T"),
        ("NPU", "NPO"),
        ("NUCLAO", "New Cloud"),
        ("SkillUp", "Scale Up"),
        ("Skill Out", "Scale Out"),
        ("Scale-off", "Scale Up"),
        ("光磨和", "光模块"),
        ("光磨", "光模块"),
        ("光幕化", "光模块"),
        ("光棍的行业", "光模块行业"),
        ("光年这方面", "光连接方面"),
        ("交不料", "交付量"),
        ("归定", "规定"),
        ("资本开始", "资本开支"),
        ("大哥户", "大客户"),
        ("采用进而", "采购金额"),
        ("液末版本", "EML版本"),
        ("微光版本", "硅光版本"),
        ("灰光芯片", "硅光芯片"),
        ("辉光", "硅光"),
        ("模纹三里", "薄膜铌酸锂"),
        ("薄目遗酸力", "薄膜铌酸锂"),
        ("薄木铃酸链", "薄膜铌酸锂"),
        ("先进崩装", "先进封装"),
        ("心理工程", "先进封装"),
        ("心理工庄", "先进封装"),
        ("KPEX", "CAPEX"),
        ("Bone成本", "BOM成本"),
        ("贷款", "带宽"),
        ("斯科普流", "Scale Up"),
        ("NVR、华为", "NVL、华为"),
        ("Sale客户", "CSP客户"),
        ("Fuel-UP", "Scale Up"),
        ("320T", "3.2T"),
        ("2017年到2018年", "2027年到2028年"),
        ("2017到2018年", "2027到2028年"),
        ("2018年", "2028年"),
        ("规光芯片", "硅光芯片"),
    ]
    notes: list[str] = []
    corrected = text
    for old, new in corrections:
        corrected = corrected.replace(old, new)

    if 1140 <= start < 1170:
        corrected = corrected.replace("2.4G", "2.4T")
        corrected = corrected.replace("Cuponite", "【技术名听不清】")
        notes.append("技术清单首个技术名听不清")
    if 1675 <= start < 1740:
        corrected = corrected.replace("210G或者3.2T", "【前一速率听不清】或者3.2T")
        corrected = corrected.replace("NPO或者是FPU", "NPO或者CPO【低置信】")
        corrected = corrected.replace("QQNight或者QQNight", "【DCI相关产品名听不清】")
    if 1845 <= start < 1885:
        corrected = corrected.replace("Covirium Nite", "【技术名听不清】")
        corrected = corrected.replace("K-VIRN NIGHT", "【技术名听不清】")
        notes.append("技术清单中有一个英文技术名听不清")
    if 2370 <= start < 2455:
        corrected = corrected.replace("16T", "1.6T")
    if 2530 <= start < 2580:
        corrected = corrected.replace("对影镜件", "对应AI芯片")
        corrected = corrected.replace("晶,", "芯片")

    corrected = corrected.replace("�", "【听不清】")
    return corrected, notes


def main() -> None:
    draft_payload = read_json(DRAFT)
    duration = float(draft_payload["metadata"]["source_duration"])
    segments = normalized(draft_payload["segments"], "small_beam1_vad")

    turbo_first = normalized(read_json(TURBO_FIRST)["segments"], "large_v3_turbo_beam5")
    segments = replace_range(segments, 0.0, 300.0, turbo_first)

    overlays = [
        (450.0, 515.0, SPOT / "spot_001_0730_segments.json"),
        (615.0, 638.5, SPOT / "spot_002_1015_segments.json"),
        (1140.0, 1210.0, SPOT / "spot_003_1900_segments.json"),
        (1500.0, 1590.0, SPOT / "gap_2500_recovered.json"),
        (1590.0, 1634.7, SPOT / "spot_004_2445_segments.json"),
        (1785.0, 1845.0, SPOT / "spot_006_2945_segments.json"),
        (1845.0, 1885.0, SPOT / "spot_007_3045_segments.json"),
        (2370.0, 2454.0, SPOT / "spot_008_3930_segments.json"),
        (2530.0, 2575.0, SPOT / "spot_009_4210_segments.json"),
    ]
    for start, end, path in overlays:
        replacement_payload = read_json(path)
        replacement_items = replacement_payload.get("segments", [])
        replacements = normalized(replacement_items, "large_v3_turbo_spotcheck")
        segments = replace_range(segments, start, end, replacements)

    final_segments: list[dict] = []
    for index, item in enumerate(sorted(segments, key=lambda row: row["start"]), start=1):
        text, correction_notes = correct_text(str(item["text"]).strip(), float(item["start"]))
        if not text or text == "。":
            continue
        avg_logprob = item.get("avg_logprob")
        low_confidence = bool(
            item.get("low_confidence", False)
            or (avg_logprob is not None and float(avg_logprob) < -0.7)
            or correction_notes
            or "【低置信" in text
            or "【技术名听不清】" in text
            or "【听不清】" in text
        )
        final_segments.append(
            {
                **item,
                "id": len(final_segments) + 1,
                "text": text,
                "correction_notes": correction_notes,
                "low_confidence": low_confidence,
            }
        )

    raw_lines = [
        f"[{item['start_text']} - {item['end_text']}] {item['text']}"
        for item in final_segments
    ]
    (ROOT / "transcript_raw.txt").write_text(
        "\n".join(raw_lines) + "\n", encoding="utf-8"
    )
    (ROOT / "transcript_corrected.txt").write_text(
        "\n".join(raw_lines) + "\n", encoding="utf-8"
    )

    vtt = ["WEBVTT", ""]
    srt: list[str] = []
    for index, item in enumerate(final_segments, start=1):
        vtt.extend(
            [
                str(index),
                f"{fmt_time(item['start'])} --> {fmt_time(item['end'])}",
                item["text"],
                "",
            ]
        )
        srt.extend(
            [
                str(index),
                f"{fmt_time(item['start'], comma=True)} --> {fmt_time(item['end'], comma=True)}",
                item["text"],
                "",
            ]
        )
    (ROOT / "transcript_timestamped.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (ROOT / "transcript_timestamped.srt").write_text("\n".join(srt), encoding="utf-8")

    section_starts = [
        (0.0, "管理层开场与市场传闻澄清"),
        (383.0, "互动问答一：2028新产品与上游物料"),
        (695.0, "互动问答二：价格、竞争格局与技术门槛"),
        (1270.0, "互动问答三：2027订单与毛利率"),
        (1454.0, "互动问答四：Scale Up与光连接CAPEX占比"),
        (1890.0, "互动问答五：单波200G、柜内互连与国内需求"),
        (2320.0, "互动问答六：NPO节奏、光模块/AI芯片比例与订单来源"),
        (2635.0, "管理层总结"),
    ]
    markdown = [
        "# 中际旭创 2026-07-28 电话会校订逐字稿",
        "",
        "> 由 faster-whisper 分块转录并对关键段使用 large-v3-turbo 复核。",
        "> `【低置信】` / `【技术名听不清】` 表示原声或专业词仍需人工听校。",
        "",
    ]
    section_index = 0
    for item in final_segments:
        while (
            section_index + 1 < len(section_starts)
            and item["start"] >= section_starts[section_index + 1][0]
        ):
            section_index += 1
        heading = section_starts[section_index][1]
        marker = f"## {heading}"
        if marker not in markdown:
            markdown.extend([marker, ""])
        confidence = "〔低置信〕" if item["low_confidence"] else ""
        markdown.append(
            f"[{item['start_text']}–{item['end_text']}] {confidence}{item['text']}"
        )
        markdown.append("")
    (ROOT / "transcript_structured.md").write_text(
        "\n".join(markdown), encoding="utf-8"
    )

    payload = {
        "metadata": {
            "event_date": "2026-07-28",
            "event_identity": "当日晚间针对市场、股价和行业传闻召开的临时电话会",
            "provider": "faster-whisper",
            "base_model": "small",
            "base_device": "cpu",
            "base_compute_type": "int8",
            "base_beam_size": 1,
            "spotcheck_model": "large-v3-turbo",
            "spotcheck_device": "cpu",
            "spotcheck_compute_type": "int8",
            "spotcheck_beam_size": 5,
            "source_duration": duration,
            "last_segment_end": final_segments[-1]["end"],
            "timeline_coverage_ratio": final_segments[-1]["end"] / duration,
            "segment_count": len(final_segments),
            "low_confidence_segment_count": sum(
                bool(item["low_confidence"]) for item in final_segments
            ),
            "gap_recovery": (
                "25:00-26:49并非整段静音；25:15左右原发言线路中断，"
                "25:20主持人确认听不到声音，25:30-25:50调试并切换提问者；"
                "25:50后新提问已用10秒微片、large-v3-turbo、VAD关闭恢复。"
            ),
        },
        "segments": final_segments,
    }
    (ROOT / "transcript_segments.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    notes = """# 转录说明与低置信片段

## 完整性

- 原始音频：45:47.160（2,747.160 秒），MP3，44.1 kHz，双声道，128 kbps。
- 最后有效转录结束：45:46.906；时间轴覆盖率约 99.99%。
- 25:00–26:49 的大缺口已经复核：25:15 左右原提问者线路中断，25:20 主持人明确说“听不到你的声音”，25:30–25:50 为调试/切换提问者；25:50 后的新提问已恢复。该区间不是管理层回答被漏转。
- 30:00–30:30 的原 fast draft 缺口已用 large-v3-turbo 补回，为光连接应用场景、DCI/园区互连相关表述。

## 主要低置信片段

1. 07:42–08:34：原声及多模型 ASR 的 `2.4T`、`NPO`、`XPO` 已由公司 2026-007 正式纪要书面确认。该口径与 7 月 12 日正式纪要中的 `3.2T` 可以并存；公司未披露两者的具体技术映射，不应推定为同一产品或互相替代。
2. 19:13–19:30：`2.4T` 已由公司 2026-007 正式纪要确认；高端技术清单可确认包含“硅光、薄膜铌酸锂”，其首个英文/专业技术名仍听不清。
3. 24:45–25:15：原提问者线路质量差；能确认其在问 Scale Up 增量与大客户方案，具体架构词不清，随后线路中断。
4. 27:50–28:30：能确认产品速率序列含 3.2T、6.4T、12.8T；3.2T 前一个速率听不清；另提及 NPO/CPO 类方案，DCI 相关具体产品名听不清。
5. 30:54–31:09：技术清单可确认“硅光芯片、薄膜铌酸锂、先进封装”；另一个英文技术名听不清。
6. 与会者姓名、机构名和电话尾号多处受线路/口音影响，未用于关键结论。

## 关键纠错

- 原始 ASR 的 `EWT`、`一流气`、`一周期` 等，按上下文统一校为 `1.6T`。
- `NPU` 在本次光连接产品语境中统一校为 `NPO`。
- 42:23–42:32 的核心口径为“光模块对应 AI 芯片的比例进一步增长，至少翻一倍、甚至更多”；不是公司确认 GPU 出货量。
"""
    (ROOT / "transcript_cn_notes.md").write_text(notes, encoding="utf-8")

    key_numbers = """# 可核验数字与关键时间戳

| 时间戳 | 数字/口径 | 证据属性 | 置信度 |
|---|---|---|---|
| 00:00:40–00:01:24 | 市场传闻 1.6T 光模块价格降至 600 美元或更低；管理层称公司明年价格远高于该数 | 传闻 + 管理层否认 | 高 |
| 00:04:03–00:04:29 | 有些客户已下 2027 年订单，不只是指引；月度交付量已规定 | 管理层主张 | 高 |
| 00:05:00–00:05:45 | 部分重点客户给出 2028 年新产品指引/采购金额，管理层称金额“非常大” | 管理层主张，未给数 | 中高 |
| 00:07:42–00:08:34 | 2028 年新产品涉及 2.4T、NPO 与 XPO；管理层称量和采购金额较大。三个术语已由公司 2026-007 正式纪要确认；与 7 月 12 日 3.2T 口径可并存，但技术映射未披露 | 管理层主张 + 官方纪要确认 | 高（术语）；采购规模未量化 |
| 00:10:21–00:10:38 | 下半年物料将阶段性改善，预计出货量等各方面明显好转 | 管理层主张 | 高 |
| 00:14:34–00:15:25 | 1.6T 产品含 EML/硅光、500 米 DR、2 公里及更长 FR/LR 等，不能用单一价格概括 | 管理层主张 | 中高 |
| 00:21:53–00:23:42 | 对现有毛利保持稳定有信心；2027 新产品毛利高于现有成熟产品并可拉动整体毛利率 | 管理层主张 | 高 |
| 00:27:14–00:27:29 | 传统互联网/云数据中心时代光模块占 CSP 资本开支“不超过/不到 5 个百分点” | 管理层估计 | 中 |
| 00:28:16–00:28:30 | 提及 3.2T、6.4T、12.8T 与 DCI/园区互连方向 | 管理层主张 | 中（个别产品名不清） |
| 00:39:30–00:40:00 | 2027 年下半年至少两个有影响力客户开始批量采购 NPO；更大规模上量在 2028 年 | 管理层主张 | 高 |
| 00:40:00–00:40:54 | 更多 CSP、大模型公司、New Cloud 客户在 2026–2027 年导入 NPO；管理层类比 1.6T 放量路径 | 管理层主张 | 高 |
| 00:41:00–00:42:32 | 提问者引用 GPU:光模块 1:3/1:4；管理层称光模块对应 AI 芯片的比例进一步增长，至少翻一倍、甚至更多 | 提问背景 + 管理层主张 | 高 |
| 00:43:22–00:43:50 | 有些客户告知总需求与份额；另一些只给公司量，公司按历史份额反推总需求 | 管理层主张 | 高 |
"""
    (ROOT / "key_numbers_and_timestamps.md").write_text(key_numbers, encoding="utf-8")


if __name__ == "__main__":
    main()

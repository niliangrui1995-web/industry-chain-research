# -*- coding: utf-8 -*-
"""一次性修复 build_report.py 中未落盘的 10 处编辑（带断言与回读校验）。"""
from pathlib import Path

P = Path(r"D:\vcp_hunter\产业链投研\research_outputs\global_biotech_20260916\build_report.py")
s = P.read_text(encoding="utf-8")

REPS = [
    # R1 c2 2021 tip
    ('"tip": "2021 全年：约 509 亿美元（按 E-015 中 2022 年 290 亿、同比 -43% 反推，为推算值）"',
     '"tip": "2021 全年：约 509 亿美元（按 2022 年披露值 290 亿、同比 -43% 反推，为推算值；来源见下方角标）"'),
    # R2 c2 2024 tip
    ('"tip": "2024 全年：约 365 亿美元（按 E-011 中 2025 年 344.44 亿、同比 -5.61% 反推，为推算值）"',
     '"tip": "2024 全年：约 365 亿美元（按 2025 年披露值 344.44 亿、同比 -5.61% 反推，为推算值）"'),
    # R3 c3 2022 tip
    ('"tip": "2022 全年：约 372 亿美元（按 E-007 中“2022 较 2021 降 185 亿”推算）"',
     '"tip": "2022 全年：约 372 亿美元（按“2022 较 2021 降 185 亿”的披露口径推算）"'),
    # R4 c13 2021 tip
    ('"tip": "2021 全年：约 149 亿美元（按 E-015 中 2022 年 67 亿、同比 -55% 反推）"',
     '"tip": "2021 全年：约 149 亿美元（按 2022 年披露值 67 亿、同比 -55% 反推）"'),
    # R5 c13 2024 tip
    ('"tip": "2024 全年：约 47.8 亿美元（按 E-011 中 2025 年 92.34 亿、同比 +93.35% 反推）"',
     '"tip": "2024 全年：约 47.8 亿美元（按 2025 年披露值 92.34 亿、同比 +93.35% 反推）"'),
    # R6 c11 2024 tip
    ('"tip": "2024 全年：522 亿美元（94 笔；E-023 记为 519 亿，统计截止日差异）"',
     '"tip": "2024 全年：522 亿美元（94 笔；另一官方转载口径记为 519 亿，统计截止日差异）"'),
    # R7 c11 2026H1 tip
    ('"tip": "2026 上半年：超 997 亿美元（约 100 笔，保守口径；E-003 转述口径约 1,100 亿/81 笔，统计截止日差异）——半年数据"',
     '"tip": "2026 上半年：超 997 亿美元（约 100 笔，保守口径；另一转述口径约 1,100 亿/81 笔，统计截止日差异）——半年数据"'),
    # R8 c11 caption
    ('], "医药魔方；2024 年 E-022 记 522 亿、E-023 记 519 亿，为统计截止日差异"),',
     '], "医药魔方；2024 年两个来源分别记 522 亿与 519 亿，为统计截止日差异（来源编号见上方图注角标）"),'),
    # R9 trace text
    ('共采用 40 项证据（E-001 ~ E-040），页尾可逐项回溯原始链接。',
     '共采用 40 项证据（<a class="source-link" href="#sec-evidence">E-001 ~ E-040</a>），页尾可逐项回溯原始链接。'),
    # R10 TOC item
    ('("#sec-evidence", "证据链与方法论（E-001 ~ E-040）"),',
     '("#sec-evidence", "证据链与方法论（证据索引 40 项）"),'),
    # R11 whitelist
    ("or ('href=\"#cite-' in ctx):",
     "or ('href=\"#cite-' in ctx) or ('#sec-evidence\">' in ctx):"),
]

results = []
for i, (old, new) in enumerate(REPS, 1):
    n = s.count(old)
    if n != 1:
        results.append(f"R{i}: SKIP old_count={n} :: {old[:50]}")
        continue
    s = s.replace(old, new)
    results.append(f"R{i}: replaced")

P.write_text(s, encoding="utf-8")

# 回读校验
s2 = P.read_text(encoding="utf-8")
ok = True
for i, (old, new) in enumerate(REPS, 1):
    if old in s2:
        results.append(f"R{i}: READBACK_FAIL old still present")
        ok = False
    if new not in s2:
        results.append(f"R{i}: READBACK_FAIL new missing")
        ok = False
results.append("ALL_OK" if ok else "HAS_FAIL")
Path(r"D:\vcp_hunter\产业链投研\research_outputs\global_biotech_20260916\fix_tips_result.txt").write_text(
    "\n".join(results), encoding="utf-8")
print("DONE")

# -*- coding: utf-8 -*-
"""给 build_report.py 打补丁：接入周期章节（详章6）、证据 40→46、章节编号顺延、自检更新。
幂等：每处替换 assert count==1；已打过则报告 SKIP 并退出非零由人工判断。"""
import io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
P = "build_report.py"
s = open(P, encoding="utf-8").read()

REPS = [
    # 1. import
    ("import report_charts as RC\n",
     "import report_charts as RC\nimport report_cycle\n"),
    # 2. report-sub
    ("宏观驱动 / 2026-2028 前瞻研判</div>",
     "宏观驱动 / 2026-2028 前瞻研判 / 周期复盘与前瞻（追加）</div>"),
    # 3. header 证据计数
    ('<span>🧩 证据：<a class="source-link" href="#sec-evidence">E-001 ~ E-040</a>（40 项，页尾可回溯）</span>',
     '<span>🧩 证据：<a class="source-link" href="#sec-evidence">E-001 ~ E-046</a>（46 项，页尾可回溯）</span>'),
    # 4. TOC 周期章节
    ('    ("#sec-china", "数据详章 5 · 对中国创新药行业的启示"),\n',
     '    ("#sec-china", "数据详章 5 · 对中国创新药行业的启示"),\n'
     '    ("#sec-cycle", "数据详章 6 · 周期复盘与前瞻（追加章节）"),\n'),
    # 5. TOC 证据计数
    ('("#sec-evidence", "证据链与方法论（证据索引 40 项）"),',
     '("#sec-evidence", "证据链与方法论（证据索引 46 项）"),'),
    # 6. 问题树 Q8
    ('<tr><td>Q7 中国启示：对国内创新药行业（含 CXO 传导）的启示？</td><td>详章 5</td><td><span class="tag tag-p2">已覆盖</span></td></tr>\n',
     '<tr><td>Q7 中国启示：对国内创新药行业（含 CXO 传导）的启示？</td><td>详章 5</td><td><span class="tag tag-p2">已覆盖</span></td></tr>\n'
     '<tr><td>Q8 周期复盘与前瞻：2021 年为何见顶、下一轮上行周期何时见顶？（追加）</td><td>详章 6</td><td><span class="tag tag-p1">复盘 + 推演</span></td></tr>\n'),
    # 7. 检索地图新增行
    ('<tr><td>产业传导（CXO）</td>',
     '<tr><td>周期复盘锚点（追加）</td><td>美联储（央行官方）{C(\'E-044\')}、CDE（官方）{C(\'E-042\')}、港交所（官方）{C(\'E-043\')}、XBI 行情数据库{C(\'E-041\')}、美国会调查报告{C(\'E-045\')}、默沙东年报（公司官方）{C(\'E-046\')}</td><td>2020-2025</td><td>历史事件时间线 / 政策路径</td></tr>\n'
     '<tr><td>产业传导（CXO）</td>'),
    # 8. 收束区证据计数
    ('共采用 40 项证据（<a class="source-link" href="#sec-evidence">E-001 ~ E-040</a>），页尾可逐项回溯原始链接。',
     '共采用 46 项证据（<a class="source-link" href="#sec-evidence">E-001 ~ E-046</a>），页尾可逐项回溯原始链接。'),
    # 9. 插入章节
    ("# ===== 结论 =====",
     "# ===== 数据详章 6：周期复盘与前瞻（追加） =====\nA(report_cycle.chapter_html(C, JC))\n\n# ===== 结论 ====="),
    # 10. 结论编号顺延
    ("<h3>9.1 结论（逐条回链证据）</h3>", "<h3>10.1 结论（逐条回链证据）</h3>"),
    ("<h3>9.2 跟踪指标看板</h3>", "<h3>10.2 跟踪指标看板</h3>"),
    # 11. 结论新增交叉引用条
    ("</ol>\n<h3>10.2 跟踪指标看板</h3>",
     "<li><strong>周期复盘与前瞻（追加章）</strong>：2021 年见顶为「流动性预期转向 × 估值泡沫 × IPO 窗口」共振；下一轮基准见顶窗口 2028 年前后（2027H2-2029H1，主观概率约 50%，推演），形态更可能为结构性分化见顶——详见数据详章 6。{C('E-041')}{C('E-044')}{C('E-046')}</li>\n"
     "</ol>\n<h3>10.2 跟踪指标看板</h3>"),
    # 12. 证据章节编号与计数
    ("<h2>证据链与方法论（证据索引 40 项）</h2>", "<h2>证据链与方法论（证据索引 46 项）</h2>"),
    ("<h3>10.1 方法论</h3>", "<h3>11.1 方法论</h3>"),
    ("<h3>10.2 证据索引（点击徽章查看详情抽屉；每条可返回正文引用处）</h3>",
     "<h3>11.2 证据索引（点击徽章查看详情抽屉；每条可返回正文引用处）</h3>"),
    # 13-15. 自检更新
    ('check("全部 40 条证据均被引用", len(uncited) == 0, f"未引用: {uncited}")',
     'check(f"全部 {len(EV)} 条证据均被引用", len(uncited) == 0, f"未引用: {uncited}")'),
    ('check("图表数量 = 13", fig_count == 13, f"found={fig_count}")',
     'check("图表数量 = 15", fig_count == 15, f"found={fig_count}")'),
    ('check("每图均有数据表回退", html_doc.count(\'class="chart-data"\') == 13, "")',
     'check("每图均有数据表回退", html_doc.count(\'class="chart-data"\') == 15, "")'),
    ('      ["sec-trace", "sec-dashboard", "sec-i1", "sec-i2", "sec-i3", "sec-global", "sec-region",\n'
     '       "sec-track", "sec-exit", "sec-china", "sec-conclusion", "sec-evidence", "sec-disclaimer"]), "")',
     '      ["sec-trace", "sec-dashboard", "sec-i1", "sec-i2", "sec-i3", "sec-global", "sec-region",\n'
     '       "sec-track", "sec-exit", "sec-china", "sec-cycle", "sec-conclusion", "sec-evidence", "sec-disclaimer"]), "")'),
]

n_ok = 0
for i, (old, new) in enumerate(REPS, 1):
    cnt = s.count(old)
    if cnt == 0:
        print(f"MISS #{i}: 未找到锚点 → {old[:60]!r}")
        sys.exit(2)
    assert cnt == 1, f"#{i} 锚点不唯一 count={cnt}: {old[:60]!r}"
    s = s.replace(old, new)
    n_ok += 1
    print(f"OK  #{i}")

open(P, "w", encoding="utf-8").write(s)
print(f"PATCH_DONE {n_ok}/{len(REPS)}")

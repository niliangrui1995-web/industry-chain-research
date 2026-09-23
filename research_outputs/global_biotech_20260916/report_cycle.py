# -*- coding: utf-8 -*-
"""数据详章 6 · 周期复盘与前瞻（追加章节）。

图14：2020-2022 见顶传导时序（事实层，证据 E-041~E-045 + 既有 E-007/E-015/E-037/E-043）；
图15：2026-2030 下一轮见顶窗口推演（推演层，锚点 E-034/E-046，概率为主观推演）。
所有图形遵守图表契约：viewBox、图例可切换、<title> 悬浮提示（不含来源编号）、<details> 数据表。
"""
from __future__ import annotations

import report_charts as RC

# ---------------------------------------------------------------- 图14：2020-2022 传导时序

# (年份小数, 组, 两行标签, 悬浮提示)
_G14 = {
    "s0": ("货币政策", RC.AMBER),
    "s1": ("二级市场", RC.BLUE),
    "s2": ("政策/监管", RC.PURPLE),
    "s3": ("一二级融资", RC.GREEN),
}
EVENTS14 = [
    (2020.21, "s0", ["2020-03 零利率", "+无限量QE"], "2020-03 · 货币政策：联邦基金利率降至 0-0.25% 并启动无上限 QE（官方复盘口径）"),
    (2021.11, "s1", ["2021-02-09", "XBI 174.79 见顶"], "2021-02-09 · 二级市场：XBI 盘中 174.79 美元，历史最高（收盘最高为前一日 173.99）"),
    (2021.43, "s2", ["2021-06", "Aduhelm 争议"], "2021-06-07 · 政策/监管：FDA 不顾咨询委员会全票反对加速批准 Aduhelm，三名委员辞职"),
    (2021.50, "s2", ["2021-07", "CDE 临床价值导向"], "2021-07-02 · 政策/监管：CDE 发布抗肿瘤药临床价值导向征求意见稿，7-06 医药股大跌"),
    (2021.62, "s3", ["2021 全年", "IPO 105起/145亿"], "2021 全年 · 一二级融资：全球 biotech IPO 105 起/145 亿美元，周期顶点（年度值，绘于年内位置）"),
    (2021.72, "s3", ["2021 全年", "18A 20家创纪录"], "2021 全年 · 一二级融资：港股 18A 20 家上市创历史纪录，募资约 377 亿港元（年度值，绘于年内位置）"),
    (2021.82, "s3", ["2021 全年", "VC 557亿见顶"], "2021 全年 · 一二级融资：全球 biopharma VC 557 亿美元（PitchBook 口径）见顶（年度值，绘于年内位置）"),
    (2021.87, "s0", ["2021-11", "taper 启动"], "2021-11 · 货币政策：FOMC 宣布缩减购债（每月 -150 亿美元）"),
    (2021.96, "s0", ["2021-12", "提速/删暂时性"], "2021-12 · 货币政策：taper 加倍提速，声明删除「暂时性」表述"),
    (2022.20, "s0", ["2022-03 首加息", "全年 +425bp"], "2022-03 · 货币政策：结束购债并首次加息，2022 全年累计 +425bp 至 4.25-4.50%"),
    (2022.36, "s1", ["2022-05-12", "XBI 61.78 低点"], "2022-05-12 · 二级市场：XBI 最低 61.78 美元，自顶点最大回撤 -64.5%"),
    (2022.70, "s3", ["2022 全年", "IPO 24起/一级-43%"], "2022 全年 · 一二级融资：IPO 骤降至 24 起；全球一级市场 -43%、中国 -55%（年度值，绘于年内位置）"),
]


def fig14():
    W, H = 980, 430
    x0, x1 = 55, 945
    yr0, yr1 = 2020.0, 2023.0
    ax_y = 215

    def X(yr):
        return x0 + (yr - yr0) / (yr1 - yr0) * (x1 - x0)

    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="2020-2022 见顶传导时序" preserveAspectRatio="xMidYMid meet">']
    # 季度网格与年份刻度
    for q in range(13):
        yr = 2020.0 + q * 0.25
        x = X(yr)
        parts.append(f'<line x1="{x:.1f}" y1="{ax_y-14}" x2="{x:.1f}" y2="{ax_y+14}" stroke="{RC.GRID}" stroke-width="1"/>')
    for y in (2020, 2021, 2022, 2023):
        x = X(y)
        parts.append(f'<line x1="{x:.1f}" y1="34" x2="{x:.1f}" y2="{H-30}" stroke="{RC.GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{x+4:.1f}" y="30" font-size="12" fill="{RC.TXT_DIM}">{y}</text>')
    parts.append(f'<line x1="{x0}" y1="{ax_y}" x2="{x1}" y2="{ax_y}" stroke="{RC.AXIS}" stroke-width="1.6"/>')
    # 事件：四车道避让（上2 下2）
    lanes = [(128, "up"), (66, "up"), (302, "down"), (364, "down")]
    for i, (yr, gkey, lines, tip) in enumerate(EVENTS14):
        color = _G14[gkey][1]
        x = X(yr)
        ty, d = lanes[i % 4]
        parts.append(f'<g data-series-group="{gkey}">')
        parts.append(f'<line x1="{x:.1f}" y1="{ty + 26:.1f}" x2="{x:.1f}" y2="{ax_y:.1f}" stroke="{color}" stroke-width="1.1" stroke-dasharray="3 2" opacity="0.75"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{ax_y}" r="5" fill="{color}"><title>{RC.esc(tip)}</title></circle>')
        anchor_y = ty + 12
        for j, ln in enumerate(lines):
            parts.append(f'<text x="{x:.1f}" y="{anchor_y + j * 13:.1f}" text-anchor="middle" font-size="10.5" fill="{RC.TXT}">{RC.esc(ln)}</text>')
        parts.append(f'<rect x="{x - 4:.1f}" y="{ty + 26:.1f}" width="8" height="6" fill="{color}" opacity="0.9"/>')
        parts.append("</g>")
    parts.append(f'<text x="{x0}" y="{H - 8}" font-size="10.5" fill="{RC.TXT_DIM}">读法：气泡落在时间轴上为事件时点；年度汇总值（IPO/18A/VC）绘于对应年份内位置。二级（2021-02）→ IPO/一级（2021 全年见顶）→ 速冻（2022）。</text>')
    parts.append("</svg>")
    legend = RC._legend_html([(k, v[1], v[0], False) for k, v in _G14.items()])
    return "".join(parts), legend


# ---------------------------------------------------------------- 图15：2026-2030 见顶窗口推演

_G15 = {
    "s0": ("提前情景 · 2027 见顶（约 30%）", RC.AMBER),
    "s1": ("基准情景 · 2028 前后（约 50%）", RC.BLUE),
    "s2": ("延后情景 · 2029-2030（约 20%）", RC.PURPLE),
    "s3": ("关键锚点", RC.GREEN),
}
BARS15 = [
    ("s0", 2026.75, 2028.25, 150, "提前 · 2027 见顶", "约 30%", "触发：再通胀迫使重新加息 / IPO 抽血过快 / 重大临床失败事件提前刺破风险偏好"),
    ("s1", 2027.50, 2029.50, 216, "基准 · 2028 前后", "约 50%", "锚定：峰-峰约 6 年节律 + K药 2028 专利到期 + AI 药物 2027 验证 + 降息周期中后段"),
    ("s2", 2028.75, 2030.60, 282, "延后 · 2029-2030", "约 20%", "触发：利率维持低位更久 + 并购/BD 持续超预期的结构性牛市"),
]
ANCHORS15 = [
    (2027.0, "2027 AI 药物验证点", "2027 · 锚点：首个 AI 发现药物获批概率估计约 60%（DealForma/Metix 口径）"),
    (2027.15, "上轮顶点 +6 年", "2027 · 锚点：按 2015→2021 约 6 年的峰-峰节律外推（推演）"),
    (2028.0, "2028 K药专利到期", "2028 · 锚点：K药（2024 年销售 295 亿美元）美国核心专利到期，MNC 补管线节奏变化"),
]


def fig15():
    W, H = 980, 360
    x0, x1 = 70, 930
    yr0, yr1 = 2026.0, 2030.75

    def X(yr):
        return x0 + (yr - yr0) / (yr1 - yr0) * (x1 - x0)

    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="2026-2030 见顶窗口推演" preserveAspectRatio="xMidYMid meet">']
    for y in (2026, 2027, 2028, 2029, 2030):
        x = X(y)
        parts.append(f'<line x1="{x:.1f}" y1="46" x2="{x:.1f}" y2="{H-34}" stroke="{RC.GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{H-14}" text-anchor="middle" font-size="12" fill="{RC.TXT_DIM}">{y}</text>')
    # 当前时点
    xn = X(2026.70)
    parts.append(f'<line x1="{xn:.1f}" y1="46" x2="{xn:.1f}" y2="{H-34}" stroke="{RC.RED}" stroke-width="1.4" stroke-dasharray="6 3"/>')
    parts.append(f'<text x="{xn:.1f}" y="40" text-anchor="middle" font-size="11" fill="{RC.RED}">当前 2026-09</text>')
    # 锚点（顶部车道）
    for yr, label, tip in ANCHORS15:
        x = X(yr)
        parts.append(f'<g data-series-group="s3">')
        parts.append(f'<path d="M{x:.1f},62 l7,9 l-7,9 l-7,-9 Z" fill="{RC.GREEN}"><title>{RC.esc(tip)}</title></path>')
        parts.append(f'<line x1="{x:.1f}" y1="80" x2="{x:.1f}" y2="128" stroke="{RC.GREEN}" stroke-width="1" stroke-dasharray="3 2" opacity="0.6"/>')
        parts.append(f'<text x="{x:.1f}" y="98" text-anchor="middle" font-size="10.5" fill="{RC.GREEN}">{RC.esc(label)}</text>')
        parts.append("</g>")
    # 情景窗口条
    for gkey, a, b, y, label, prob, tip in BARS15:
        color = _G15[gkey][1]
        xa, xb = X(a), X(b)
        parts.append(f'<g data-series-group="{gkey}">')
        parts.append(f'<rect x="{xa:.1f}" y="{y}" width="{xb - xa:.1f}" height="34" rx="8" fill="{color}" fill-opacity="0.28" stroke="{color}" stroke-width="1.6" stroke-dasharray="6 3"><title>{RC.esc(label + "（窗口 " + str(a) + "-" + str(b) + "，主观概率 " + prob + "）" + "：" + tip)}</title></rect>')
        parts.append(f'<text x="{(xa + xb) / 2:.1f}" y="{y + 21:.1f}" text-anchor="middle" font-size="12" font-weight="600" fill="{color}">{RC.esc(label)}（{prob}）</text>')
        parts.append("</g>")
    parts.append(f'<text x="{x0}" y="{H - 0}" font-size="10.5" fill="{RC.TXT_DIM}">读法：虚线条为主观推演的见顶时间窗口（非预测承诺）；菱形为可核验的产业锚点。概率三档合计 100%。</text>')
    parts.append("</svg>")
    legend = RC._legend_html([(k, v[1], v[0], k != "s3") for k, v in _G15.items()])
    return "".join(parts), legend


# ---------------------------------------------------------------- 章节 HTML

def chapter_html(C, JC) -> str:
    svg14, lg14 = fig14()
    svg15, lg15 = fig15()

    fig14_html = RC.figure_block(
        "fig-c14", 14, "上一轮周期见顶的传导时序（2020-2022，事实层）",
        ["类型：事件时间轴", "期间：2020-03 至 2022 全年", "口径：官方/行情/数据库原始记录（见角标）"],
        svg14, lg14,
        f"核心发现：顶点是「流动性预期转向（触发器）× 估值泡沫化（放大器）× IPO 窗口（传导器）」的共振——XBI 于 2021-02-09 率先见顶{C('E-041')}，而 IPO（105 起/145 亿美元）{C('E-037')}、港股 18A（20 家创纪录）{C('E-043')}与一级市场 VC（557 亿美元）{C('E-007')}均以 2021 全年为顶，2022 年在 taper→加息 425bp 的紧缩路径下同步速冻{C('E-044')}；中国 CDE 新政（2021-07）{C('E-042')}与美国 Aduhelm 争议（2021-06）{C('E-045')}分别从两端压制了监管情绪。",
        RC.data_table(["时点", "事件", "类别", "关键数值/口径"], [
            ["2020-03", "美联储降至 0-0.25% + 无限量 QE", "货币政策", "流动性极宽松起点"],
            ["2021-02-09", "XBI 盘中 174.79 美元，历史最高", "二级市场", "收盘最高 173.99（前一日）"],
            ["2021-06-07", "FDA 加速批准 Aduhelm，咨询委员辞职", "政策/监管", "替代终点获批，监管宽松顶点信号"],
            ["2021-07-02", "CDE 临床价值导向征求意见稿", "政策/监管", "me-too 门槛抬升，7-06 医药股大跌"],
            ["2021 全年", "全球 biotech IPO 105 起/145 亿美元", "一二级融资", "周期顶点（DRI 口径）"],
            ["2021 全年", "港股 18A 20 家上市（历史纪录）", "一二级融资", "募资约 377 亿港元"],
            ["2021 全年", "全球 biopharma VC 557 亿美元", "一二级融资", "周期顶点（PitchBook 口径）"],
            ["2021-11 / 2021-12", "taper 启动 → 加倍提速、删「暂时性」", "货币政策", "紧缩路径确认"],
            ["2022-03 → 2022 全年", "首次加息，全年累计 +425bp", "货币政策", "利率 0-0.25% → 4.25-4.50%"],
            ["2022-05-12", "XBI 最低 61.78 美元", "二级市场", "最大回撤 -64.5%"],
            ["2022 全年", "IPO 24 起；一级市场 -43%（中国 -55%）", "一二级融资", "速冻确认"],
        ], "事件性质以图注角标来源为准；年度汇总值绘于对应年份内位置"),
    )

    fig15_html = RC.figure_block(
        "fig-c15", 15, "下一轮上行周期见顶时间窗口推演（2026-2030，推演层）",
        ["类型：窗口推演（甘特式）", "性质：主观概率推演，非预测承诺", "锚点：K药 2028 / AI 2027 / 周期节律"],
        svg15, lg15,
        f"<span class='tag tag-p1'>推算</span> 基准判断：下一轮顶部落在 <strong>2028 年前后（2027H2-2029H1）</strong>，主观概率约 50%；提前至 2027 年见顶约 30%、延后至 2029-2030 约 20%。三个可核验锚点：K药 2028 年美国专利到期（2024 年销售 295 亿美元，史上最大单品专利悬崖）{C('E-046')}、AI 药物 2027 年验证点（首个获批概率估计约 60%）{C('E-034')}、以及上轮顶点 +6 年的周期节律（推演）。货币政策位置是最大摆动项{C('E-027')}。",
        RC.data_table(["情景", "见顶窗口", "主观概率", "核心假设"], [
            ["提前情景", "2027 年（2026H2-2028H1）", "约 30%", "再通胀迫使重新加息 / IPO 抽血过快 / 重大临床失败提前刺破风险偏好"],
            ["基准情景", "2028 年前后（2027H2-2029H1）", "约 50%", "峰-峰约 6 年节律 + K药 2028 到期 + AI 2027 验证 + 降息周期中后段"],
            ["延后情景", "2029-2030 年", "约 20%", "利率低位更久 + 并购/BD 持续超预期的结构性牛市"],
        ], "概率为主观推演，用于动态证伪；锚点事件见图中菱形标记"),
    )

    return f'''
<div class="content-section" id="sec-cycle">
<h2>数据详章 6 · 周期复盘与前瞻：2021 年为何见顶、下一轮何时见顶（追加章节）</h2>
{JC("本节判断", "上一轮（2021 年）融资顶点的本质是<strong>「流动性预期转向（触发器）× 估值泡沫化（放大器）× IPO 窗口（传导器）」</strong>的共振，而非产业基本面恶化；展望下一轮，若以当前为新一轮上行周期起点，基准见顶窗口在 <strong>2028 年前后（2027H2-2029H1）</strong>——但因本轮复苏由产业性需求（专利悬崖并购 + 中国 BD + AI 范式）驱动、而非放水驱动，见顶形态更可能是<em>「结构性分化见顶」</em>而非 2021 式全面崩塌。本章事实层（已发生）与推演层（假设性前瞻）全程分开标注。")}
<p class="small">本章为 2026-09-16 应要求追加的章节：第一部分为历史复盘（事实层，对应新增证据 <a class="source-link" href="#sec-evidence">E-041 ~ E-045</a> 与既有证据），第二部分为未来推演（推演层，概率与窗口均为主观判断，用于动态证伪）。</p>

<h3>9.1 历史复盘：2021 年见顶的五维度机制</h3>
<table class="data-table">
<thead><tr><th>维度</th><th>关键事实（证据）</th><th>作用逻辑（推断）</th></tr></thead>
<tbody>
<tr><td><b>① 宏观流动性</b></td><td>2020-03 零利率 + 无限量 QE 催生史诗级宽松；2021-10 CPI 同比 6.2%，2021-11 taper 启动、12 月提速并删除「暂时性」表述，2022-03 首次加息、全年 +425bp{C('E-044')}</td><td>成长股定价对贴现率最敏感——<b>顶点出现在「预期转向」而非「实际加息」</b>：XBI 于 2021-02 见顶时 CPI 已连续 3 个月超预期，市场开始为紧缩定价；taper（2021-11）确认拐点后，下跌进入第二阶段</td></tr>
<tr><td><b>② 资本市场表现</b></td><td>XBI 2021-02-09 盘中 174.79 美元历史见顶，2022-05-12 最低 61.78 美元，最大回撤 -64.5%{C('E-041')}</td><td>二级市场是整条传导链的「温度计」：等权重构成的 XBI 对中小 biotech 情绪最敏感，其领先见顶预示风险偏好已先行逆转</td></tr>
<tr><td><b>③ 行业政策</b></td><td>美国：2021-06-07 FDA 不顾咨询委员会全票反对加速批准 Aduhelm，三名委员辞职，国会随后启动调查{C('E-045')}；中国：2021-07-02 CDE 发布《以临床价值为导向的抗肿瘤药物临床研发指导原则》征求意见稿，7-06 医药股集体大跌{C('E-042')}</td><td>Aduhelm 事件标志「监管宽松」的情绪顶点（此后监管信用受损、加速审批趋严）；CDE 新政则直接打击 me-too 管线的商业化预期——<b>中美两端同时压缩「伪创新」的估值空间</b></td></tr>
<tr><td><b>④ 一二级估值水平</b></td><td>2021 年全口径融资 1,196 亿美元（历史最高）{C('E-014')}；biopharma VC 557 亿美元{C('E-007')}；IPO 105 起/145 亿美元{C('E-037')}；中国一级市场约 149 亿美元（推算）{C('E-015')}；港股 18A 20 家上市/约 377 亿港元，双双创纪录{C('E-043')}</td><td>一级市场估值跟随二级水涨船高：pre-IPO 轮按「上市即翻倍」定价，IPO 又以高估值滥发——<b>当二级接盘意愿消失，倒挂沿「二级 → IPO → 一级」反噬</b></td></tr>
<tr><td><b>⑤ 二级 → 一级传导机制</b></td><td>XBI 顶点（2021-02）→ IPO 年度顶点（2021 全年，2022 年骤降至 24 起）{C('E-037')}→ 一级市场年度顶点（2021 年 557 亿，2022 年 -43%）{C('E-007')}{C('E-015')}</td><td>（推断）二级领先 IPO 约 1-2 个季度、领先一级融资约 2-4 个季度：二级估值压缩先关闭 IPO 窗口，IPO 关闭再抽走一级的退出预期与 LP 回流，一级最后在「估值倒挂 + 退出无门」中速冻</td></tr>
</tbody></table>
{fig14_html}
<h4>因素权重（推断，主观评估）</h4>
<table class="data-table">
<thead><tr><th>因素</th><th>角色</th><th>主观权重</th><th>依据</th></tr></thead>
<tbody>
<tr><td>流动性预期转向</td><td class="highlight">触发器</td><td>约 35%</td><td>XBI 顶点（2021-02）与通胀连续超预期、taper 预期发酵的时点高度吻合{C('E-041')}{C('E-044')}</td></tr>
<tr><td>一二级估值泡沫化</td><td class="warning">放大器</td><td>约 25%</td><td>2021 年各口径融资额均创历史新高，pre-IPO 定价脱离基本面{C('E-014')}{C('E-037')}</td></tr>
<tr><td>IPO 窗口关闭</td><td class="warning">传导器</td><td>约 20%</td><td>IPO 从 105 起骤降至 24 起，直接切断一级退出预期{C('E-037')}</td></tr>
<tr><td>政策收紧（中/美）</td><td>助推</td><td>约 15%</td><td>CDE 新政压制 me-too 估值；Aduhelm 后监管信用逆转{C('E-042')}{C('E-045')}</td></tr>
<tr><td>产业/情绪事件</td><td>边际</td><td>约 5%</td><td>个别临床失败与获批争议影响情绪但非主因</td></tr>
</tbody></table>

<h3>9.2 未来推演：下一轮上行周期何时见顶</h3>
{JC("条件性研判（推演层）", f"<span class='tag tag-p1'>推算</span> 假设当前已进入新一轮上行周期，<strong>基准见顶窗口为 2028 年前后（2027H2-2029H1，主观概率约 50%）</strong>；提前至 2027 年见顶约 30%、延后至 2029-2030 年约 20%。四个锚点：① 周期节律——上轮 XBI 顶点（2021-02）{C('E-041')} 与 2015 年 biotech 顶点间隔约 6 年，外推下一顶点在 2027 年前后（推演假设）；② K药 2028 年美国专利到期{C('E-046')}——史上最大单品专利悬崖既是本轮并购需求之源，也可能在 2028 年后改变 MNC 补管线的节奏与预算；③ AI 药物 2027 年验证点（首个获批概率估计约 60%）{C('E-034')}——兑现则延长行情、证伪则刺破新范式溢价；④ 货币政策位置——当前利率 3.63% 且本轮回暖非降息驱动{C('E-027')}，若 2026-2027 降息重启则行情弹性与寿命同步放大，见顶推迟。")}
{fig15_html}
<h4>可能触发见顶的七类情形（推演）</h4>
<table class="data-table">
<thead><tr><th>情形</th><th>触发路径</th><th>2021 年对应</th><th>当前可读信号</th></tr></thead>
<tbody>
<tr><td><b>① 货币政策转向</b></td><td>再通胀 → 暂停降息甚至再加息 → 成长股贴现率抬升</td><td>taper + 425bp{C('E-044')}</td><td>逐次 FOMC 点阵图；CPI 反弹至 3.5%+</td></tr>
<tr><td><b>② IPO 通道收紧</b></td><td>二级回撤 → IPO 冰封 → 一级退出预期崩塌</td><td>IPO 105 起 → 24 起{C('E-037')}</td><td>连续 2 个月零 IPO 或撤材料潮</td></tr>
<tr><td><b>③ 估值泡沫化</b></td><td>XBI 创新高后 IPO/增发抽血过快，pre-IPO 倒挂再现</td><td>2021 年各口径齐创纪录{C('E-014')}</td><td>XBI 显著突破 174.79 前高{C('E-041')}且 IPO 单月募资异常放大</td></tr>
<tr><td><b>④ 重大临床失败 / 监管事件</b></td><td>标志性 III 期失败或获批争议 → 板块情绪逆转</td><td>Aduhelm 获批争议{C('E-045')}</td><td>AI 药物/代谢领域关键读出的黑天鹅</td></tr>
<tr><td><b>⑤ License-out 降温</b></td><td>MNC 预算收紧或同质化供给过剩 → 首付款下降 → 中国第二融资曲线受损</td><td>—（上轮无此结构）</td><td>季度首付款同比转负{C('E-023')}</td></tr>
<tr><td><b>⑥ 药价政策冲击</b></td><td>MFN/IRA 挤压 MNC 利润 → 并购预算收缩（或反向强化引进需求，双向）</td><td>—（上轮无此政策）</td><td>MFN 执行细则、IRA 第三轮名单{C('E-027')}</td></tr>
<tr><td><b>⑦ 地缘政策升级</b></td><td>BIOSECURE 细则扩大 / 关税升级 → 中国资产与 CXO 链受损</td><td>—（上轮无此变量）</td><td>BIOSECURE 执行细则（已立法）{C('E-029')}</td></tr>
</tbody></table>

<h3>9.3 见顶预警仪表盘（8 项指标，含 2 项数据缺口）</h3>
<table class="data-table">
<thead><tr><th>指标</th><th>当前读数（2026-09）</th><th>预警阈值</th><th>数据状态 / 频率</th></tr></thead>
<tbody>
<tr><td>XBI 自高点回撤</td><td>约 170，逼近前高 174.79{C('E-041')}</td><td class="warning">回撤 &gt;25% 且持续一季</td><td>可跟踪 · 周度</td></tr>
<tr><td>IPO 月度数量</td><td>至 8 月 20 家、中位 3.02 亿{C('E-032')}</td><td class="warning">连续 2 个月零 IPO</td><td>可跟踪 · 月度</td></tr>
<tr><td>早期融资占比</td><td>32%（2025）{C('E-007')}</td><td class="warning">跌破 25%（断层加剧）</td><td>可跟踪 · 季度</td></tr>
<tr><td>License-out 首付款同比</td><td>2025 年 70 亿美元{C('E-023')}</td><td class="warning">同比转负</td><td>可跟踪 · 季度</td></tr>
<tr><td>并购溢价水平</td><td>2026H1 近 2/3 并购 ≥10 亿美元{C('E-001')}</td><td class="warning">头部交易溢价显著下降</td><td>可跟踪 · 季度</td></tr>
<tr><td>通胀 / 利率路径</td><td>3.63%（2025-12 起维持）{C('E-027')}</td><td class="warning">CPI 反弹 → 再加息预期</td><td>可跟踪 · 逐次 FOMC</td></tr>
<tr><td>VC 募资额（LP 端）</td><td>—</td><td class="warning">募资同比连续两年下滑</td><td><span class="tag tag-dim">数据缺口</span> · 需补 PitchBook NVCA 季报</td></tr>
<tr><td>增发折价率</td><td>—</td><td class="warning">折价率走阔 &gt;15%</td><td><span class="tag tag-dim">数据缺口</span> · 需补 Jefferies 月度统计</td></tr>
</tbody></table>

<h3>9.4 本轮与 2021 年的「同与不同」→ 见顶形态预判</h3>
<table class="data-table">
<thead><tr><th>相同点（节律可复用）</th><th>不同点（形态将分化）</th></tr></thead>
<tbody>
<tr><td>二级领先于 IPO、IPO 领先于一级的传导时序不变{C('E-037')}{C('E-041')}</td><td>本轮复苏<b>非降息驱动</b>（利率 3.63% 暂停期），对利率路径敏感度下降{C('E-006')}{C('E-027')}</td></tr>
<tr><td>估值泡沫化仍是最大内生风险——XBI 已逼近前高{C('E-041')}</td><td>需求侧有<b>专利悬崖的刚性买盘</b>（2025-2030 敞口 &gt;2,000 亿美元）托底{C('E-032')}</td></tr>
<tr><td>政策仍是最快的外生冲击（对标 CDE 新政与 Aduhelm 的情绪杀伤力）{C('E-042')}{C('E-045')}</td><td>中国存在 <b>BD 第二融资曲线</b>（首付款 70 亿美元 ≈ 一级市场），单一股权融资崩塌的破坏力被对冲{C('E-023')}{C('E-011')}</td></tr>
<tr><td>见顶前通常伴随 IPO/增发抽血加速</td><td>AI 制药是新范式变量：2027 年验证点可能单独制造一轮「结构性顶/底」{C('E-034')}</td></tr>
</tbody></table>
<p><strong>形态预判（推演）</strong>：2021 年是「流动性单因子驱动」的全面泡沫，崩塌也是全面的（XBI -64.5%{C('E-041')}）；本轮由多条产业逻辑驱动，见顶更可能呈<em>结构性分化</em>——无 BD 能力、无临床数据的纯故事型公司先行出清，而有专利悬崖买盘支撑的中后期资产与确定性赛道回调更浅。跟踪重点不是「何时崩」，而是预警仪表盘中哪一盏灯先亮。</p>
</div>'''

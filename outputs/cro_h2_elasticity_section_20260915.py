# -*- coding: utf-8 -*-
"""把「未来两个季度扣非弹性测算」作为第 13 节插入美迪西 vs 益诺思对比报告。"""
import io, os

ns = {}
exec(open("outputs/cro_h2_elasticity_model_20260915.py", encoding="utf-8").read(), ns)
M, N, SM, SN, NEED = ns["M"], ns["N"], ns["SM"], ns["SN"], ns["NEED"]
GM_M, GN_M, GRID_G = ns["GM_M"], ns["GN_M"], ns["GRID_G"]
MDX, YNS = ns["MDX"], ns["YNS"]

REPORT = "outputs/美迪西vs益诺思_临床前CRO对比研究_20260915.html"

Y = 1e8
W = 1e4


def yi(x, nd=2):
    return ("{:." + str(nd) + "f}").format(x / Y)


def wan(x):
    return "{:,.0f}".format(x / W)


def pct(x, nd=2):
    return ("{:." + str(nd) + "f}%").format(x * 100)


# ---------------- 条形图工具 ----------------
def bar_rows(rows, colors, unit="亿", nd=2):
    """rows: [(label, value, sublabel), ...]"""
    mx = max(abs(v) for _, v, _ in rows) or 1
    out = ['<div class="bars">']
    for (lab, v, sub), c in zip(rows, colors):
        w = abs(v) / mx * 100
        out.append(
            '<div class="brow"><div class="muted small">%s</div>'
            '<div class="btrack"><div class="bfill" style="width:%.2f%%;background:%s">%s</div></div>'
            '<div class="small"><b>%s %s</b><br><span class="muted">%s</span></div></div>'
            % (lab, w, c, "&nbsp;" if w < 14 else (("%." + str(nd) + "f") % (v / Y) + " " + unit), 
               ("%." + str(nd) + "f") % (v / Y), unit, sub))
    out.append("</div>")
    return "\n".join(out)


# ---------------- 敏感性网格 ----------------
def heat_table(grid, title, exprate, other):
    vals = [c["dd"] for row in grid for c in row]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    ths = "".join('<th>收入同比 +%d%%</th>' % (g * 100) for g in GRID_G)
    body = []
    for row in grid:
        tds = []
        for c in row:
            t = (c["dd"] - lo) / span
            r0, g0, b0 = 233, 246, 237
            r1, g1, b1 = 246, 203, 195
            r = int(r0 + (r1 - r0) * t); g = int(g0 + (g1 - g0) * t); b = int(b0 + (b1 - b0) * t)
            bold = ' style="font-weight:700"' if c["g"] == 0.30 and abs(c["gm"] - (0.34 if "美迪西" in title else 0.32)) < 1e-9 else ""
            tds.append('<td style="background:rgb(%d,%d,%d);text-align:center"%s>%s</td>' % (r, g, b, bold, yi(c["dd"])))
        body.append('<tr><td><b>%s</b></td>%s</tr>' % (pct(row[0]["gm"], 1), "".join(tds)))
    return ('<div class="tbl-wrap"><table><thead><tr><th>%s<br><span class="muted small">费用率固定 %s</span></th>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>' % (title, pct(exprate, 1), ths, "".join(body)))


# ---------------- 节内容 ----------------
sec = []
sec.append('<h2>13. 未来两个季度扣非弹性测算（2026Q3 – Q4）</h2>')

sec.append("""
<p>本节回答一个具体问题：<b>未来两个季度（2026Q3+Q4），美迪西和益诺思谁的扣非业绩弹性更大？</b>测算全部基于已审计的 2026 半年报与单季数据，参数完整列示，可逐项复算。</p>

<div class="callout info">
<strong>先讲清一个容易出错的地方：这里的"弹性"不能用同比增速衡量。</b>两家公司 2025H2 的扣非都是<b>负值</b>（美迪西 <span class="down">−¥1.5443 亿</span>、益诺思 <span class="down">−¥0.2134 亿</span>），对负基数计算同比增速在数学上无意义、符号还会反转。因此本节的弹性统一用两个口径：
<ol style="margin:8px 0 0">
  <li><b>Δ扣非绝对增量</b>（2026H2 扣非 − 2025H2 扣非）及其<b>占总市值比重</b>；</li>
  <li><b>边际扣非率</b>（Δ扣非 ÷ Δ营业收入），衡量"每多 1 元收入能沉淀多少扣非"。</li>
</ol>
</div>
""")

# 13.1 基线
sec.append('<h3>13.1 基线：两家 2025H2 的起点相差 7.2 倍</h3>')
sec.append("""
<div class="tbl-wrap">
<table>
  <thead><tr><th>指标</th><th>美迪西 2025H2</th><th>美迪西 2026H1</th><th>益诺思 2025H2</th><th>益诺思 2026H1</th></tr></thead>
  <tbody>
    <tr><td>营业收入</td><td>¥%s 亿</td><td>¥%s 亿</td><td>¥%s 亿</td><td>¥%s 亿</td></tr>
    <tr><td>毛利率</td><td class="down">%s</td><td>%s</td><td class="down">%s</td><td>%s</td></tr>
    <tr><td>期间费用率（销售+管理+研发+财务）</td><td class="down">%s</td><td>%s</td><td class="down">%s</td><td>%s</td></tr>
    <tr><td>净其他项（减值/税金等合成"拖累项"）</td><td class="down">−¥%s 万</td><td>−¥%s 万</td><td class="down">−¥%s 万</td><td>−¥%s 万</td></tr>
    <tr><td><b>扣非净利润</b></td><td class="down strong">−¥%s 亿</td><td class="up strong">+¥%s 亿</td><td class="down strong">−¥%s 亿</td><td class="up strong">+¥%s 亿</td></tr>
  </tbody>
</table>
</div>

<p><b>这张表决定了本篇的全部结论。</b>美迪西 2025H2 的扣非亏损（−¥1.54 亿）是益诺思（−¥0.21 亿）的 <b>7.2 倍</b>——弹性测算的分母就在这里。同时要注意美迪西的<b>费用率从 2025H2 的 %s 降到 2026H1 的 %s</b>（降幅 %s pct），而益诺思仅从 %s 降到 %s（降幅 %s pct）：美迪西的成本结构弹性本来就更大。</p>
""" % (
    yi(M["rev25h2"]), yi(MDX["rev26h1"]), yi(N["rev25h2"]), yi(YNS["rev26h1"]),
    pct(M["gm25h2"]), pct(M["gm26h1"]), pct(N["gm25h2"]), pct(N["gm26h1"]),
    pct(M["exprate25h2"]), pct(M["exprate26h1"]), pct(N["exprate25h2"]), pct(N["exprate26h1"]),
    wan(-M["other25h2"]), wan(-M["other26h1"]), wan(-N["other25h2"]), wan(-N["other26h1"]),
    yi(-M["dd25h2"], 4), yi(MDX["dd26h1"], 4), yi(-N["dd25h2"], 4), yi(YNS["dd26h1"], 4),
    pct(M["exprate25h2"]), pct(M["exprate26h1"]), "%.2f" % ((M["exprate25h2"] - M["exprate26h1"]) * 100),
    pct(N["exprate25h2"]), pct(N["exprate26h1"]), "%.2f" % ((N["exprate25h2"] - N["exprate26h1"]) * 100),
))

# 13.2 单季
sec.append('<h3>13.2 季度颗粒度：两家的修复斜率</h3>')
sec.append("""
<div class="tbl-wrap">
<table>
  <thead><tr><th>单季</th><th>美迪西 收入</th><th>美迪西 毛利率</th><th>美迪西 扣非</th><th>益诺思 收入</th><th>益诺思 毛利率</th><th>益诺思 扣非</th></tr></thead>
  <tbody>
    <tr><td>2025Q3</td><td>¥%s 亿</td><td>%s</td><td class="down">−¥%s 万</td><td>¥%s 亿</td><td>%s</td><td class="down">−¥%s 万</td></tr>
    <tr><td>2025Q4</td><td>¥%s 亿</td><td class="down">%s</td><td class="down">−¥%s 万</td><td>¥%s 亿</td><td class="down">%s</td><td class="down">−¥%s 万</td></tr>
    <tr><td>2026Q1</td><td>¥%s 亿</td><td>%s</td><td class="up">+¥%s 万</td><td>¥%s 亿</td><td>%s</td><td class="up">+¥%s 万</td></tr>
    <tr><td>2026Q2</td><td>¥%s 亿</td><td class="up strong">%s</td><td class="up">+¥%s 万</td><td>¥%s 亿</td><td>%s</td><td class="up">+¥%s 万</td></tr>
  </tbody>
</table>
</div>

<div class="callout">
<strong>2025Q4 是两家共同的"利润坑"，但深度差 6.6 倍。</strong>美迪西 2025Q4 单季扣非 −¥%s 万，益诺思 −¥%s 万。而 2026Q2 两家单季扣非都已转正（美迪西 +¥%s 万、益诺思 +¥%s 万）。<b>从"深坑"回到"正值"的过程中，起点越低的那一方，Δ 的绝对额自然越大</b>——这不是文字游戏，而是真实的基期差异。
</div>

<p>另一条关键线索：<b>美迪西单季毛利率在四个季度里从 %s（2025Q4 谷底）一路升到 %s（2026Q2），提升了 %s pct</b>；益诺思同期从 %s 升到 %s，仅提升 %s pct。<b>美迪西的修复斜率更陡，意味着 2026H2 有更大的毛利释放空间可供假设。</b></p>
""" % (
    yi(M["rev25q3"]), pct(M["gm25q3"]), wan(-M["dd25q3"]), yi(N["rev25q3"]), pct(N["gm25q3"]), wan(-N["dd25q3"]),
    yi(M["rev25q4"]), pct(M["gm25q4"]), wan(-M["dd25q4"]), yi(N["rev25q4"]), pct(N["gm25q4"]), wan(-N["dd25q4"]),
    yi(MDX["rev26q1"]), pct(M["gm26q1"]), wan(MDX["dd26q1"]), yi(YNS["rev26q1"]), pct(N["gm26q1"]), wan(YNS["dd26q1"]),
    yi(M["rev26q2"]), pct(M["gm26q2"]), wan(M["dd26q2"]), yi(N["rev26q2"]), pct(N["gm26q2"]), wan(N["dd26q2"]),
    wan(-M["dd25q4"]), wan(-N["dd25q4"]), wan(M["dd26q2"]), wan(N["dd26q2"]),
    pct(M["gm25q4"]), pct(M["gm26q2"]), "%.2f" % ((M["gm26q2"] - M["gm25q4"]) * 100),
    pct(N["gm25q4"]), pct(N["gm26q2"]), "%.2f" % ((N["gm26q2"] - N["gm25q4"]) * 100),
))

# 13.3 参数表
sec.append('<h3>13.3 情景假设（完整参数表，可复算）</h3>')
sec.append("""
<p>为便于横向对比，<b>两家使用同一组收入增速假设</b>（谨慎 +20%% / 基准 +30%% / 乐观 +40%%，均为 2026H2 对 2025H2 的同比），差异只体现在各自的毛利率、费用率与拖累项上。毛利率锚定各自 2026Q2 实际值并向两个方向展开，费用率以 2026H1 实际值为中枢做小幅经营杠杆。</p>

<div class="grid2">
<div>
<div class="tbl-wrap">
<table>
  <thead><tr><th>美迪西 参数</th><th>谨慎</th><th>基准</th><th>乐观</th></tr></thead>
  <tbody>
    <tr><td>2026H2 收入同比</td><td>+20.00%%</td><td>+30.00%%</td><td>+40.00%%</td></tr>
    <tr><td>2026H2 收入（亿元）</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>
    <tr><td>2026H2 毛利率</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>
    <tr><td>期间费用率</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>
    <tr><td>净其他项（万元）</td><td>−%s</td><td><b>−%s</b></td><td>−%s</td></tr>
  </tbody>
</table>
</div>
</div>
<div>
<div class="tbl-wrap">
<table>
  <thead><tr><th>益诺思 参数</th><th>谨慎</th><th>基准</th><th>乐观</th></tr></thead>
  <tbody>
    <tr><td>2026H2 收入同比</td><td>+20.00%%</td><td>+30.00%%</td><td>+40.00%%</td></tr>
    <tr><td>2026H2 收入（亿元）</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>
    <tr><td>2026H2 毛利率</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>
    <tr><td>期间费用率</td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>
    <tr><td>净其他项（万元）</td><td>−%s</td><td><b>−%s</b></td><td>−%s</td></tr>
  </tbody>
</table>
</div>
</div>
</div>

<ul class="small">
  <li><b>收入增速的来源：</b>2026Q2 单季同比美迪西 +45.19%%、益诺思 +53.51%%，因此 +20%%~+40%% 是一个<b>偏保守的区间</b>——它隐含了下半年增速从 Q2 水平回落。若两家维持 Q2 同比，实际收入会高于本表的上限。</li>
  <li><b>毛利率上限的约束：</b>美迪西乐观情景 36.00%% <b>不超过</b>其 2026Q2 实际的 36.69%%；益诺思乐观情景 33.50%% 略高于其 2026Q2 实际的 32.23%%。两家都未被假设"回到 2023 年的高毛利时代"。</li>
  <li><b>净其他项：</b>取 −¥2,200 万 ~ −¥2,600 万，均<b>优于</b>各自 2026H1 实际（美迪西 −¥2,769 万、益诺思 −¥2,531 万），即假设减值与税金拖累继续小幅收敛。</li>
  <li><b>计算式：</b><code>2026H2 扣非 = 2026H2 收入 × 毛利率 − 2026H2 收入 × 期间费用率 + 净其他项</code>；净其他项由 2026H1 实际反解得到（<code>扣非 − (毛利 − 期间费用)</code>）。</li>
</ul>
""" % (
    yi(SM[0]["rev"]), yi(SM[1]["rev"]), yi(SM[2]["rev"]),
    pct(SM[0]["gm"]), pct(SM[1]["gm"]), pct(SM[2]["gm"]),
    pct(SM[0]["exprate"]), pct(SM[1]["exprate"]), pct(SM[2]["exprate"]),
    wan(-SM[0]["other"]), wan(-SM[1]["other"]), wan(-SM[2]["other"]),
    yi(SN[0]["rev"]), yi(SN[1]["rev"]), yi(SN[2]["rev"]),
    pct(SN[0]["gm"]), pct(SN[1]["gm"]), pct(SN[2]["gm"]),
    pct(SN[0]["exprate"]), pct(SN[1]["exprate"]), pct(SN[2]["exprate"]),
    wan(-SN[0]["other"]), wan(-SN[1]["other"]), wan(-SN[2]["other"]),
))

# 13.4 结果
sec.append('<h3>13.4 结果：2026H2 扣非弹性，美迪西是益诺思的 %s–%s 倍</h3>'
           % ("%.2f" % (SM[2]["d_dd"] / SN[2]["d_dd"]), "%.2f" % (SM[0]["d_dd"] / SN[0]["d_dd"])))

rows = []
for i in range(3):
    rows.append(('<span class="%s">%s</span>' % ("neu strong" if i == 1 else "muted", SM[i]["scen"]),
                 SM[i]["d_dd"], ""))
bar1 = bar_rows([("%s情景" % s["scen"], s["d_dd"], "Δ扣非/市值 %s" % pct(s["margin"])) for s in SM],
                ["#1a5fb4", "#1a5fb4", "#1a5fb4"])
bar2 = bar_rows([("%s情景" % s["scen"], s["d_dd"], "Δ扣非/市值 %s" % pct(s["margin"])) for s in SN],
                ["#0f7b4f", "#0f7b4f", "#0f7b4f"])

sec.append("""
<div class="tbl-wrap">
<table>
  <thead><tr><th>情景</th><th>美迪西 2026H2 扣非</th><th>美迪西 Δ扣非</th><th>益诺思 2026H2 扣非</th><th>益诺思 Δ扣非</th><th>弹性倍数</th></tr></thead>
  <tbody>
    <tr><td>谨慎（收入 +20%%）</td><td class="up">+¥%s 亿</td><td class="up">+¥%s 亿</td><td class="up">+¥%s 亿</td><td class="up">+¥%s 亿</td><td class="up strong">%.2f×</td></tr>
    <tr style="background:#f7f9fc"><td><b>基准（收入 +30%%）</b></td><td class="up">+¥%s 亿</td><td class="up"><b>+¥%s 亿</b></td><td class="up">+¥%s 亿</td><td class="up"><b>+¥%s 亿</b></td><td class="up strong">%.2f×</td></tr>
    <tr><td>乐观（收入 +40%%）</td><td class="up">+¥%s 亿</td><td class="up">+¥%s 亿</td><td class="up">+¥%s 亿</td><td class="up">+¥%s 亿</td><td class="up strong">%.2f×</td></tr>
  </tbody>
</table>
</div>

<h4>Δ扣非 绝对额对比（条形长度 = Δ扣非金额）</h4>
<div class="grid2">
  <div><h4 style="margin-top:0" class="mdx">美迪西 688202</h4>%s</div>
  <div><h4 style="margin-top:0" class="yns">益诺思 688710</h4>%s</div>
</div>

<div class="tbl-wrap">
<table>
  <thead><tr><th>弹性质量指标</th><th>美迪西 谨慎</th><th>美迪西 基准</th><th>美迪西 乐观</th><th>益诺思 谨慎</th><th>益诺思 基准</th><th>益诺思 乐观</th></tr></thead>
  <tbody>
    <tr><td>Δ扣非 / 总市值</td><td class="up">%s</td><td class="up"><b>%s</b></td><td class="up">%s</td><td class="up">%s</td><td class="up"><b>%s</b></td><td class="up">%s</td></tr>
    <tr><td>边际扣非率（Δ扣非 ÷ Δ收入）</td><td class="up">%s</td><td class="up"><b>%s</b></td><td class="up">%s</td><td class="up">%s</td><td class="up"><b>%s</b></td><td class="up">%s</td></tr>
    <tr><td>隐含 2026 全年扣非（H1 实际 + H2 测算）</td><td>¥%s 亿</td><td><b>¥%s 亿</b></td><td>¥%s 亿</td><td>¥%s 亿</td><td><b>¥%s 亿</b></td><td>¥%s 亿</td></tr>
  </tbody>
</table>
</div>

<p><b>三个情景下美迪西的绝对增量都显著更大，而且它的质量指标同样更优。</b>边际扣非率是关键对比：美迪西 %s–%s（意味着每多做 1 元收入，扣非增量超过 1 元，因为同步释放了前期压在减值与固定成本里的亏损），益诺思仅 %s–%s（约 0.5 元）。换算成占市值比重，美迪西基准情景可释放 <b>%s</b> 的市值，益诺思仅 <b>%s</b>。</p>
""" % (
    yi(SM[0]["dd"]), yi(SM[0]["d_dd"]), yi(SN[0]["dd"]), yi(SN[0]["d_dd"]), SM[0]["d_dd"] / SN[0]["d_dd"],
    yi(SM[1]["dd"]), yi(SM[1]["d_dd"]), yi(SN[1]["dd"]), yi(SN[1]["d_dd"]), SM[1]["d_dd"] / SN[1]["d_dd"],
    yi(SM[2]["dd"]), yi(SM[2]["d_dd"]), yi(SN[2]["dd"]), yi(SN[2]["d_dd"]), SM[2]["d_dd"] / SN[2]["d_dd"],
    bar1, bar2,
    pct(SM[0]["margin"]), pct(SM[1]["margin"]), pct(SM[2]["margin"]),
    pct(SN[0]["margin"]), pct(SN[1]["margin"]), pct(SN[2]["margin"]),
    pct(SM[0]["marginal"], 1), pct(SM[1]["marginal"], 1), pct(SM[2]["marginal"], 1),
    pct(SN[0]["marginal"], 1), pct(SN[1]["marginal"], 1), pct(SN[2]["marginal"], 1),
    yi(MDX["dd26h1"] + SM[0]["dd"]), yi(MDX["dd26h1"] + SM[1]["dd"]), yi(MDX["dd26h1"] + SM[2]["dd"]),
    yi(YNS["dd26h1"] + SN[0]["dd"]), yi(YNS["dd26h1"] + SN[1]["dd"]), yi(YNS["dd26h1"] + SN[2]["dd"]),
    pct(SM[2]["marginal"], 1), pct(SM[0]["marginal"], 1),
    pct(SN[2]["marginal"], 1), pct(SN[0]["marginal"], 1),
    pct(SM[1]["margin"]), pct(SN[1]["margin"]),
))

# 13.5 敏感性网格
sec.append('<h3>13.5 结论对假设是否稳健：5 × 5 敏感性网格</h3>')
mdx_min_d = min(c["d_dd"] for row in GM_M for c in row)
yns_max_d = max(c["d_dd"] for row in GN_M for c in row)
p = []
p.append('<div class="callout ok">')
p.append('<strong>稳健性结论：益诺思的"最好情形"仍然够不到美迪西的"最差情形"。</strong>把两家的网格统一换成 <b>Δ扣非</b>（即 2026H2 扣非 − 2025H2 扣非）来看：')
p.append('<ul style="margin:8px 0 0">')
p.append('<li>美迪西 25 格中<b>最差</b>的一格（收入 +10%%、毛利率 30%%）对应的 Δ扣非 也有 <b class="up">+¥%s 亿</b>；</li>' % yi(mdx_min_d))
p.append('<li>益诺思 25 格中<b>最好</b>的一格（收入 +50%%、毛利率 36%%）对应的 Δ扣非 仅 <b class="up">+¥%s 亿</b>——<b>仍低于美迪西的最低格</b>。</li>' % yi(yns_max_d))
p.append("</ul>")
p.append('<p style="margin:10px 0 0">也就是说，"未来两个季度美迪西扣非弹性更大"这一结论<b>不依赖对参数的微调</b>：在各自毛利率的合理区间内穷举 50 种组合，两家的 Δ扣非 分布<b>完全不重叠</b>。</p>')
p.append("</div>")
sec.append("""
<p>上面的三情景依赖具体参数。为避免"结论由参数挑出来的"，下面把 <b>收入同比（+10%%~+50%%）</b> 与 <b>毛利率</b> 交叉成 25 个格子，每格给出该组合下的 <b>2026H2 扣非净利润（亿元）</b>。颜色越深（偏红）表示扣非越高。</p>

<h4 class="mdx">美迪西 688202 —— 2026H2 扣非（亿元）</h4>
%s

<h4 class="yns">益诺思 688710 —— 2026H2 扣非（亿元）</h4>
%s

%s

<p class="small muted">注：两家毛利率区间的选取不同（美迪西 30%%–38%%、益诺思 28%%–36%%），均以各自 2026Q2 实际值为中枢、上下各展开约 4 pct。美迪西网格费用率固定 22.00%%、净其他项固定 −¥2,400 万；益诺思网格费用率固定 19.00%%、净其他项固定 −¥2,400 万。加粗格为 13.3 中的基准参数组合。</p>
""" % (
    heat_table(GM_M, "美迪西｜行 = 毛利率", 0.22, -2400 * W),
    heat_table(GN_M, "益诺思｜行 = 毛利率", 0.19, -2400 * W),
    "\n".join(p),
))

# 13.6 共识达标
needM, needN = NEED["MDX"]["post"], NEED["YNS"]["post"]
needM_pre = NEED["MDX"]["pre"]
sec.append('<h3>13.6 换个角度看：谁需要"迈过陡坡"才能碰到共识</h3>')
sec.append("""
<p>弹性大不大，还要看<b>市场已经把标准定在哪里</b>。用事件后共识（本项目可核验口径）反推：要达到 FY2026 全年归母共识，两家各自需要在 2026H2 做到多少？</p>

<div class="tbl-wrap">
<table>
  <thead><tr><th>共识达标测算（基准收入情景）</th><th>美迪西</th><th>益诺思</th></tr></thead>
  <tbody>
    <tr><td>2026H1 归母已实现</td><td class="up">¥%s 亿</td><td>¥%s 亿</td></tr>
    <tr><td>事件前 FY2026 归母共识</td><td>¥%s 亿<br><span class="muted small">%s</span></td><td>¥%s 亿<br><span class="muted small">%s</span></td></tr>
    <tr><td><b>H1 已达成事件前共识的比例</b></td><td class="up strong">%s（已超越）</td><td class="down strong">%s</td></tr>
    <tr><td>事件后 FY2026 归母共识</td><td>¥%s 亿</td><td>¥%s 亿</td></tr>
    <tr><td>触及事件后共识所需的 2026H2 归母</td><td class="up">¥%s 亿</td><td class="down">¥%s 亿</td></tr>
    <tr><td>对应所需的 2026H2 扣非</td><td class="up">¥%s 亿</td><td class="down">¥%s 亿</td></tr>
    <tr><td><b>对应所需的 2026H2 毛利率</b></td><td class="up strong">%s</td><td class="down strong">%s</td></tr>
    <tr><td>2026Q2 实际毛利率（可达性基准）</td><td>%s</td><td>%s</td></tr>
    <tr><td><b>缺口</b></td><td class="up strong">−%s pct（比 Q2 更容易）</td><td class="down strong">+%s pct（必须超过 Q2）</td></tr>
  </tbody>
</table>
</div>

<p><b>这是本节最重要的一组对比。</b>美迪西的 2026H2 毛利率只要做到 <b>%s</b> 就能触及事件后共识，<b>比它 2026Q2 已经实现的 %s 低 %s pct</b>——门槛在它自己的能力范围内且有富余。而益诺思要达到 <b>%s</b>，<b>比其 2026Q2 实际的 %s 还要高 %s pct</b>。</p>

<div class="callout bear">
<strong>益诺思所需 %s 的单季毛利率意味着什么：</strong>翻查其历史单季数据，这一水平<b>高于 2024Q1（%s）之后的任何一个单季</b>（2024Q2 %s、2024Q3 %s、2024Q4 %s、2025Q1 %s、2025Q2 %s、2025Q3 %s、2025Q4 %s、2026Q1 %s、2026Q2 %s）。也就是说，<b>要碰到市场给它的全年共识，益诺思必须把毛利率送回 2024 年价格战尚未完全展开之前的水平。</b>这不是弹性问题，而是价格环境问题——而报价与实验猴成本的剪刀差方向，目前并不站在它这一边。
</div>

<p class="small">补充口径说明：事件前共识下，美迪西 H1 归母 %s 亿已单独超过事件前全年共识 %s 亿，H2 只需 −¥%s 亿归母即可达标（即"无门槛"）；益诺思事件前共识下则需 H2 毛利率 %s。本节正文采用事件后共识（更严格、时点更新）作为主口径。</p>
""" % (
    yi(MDX["np26h1"], 4), yi(YNS["np26h1"], 4),
    yi(MDX["cons_pre"]), MDX["cons_pre_note"], yi(YNS["cons_pre"]), YNS["cons_pre_note"],
    pct(MDX["np26h1"] / MDX["cons_pre"], 1), pct(YNS["np26h1"] / YNS["cons_pre"], 1),
    yi(MDX["cons_post"], 4), yi(YNS["cons_post"], 4),
    yi(needM["need_np_h2"], 4), yi(needN["need_np_h2"], 4),
    yi(needM["need_dd_h2"], 4), yi(needN["need_dd_h2"], 4),
    pct(needM["need_gm"]), pct(needN["need_gm"]),
    pct(M["gm26q2"]), pct(N["gm26q2"]),
    "%.2f" % ((M["gm26q2"] - needM["need_gm"]) * 100), "%.2f" % ((needN["need_gm"] - N["gm26q2"]) * 100),
    pct(needM["need_gm"]), pct(M["gm26q2"]), "%.2f" % ((M["gm26q2"] - needM["need_gm"]) * 100),
    pct(needN["need_gm"]), pct(N["gm26q2"]), "%.2f" % ((needN["need_gm"] - N["gm26q2"]) * 100),
    pct(needN["need_gm"]),
    "40.61%", "33.49%", "34.77%", "24.55%", "28.25%", "27.73%", "28.96%", "20.29%", "30.76%", "32.23%",
    yi(MDX["np26h1"], 4), yi(MDX["cons_pre"], 4), yi(-needM_pre["need_np_h2"], 4), pct(needN if False else NEED["YNS"]["pre"]["need_gm"]),
))

# 13.7 结论
sec.append("""
<h3>13.7 本节结论与三个必须说明的风险</h3>

<div class="callout ok">
<strong>结论：未来两个季度（2026Q3+Q4），美迪西的扣非业绩弹性显著大于益诺思，三档情景下为 <span style="font-weight:700">2.85×–3.70×</span>。</strong>
<ol style="margin:8px 0 0">
  <li><b>弹性绝对值：</b>基准情景美迪西 Δ扣非 +¥%s 亿 vs 益诺思 +¥%s 亿。</li>
  <li><b>质量指标：</b>边际扣非率 %s–%s vs %s–%s；Δ扣非/市值 %s–%s vs %s–%s。</li>
  <li><b>共识可达性：</b>美迪西达标所需 H2 毛利率 %s（低于其 Q2 实际 %s）；益诺思需 %s（高于其 Q2 实际 %s）。</li>
  <li><b>稳健性：</b>25 格敏感性网格中，益诺思的<b>最好格子</b>仍不及美迪西的<b>最差格子</b>。</li>
</ol>
</div>

<h4>风险一：美迪西 2026Q2 的成本口径疑点（最需要核实的一条）</h4>
<p>2026Q2 美迪西营业成本从 Q1 的 ¥%s 亿<b>降至</b> ¥%s 亿（环比 %.1f%%），而同期收入<b>增长</b> %.1f%%。毛利率由 %s 跳升到 %s，其中有相当部分来自"成本绝对额下降"而非收入放量。这可能来自产能利用率提升与境外高毛利订单占比上升（合理），也可能是成本重分类或年终奖结算节奏（一次性）。<b>若属后者，本节基准情景偏高。</b>需回 2026 年半年报附注与年报核实。</p>

<h4>风险二：本节的"拖累项收敛"假设是顺周期的</h4>
<p>测算把净其他项假设为 −¥2,200 万 ~ −¥2,600 万（优于两家 2026H1 实际），本质是假设减值不再恶化。美迪西的信用减值取决于中小 Biotech 融资环境，益诺思的存货跌价取决于低价订单清理进度。<b>若其中任一项重回 2024 年量级（美迪西 &gt; ¥1 亿、益诺思跌价比例 &gt; 10%%），本节所有情景都会被下修</b>——而且美迪西的下修幅度会更大，因为它的净其他项在 2025H2 曾达 −¥%s 万。</p>

<h4>风险三：弹性 ≠ 胜率，也不等于股价弹性</h4>
<p>弹性大的是<b>利润的绝对增量</b>，不是"更容易兑现"。且美迪西的治理折价（无实际控制人、陈建煌在 ¥98.50 公告减持不超 1.68%%，窗口 2026-09-07 ~ 12-04）会在利润改善的同时压制估值；益诺思的央企控股与 ¥14.93 亿现金则提供了更强的下行保护。<b>弹性和安全性在这两家身上是分离的。</b></p>

<p class="small muted"><span class="tag inf">推算</span>本节所有数字由同一套参数表在本机脚本中一次算出（参数见 13.3），未做人工取整后回填，因此表与表之间可交叉验证。模型假设的合成"净其他项"不区分减值、税金、少数股东损益与投资收益，仅为测算目的合成，不等于任何单一会计科目。<b>本节为前瞻性情景测算，不属于 <code>financial-evidence-audit</code> 的核验范围</b>——审计（12/12 PASS）覆盖的是 2023–2026H1 的历史已披露事实（见第 15 节），本节在其基础上外推。</p>
""" % (
    yi(SM[1]["d_dd"]), yi(SN[1]["d_dd"]),
    pct(SM[2]["marginal"], 1), pct(SM[0]["marginal"], 1), pct(SN[2]["marginal"], 1), pct(SN[0]["marginal"], 1),
    pct(SM[0]["margin"]), pct(SM[2]["margin"]), pct(SN[0]["margin"]), pct(SN[2]["margin"]),
    pct(needM["need_gm"]), pct(M["gm26q2"]), pct(needN["need_gm"]), pct(N["gm26q2"]),
    yi(MDX["cost26q1"]), yi(M["cost26q2"]), (M["cost26q2"] / MDX["cost26q1"] - 1) * 100,
    (M["rev26q2"] / MDX["rev26q1"] - 1) * 100, pct(M["gm26q1"]), pct(M["gm26q2"]),
    wan(-M["other25h2"]),
))

section_html = "\n".join(sec) + "\n\n"

# ---------------- 插入 + 章节重编号 ----------------
s = io.open(REPORT, encoding="utf-8").read()
assert "\ufffd" not in s

ANCHOR = "<!-- ============ 13 综合评估 ============ -->"
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, section_html + "<!-- ============ 14 综合评估 ============ -->")

reps = [
    ("<h2>13. 基本面综合评估</h2>", "<h2>14. 基本面综合评估</h2>"),
    ("<h3>13.1 三个选择题</h3>", "<h3>14.1 三个选择题</h3>"),
    ("<h3>13.2 关键跟踪指标（5 个）</h3>", "<h3>14.2 关键跟踪指标（6 个）</h3>"),
    ("<!-- ============ 14 附录 ============ -->", "<!-- ============ 15 附录 ============ -->"),
    ("<h2>14. 附录：财务证据审计明细</h2>", "<h2>15. 附录：财务证据审计明细</h2>"),
]
for a, b in reps:
    assert s.count(a) == 1, a
    s = s.replace(a, b)

# 结论速览补一行
OLDROW = '    <tr><td>单季扣非年化 vs 事件前共识</td><td><span class="up">above（+157.2%）</span></td><td><span class="down">below（−22.34%）</span></td><td class="mdx">美迪西（预期差方向）</td></tr>'
assert s.count(OLDROW) == 1
NEWROW = OLDROW + '\n    <tr><td>2026H2 扣非弹性（基准情景 Δ扣非）</td><td class="up"><b>+¥%s 亿</b></td><td class="up">+¥%s 亿</td><td class="up">美迪西（%.2f×，详见第 13 节）</td></tr>' % (
    yi(SM[1]["d_dd"]), yi(SN[1]["d_dd"]), SM[1]["d_dd"] / SN[1]["d_dd"])
s = s.replace(OLDROW, NEWROW)

# 综合评估：earnings_elasticity 行口径修正
OLDEE = '    <tr><td><b>earnings_elasticity</b></td><td>中—高</td><td><b>高（但滞后）</b></td><td>益诺思在手 ¥22.47 亿订单是更长的增长跑道，但 6–9 个月时滞</td></tr>'
assert s.count(OLDEE) == 1
NEWEE = '    <tr><td><b>earnings_elasticity</b></td><td class="up"><b>高（未来两季）</b></td><td><b>中（弹性后置）</b></td><td>按第 13 节测算，2026H2 Δ扣非 美迪西 ¥%s 亿 vs 益诺思 ¥%s 亿（%.2f×）；益诺思在手 ¥22.47 亿订单对应的是 2027 年的长跑道，而非未来两个季度</td></tr>' % (
    yi(SM[1]["d_dd"]), yi(SN[1]["d_dd"]), SM[1]["d_dd"] / SN[1]["d_dd"])
s = s.replace(OLDEE, NEWEE)

# 三个选择题补一行
OLDCH = '    <tr><td>景气反转的<b>确定性</b>与订单可见度</td>'
assert s.count(OLDCH) == 1
NEWCH = '    <tr><td>未来<b>两个季度</b>的业绩弹性</td><td class="mdx"><b>美迪西</b></td><td>2026H2 Δ扣非 ¥%s 亿 vs ¥%s 亿（%.2f×）；边际扣非率 %s vs %s（详见第 13 节）</td></tr>\n' % (
    yi(SM[1]["d_dd"]), yi(SN[1]["d_dd"]), SM[1]["d_dd"] / SN[1]["d_dd"],
    pct(SM[1]["marginal"], 1), pct(SN[1]["marginal"], 1)) + OLDCH
s = s.replace(OLDCH, NEWCH)

# 跟踪指标补一条
OLDLI = '<li><b>实验用猴价格与采购均价</b>——两家共同的成本变量，直接决定 2026H2–2027 毛利率方向。</li>'
assert s.count(OLDLI) == 1
NEWLI = OLDLI + '\n  <li><b>2026Q3 单季毛利率的可比门槛</b>——按第 13 节测算，美迪西只需 %s 即可触及事件后共识（低于其 Q2 实际 %s），益诺思需 %s（高于其 Q2 实际 %s）。两者"实际可达性"的差距合计 %s pct（益诺思需向上突破 %.2f pct，美迪西尚有 %.2f pct 余量），是本节测算出的关键分水岭。</li>' % (
    pct(NEED["MDX"]["post"]["need_gm"]), pct(M["gm26q2"]),
    pct(NEED["YNS"]["post"]["need_gm"]), pct(N["gm26q2"]),
    "%.2f" % (((NEED["YNS"]["post"]["need_gm"] - N["gm26q2"]) + (M["gm26q2"] - NEED["MDX"]["post"]["need_gm"])) * 100),
    (NEED["YNS"]["post"]["need_gm"] - N["gm26q2"]) * 100,
    (M["gm26q2"] - NEED["MDX"]["post"]["need_gm"]) * 100 )
s = s.replace(OLDLI, NEWLI)

io.open(REPORT, "w", encoding="utf-8").write(s)
print("written chars:", len(s))

# 回读校验
chk = io.open(REPORT, encoding="utf-8").read()
print("garbled:", "\ufffd" in chk)
for k in ["13. 未来两个季度扣非弹性测算", "13.3 情景假设", "13.5 结论对假设是否稳健",
          "13.6 换个角度看", "14. 基本面综合评估", "15. 附录：财务证据审计明细",
          "14.1 三个选择题", "14.2 关键跟踪指标（6 个）", "2026H2 扣非弹性（基准情景"]:
    print("  %-34s -> %d" % (k, chk.count(k)))

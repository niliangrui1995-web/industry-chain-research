# -*- coding: utf-8 -*-
"""太辰光（300570）深度研究 · 决策看板 HTML 生成器
数据与 evidence_ledger.json 同源；图表数值与正文/数据表同源。
自检：标签配平 / \ufffd / 残留占位符 / 证据引用闭环 / 裸E编号扫描 / 契约token。
"""
import json, re, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER = json.load(open(os.path.join(BASE, "evidence_ledger.json"), encoding="utf-8"))
EV = {e["id"]: e for e in LEDGER["evidence"]}

# ---------------- 引用管理 ----------------
cite_registry = {}   # eid -> [anchor names]
def cite(eid):
    anchors = cite_registry.setdefault(eid, [])
    n = len(anchors) + 1
    anchor = f"cite-{eid}-{n}"
    anchors.append(anchor)
    return (f'<a class="evd" data-evidence-id="{eid}" id="{anchor}" '
            f'href="#evidence-{eid}" title="{EV[eid]["name"]}">{eid}</a>')

def evd_index_link():
    return '<a class="evd-locate" href="#sec-evidence">↓ 定位证据索引</a>'

# ---------------- 数据（唯一事实源） ----------------
annual_rev = {2022: 9.34, 2023: 8.85, 2024: 13.78, 2025: 15.47, "2026H1": 10.01}
annual_np = {2022: 1.80, 2023: 1.55, 2024: 2.61, 2025: 2.99, "2026H1": 1.76}
q_labels = ["24Q1","24Q2","24Q3","24Q4","25Q1","25Q2","25Q3","25Q4","26Q1","26Q2"]
q_rev = [2.23, 2.87, 4.06, 4.62, 3.71, 4.58, 3.86, 3.32, 3.41, 6.60]
q_np  = [0.32, 0.48, 0.66, 1.15, 0.79, 0.94, 0.87, 0.39, 0.66, 1.11]
mix_product = [("光器件", 9.589, "+18.09%"), ("其他", 0.404, "—"), ("光传感", 0.016, "—")]
mix_region = [("外销（境外）", 6.994, "+2.71%"), ("内销（境内）", 3.015, "+104.38%")]
scen_names = ["悲观", "中性", "乐观"]
scen_rev = {"悲观": {2026: 22.0, 2027: 26.4, 2028: 29.0},
            "中性": {2026: 24.5, 2027: 34.3, 2028: 42.9},
            "乐观": {2026: 26.5, 2027: 42.4, 2028: 57.2}}
scen_margin = {"悲观": {2026: 0.16, 2027: 0.167, 2028: 0.17},
               "中性": {2026: 0.175, 2027: 0.19, 2028: 0.20},
               "乐观": {2026: 0.185, 2027: 0.21, 2028: 0.22}}
def scen_np(s, y): return round(scen_rev[s][y] * scen_margin[s][y], 2)
peers = [  # 名称, 2026H1营收(亿), 营收YoY, 毛利率, PE(TTM), PE口径时点
    ("太辰光", 10.01, "+20.8%", "34.8%", "163.1", "2026-09-17"),
    ("天孚通信", 28.28, "+15.2%", "60.9%", "136.9", "2026-08-18"),
    ("长芯博创", 16.88, "+40.7%", "48.9%", "130.0", "2026-09-09"),
]
sens_rev = [26, 30, 34, 38, 42]
sens_mg = [0.16, 0.175, 0.19, 0.205, 0.22]
MKT = 492.32  # 总市值（亿元，2026-09-17）

# ---------------- 工具 ----------------
def tag(kind, text):
    return f'<span class="tag {kind}">{text}</span>'

def pct_up(t): return f'<b class="up">{t}</b>'
def pct_dn(t): return f'<b class="down">{t}</b>'

def h2(num, title, sid):
    return f'<h2 id="{sid}"><span class="hno">{num}</span>{title}</h2>'

def barchart_annual():
    # 年度营收柱 + 归母净利折线（2022-2025实际 + 2026H1）
    W, H, L, R, T, B = 680, 320, 56, 20, 24, 46
    pw, ph = W - L - R, H - T - B
    keys = ["2022", "2023", "2024", "2025", "2026H1"]
    rv = [annual_rev[k] for k in [2022, 2023, 2024, 2025, "2026H1"]]
    np_ = [annual_np[k] for k in [2022, 2023, 2024, 2025, "2026H1"]]
    ymax = 16.0
    def y(v): return T + ph * (1 - v / ymax)
    bw = pw / len(keys) * 0.52
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="年度营收与归母净利润">']
    for gv in [4, 8, 12, 16]:
        s.append(f'<line x1="{L}" y1="{y(gv):.1f}" x2="{W-R}" y2="{y(gv):.1f}" class="grid"/>')
        s.append(f'<text x="{L-6}" y="{y(gv)+4:.1f}" class="ax" text-anchor="end">{gv}</text>')
    pts = []
    for i, k in enumerate(keys):
        cx = L + pw * (i + 0.5)
        x0 = cx - bw / 2
        hbar = ph * rv[i] / ymax
        s.append(f'<rect x="{x0:.1f}" y="{y(rv[i]):.1f}" width="{bw:.1f}" height="{hbar:.1f}" class="bar-rev">'
                 f'<title>{k} 营收 {rv[i]:.2f} 亿元（人民币，年报/半年报口径）</title></rect>')
        s.append(f'<text x="{cx:.1f}" y="{y(rv[i])-6:.1f}" class="bv" text-anchor="middle">{rv[i]:.2f}</text>')
        s.append(f'<text x="{cx:.1f}" y="{H-24}" class="ax" text-anchor="middle">{k}</text>')
        pts.append((cx, y(np_[i])))
    for i in range(len(pts) - 1):
        s.append(f'<line x1="{pts[i][0]:.1f}" y1="{pts[i][1]:.1f}" x2="{pts[i+1][0]:.1f}" y2="{pts[i+1][1]:.1f}" class="line-np"/>')
    for i, p in enumerate(pts):
        s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4.5" class="dot-np">'
                 f'<title>{keys[i]} 归母净利润 {np_[i]:.2f} 亿元</title></circle>')
        s.append(f'<text x="{p[0]:.1f}" y="{p[1]-9:.1f}" class="bv np" text-anchor="middle">{np_[i]:.2f}</text>')
    s.append(f'<text x="{L}" y="{H-6}" class="ax">单位：亿元（人民币）；2026H1 为半年度数据</text>')
    s.append('</svg>')
    return "".join(s)

def barchart_quarter():
    W, H, L, R, T, B = 680, 320, 56, 20, 26, 46
    pw, ph = W - L - R, H - T - B
    ymax = 7.0
    def y(v): return T + ph * (1 - v / ymax)
    bw = pw / len(q_labels) * 0.55
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="单季营收与归母净利润">']
    for gv in [0, 2, 4, 6]:
        s.append(f'<line x1="{L}" y1="{y(gv):.1f}" x2="{W-R}" y2="{y(gv):.1f}" class="grid"/>')
        s.append(f'<text x="{L-6}" y="{y(gv)+4:.1f}" class="ax" text-anchor="end">{gv}</text>')
    pts = []
    for i, lab in enumerate(q_labels):
        cx = L + pw * (i + 0.5)
        x0 = cx - bw / 2
        hbar = ph * q_rev[i] / ymax
        hl = ' bar-hl' if i == 9 else ''
        s.append(f'<rect x="{x0:.1f}" y="{y(q_rev[i]):.1f}" width="{bw:.1f}" height="{hbar:.1f}" class="bar-rev{hl}">'
                 f'<title>{lab} 单季营收 {q_rev[i]:.2f} 亿元（YoY：' + (["—"]*0+[ "24Q1 同比基数未披露","24Q2","24Q3","24Q4","25Q1","25Q2 +96.8%","25Q3 +31.2%","25Q4 -66.5%","26Q1 -8.0%","26Q2 +44.2%"])[i] + '）</title></rect>')
        if i >= 6:
            s.append(f'<text x="{cx:.1f}" y="{y(q_rev[i])-6:.1f}" class="bv" text-anchor="middle">{q_rev[i]:.2f}</text>')
        s.append(f'<text x="{cx:.1f}" y="{H-24}" class="ax" text-anchor="middle" transform="rotate(-38 {cx:.1f} {H-24})">{lab}</text>')
        pts.append((cx, y(q_np[i])))
    for i in range(len(pts) - 1):
        s.append(f'<line x1="{pts[i][0]:.1f}" y1="{pts[i][1]:.1f}" x2="{pts[i+1][0]:.1f}" y2="{pts[i+1][1]:.1f}" class="line-np"/>')
    for i, p in enumerate(pts):
        s.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4.2" class="dot-np">'
                 f'<title>{q_labels[i]} 单季归母净利润 {q_np[i]:.2f} 亿元</title></circle>')
    s.append(f'<text x="{L}" y="{H-6}" class="ax">单位：亿元（人民币）；单季=累计数差分推算（24Q1/25Q1/26Q1 为披露值校验）</text>')
    s.append('</svg>')
    return "".join(s)

def stacked_mix():
    W, H, L, R = 680, 200, 12, 12
    bar_y = [34, 104]
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="2026H1收入结构">']
    total_p = sum(v for _, v, _ in mix_product)
    total_r = sum(v for _, v, _ in mix_region)
    cols_p = ["#17213D", "#8A93AD", "#E4572E"]
    cols_r = ["#0F5E5E", "#C9A66B"]
    x = L
    for (name, v, g), c in zip(mix_product, cols_p):
        w = (W - L - R) * v / total_p
        s.append(f'<rect x="{x:.1f}" y="{bar_y[0]}" width="{w:.1f}" height="34" fill="{c}">'
                 f'<title>{name} {v:.2f} 亿元，占比 {v/total_p*100:.1f}%（2026H1）</title></rect>')
        if w > 40:
            s.append(f'<text x="{x+w/2:.1f}" y="{bar_y[0]+22}" class="mixlb" fill="#fff" text-anchor="middle">{name} {v/total_p*100:.1f}%</text>')
        x += w
    x = L
    for (name, v, g), c in zip(mix_region, cols_r):
        w = (W - L - R) * v / total_r
        s.append(f'<rect x="{x:.1f}" y="{bar_y[1]}" width="{w:.1f}" height="34" fill="{c}">'
                 f'<title>{name} {v:.2f} 亿元，占比 {v/total_r*100:.1f}%（2026H1，同比 {g}）</title></rect>')
        if w > 40:
            s.append(f'<text x="{x+w/2:.1f}" y="{bar_y[1]+22}" class="mixlb" fill="#fff" text-anchor="middle">{name} {v/total_r*100:.1f}%（{g}）</text>')
        x += w
    s.append(f'<text x="{L}" y="20" class="ax">按产品（上，2026H1 合计 10.01 亿元）</text>')
    s.append(f'<text x="{L}" y="92" class="ax">按地域（下）</text>')
    s.append('</svg>')
    return "".join(s)

def chart_scenario():
    W, H, L, R, T, B = 680, 330, 56, 16, 30, 46
    pw, ph = W - L - R, H - T - B
    ymax = 14.0
    def y(v): return T + ph * (1 - v / ymax)
    years = [2026, 2027, 2028]
    cols = {"悲观": "#8A93AD", "中性": "#17213D", "乐观": "#E4572E"}
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="归母净利润情景推算">']
    for gv in [0, 3.5, 7, 10.5, 14]:
        s.append(f'<line x1="{L}" y1="{y(gv):.1f}" x2="{W-R}" y2="{y(gv):.1f}" class="grid"/>')
        s.append(f'<text x="{L-6}" y="{y(gv)+4:.1f}" class="ax" text-anchor="end">{gv}</text>')
    slot = pw / len(years)
    bw = slot * 0.24
    for si, sc in enumerate(scen_names):
        s.append(f'<g class="ser" id="sc-ser-{si}">')
        for yi, yr in enumerate(years):
            v = scen_np(sc, yr)
            cx = L + slot * (yi + 0.5)
            x0 = cx - 1.5 * bw - 6 + si * (bw + 6)
            hb = ph * v / ymax
            s.append(f'<rect x="{x0:.1f}" y="{y(v):.1f}" width="{bw:.1f}" height="{hb:.1f}" fill="{cols[sc]}" class="bar-est">'
                     f'<title>{yr}E {sc}情景：归母净利润 {v:.2f} 亿元（推算值，非公司指引）</title></rect>')
            s.append(f'<text x="{x0+bw/2:.1f}" y="{y(v)-5:.1f}" class="bv" text-anchor="middle">{v:.1f}</text>')
        s.append('</g>')
    for yi, yr in enumerate(years):
        cx = L + slot * (yi + 0.5)
        s.append(f'<text x="{cx:.1f}" y="{H-24}" class="ax" text-anchor="middle">{yr}E</text>')
        cons = {2026: 5.19, 2027: 8.83, 2028: 13.18}[yr]
        s.append(f'<line x1="{cx-slot*0.42:.1f}" y1="{y(cons):.1f}" x2="{cx+slot*0.42:.1f}" y2="{y(cons):.1f}" class="cons-line">'
                 f'<title>{yr}E 机构一致预期归母净利润 {cons:.2f} 亿元（口径见证据索引）</title></line>')
        s.append(f'<text x="{cx+slot*0.42:.1f}" y="{y(cons)-5:.1f}" class="cons-lb" text-anchor="end">一致预期 {cons:.2f}</text>')
    s.append(f'<text x="{L}" y="{H-6}" class="ax">单位：亿元；虚线描边柱=情景推算值；横虚线=机构一致预期（机构覆盖样本少，仅作参考锚）</text>')
    s.append('</svg>')
    return "".join(s)

def chart_peers():
    W, H, L, R, T, B = 680, 300, 56, 16, 26, 60
    pw, ph = W - L - R, H - T - B
    ymax = 70.0
    def y(v): return T + ph * (1 - v / ymax)
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="同业2026H1对比">']
    for gv in [0, 20, 40, 60]:
        s.append(f'<line x1="{L}" y1="{y(gv):.1f}" x2="{W-R}" y2="{y(gv):.1f}" class="grid"/>')
        s.append(f'<text x="{L-6}" y="{y(gv)+4:.1f}" class="ax" text-anchor="end">{gv}%</text>')
    groups = [("营收增速", 1), ("毛利率", 2)]
    vals_g = [[20.8, 15.2, 40.7], [34.8, 60.9, 48.9]]
    labels = [p[0] for p in peers]
    cols = ["#E4572E", "#17213D", "#0F5E5E"]
    slot = pw / 2
    bw = slot * 0.2
    for gi, (gname, _) in enumerate(groups):
        gx = L + slot * gi + slot * 0.18
        s.append(f'<text x="{L+slot*gi+slot/2:.1f}" y="{T-8}" class="ax" text-anchor="middle">{gname}（2026H1）</text>')
        for i in range(3):
            v = vals_g[gi][i]
            x0 = gx + i * (bw + 8) - 8
            hb = ph * v / ymax
            s.append(f'<rect x="{x0:.1f}" y="{y(v):.1f}" width="{bw:.1f}" height="{hb:.1f}" fill="{cols[i]}">'
                     f'<title>{labels[i]} {gname} {v:.1f}%（2026H1，财报口径）</title></rect>')
            s.append(f'<text x="{x0+bw/2:.1f}" y="{y(v)-5:.1f}" class="bv" text-anchor="middle">{v:.1f}%</text>')
    for i in range(3):
        s.append(f'<rect x="{L+18+i*24:.1f}" y="{H-42}" width="12" height="12" fill="{cols[i]}"/>')
        s.append(f'<text x="{L+34+i*24:.1f}" y="{H-32}" class="ax">{labels[i]}</text>')
    s.append(f'<text x="{L}" y="{H-8}" class="ax">三家公司 PE(TTM)：太辰光 163.1（09-17）/ 天孚 136.9（08-18）/ 长芯博创 130.0（09-09），时点不同仅作量级参考</text>')
    s.append('</svg>')
    return "".join(s)

def details_table(headers, rows, caption):
    th = "".join(f'<th>{h}</th>' for h in headers)
    trs = []
    for r in rows:
        tds = "".join(f'<td>{c}</td>' for c in r)
        trs.append(f'<tr>{tds}</tr>')
    return (f'<details class="datatable"><summary>数据表：{caption}</summary>'
            f'<table><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></details>')

# ---------------- 页面内容 ----------------
P = []
P.append('<!DOCTYPE html>')
P.append('<html data-moss-artifact-mode="interactive-web" data-moss-visual-baseline="editorial-impact" data-moss-render-seed="0bc6a2dac0da07ad">')
P.append('<head>')
P.append('<meta charset="UTF-8">')
P.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
P.append('<title>太辰光（300570）深度研究 · 决策看板</title>')
P.append('<style>')
P.append('''/* 契约 token（moss-html-artifact/v1，程序化输出，勿手改） */
:root{--moss-color-primary:#17213D;--moss-color-secondary:#F2EDE4;--moss-color-accent:#E4572E;--moss-color-surface:#FFFDF8;--moss-color-text:#10131A;--moss-font-display:Georgia, "Times New Roman", serif;--moss-font-body:"Aptos", "Segoe UI", "Microsoft YaHei", sans-serif;--moss-type-ratio:1.250;--moss-space-unit:8px;--moss-radius:4px;--moss-shadow:0 22px 70px rgba(23, 33, 61, 0.18);--moss-motion-duration:520ms;--moss-motion-easing:cubic-bezier(0.22, 1, 0.36, 1);--moss-tone:editorial;--moss-density:balanced;}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--moss-font-body);background:var(--moss-color-surface);color:var(--moss-color-text);line-height:1.75;font-size:15px}
.wrap{max-width:1080px;margin:0 auto;padding:0 28px}
h1,h2,h3,h4{font-family:var(--moss-font-display);color:var(--moss-color-primary);line-height:1.3}
h2{font-size:26px;margin:56px 0 18px;padding-bottom:10px;border-bottom:3px solid var(--moss-color-primary)}
.hno{display:inline-block;background:var(--moss-color-primary);color:var(--moss-color-secondary);font-size:15px;padding:2px 10px;margin-right:12px;border-radius:var(--moss-radius);vertical-align:middle;font-family:var(--moss-font-body)}
h3{font-size:19px;margin:30px 0 10px}
h4{font-size:16px;margin:20px 0 8px}
p{margin:10px 0}
.hero{background:var(--moss-color-primary);color:var(--moss-color-secondary);padding:56px 0 44px;margin-bottom:8px}
.hero h1{color:var(--moss-color-secondary);font-size:40px;max-width:960px}
.hero .sub{font-size:17px;opacity:.88;margin-top:12px;max-width:860px}
.hero .meta{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.hero .meta span{border:1px solid rgba(242,237,228,.45);border-radius:var(--moss-radius);padding:3px 12px;font-size:13px}
.toc{background:var(--moss-color-secondary);padding:16px 28px;font-size:14px}
.toc a{color:var(--moss-color-primary);text-decoration:none;margin-right:18px;white-space:nowrap}
.toc a:hover{color:var(--moss-color-accent)}
section{scroll-margin-top:16px}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px;background:#fff}
th,td{border:1px solid #D8D2C4;padding:7px 10px;text-align:left;vertical-align:middle}
th{background:var(--moss-color-secondary);font-weight:600}
tr:nth-child(even) td{background:#FAF7F0}
.tag{display:inline-block;font-size:11.5px;padding:1px 8px;border-radius:3px;margin:0 2px;font-family:var(--moss-font-body);font-weight:600;vertical-align:1px}
.tag.fact{background:#17213D;color:#fff}
.tag.calc{background:#F5A623;color:#231A00}
.tag.inf{background:#7A4E9B;color:#fff}
.tag.view{background:#0F5E5E;color:#fff}
.tag.risk{background:#C0392B;color:#fff}
.up{color:#C43D3D}
.down{color:#1E7A46}
.evd{display:inline-block;background:var(--moss-color-accent);color:#fff;font-size:11px;font-weight:700;padding:0 6px;border-radius:3px;text-decoration:none;margin:0 1px;vertical-align:1px;line-height:1.6}
.evd:hover{background:#17213D}
.evd-locate{font-size:12.5px;color:#8A6D3B;text-decoration:none;border-bottom:1px dotted #B49A5E;margin-left:6px}
.grid{stroke:#E4DECF;stroke-width:1}
.ax{font-size:11px;fill:#6B6455;font-family:var(--moss-font-body)}
.bv{font-size:11.5px;font-weight:700;fill:#17213D;font-family:var(--moss-font-body)}
.bv.np{fill:#C0392B}
.bar-rev{fill:#17213D}
.bar-hl{fill:#E4572E}
.line-np{stroke:#C0392B;stroke-width:2}
.dot-np{fill:#C0392B;stroke:#FFFDF8;stroke-width:1.5}
.bar-est{fill-opacity:.85;stroke-dasharray:5 3;stroke:#10131A;stroke-width:1.2}
.cons-line{stroke:#7A4E9B;stroke-width:1.6;stroke-dasharray:7 4}
.cons-lb{font-size:11px;fill:#7A4E9B;font-family:var(--moss-font-body)}
.mixlb{font-size:12px;font-family:var(--moss-font-body);font-weight:600}
.chartbox{background:#fff;border:1px solid #E4DECF;border-radius:var(--moss-radius);padding:18px 14px 8px;margin:16px 0;box-shadow:0 6px 24px rgba(23,33,61,.06)}
.chartbox .ct{font-weight:700;color:var(--moss-color-primary);margin:0 4px 4px;font-size:15px}
.chartbox .csrc{font-size:12px;color:#6B6455;margin:2px 4px 8px}
.legend{display:flex;flex-wrap:wrap;gap:8px;margin:0 4px 6px}
.legend button{border:1px solid #C9C2B0;background:#fff;border-radius:3px;padding:2px 10px;font-size:12px;cursor:pointer}
.legend button.off{opacity:.38}
details.datatable{margin:6px 4px 10px;font-size:13px}
details.datatable summary{cursor:pointer;color:#8A6D3B;font-size:12.5px}
details.datatable table{font-size:12.5px}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:16px 0}
.kpi .card{background:#fff;border:1px solid #E4DECF;border-left:4px solid var(--moss-color-primary);border-radius:var(--moss-radius);padding:12px 14px}
.kpi .card .v{font-size:24px;font-weight:800;font-family:var(--moss-font-display);color:var(--moss-color-primary)}
.kpi .card .l{font-size:12.5px;color:#6B6455;margin-top:2px}
.kpi .card.acc{border-left-color:var(--moss-color-accent)}
.callout{background:var(--moss-color-secondary);border-left:4px solid var(--moss-color-accent);padding:14px 18px;margin:16px 0;border-radius:0 var(--moss-radius) var(--moss-radius) 0}
.callout b.t{color:var(--moss-color-primary)}
.dbmod{background:#fff;border:1px solid #E4DECF;border-radius:var(--moss-radius);padding:20px 22px;margin:14px 0}
.dbmod h3{margin-top:0;border-bottom:2px solid var(--moss-color-secondary);padding-bottom:6px}
.dbmod .dh{font-size:12px;letter-spacing:2px;color:var(--moss-color-accent);font-weight:700}
.q2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}
.q2 .q{padding:12px;border-radius:var(--moss-radius);font-size:13px}
.q .qt{font-weight:700;margin-bottom:4px}
.q2x2{position:relative;padding:6px 0 10px}
.heat td.heatc{text-align:center;font-weight:700}
.heat .h1{background:#FDF1EA}.heat .h2{background:#FADEC9}.heat .h3{background:#F5BFA3}.heat .h4{background:#EFA079}.heat .h5{background:#E4572E;color:#fff}
ol,ul{margin:8px 0 8px 26px}
li{margin:4px 0}
.evd-index li{margin:10px 0;font-size:13.5px}
.evd-index .ename{font-weight:700;color:var(--moss-color-primary)}
.evd-index .emeta{color:#6B6455;font-size:12.5px}
.evd-index a.elink{color:#0F5E5E;word-break:break-all}
.evd-index .back a{font-size:12px;color:#8A6D3B;text-decoration:none;margin-right:8px}
#evd-drawer{position:fixed;right:0;top:0;height:100%;width:min(400px,92vw);background:#17213D;color:#F2EDE4;transform:translateX(105%);transition:transform .35s cubic-bezier(.22,1,.36,1);padding:22px 24px;overflow-y:auto;z-index:99;box-shadow:var(--moss-shadow)}
#evd-drawer.open{transform:translateX(0)}
#evd-drawer h4{color:#F2EDE4}
#evd-drawer .dm{font-size:12.5px;opacity:.85;margin:6px 0}
#evd-drawer a{color:#F5BFA3}
#evd-drawer .close{cursor:pointer;position:absolute;right:16px;top:14px;font-size:22px;color:#F2EDE4;background:none;border:none}
footer{margin:60px 0 30px;padding-top:18px;border-top:2px solid var(--moss-color-primary);font-size:12.5px;color:#6B6455}
@media (max-width:760px){.hero h1{font-size:30px}.q2{grid-template-columns:1fr}h2{font-size:21px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
''')
P.append('</style>')
P.append('</head>')
P.append('<body>')

# ---------- Hero ----------
P.append(f'''<header class="hero"><div class="wrap">
<h1>太辰光（300570）深度研究<br>AI 光互连高密度无源环节的"卖铲人"，估值已先于业绩站上高位</h1>
<div class="sub">主营业务与产品构成 · 光通信/光器件竞争格局 · 技术演进与政策风险 · 未来三年收入利润来源与预期差</div>
<div class="meta">
<span>研究时点：2026-09-17</span><span>视角：投资研究</span><span>深度：深度行业研究</span>
<span>展望期：2026–2028</span><span>对象：深圳太辰光通信股份有限公司（创业板）</span>
</div></div></header>''')
P.append('<nav class="toc"><a href="#sec-closure">研究收束</a><a href="#sec-dashboard">决策看板</a><a href="#sec-company">1 公司基础盘</a><a href="#sec-industry">2 行业基础盘</a><a href="#sec-trend">3 趋势与技术演进</a><a href="#sec-chain">4 产业链与竞争</a><a href="#sec-finance">5 财务与情景测算</a><a href="#sec-expectation">6 预期差与估值</a><a href="#sec-risk">7 风险与验证</a><a href="#sec-evidence">证据索引</a></nav>')

# ---------- 研究收束区 ----------
P.append(h2("◆", "研究收束区：结论如何从证据收束", "sec-closure"))
P.append(f'''<div class="dbmod"><div class="dh">RESEARCH CLOSURE</div>
<h3>范围 · 检索 · 证据 · 收束</h3>
<p><b>研究范围与问题树</b>：以太辰光（300570）为对象，覆盖三大子问题——业务与产品构成、行业竞争格局、未来三年收入利润来源与预期差；财务基准截至 2026-06-30（2026 年半年报），行情与估值时点 2026-09-17，最近完整年度 2025 年。</p>
<p><b>检索与证据地图</b>：实际检索覆盖公司财报快讯与研报点评（{cite("E-001")} {cite("E-002")} {cite("E-009")}）、公司背景与产品（{cite("E-003")} {cite("E-004")} {cite("E-005")} {cite("E-006")}）、行情与一致预期（{cite("E-007")} {cite("E-008")}）、MPO 市场规模多口径（{cite("E-010")} {cite("E-011")}）、CPO 产业化节奏（{cite("E-012")} {cite("E-013")}）、同业财报（{cite("E-014")} {cite("E-015")}）、大客户康宁景气（{cite("E-016")} {cite("E-017")} {cite("E-019")} {cite("E-021")}）、AI 资本开支周期（{cite("E-018")}）与产业链图谱线索（{cite("E-020")}）。共 21 条证据，覆盖公司/行业/竞争/宏观四层。</p>
<p><b>证据收束与分歧</b>：关键判断依赖"公司披露（事实）→ 行业机构数据（机构观点/口径）→ 推断"三级。已标注的主要口径冲突：MPO 市场规模在不同机构间差近一倍（组件口径 vs 含跳线/配套口径）；太辰光 MPO 全球份额存在 25% 与 33% 两种口径；一致预期机构覆盖样本极少，仅作参考锚。这些分歧不改变方向性结论，但影响幅度判断，报告中均以区间呈现。</p>
<p><b>结论形成</b>：事实层——2026H1 业绩、客户结构、产能与扩产、CPO 量产节点；推断层——收入驱动拆解、2026–2028 情景测算（全部标注{tag("calc", "推算")}）；假设层——汇率、康宁占比、AI 资本开支节奏。条件性结论见决策看板与第 6 节。{evd_index_link()}</p></div>''')

# ---------- 决策看板 ----------
P.append(h2("◆", "决策看板", "sec-dashboard"))
P.append('<div class="kpi">')
P.append(f'<div class="card"><div class="v">10.01 亿</div><div class="l">2026H1 营收（+20.8%）{cite("E-001")}</div></div>')
P.append(f'<div class="card"><div class="v">34.8%</div><div class="l">2026H1 毛利率（-4.1pct，汇率与结构拖累）{cite("E-001")}</div></div>')
P.append(f'<div class="card acc"><div class="v">163 倍</div><div class="l">PE(TTM)，市值 492 亿（2026-09-17）{cite("E-007")}</div></div>')
P.append(f'<div class="card acc"><div class="v">~70%</div><div class="l">第一大客户康宁收入占比（2024 年口径）{cite("E-003")}</div></div>')
P.append('</div>')

P.append(f'''<div class="dbmod"><div class="dh">MODULE 01 · 战场仪表盘</div><h3>一、战场仪表盘</h3>
<table><tr><th style="width:150px">字段</th><th>判断</th></tr>
<tr><td>行业阶段</td><td>AI 算力光互连<b>高景气中段</b>：北美四大云厂商资本开支 2026 年约 9,170 亿美元、2027 年约 1.47 万亿（增速 +60%），2028 年增速预计骤降至约 12%——2027 年是需求峰值年，2028 年进入消化期 {cite("E-018")} {tag("view","机构观点")}</td></tr>
<tr><td>核心判断</td><td>太辰光是 A 股<b>MPO 高密度光连接纯度最高</b>的标的之一，绑定康宁间接进入英伟达/微软供应链，业绩兑现在途（Q2 单季营收创上市新高）；但当前估值已透支 2–3 年高增长，安全边际依赖 2026H2–2027 业绩逐季兑现</td></tr>
<tr><td>决策窗口期</td><td><b>2026Q3–Q4</b>：公司三季报（毛利率环比方向）、康宁 Q3 财报（10 月底，指引环比放缓与否）、英伟达 CPO 交换机出货爬坡、坪山基地建设进展——四个验证点密集落地</td></tr>
<tr><td>市场规模</td><td>全球 MPO 市场约 10–12 亿美元（2025–2026，窄口径）至 2029 年 61 亿美元（LightCounting 含 CPO 配套口径，2023–2029 CAGR≈22%）；中国 MPO 市场 2026 年约 59–121 亿元（两种口径）{cite("E-010")} {cite("E-011")} {tag("view","机构口径区间")}</td></tr>
</table></div>''')

P.append(f'''<div class="dbmod"><div class="dh">MODULE 02 · 钱在哪里</div><h3>二、钱在哪里</h3>
<table><tr><th style="width:190px">价值池</th><th>驱动机制与证据</th><th style="width:90px">量级/弹性</th></tr>
<tr><td>高芯数 MPO 结构升级</td><td>800G→1.6T→3.2T 光模块配套 MPO 芯数 16→32→64 翻倍，单价非线性上升；公司 2026H1 销量仅 +1.55% 而光器件收入 +18.09%，"弱量升强价升" {cite("E-002")}</td><td>{pct_up("高")}</td></tr>
<tr><td>CPO 配套增量（保偏 MPO / Shuffle Box）</td><td>英伟达 Quantum-X 2026 年 6 月交付、Spectrum-X 2026 年 8 月全面量产；单台 CPO 交换机 MPO 组件价值量 1,500–2,000 美元，保偏 MPO 毛利率 50–60% {cite("E-010")} {cite("E-012")} {cite("E-013")}</td><td>{pct_up("高")}</td></tr>
<tr><td>国产算力内销</td><td>2026H1 内销 3.02 亿元，同比 +104.38%，毛利率 +3.12pct；国内智算中心集采放量 {cite("E-002")}</td><td>{pct_up("中高")}</td></tr>
<tr><td>海外存量（康宁链）</td><td>外销 +2.71% 增长平缓但基数大（占 70%）；康宁光通信 Q2 销售 +32%、与英伟达合作扩产 10 倍，需求外溢 {cite("E-016")}</td><td>{pct_dn("中")}</td></tr>
<tr><td>光传感/其他</td><td>占比 &lt;0.2%，电网监测细分，现金流性质，非增长引擎 {cite("E-005")}</td><td>低</td></tr>
</table></div>''')

P.append(f'''<div class="dbmod"><div class="dh">MODULE 03 · 仗怎么打</div><h3>三、仗怎么打（需求确定性 × 公司卡位）</h3>
<div class="q2x2"><div class="q2">
<div class="q" style="background:#FDF1EA"><div class="qt">① 双高：CPO 保偏 MPO / Shuffle Box</div>需求确定性高（英伟达已量产、康宁 photonics 平台 2030 年 100 亿美元机会 {cite("E-017")}）× 公司卡位强（保偏 MPO 已进英伟达 144 口 CPO 交换机 {cite("E-003")}）。<b>业绩期权，2027–2028 主弹性。</b></div>
<div class="q" style="background:#F5F3E9"><div class="qt">② 高×中：高芯数 MPO 结构升级</div>需求确定性高 × 卡位强但需份额防守（US Conec/Senko 专利与先发、国内致尚/长盈通追赶 {cite("E-011")} {cite("E-020")}）。<b>当前利润基本盘。</b></div>
<div class="q" style="background:#EEF1F4"><div class="qt">③ 中×高：国产算力内销</div>需求确定性中（国产 capex 政策驱动，但 2027 后基数抬高）× 公司卡位强（内销毛利率逆势 +3.12pct {cite("E-002")}）。<b>增速最快板块。</b></div>
<div class="q" style="background:#F0EEE9"><div class="qt">④ 中×中：电信/传感存量</div>5G/FTTH/电网监测，随行业 3–8% 低速增长 {cite("E-010")}。<b>防守型现金流。</b></div>
</div></div></div>''')

P.append(f'''<div class="dbmod"><div class="dh">MODULE 04 · 现在做什么</div><h3>四、现在做什么</h3>
<table><tr><th style="width:210px">验证动作（假设检验）</th><th style="width:210px">持续追踪（触发信号）</th><th>停止/再评估信号</th></tr>
<tr><td>跟踪 2026 三季报：毛利率能否环比回升至 35% 以上（检验"价升"逻辑对冲汇兑与结构压力）{cite("E-001")}</td>
<td>康宁季度财报（光通信增速、企业网络增速、Springboard 执行）{cite("E-016")}</td>
<td>康宁下修指引或企业网络增速显著回落；其 Q3 指引已隐含环比放缓 {cite("E-019")}</td></tr>
<tr><td>跟踪英伟达 CPO 交换机出货量与保偏 MPO/Shuffle Box 订单披露 {cite("E-012")} {cite("E-013")}</td>
<td>公司坪山基地（7.2 亿元，6.87 万㎡）建设与产能爬坡 {cite("E-006")}</td>
<td>连续两个季度毛利率低于 33%，或收入环比零增长</td></tr>
<tr><td>复盘美元兑人民币汇率对财务费用的敏感性（2026H1 财务费用 2,591 万 vs 上年 -855 万 {cite("E-001")}）</td>
<td>一致预期修订方向（当前样本极少，参考价值有限 {cite("E-008")}）</td>
<td>美国数据中心光模块进口限制从传闻变为立法（冲击 70% 外销与间接需求）{cite("E-020")}</td></tr>
</table></div>''')

# ---------- 1 公司基础盘 ----------
P.append(h2("01", "公司基础盘：业务、产品、客户与商业模式", "sec-company"))
P.append(f'''<p><b>公司画像</b>：太辰光成立于 2000 年，2016 年 12 月创业板上市，主营光器件（无源为主）及光传感产品的研发、生产与销售，是全球主要的光密集连接（MPO/MTP）产品制造商之一 {cite("E-003")}。产品矩阵覆盖：陶瓷插芯与 MT 插芯、MPO/MTP 高密度光纤连接器及组件、光纤柔性板（Shuffle Box）、PLC 分路器、波分复用器、保偏连接器等无源产品，AOC/光模块等有源产品，以及基于 FBG 的光纤传感系统（电网/桥隧监测）{cite("E-004")}。2026H1 光器件收入 9.59 亿元、占比 95.80%，光传感仅 0.02%（161 万元），业务高度聚焦 {cite("E-005")}。</p>
<p><b>商业模式</b>：以市场订单为导向的直销制造模式，赚的是"精密制造 + 规模交付 + 客户认证壁垒"的钱。核心特征有三：其一，<b>客户高度集中</b>——美国康宁为第一大客户，2024 年贡献约 70% 收入，公司通过康宁间接供应英伟达、微软等终端客户 {cite("E-003")}；2026H1 北美收入 6.20 亿元、占光器件收入约 64.61% {cite("E-002")}。其二，<b>资产轻、扩产快</b>——2025 年末资产负债率仅 17.13%、ROE（加权）18.38% {cite("E-005")}，产能扩张以租赁厂房过渡、越南基地（2025 年投产，贴近北美客户缩短交期）+ 坪山自建基地（2026 年 8 月公告，7.2 亿元/6.87 万㎡）双轨推进 {cite("E-003")} {cite("E-006")}。其三，<b>关键物料自给</b>——子公司特思路自研多款 MT 插芯已批量供货，降低对海外插芯的依赖 {cite("E-002")}；2025 年 4 月获 US Conec MDC 连接器 11 项核心专利非独占许可，打开新一代微型连接器合规空间 {cite("E-003")}。</p>''')
P.append(f'''<div class="chartbox"><div class="ct">图 1 · 收入与利润的年度轨迹（2022–2026H1）</div><div class="csrc">数据来源：公司历年年报/半年报（经财报结构化数据与业绩快讯整理，人民币口径）{cite("E-001")} {cite("E-005")}</div>
{barchart_annual()}
<details class="datatable"><summary>数据表：年度营收与归母净利润</summary><table><thead><tr><th>期间</th><th>营收（亿元）</th><th>归母净利润（亿元）</th></tr></thead><tbody>
<tr><td>2022</td><td>9.34</td><td>1.80</td></tr><tr><td>2023</td><td>8.85</td><td>1.55</td></tr><tr><td>2024</td><td>13.78</td><td>2.61</td></tr><tr><td>2025</td><td>15.47</td><td>2.99</td></tr><tr><td>2026H1</td><td>10.01</td><td>1.76</td></tr></tbody></table></details></div>''')
P.append(f'''<div class="callout"><b class="t">洞察：单季度的"深蹲起跳"比年度数据更能说明周期位置。</b>2025Q4 归母净利一度同比 -66.5%，2026Q1 营收 -8.0%；但 2026Q2 营收 6.60 亿元（同比 +44.2%、环比 +93.7%）创上市以来单季新高 {cite("E-001")}。事实 → 机制：Q1 受春节与订单节奏扰动、Q2 起北美 AI 算力集群订单与国内智算需求集中释放，叠加租赁厂房扩容缓解产能瓶颈 → 影响：本轮收入弹性由"需求 + 交付能力"共同决定，坪山与越南产能是 2027 年收入的物理前提 → 反证：若 Q3 营收环比走平，则说明 Q2 是抢单透支而非趋势拐点。{evd_index_link()}</div>''')
P.append(f'''<div class="chartbox"><div class="ct">图 2 · 单季营收与归母净利润（24Q1–26Q2）</div><div class="csrc">数据来源：公司季报（单季为累计数差分推算，与披露同比增速交叉校验一致）{cite("E-001")} {cite("E-005")}</div>
{barchart_quarter()}
<details class="datatable"><summary>数据表：单季营收与归母净利润（亿元）</summary><table><thead><tr><th>季度</th>{''.join(f'<th>{q}</th>' for q in q_labels)}</tr></thead><tbody>
<tr><td>营收</td>{''.join(f'<td>{v:.2f}</td>' for v in q_rev)}</tr>
<tr><td>归母净利润</td>{''.join(f'<td>{v:.2f}</td>' for v in q_np)}</tr></tbody></table></details></div>''')
P.append(f'''<div class="chartbox"><div class="ct">图 3 · 2026H1 收入结构：产品与地域</div><div class="csrc">数据来源：2026 年半年报主营构成 {cite("E-005")}；增速来自券商点评 {cite("E-002")}</div>
{stacked_mix()}
<details class="datatable"><summary>数据表：2026H1 收入构成</summary><table><thead><tr><th>维度</th><th>构成</th><th>收入（亿元）</th><th>占比</th><th>同比</th></tr></thead><tbody>
<tr><td>产品</td><td>光器件</td><td>9.59</td><td>95.80%</td><td>+18.09%</td></tr>
<tr><td>产品</td><td>其他</td><td>0.40</td><td>4.04%</td><td>—</td></tr>
<tr><td>产品</td><td>光传感</td><td>0.02</td><td>0.16%</td><td>—</td></tr>
<tr><td>地域</td><td>外销</td><td>6.99</td><td>69.88%</td><td>+2.71%</td></tr>
<tr><td>地域</td><td>内销</td><td>3.02</td><td>30.12%</td><td>+104.38%</td></tr></tbody></table></details></div>''')

# ---------- 2 行业基础盘 ----------
P.append(h2("02", "行业基础盘：MPO 赛道的规模、需求传导与景气度", "sec-industry"))
P.append(f'''<p><b>行业定义与边界</b>：光通信器件位于光模块与网络设备之间，MPO（多芯光纤连接器）以 MT 精密插芯实现 12/16/24/48/144 芯并行光传输，是 AI 数据中心高密度布线的基础无源器件 {cite("E-010")}。需求分两大场景：其一，传统存量——800G/1.6T 可插拔光模块的标准接口配套（800G 标配 16 芯、1.6T 升 32 芯、3.2T 用 64 芯）；其二，CPO 增量——CPO 交换机内部光引擎与面板互联、硅光方案的保偏光纤配套 {cite("E-010")} {cite("E-013")}。</p>
<p><b>市场规模：口径差异必须正视</b> {tag("view", "机构口径区间")}。LightCounting 口径下全球 MPO 市场 2023 年 18 亿美元 → 2029 年 61 亿美元（CAGR 约 22%，含 CPO 增量）；同期商业市场报告的窄口径（连接器本体）仅 2025 年 10.4 亿美元、2035 年 58.4 亿美元（CAGR 18.84%）；360iResearch 更保守（CAGR 7.12%）。中国市场 2026 年约 58.7–121 亿元（两种口径），2026–2030 CAGR 36.5%，MPO 在整体光纤连接器中的渗透率将从 20%+ 提升至 2030 年约 64% {cite("E-010")} {cite("E-011")}。<b>判断</b>：绝对规模各口径差近一倍，但方向一致——MPO 增速是传统光纤连接器（3–8%）的 3–6 倍，属于"结构性吃份额"的赛道；投资上应更关注太辰光在客户处的份额与单机价值量，而非市场总额的精确值。</p>
<p><b>需求传导链</b>：AI 资本开支 → 光模块出货 → 光模块端口配套 MPO → 高密度无源器件量价。当前链上各环节的证据：北美四大云厂商资本开支 2026 年约 9,170 亿美元、2027 年约 1.47 万亿美元（+60%），2028 年增速降至约 12% {cite("E-018")}；高盛 2026 年 9 月上修全球光模块出货预期，2026–2028 年分别 +33%/+81%/+115%（二手转述，待核验）{cite("E-020")} {tag("view", "机构观点")}；康宁光通信 2026Q2 销售 +32%、企业网络 +65%、AI 数据中心相关销售接近翻倍，并计划将光互连产能扩张绑定英伟达（扩 10 倍）与亚马逊（多年期数十亿美元协议）{cite("E-016")} {cite("E-017")}。</p>
<div class="callout"><b class="t">洞察：康宁既是太辰光的"利润天花板"，也是其需求景气度的最直接印证。</b>事实：太辰光约 70% 收入来自康宁（2024 年口径）{cite("E-003")}，康宁 2025 年光通信收入 62.74 亿美元、为其第一大业务 {cite("E-021")}；2026Q2 康宁光通信 +32%、企业网络 +65% {cite("E-016")}。机制：康宁承接云厂商数据中心布线总包，太辰光的 MPO/密集连接组件是其方案中的核心外购件，康宁订单 ≈ 太辰光收入的先行指标。影响：跟踪康宁季度披露比跟踪任何行业报告都更贴近太辰光的收入真实节奏。反证/风险：康宁 Q3 指引隐含环比增速从 9% 降至 3–6%，财报超预期股价仍暴跌 12%——若康宁增速中枢下移，太辰光 2027 年收入预期将直接承压 {cite("E-019")}。{evd_index_link()}</div>''')

# ---------- 3 趋势与技术演进 ----------
P.append(h2("03", "趋势与技术演进：速率迭代、CPO 共生与政策变量", "sec-trend"))
P.append(f'''<h3>3.1 技术演进：三条路线都指向更高密度的光互连</h3>
<p><b>速率迭代</b>：400G→800G→1.6T→3.2T 光模块演进使单模块配套 MPO 芯数从 8→16→32→64 翻倍，MPO 单价随芯数非线性上升（16 芯约为 12 芯 2 倍、32 芯为 16 芯 2.5–3 倍）{cite("E-010")}。太辰光 2026H1 销量 +1.55% vs 光器件收入 +18.09% 的"弱量升强价升"正是结构升级的直接财务证据 {cite("E-002")}。</p>
<p><b>CPO：共生而非替代</b> {tag("fact", "事实")}：英伟达 Quantum-X Photonics（115.2T，144 个物理 MPO 端口、72 个 1.6T 光引擎）2026 年 6 月首次交付；Spectrum-X Photonics（102.4T/409.6T，第二代 3.2T 光引擎）2026 年 8 月全面量产，首批客户 CoreWeave、Lambda、甲骨文、Meta {cite("E-012")} {cite("E-013")}。<b>机制</b>：CPO 将光引擎与交换芯片共封装，外部可插拔连接被压缩，但机内光引擎与面板之间反而需要更多高密度/保偏 MPO 与光纤柔性板（Shuffle Box）做"可维护的中转关节"——高盛对 Quantum-X（售价约 13 万美元）的 BoM 拆解显示：光引擎占 43%（3.24 万美元），MPO 连接器/线缆 5,760 美元（144 个 × 40 美元）、Shuffle Box 2,500 美元、单模光纤 1.23 万美元 {cite("E-012")} {tag("view", "机构拆解")}。<b>对太辰光的含义</b>：CPO 是其第二增长曲线的载体——保偏 MPO 已应用于英伟达 144 口 CPO 交换机、光纤路由柔性板与 Shuffle Box 已完成头部客户验证 {cite("E-003")} {cite("E-006")}；保偏类产品单价与毛利率约为普通 MPO 的 2 倍（50–60%）{cite("E-010")}。反证：康宁自建 photonics 平台瞄准设备内无源器件（2030 年 100 亿美元机会），大客户向上游延伸构成中期竞争变量 {cite("E-017")}。</p>
<h3>3.2 需求与资本开支周期：2027 年是峰值共识年</h3>
<p>摩根士丹利预计四大云厂商数据中心资本开支 2025 年约 4,660 亿美元 → 2027 年约 1.47 万亿（+60%）→ 2028 年增速骤降至约 12%；算力从 2025 年 36GW 增至 2028 年约 144GW {cite("E-018")} {tag("view", "机构观点")}。对光器件链的含义：2026–2027 订单能见度高、2028 年起增速换挡；太辰光坪山基地（2028 年前后投产贡献）与越南产能的回报测算应以此为约束条件。</p>
<h3>3.3 政策与上下游</h3>
<p><b>贸易政策</b>：美国拟禁止进口中国新型数据中心光模块的政策传闻已在压制中游光模块厂商估值 {cite("E-020")} {tag("risk", "传闻级风险")}。对太辰光的影响路径不同于中际旭创/新易盛等模块整机厂：其交付物为无源器件且主要通过康宁（美国公司）集成后进入终端——但康宁同时在美扩产光连接产能 10 倍 {cite("E-016")}，长期存在"贴近客户生产"的份额再平衡可能；越南基地（2025 年投产）是现成的关税对冲工具 {cite("E-003")}。<b>上游</b>：特种光纤、精密注塑模具交付周期长，行业 2026–2028 供需紧平衡支撑价格 {cite("E-010")}。<b>汇率</b>：美元兑人民币贬值使 2026H1 财务费用 2,591 万元（上年同期 -855 万元），拖累净利率约 3.4pct，是上半年"增收不增利"的第一大解释变量 {cite("E-001")} {cite("E-002")}。</p>''')

# ---------- 4 产业链与竞争 ----------
P.append(h2("04", "产业链定位与竞争格局：核心同业深对比", "sec-chain"))
P.append(f'''<p><b>产业链位置</b>：上游（光纤/陶瓷与 MT 插芯/精密设备）→ 中游光器件（太辰光所在：MPO/密集连接/保偏/柔性板）→ 光模块与设备商（康宁/中际旭创/新易盛）→ 云厂商与 AI 集群（英伟达/微软/Meta 等）。价值分布上，AI 光互连 BOM 中"光相关"占绝对大头（CPO 交换机中约 85% {cite("E-012")} {tag("view", "机构拆解")}），无源连接器件是其中"小而刚"的环节：单机价值量不如光引擎，但认证壁垒与工艺积累使格局更稳定。</p>
<p><b>竞争格局</b>：全球 MPO 市场由 US Conec（约 18%）与 Senko（约 15%）领衔（按出货与合作口径）{cite("E-011")}；太辰光为全球第二大 MPO 供应商，市占率口径一（研报）约 33%、口径二（公司资料聚合）约 25%——两口径统计对象与年份不同，取 25–33% 区间，均指向全球前二 {cite("E-003")} {cite("E-010")}。核心竞争要素：MT 插芯微米级对准工艺（模具开发 18–24 个月）、北美云厂商认证周期（12–18 个月）、批量交付的良率与规模 {cite("E-010")}。国内追兵：致尚科技（美国头部云厂商 4.6 亿元 MPO 长协）、长盈通（Shuffle Box 全系列量产）、杰普特（MPO/MMC 通过 Senko/US Conec 认证）、中天科技（国内大厂 15.18 亿元集采）{cite("E-020")} {cite("E-010")}。</p>''')
P.append(f'''<div class="chartbox"><div class="ct">图 4 · 核心同业 2026H1 对比：增速、毛利率与估值</div><div class="csrc">数据来源：三家公司 2026 年半年报（营收增速与毛利率）；PE 为各自口径时点的 TTM 值 {cite("E-001")} {cite("E-014")} {cite("E-015")} {cite("E-007")}</div>
{chart_peers()}
<details class="datatable"><summary>数据表：同业对比（2026H1）</summary><table><thead><tr><th>公司</th><th>营收（亿元）</th><th>营收 YoY</th><th>归母净利（亿元）</th><th>净利 YoY</th><th>毛利率</th><th>PE(TTM)/时点</th></tr></thead><tbody>
<tr><td>太辰光</td><td>10.01</td><td>+20.8%</td><td>1.76</td><td>+1.7%</td><td>34.8%</td><td>163.1（09-17）</td></tr>
<tr><td>天孚通信</td><td>28.28</td><td>+15.2%</td><td>12.04</td><td>+33.9%</td><td>60.9%</td><td>136.9（08-18）</td></tr>
<tr><td>长芯博创</td><td>16.88</td><td>+40.7%</td><td>3.21</td><td>+91.1%</td><td>48.9%</td><td>130.0（09-09）</td></tr></tbody></table></details></div>''')
P.append(f'''<table><tr><th style="width:110px">维度</th><th>太辰光</th><th>天孚通信</th><th>长芯博创（原博创科技）</th></tr>
<tr><td>业务定位</td><td>MPO 高密集无源连接纯度最高；保偏 MPO/Shuffle Box 进军 CPO 配套</td><td>一站式光互连平台：无源器件 + 有源封装代工；FAU 全球份额 50%+，英伟达 CPO 供应链唯一被点名 A 股厂商 {cite("E-015")} {cite("E-020")}</td><td>数据中心有源互联（光模块/AOC/铜缆）+ PLC/AWG 无源；长飞控股，硅光/FAU/MPO 第二梯队 {cite("E-014")}</td></tr>
<tr><td>客户结构</td><td>康宁约 70%（2024），间接供英伟达/微软；北美占光器件收入 64.61%</td><td>海外占比 58.5%；深度绑定英伟达 CPO 生态</td><td>境外 69.3%；数据中心占 87.7%</td></tr>
<tr><td>2026H1 盈利质量</td><td>毛利率 34.8%（-4.1pct，汇率+结构）；经营现金流 -0.73 亿</td><td>毛利率 60.9%（+10.1pct）；经营现金流 10.01 亿</td><td>毛利率 48.9%（+8.7pct）；经营现金流 3.11 亿</td></tr>
<tr><td>核心看点</td><td>MPO 价升 + CPO 配套期权 + 内销翻倍</td><td>CPO 光引擎配套确定性最高</td><td>硅光模块 + 铜光双线弹性</td></tr>
<tr><td>主要风险</td><td>单一大客户依赖、汇率、估值最高</td><td>对英伟达生态依赖、Q2 营收已现 -0.9%</td><td>有源业务竞争激烈、商誉与备货压力</td></tr></table>''')
P.append(f'''<div class="callout"><b class="t">洞察：同业对比揭示的定位差异——太辰光赢在"纯度"，输在"盈利质量"。</b>事实：2026H1 天孚毛利率 60.9%、长芯博创 48.9%，太辰光仅 34.8% 且同比 -4.1pct {cite("E-001")} {cite("E-014")} {cite("E-015")}。机制：天孚做的是 CPO 光引擎配套（精密光学组件价值量高）、长芯博创做的是有源模块（含芯片溢价），而 MPO 连接器本体是标准化程度更高的精密制造件，议价能力天然弱一档；叠加太辰光康宁渠道占比高、汇率敞口大。影响：太辰光的盈利弹性更多来自"量与结构"（高芯数占比、保偏产品放量、内销占比提升）而非提价；其估值（163 倍 PE-TTM）却是三者最高，隐含了对其纯度溢价的充分定价。反证：若 CPO 配套（保偏 MPO、Shuffle Box）在 2027 年放量至收入 10%+，毛利率中枢有望上移至 38–40%，届时盈利质量差距收窄。{evd_index_link()}</div>''')

# ---------- 5 财务与情景测算 ----------
P.append(h2("05", "财务拆解与 2026–2028 情景测算", "sec-finance"))
P.append(f'''<h3>5.1 盈利能力拆解</h3>
<p><b>毛利率</b>：2025 年 38.00% → 2026H1 34.81%（-4.13pct）；其中光器件 35.23%（-3.54pct）；分区域看，内销毛利率 +3.12pct、外销 -5.85pct——海外收入占比变化、产品结构与美元汇率共同压制 {cite("E-001")} {cite("E-002")}。<b>净利率</b>：2025 年 19.89% → 2026H1 18.17%（-3.1pct），其中汇兑一项拖累约 3.4pct（财务费用 2,591 万 vs 上年 -855 万）{cite("E-001")}。若剔除汇兑，上半年盈利能力基本稳定。<b>现金流</b>：2026H1 经营现金流 -7,263 万元（上年同期 +1.28 亿），源于订单备货与应收扩张，与同业（长芯博创存货较年初 +98.66% {cite("E-014")}）一致，属景气扩张期特征，但需跟踪回款。<b>资产负债表</b>：2025 年末资产负债率 17.13%、有息负债率 2.94%，净现金结构为 7.2 亿元坪山投资提供内生资金 {cite("E-005")} {cite("E-006")}。</p>
<h3>5.2 收入驱动因子分解（2026H1 光器件 +18.09%）</h3>
<table><tr><th>驱动因子</th><th>方向</th><th>机制与证据</th></tr>
<tr><td>销量</td><td>{pct_up("+1.55%")}</td><td>产能瓶颈制约交付（销量 1.26 亿件 vs 产量 1.47 亿件），坪山/越南扩产是量的前提 {cite("E-002")}</td></tr>
<tr><td>单价/结构</td><td>{pct_up("+16%（推算）")}</td><td>收入增速 - 销量增速的残差即 ASP 贡献；高芯数与保偏产品占比提升 {cite("E-002")} {tag("calc", "推算")}</td></tr>
<tr><td>区域结构</td><td>{pct_up("内销 +104%")}</td><td>国内智算中心建设拉动；内销毛利率逆势 +3.12pct {cite("E-002")}</td></tr>
<tr><td>汇率</td><td>{pct_dn("拖累 ~3.4pct 净利率")}</td><td>美元贬值产生汇兑损失，收入端亦有折算影响 {cite("E-001")}</td></tr></table>
<h3>5.3 2026–2028 情景测算 {tag("calc", "全部为推算，非公司指引")}</h3>
<p>情景框架：以 2026H2 收入节奏（悲观 12.0 亿 / 中性 14.5 亿 / 乐观 16.5 亿，对应 Q3、Q4 环比爬坡幅度差异）推 2026 全年，再按 2027/2028 收入增速与净利率假设推利润。所有参数显式列示、可复算：<b>收入增速</b>——悲观 2027 +20%/2028 +10%，中性 +40%/+25%，乐观 +60%/+35%；<b>净利率</b>——悲观 16–17%，中性 17.5–20%，乐观 18.5–22%（锚定 2025 年 19.89%、2026H1 18.17%、汇兑中性假设与保偏产品占比提升）。</p>''')
sc_rows = []
for sc in scen_names:
    r = [f'<b>{sc}</b>']
    for y in [2026, 2027, 2028]:
        r.append(f'{scen_rev[sc][y]:.1f} / {scen_np(sc, y):.2f}')
    r.append(f'{MKT/scen_np(sc,2027):.0f}')
    sc_rows.append(r)
P.append('<table><tr><th>情景</th><th>2026E 营收/归母（亿元）</th><th>2027E 营收/归母（亿元）</th><th>2028E 营收/归母（亿元）</th><th>2027E 对应 PE（按 492 亿市值）</th></tr>'
         + ''.join(f'<tr>{"".join(f"<td>{c}</td>" for c in r)}</tr>' for r in sc_rows)
         + f'<tr><td><b>一致预期（参考锚）</b></td><td>26.7 / 5.19</td><td>41.2 / 8.83</td><td>57.9 / 13.18</td><td>56</td></tr></table>')
P.append(f'''<p style="font-size:13px;color:#6B6455">注：一致预期来自行情终端汇总（机构覆盖样本极少），其 2026E 营收 26.7 亿元隐含 2026H2 收入 16.7 亿元、较 2025H2 同比 +132%，高于本报告乐观情景（16.5 亿）的 H2 假设 {cite("E-008")}。</p>''')
P.append(f'''<div class="chartbox"><div class="ct">图 5 · 归母净利润情景推算 vs 一致预期（2026E–2028E）</div><div class="csrc">推算基于本节显式参数；一致预期为行情终端口径 {cite("E-008")}</div>
<div class="legend"><button data-ser="sc-ser-0" class="on">悲观</button><button data-ser="sc-ser-1" class="on">中性</button><button data-ser="sc-ser-2" class="on">乐观</button></div>
{chart_scenario()}
<details class="datatable"><summary>数据表：情景推算与一致预期（归母净利润，亿元）</summary><table><thead><tr><th>情景</th><th>2026E</th><th>2027E</th><th>2028E</th></tr></thead><tbody>
<tr><td>悲观</td><td>3.52</td><td>4.41</td><td>4.93</td></tr>
<tr><td>中性</td><td>4.29</td><td>6.52</td><td>8.58</td></tr>
<tr><td>乐观</td><td>4.90</td><td>8.90</td><td>12.58</td></tr>
<tr><td>一致预期（参考）</td><td>5.19</td><td>8.83</td><td>13.18</td></tr></tbody></table></details></div>''')
# 敏感性网格
rows_html = []
for r in sens_rev:
    cells = []
    for m in sens_mg:
        npv = r * m
        pe = MKT / npv
        cls = "heatc " + ("h5" if pe < 60 else "h4" if pe < 76 else "h3" if pe < 95 else "h2" if pe < 115 else "h1")
        cells.append(f'<td class="{cls}">{npv:.1f}<br><span style="font-size:11px;font-weight:400">PE {pe:.0f}x</span></td>')
    rows_html.append(f'<tr><td><b>{r}</b></td>{"".join(cells)}</tr>')
P.append(f'''<h3>5.4 敏感性网格：2027E 归母净利润 = 收入 × 净利率（含对应 PE）{tag("calc", "推算")}</h3>
<table class="heat"><thead><tr><th>2027E 收入（亿元）\\ 净利率</th><th>16.0%</th><th>17.5%</th><th>19.0%</th><th>20.5%</th><th>22.0%</th></tr></thead><tbody>{"".join(rows_html)}</tbody></table>
<p style="font-size:13px;color:#6B6455">读法：一致预期 2027E 归母 8.83 亿元（对应 PE 56x）需要"收入 ≥ 42 亿 且 净利率 ≥ 21%"或"收入 ≈ 45–46 亿 且 净利率 ≈ 19–20%"才能达到——即同时接近本报告乐观情景的收入与盈利假设上沿；中性情景（34 亿 × 19% = 6.5 亿）对应 PE 约 76 倍。</p>''')

# ---------- 6 预期差与估值 ----------
P.append(h2("06", "预期差与估值：价格里已经装进了什么", "sec-expectation"))
P.append(f'''<p><b>估值现状</b> {tag("fact", "事实")}（2026-09-17）：收盘价 216.76 元、总市值 492.32 亿元；PE(TTM) 163.1 倍、前瞻 PE 139.6 倍、PB 29.51 倍；52 周区间 85.02–284.85 元、年初至今 +89.3%、但近 60 日 -15.8% {cite("E-007")}。近两月 9 篇券商中报点评全部给予买入或增持评级 {cite("E-009")}。</p>
<p><b>共识反推</b> {tag("inf", "推断")}：一致预期 2027E 归母 8.83 亿元 {cite("E-008")} 隐含两个强假设——① 收入端：2026H2 需完成 16.7 亿元（同比 +132%）、2027 年再 +54%；② 盈利端：2027 年净利率需达 21.4%，高于 2025 年的 19.89% 与 2026H1 的 18.17%，隐含毛利率显著回升、汇兑转正与保偏/CPO 产品放量三者同时兑现。以当前市值计，股价 216.76 元已高于一致目标价均值 198.33 元（样本极少，参考意义有限）{cite("E-007")} {cite("E-008")}。</p>
<table><tr><th>预期差方向</th><th>触发条件</th><th>对应估值含义（按 492 亿市值）</th></tr>
<tr><td>{pct_dn("向下风险")}</td><td>康宁 Q3 指引下修 / Q3 毛利率 &lt; 33% / CPO 配套订单低于预期 / 2028 资本开支增速骤降被市场提前定价</td><td>中性情景 2027E 6.5 亿 → PE 76x；悲观 4.4 亿 → PE 112x，估值消化空间大</td></tr>
<tr><td>{pct_up("向上期权")}</td><td>保偏 MPO/Shuffle Box 在英伟达链放量、内销持续翻倍、坪山产能提前释放、汇率转正</td><td>乐观情景 2027E 8.9 亿 → PE 55x，与当前前瞻估值相当</td></tr>
<tr><td>基准情形</td><td>Q3 毛利率环比回升至 35%+、康宁企业网络维持 50%+ 增速、坪山按期推进</td><td>介于中性与乐观之间，估值随业绩逐季消化</td></tr></table>
<div class="callout"><b class="t">核心判断（条件性）</b>：太辰光的基本面方向（AI 光互连高密度化 + CPO 共生逻辑）成立且证据充分，但<b>当前价格已计入接近乐观情景的 2027 年业绩</b>。买点的本质是把"康宁订单节奏、毛利率回升、CPO 配套放量"三个验证点作为加仓/减仓的触发器，而非预先支付全部期权费。成立条件：估值溢价来自纯度与卡位；停止条件：见第 7 节。{evd_index_link()}</div>''')

# ---------- 7 风险与验证 ----------
P.append(h2("07", "风险提示与验证行动计划", "sec-risk"))
P.append(f'''<table><tr><th style="width:180px">风险</th><th>性质与传导</th><th>跟踪指标 / 缓释因素</th></tr>
<tr><td>大客户集中（康宁 ~70%）</td><td>康宁资本开支或份额再平衡（其自建 photonics 平台、美国扩产 10 倍）直接冲击收入基本盘 {cite("E-003")} {cite("E-016")} {cite("E-017")}</td><td>康宁季报企业网络增速、太辰光前五客户占比披露；内销与 CPO 直供客户多元化</td></tr>
<tr><td>汇率波动</td><td>外销约 70%，美元贬值造成汇兑损失并压制毛利率（2026H1 已拖累净利率 ~3.4pct）{cite("E-001")} {cite("E-002")}</td><td>美元兑人民币走势、财务费用科目；远期锁汇政策</td></tr>
<tr><td>贸易政策</td><td>美国对中国数据中心光模块的限制若从传闻变为立法，影响直接出口与间接需求 {cite("E-020")} {tag("risk", "传闻级")}</td><td>越南基地产能占比提升 {cite("E-003")}</td></tr>
<tr><td>AI 资本开支 2027 见顶</td><td>2028 年增速或降至 ~12%，硬件链估值中枢下移 {cite("E-018")}</td><td>云厂商季报 capex 指引；康宁 Q3 已隐含环比放缓 {cite("E-019")}</td></tr>
<tr><td>竞争加剧</td><td>US Conec/Senko 专利与先发；国内致尚/长盈通/杰普特在 CPO 配套卡位；康宁向上游延伸 {cite("E-010")} {cite("E-011")} {cite("E-017")} {cite("E-020")}</td><td>份额口径（25–33% 区间）变化、长协订单归属</td></tr>
<tr><td>估值与拥挤度</td><td>PE(TTM) 163 倍、PB 29.5 倍，板块对"不超预期的利好"已开始用脚投票（康宁案例）{cite("E-007")} {cite("E-019")}</td><td>业绩兑现节奏与一致预期修订方向</td></tr></table>
<h3>验证行动计划（时间排序）</h3>
<ol>
<li><b>2026 年 10 月底</b>：康宁 Q3 财报——光通信与企业网络增速是否维持 30%+/50%+，Springboard 执行进展 {cite("E-016")}</li>
<li><b>2026 年 10 月下旬</b>：公司三季报——营收环比、毛利率能否回到 35%+、经营现金流转正 {cite("E-001")}</li>
<li><b>持续</b>：英伟达 CPO 交换机（Quantum-X/Spectrum-X）出货与保偏 MPO、Shuffle Box 订单披露 {cite("E-012")} {cite("E-013")}</li>
<li><b>持续</b>：坪山基地建设进度（7.2 亿元投资节奏）与越南产能利用率 {cite("E-006")}</li>
<li><b>每季</b>：美元汇率对财务费用的敏感性复盘 {cite("E-001")}</li>
</ol>''')

# ---------- 证据索引 ----------
P.append(h2("◆", "证据链、数据来源与方法论", "sec-evidence"))
P.append('''<p>全部 21 条证据按引用顺序编号；正文中的橙色编号徽章可点击跳转至本节对应条目，并可在弹层中查看摘要。除标注"无可公开链接"的行情终端数据外，均提供具名原始链接（新标签页打开）。</p>''')
P.append('<ol class="evd-index">')
for e in LEDGER["evidence"]:
    eid = e["id"]
    backs = " ".join(f'<a href="#{a}">↩ 引用处{n}</a>' for n, a in enumerate(cite_registry.get(eid, []), 1))
    url_part = (f'<br><a class="elink" href="{e["url"]}" target="_blank" rel="noopener">{e["url"]}</a>' if e.get("url") else '<br><span class="emeta">无可公开链接（行情终端 MCP 数据）</span>')
    P.append(f'<li id="evidence-{eid}"><span class="ename">{eid} · {e["name"]}</span><br>'
             f'<span class="emeta">来源：{e["source"]} ｜ 时点：{e["date"]} ｜ 证据等级：{e["tier"]}</span>{url_part}'
             f'<div class="back">{backs}</div></li>')
P.append('</ol>')
P.append(f'''<h3>方法论与数据局限</h3>
<ul>
<li>财务数据以公司 2026 年半年报、2025 年年报及历期披露为准；单季数据为累计数差分推算并与披露同比增速交叉校验。</li>
<li>市场规模、份额、CPO BoM 等来自 LightCounting、高盛、摩根士丹利等机构的公开转述或商业报告，均标注为机构口径/观点，存在转述损耗；不同机构口径差异以区间呈现，未做平均处理。</li>
<li>一致预期样本极少（机构覆盖数为 0 的终端汇总），目标价统计基础薄弱，仅作参考锚而非定价依据。</li>
<li>2026–2028 情景测算全部为前瞻推算（正文以琥珀色标签标注），不构成业绩预测或投资建议；参数已显式列示，读者可自行复算。</li>
<li>美国光模块进口限制为传闻级信息（未落地立法），按风险情景处理，不作为基准假设。</li>
</ul>''')

P.append('''<footer>免责声明：本报告由 AI 研究助手基于公开信息整理，仅供研究参考，不构成任何投资建议或收益承诺。所涉前瞻性内容均为情景推算，实际结果可能存在重大差异。市场有风险，投资需谨慎。<br>报告生成时间：2026-09-17 · 研究时点数据以各证据条目标注时点为准</footer>''')

# 证据弹层数据
evdata = [{"id": e["id"], "name": e["name"], "source": e["source"], "date": e["date"], "tier": e["tier"], "url": e.get("url")} for e in LEDGER["evidence"]]
P.append('<div id="evd-drawer"><button class="close" aria-label="关闭">&times;</button><h4>证据摘要</h4><div id="evd-body"></div></div>')
P.append('<script>')
P.append('''
var EV = ''' + json.dumps(evdata, ensure_ascii=False) + ''';
var drawer = document.getElementById('evd-drawer');
document.addEventListener('click', function(ev){
  var a = ev.target.closest('a.evd');
  if(a){
    var d = EV.find(function(x){return x.id===a.getAttribute('data-evidence-id');});
    var b = document.getElementById('evd-body');
    if(d){
      var link = d.url ? ('<a href="'+d.url+'" target="_blank" rel="noopener">打开原始来源 ↗</a>') : '无可公开链接（行情终端数据）';
      b.innerHTML = '<p><b>'+d.id+'</b> · '+d.name+'</p><p class="dm">来源：'+d.source+'<br>时点：'+d.date+'<br>证据等级：'+d.tier+'</p><p class="dm">'+link+'</p><p class="dm"><a href="#evidence-'+d.id+'" onclick="closeDrawer()">跳转完整证据索引 ↓</a></p>';
    }
    drawer.classList.add('open');
    ev.preventDefault();
  }
});
function closeDrawer(){drawer.classList.remove('open');}
drawer.querySelector('.close').addEventListener('click', closeDrawer);
document.addEventListener('keydown', function(e){if(e.key==='Escape'){closeDrawer();}});
document.querySelectorAll('.legend button').forEach(function(btn){
  btn.addEventListener('click', function(){
    var g = document.getElementById(btn.getAttribute('data-ser'));
    if(g){g.style.display = (g.style.display==='none')?'':'none'; btn.classList.toggle('off');}
  });
});
''')
P.append('</script>')
P.append('</body></html>')

html = "".join(P)
out = os.path.join(BASE, "决策看板_太辰光300570.html")
open(out, "w", encoding="utf-8").write(html)

# ---------------- 自检 ----------------
checks = []
def chk(name, cond, detail=""):
    checks.append(("PASS" if cond else "FAIL", name, detail))

u = html.count("\\ufffd")
chk("U+FFFD 替换符计数为 0", u == 0, f"count={u}")
for t in ["table", "tr", "td", "div", "section", "details", "svg", "a", "ul", "ol"]:
    o = len(re.findall(r"<" + t + r"[\s>]", html))
    c = html.count("</" + t + ">")
    chk(f"<{t}> 开闭配平", o == c, f"open={o} close={c}")
o_li = len(re.findall(r"<li[\s>]", html)); c_li = html.count("</li>")
chk("<li> 开闭配平", o_li == c_li, f"open={o_li} close={c_li}")
for bad in ["%s", "%.2f", ">None<", ">nan<", "None，", "None。"]:
    chk(f"无残留占位符 {bad!r}", bad not in html)
# 证据闭环
cited = set(cite_registry.keys())
allids = set(EV.keys())
chk("全部 21 条证据均被正文引用", cited == allids, f"未引用: {sorted(allids-cited)}")
# 锚点唯一
all_anchors = []
for k, v in cite_registry.items():
    all_anchors.extend([f"cite-{k}-{n}" for n in range(1, len(v) + 1)])
chk("引用锚点唯一", len(all_anchors) == len(set(all_anchors)), f"total={len(all_anchors)}")
# 返回链接与锚点一一对应
back_links = re.findall(r'href="#(cite-[^"]+)"', html)
chk("索引返回链接与引用锚点一一对应", sorted(back_links) == sorted(all_anchors),
    f"back={len(back_links)} anchors={len(all_anchors)}")
# 裸 E-xxx 扫描（白名单：evd 徽章、id=evidence-、data-evidence-id、href=#evidence-）
tmp = re.sub(r'<a class="evd"[^>]*>E-\d+</a>', '', html)
tmp = re.sub(r'id="evidence-E-\d+"', '', tmp)
tmp = re.sub(r'href="#evidence-E-\d+"', '', tmp)
tmp = re.sub(r'evidence-E-\d+', '', tmp)
tmp = re.sub(r'<span class="ename">E-\d+[^<]*</span>', '', tmp)      # 索引区条目名（白名单）
tmp = re.sub(r'"id"\s*:\s*"E-\d+"', '', tmp)                        # 内嵌证据 JSON（弹层，白名单）
tmp = re.sub(r'<h4>.*?</h4>|<script>.*?</script>', '', tmp, flags=re.S)  # 弹层/脚本区不参与裸编号扫描
bare = re.findall(r'(?<![\w-])E-\d{3}(?![\w-])', tmp)
chk("正文无裸 E 编号（白名单外）", len(bare) == 0, f"bare={bare[:5]}")
# 契约三标记 + token
m = re.search(r'<html([^>]*)>', html)
attrs = m.group(1)
chk("html 三契约标记", 'data-moss-artifact-mode="interactive-web"' in attrs and 'data-moss-visual-baseline="editorial-impact"' in attrs and 'data-moss-render-seed="0bc6a2dac0da07ad"' in attrs)
first_root = re.search(r':root\{([^}]*)\}', html).group(1)
contract = json.load(open(os.path.join(BASE, "artifact-contract.json"), encoding="utf-8"))
ok_tokens = True
for k, v in contract["tokens"].items():
    pat = re.escape(k) + r"\s*:\s*" + re.escape(v) + r"\s*;"
    if not re.search(pat, first_root):
        ok_tokens = False
chk("契约 token 逐字写入首个 :root", ok_tokens)
chk("viewport meta 存在", 'name="viewport"' in html)
chk("charset UTF-8", '<meta charset="UTF-8">' in html)
# 图表与数据表数量
n_chart = html.count('class="chartbox"')
n_dt = html.count('<details class="datatable">')
chk("每个图表配数据表", n_chart == n_dt, f"charts={n_chart} datatables={n_dt}")
# 敏感性表格为附加表（非 chartbox），单独核对行列
chk("敏感性网格 5x5", html.count('class="heatc') == 25)

report = ["自检报告 · " + out, "size=%d bytes" % len(html.encode("utf-8"))]
fails = 0
for st, name, detail in checks:
    if st == "FAIL":
        fails += 1
    report.append(f"[{st}] {name}" + (f" | {detail}" if detail else ""))
report.append(f"SUMMARY: {'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
txt = "\\n".join(report)
open(os.path.join(BASE, "build_check.txt"), "w", encoding="utf-8").write(txt)
print(txt[-1200:])

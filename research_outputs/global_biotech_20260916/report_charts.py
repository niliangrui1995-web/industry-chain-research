# -*- coding: utf-8 -*-
"""SVG 图表引擎 + CSS/JS 资源（决策看板_全球Biotech融资）。

所有图表由同一份已核验数据生成，遵守 HTML报告生成规范.md 的图表组件契约：
- 响应式 viewBox、完整坐标轴与 4-6 个 y 刻度、轻量网格线；
- 每条系列/样式有图例或贴近图形的标签；推算值/不完整期间/缺值有明确视觉语义；
- 数据标签只标关键点；悬浮提示（SVG <title>）含期间/数值/单位/口径；
- 图下提供与图中数值完全一致的可展开数据表；来源角标在图注（HTML 侧）；
- 年度与半年/九月度数据不混入同一可比序列（独立柱+颜色+标签区分）。
"""
from __future__ import annotations

import html as _html
import math

# ---------------------------------------------------------------- 基础工具

BLUE = "#00d9ff"
GREEN = "#00e676"
AMBER = "#ffab40"
PURPLE = "#e040fb"
RED = "#ff5252"
GRID = "rgba(255,255,255,0.09)"
AXIS = "rgba(255,255,255,0.35)"
TXT = "#c7d3e0"
TXT_DIM = "#8899aa"


def esc(s) -> str:
    return _html.escape(str(s), quote=True)


def fmt(v: float) -> str:
    if v is None:
        return ""
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _nice_ticks(vmax: float, target: int = 5):
    if vmax <= 0:
        vmax = 1.0
    raw = vmax / target
    mag = 10 ** math.floor(math.log10(raw))
    step = None
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            step = m * mag
            break
    hi = math.ceil(vmax / step) * step
    ticks = []
    t = 0.0
    while t <= hi + 1e-9:
        ticks.append(round(t, 6))
        t += step
    return ticks, hi


# ---------------------------------------------------------------- SVG 片段

def _bar_rect(x, y, w, h, style, color, tip, extra=""):
    if style == "derived":
        fill = "rgba(0,217,255,0.30)"
        stroke = f' stroke="{BLUE}" stroke-width="1.4" stroke-dasharray="5 3"'
        if color != BLUE:
            fill = "rgba(0,230,118,0.30)"
            stroke = f' stroke="{GREEN}" stroke-width="1.4" stroke-dasharray="5 3"'
    elif style == "partial":
        fill = "rgba(255,171,64,0.55)"
        stroke = f' stroke="{AMBER}" stroke-width="1.4"'
    elif style == "alt":
        fill = "rgba(0,230,118,0.55)"
        stroke = f' stroke="{GREEN}" stroke-width="1.2"'
    else:
        fill = color
        stroke = ""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3"'
        f' fill="{fill}"{stroke}{extra}><title>{esc(tip)}</title></rect>'
    )


def _legend_html(items):
    """items: list of (key, color, label, dashed) -> 可点击图例按钮 + 说明。"""
    btns = []
    for key, color, label, dashed in items:
        style = f"border:1.5px dashed {color};background:transparent;" if dashed else f"background:{color};"
        btns.append(
            f'<button class="legend-item" type="button" data-series="{key}" aria-pressed="true">'
            f'<span class="legend-sw" style="{style}"></span>{esc(label)}</button>'
        )
    return '<div class="chart-legend" role="group" aria-label="图例（点击可显示/隐藏系列）">' + "".join(btns) + "</div>"


# ---------------------------------------------------------------- 单系列柱状图

def chart_single(cid, cats, unit, color=BLUE, ylab_size=11.5):
    """cats: list of dict(label, value, style, tip_extra)
    style: normal | derived(推算) | partial(不完整期间) | alt(第二口径) | missing(缺值)
    """
    W, H = 760, 400
    ml, mr, mt, mb = 64, 24, 30, 58
    x0, y0 = ml, mt
    plot_w, plot_h = W - ml - mr, H - mt - mb
    vals = [c["value"] for c in cats if c.get("value") is not None]
    vmax = max(vals) * 1.08
    ticks, hi = _nice_ticks(vmax)
    n = len(cats)
    slot = plot_w / n
    bw = min(58.0, slot * 0.56)
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(cid)}" preserveAspectRatio="xMidYMid meet">']
    # 网格与轴
    grid = []
    for t in ticks:
        y = y0 + plot_h - (t / hi) * plot_h
        grid.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + plot_w}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        grid.append(f'<text x="{x0 - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="{TXT_DIM}">{esc(fmt(t))}</text>')
    parts.append("".join(grid))
    parts.append(f'<line x1="{x0}" y1="{y0 + plot_h}" x2="{x0 + plot_w}" y2="{y0 + plot_h}" stroke="{AXIS}" stroke-width="1"/>')
    parts.append(f'<text x="{x0 - 8}" y="{y0 - 8}" text-anchor="end" font-size="11" fill="{TXT_DIM}">单位：{esc(unit)}</text>')
    legend_items = {}
    for i, c in enumerate(cats):
        cx = x0 + slot * i + slot / 2
        label = c["label"]
        star = ""
        if c.get("style") == "derived":
            star = "*"
        parts.append(
            f'<text x="{cx:.1f}" y="{y0 + plot_h + 18}" text-anchor="middle" font-size="11.5" fill="{TXT}">{esc(label)}{star}</text>'
        )
        if c.get("style") == "partial":
            parts.append(
                f'<text x="{cx:.1f}" y="{y0 + plot_h + 33}" text-anchor="middle" font-size="10" fill="{AMBER}">{esc(c.get("sub", "不完整期间"))}</text>'
            )
        elif c.get("sub"):
            parts.append(
                f'<text x="{cx:.1f}" y="{y0 + plot_h + 33}" text-anchor="middle" font-size="10" fill="{TXT_DIM}">{esc(c["sub"])}</text>'
            )
        style = c.get("style", "normal")
        v = c.get("value")
        gkey = c.get("gkey", "s0")
        if style == "missing" or v is None:
            parts.append(
                f'<g data-series-group="{gkey}"><text x="{cx:.1f}" y="{y0 + plot_h - 6}" text-anchor="middle" font-size="10.5" fill="{TXT_DIM}">缺值</text></g>'
            )
            legend_items[gkey] = (gkey, TXT_DIM, c.get("glabel", "缺值"), True)
            continue
        h = (v / hi) * plot_h
        y = y0 + plot_h - h
        tip = c.get("tip", f'{c["label"]}：{fmt(v)} {unit}')
        parts.append(f'<g data-series-group="{gkey}">')
        parts.append(_bar_rect(cx - bw / 2, y, bw, h, style, c.get("color", color), tip))
        lbl_fill = AMBER if style == "partial" else "#ffffff"
        parts.append(
            f'<text x="{cx:.1f}" y="{y - 6:.1f}" text-anchor="middle" font-size="{ylab_size}" font-weight="600" fill="{lbl_fill}">{esc(fmt(v))}</text>'
        )
        parts.append("</g>")
        glabel = c.get("glabel")
        if glabel and gkey not in legend_items:
            dashed = style in ("derived", "missing")
            sw_color = AMBER if style == "partial" else (c.get("color", color) if style != "derived" else BLUE)
            if style == "alt":
                sw_color = GREEN
            legend_items[gkey] = (gkey, sw_color, glabel, dashed)
    parts.append("</svg>")
    return "".join(parts), _legend_html(list(legend_items.values()))


# ---------------------------------------------------------------- 分组柱状图（2 系列）

def chart_grouped(cid, cats, s1, s2, unit, partial_idx=()):
    """cats: x 标签 list；s1/s2: dict(name,color,values,gkey) values 长度与 cats 对齐，None=缺值。
    partial_idx: 不完整期间的 cat 下标（两系列同柱位改为琥珀色）。
    """
    W, H = 780, 400
    ml, mr, mt, mb = 64, 24, 30, 58
    x0, y0 = ml, mt
    plot_w, plot_h = W - ml - mr, H - mt - mb
    allv = [v for v in s1["values"] + s2["values"] if v is not None]
    vmax = max(allv) * 1.08
    ticks, hi = _nice_ticks(vmax)
    n = len(cats)
    slot = plot_w / n
    bw = min(34.0, slot * 0.34)
    gap = 6.0
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(cid)}" preserveAspectRatio="xMidYMid meet">']
    for t in ticks:
        y = y0 + plot_h - (t / hi) * plot_h
        parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + plot_w}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{x0 - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="{TXT_DIM}">{esc(fmt(t))}</text>')
    parts.append(f'<line x1="{x0}" y1="{y0 + plot_h}" x2="{x0 + plot_w}" y2="{y0 + plot_h}" stroke="{AXIS}" stroke-width="1"/>')
    parts.append(f'<text x="{x0 - 8}" y="{y0 - 8}" text-anchor="end" font-size="11" fill="{TXT_DIM}">单位：{esc(unit)}</text>')
    for i, label in enumerate(cats):
        cx = x0 + slot * i + slot / 2
        star = "*" if i in partial_idx else ""
        parts.append(f'<text x="{cx:.1f}" y="{y0 + plot_h + 18}" text-anchor="middle" font-size="11.5" fill="{TXT}">{esc(label)}{star}</text>')
        if i in partial_idx:
            parts.append(f'<text x="{cx:.1f}" y="{y0 + plot_h + 33}" text-anchor="middle" font-size="10" fill="{AMBER}">九月度</text>')
        for k, s in enumerate((s1, s2)):
            v = s["values"][i]
            bx = cx - bw - gap / 2 if k == 0 else cx + gap / 2
            gkey = s["gkey"]
            if v is None:
                parts.append(f'<g data-series-group="{gkey}"><text x="{bx + bw / 2:.1f}" y="{y0 + plot_h - 6}" text-anchor="middle" font-size="9.5" fill="{TXT_DIM}">缺值</text></g>')
                continue
            h = (v / hi) * plot_h
            y = y0 + plot_h - h
            style = "partial" if i in partial_idx else "normal"
            tip = f'{label} · {s["name"]}：{fmt(v)} {unit}'
            parts.append(f'<g data-series-group="{gkey}">')
            parts.append(_bar_rect(bx, y, bw, h, style, s["color"], tip))
            parts.append(f'<text x="{bx + bw / 2:.1f}" y="{y - 5:.1f}" text-anchor="middle" font-size="10" font-weight="600" fill="#ffffff">{esc(fmt(v))}</text>')
            parts.append("</g>")
    parts.append("</svg>")
    legend = _legend_html([
        (s1["gkey"], s1["color"], s1["name"], False),
        (s2["gkey"], s2["color"], s2["name"], False),
    ])
    return "".join(parts), legend


# ---------------------------------------------------------------- 双轴图（柱=左轴金额，线=右轴数量）

def chart_dual(cid, cats, bars, line, unit_l, unit_r):
    """bars: dict(name,color,values,gkey) 左轴；line: dict(name,color,values,gkey) 右轴。"""
    W, H = 780, 410
    ml, mr, mt, mb = 64, 64, 30, 56
    x0, y0 = ml, mt
    plot_w, plot_h = W - ml - mr, H - mt - mb
    ticks_l, hi_l = _nice_ticks(max(bars["values"]) * 1.10)
    ticks_r, hi_r = _nice_ticks(max(line["values"]) * 1.15)
    n = len(cats)
    slot = plot_w / n
    bw = min(46.0, slot * 0.5)
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(cid)}" preserveAspectRatio="xMidYMid meet">']
    for t in ticks_l:
        y = y0 + plot_h - (t / hi_l) * plot_h
        parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + plot_w}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{x0 - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="{TXT_DIM}">{esc(fmt(t))}</text>')
    for t in ticks_r:
        y = y0 + plot_h - (t / hi_r) * plot_h
        parts.append(f'<text x="{x0 + plot_w + 8}" y="{y + 4:.1f}" text-anchor="start" font-size="11" fill="{GREEN}">{esc(fmt(t))}</text>')
    parts.append(f'<line x1="{x0}" y1="{y0 + plot_h}" x2="{x0 + plot_w}" y2="{y0 + plot_h}" stroke="{AXIS}" stroke-width="1"/>')
    parts.append(f'<line x1="{x0 + plot_w}" y1="{y0}" x2="{x0 + plot_w}" y2="{y0 + plot_h}" stroke="{AXIS}" stroke-width="1"/>')
    parts.append(f'<text x="{x0 - 8}" y="{y0 - 8}" text-anchor="end" font-size="11" fill="{TXT_DIM}">左轴：{esc(unit_l)}</text>')
    parts.append(f'<text x="{x0 + plot_w + 8}" y="{y0 - 8}" text-anchor="start" font-size="11" fill="{GREEN}">右轴：{esc(unit_r)}</text>')
    pts = []
    for i, label in enumerate(cats):
        cx = x0 + slot * i + slot / 2
        parts.append(f'<text x="{cx:.1f}" y="{y0 + plot_h + 18}" text-anchor="middle" font-size="11.5" fill="{TXT}">{esc(label)}</text>')
        v = bars["values"][i]
        h = (v / hi_l) * plot_h
        y = y0 + plot_h - h
        tip = f'{label} · {bars["name"]}：{fmt(v)} {unit_l}'
        parts.append(f'<g data-series-group="{bars["gkey"]}">')
        parts.append(_bar_rect(cx - bw / 2, y, bw, h, "normal", bars["color"], tip))
        parts.append(f'<text x="{cx:.1f}" y="{y - 5:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="#ffffff">{esc(fmt(v))}</text>')
        parts.append("</g>")
        lv = line["values"][i]
        ly = y0 + plot_h - (lv / hi_r) * plot_h
        pts.append((cx, ly, lv, label))
    d = " ".join(f'{"M" if i == 0 else "L"}{p[0]:.1f},{p[1]:.1f}' for i, p in enumerate(pts))
    parts.append(f'<g data-series-group="{line["gkey"]}">')
    parts.append(f'<path d="{d}" fill="none" stroke="{line["color"]}" stroke-width="2.4"/>')
    for cx, ly, lv, label in pts:
        parts.append(f'<circle cx="{cx:.1f}" cy="{ly:.1f}" r="4.2" fill="{line["color"]}"><title>{esc(label)} · {line["name"]}：{fmt(lv)} {unit_r}</title></circle>')
        parts.append(f'<text x="{cx:.1f}" y="{ly - 9:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{line["color"]}">{esc(fmt(lv))}</text>')
    parts.append("</g>")
    parts.append("</svg>")
    legend = _legend_html([
        (bars["gkey"], bars["color"], f'{bars["name"]}（左轴）', False),
        (line["gkey"], line["color"], f'{line["name"]}（右轴）', False),
    ])
    return "".join(parts), legend


# ---------------------------------------------------------------- 横向条形图

def chart_hbar(cid, rows, unit):
    """rows: list of dict(label, value, color)。"""
    W = 760
    row_h = 46
    mt, mb, ml, mr = 26, 30, 120, 70
    H = mt + mb + row_h * len(rows)
    plot_w = W - ml - mr
    vmax = max(r["value"] for r in rows) * 1.06
    ticks, hi = _nice_ticks(vmax, target=4)
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(cid)}" preserveAspectRatio="xMidYMid meet">']
    for t in ticks:
        x = ml + (t / hi) * plot_w
        parts.append(f'<line x1="{x:.1f}" y1="{mt}" x2="{x:.1f}" y2="{mt + row_h * len(rows)}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{mt + row_h * len(rows) + 16}" text-anchor="middle" font-size="11" fill="{TXT_DIM}">{esc(fmt(t))}%</text>')
    for i, r in enumerate(rows):
        cy = mt + row_h * i + row_h / 2
        w = (r["value"] / hi) * plot_w
        tip = f'{r["label"]}：{fmt(r["value"])}%（{unit}）'
        parts.append(f'<text x="{ml - 10}" y="{cy + 4:.1f}" text-anchor="end" font-size="12" fill="{TXT}">{esc(r["label"])}</text>')
        parts.append(f'<g data-series-group="s0">')
        parts.append(f'<rect x="{ml}" y="{cy - 13:.1f}" width="{w:.1f}" height="26" rx="4" fill="{r.get("color", BLUE)}"><title>{esc(tip)}</title></rect>')
        parts.append(f'<text x="{ml + w + 8:.1f}" y="{cy + 4:.1f}" font-size="12" font-weight="600" fill="#ffffff">+{esc(fmt(r["value"]))}%</text>')
        parts.append("</g>")
    parts.append("</svg>")
    legend = _legend_html([("s0", BLUE, "2026 年内涨跌幅（%）", False)])
    return "".join(parts), legend


# ---------------------------------------------------------------- 图块包装

def figure_block(fid, no, title, meta_chips, svg, legend, note_html, table_html):
    chips = "".join(f'<span class="chip">{esc(m)}</span>' for m in meta_chips)
    return f'''
<figure class="chart-card" id="{fid}">
  <figcaption class="chart-title">图 {no} · {esc(title)}</figcaption>
  <div class="chart-meta">{chips}</div>
  {legend}
  <div class="chart-wrap">{svg}</div>
  <p class="chart-note">{note_html}</p>
  <details class="chart-data"><summary>查看数据表（与图中数值一致）</summary>{table_html}</details>
</figure>'''


def data_table(headers, rows, caption=None):
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    trs = []
    for row in rows:
        tds = "".join(f"<td>{esc(c)}</td>" for c in row)
        trs.append(f"<tr>{tds}</tr>")
    cap = f"<caption style='text-align:left;color:#8899aa;font-size:12px;padding:6px 0;'>{esc(caption)}</caption>" if caption else ""
    return f'<table class="data-table">{cap}<thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'


# ---------------------------------------------------------------- CSS / JS

CSS_TEMPLATE = r"""
/*__MOSS_TOKENS__*/
:root {
  --bg-primary:#0f1419; --bg-secondary:#1a2332; --bg-card:#242d38; --bg-card-hover:#2d3a4a;
  --color-p0:#ff5252; --color-p1:#ffab40; --color-p2:#69f0ae;
  --color-accent-blue:#00d9ff; --color-accent-green:#00e676; --color-accent-orange:#ff9100;
  --color-accent-purple:#e040fb; --color-accent-yellow:#ffea00;
  --text-primary:#ffffff; --text-secondary:#8899aa; --text-tertiary:#6b7785;
  --border-color:rgba(255,255,255,0.1);
}
* { margin:0; padding:0; box-sizing:border-box; }
html { scroll-behavior:smooth; }
body {
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
  min-height:100vh; padding:40px; color:#fff; line-height:1.65;
}
.container { max-width:1400px; margin:0 auto; }
.report-header { text-align:center; margin-bottom:32px; padding:34px 26px; background:rgba(255,255,255,0.05); border-radius:20px; backdrop-filter:blur(10px); }
.report-title { font-size:34px; font-weight:700; margin-bottom:14px; background:linear-gradient(90deg,#00d9ff,#00ff88); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.report-sub { font-size:16px; color:#c7d3e0; margin-bottom:14px; }
.report-meta { font-size:13px; color:#8899aa; display:flex; justify-content:center; gap:18px; flex-wrap:wrap; }
.content-section { background:rgba(255,255,255,0.06); border-radius:20px; padding:30px; margin-bottom:30px; border:1px solid rgba(255,255,255,0.08); }
.content-section h2 { font-size:24px; font-weight:600; margin-bottom:20px; padding-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.1); }
.content-section h3 { font-size:18px; font-weight:600; margin:25px 0 15px 0; color:#00d9ff; }
.content-section h4 { font-size:16px; font-weight:600; margin:20px 0 10px 0; color:#a9bccf; }
.content-section p { margin:12px 0; color:#e8eef5; }
.content-section ul,.content-section ol { margin:14px 0; padding-left:25px; }
.content-section li { margin-bottom:8px; color:#e8eef5; }
.content-section li::marker { color:#00d9ff; }
.content-section strong { color:#00e676; }
.content-section em { color:#ffab40; font-style:normal; }
.small { font-size:12.5px; color:#8899aa; }
.toc-list { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:10px 24px; }
.toc-list a { color:#c7d3e0; text-decoration:none; padding:7px 12px; border-radius:8px; background:rgba(255,255,255,0.04); display:block; font-size:14px; }
.toc-list a:hover,.toc-list a:focus { color:#00d9ff; background:rgba(0,217,255,0.10); }
.verdict { font-size:26px; font-weight:700; text-align:center; margin-bottom:12px; line-height:1.5; background:linear-gradient(90deg,#00d9ff,#00ff88); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.verdict-sub { text-align:center; color:#8899aa; font-size:13.5px; margin-bottom:26px; }
.key-metrics { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-bottom:34px; }
.metric-card { background:rgba(255,255,255,0.08); border-radius:16px; padding:20px 16px; text-align:center; border:1px solid rgba(255,255,255,0.1); transition:all .3s; }
.metric-card:hover { background:rgba(255,255,255,0.12); transform:translateY(-3px); }
.metric-value { font-size:30px; font-weight:700; margin-bottom:6px; }
.metric-label { font-size:12.5px; color:#8899aa; line-height:1.5; }
.main-content { display:grid; grid-template-columns:1fr 1fr; gap:26px; margin-bottom:34px; }
.section-card { background:rgba(255,255,255,0.05); border-radius:18px; padding:26px; border:1px solid rgba(255,255,255,0.08); }
.section-title { font-size:18px; font-weight:600; margin-bottom:20px; display:flex; align-items:center; gap:10px; }
.section-title::before { content:""; width:4px; height:20px; background:linear-gradient(180deg,#00d9ff,#00ff88); border-radius:2px; }
.client-tier { display:flex; align-items:flex-start; padding:16px 18px; background:rgba(255,255,255,0.04); border-radius:12px; margin-bottom:12px; border-left:4px solid; transition:all .3s; }
.client-tier:hover { background:rgba(255,255,255,0.08); }
.tier-p0 { border-color:#ff5252; } .tier-p1 { border-color:#ffab40; } .tier-p2 { border-color:#69f0ae; }
.tier-badge { min-width:50px; height:50px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:16px; margin-right:16px; }
.tier-p0 .tier-badge { background:rgba(255,82,82,0.2); color:#ff5252; }
.tier-p1 .tier-badge { background:rgba(255,171,64,0.2); color:#ffab40; }
.tier-p2 .tier-badge { background:rgba(105,240,174,0.2); color:#69f0ae; }
.tier-body { flex:1; font-size:13.5px; }
.tier-body b { font-size:15px; display:block; margin-bottom:4px; }
.matrix-wrap { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.matrix-cell { padding:16px; border-radius:14px; font-size:12.8px; line-height:1.55; }
.matrix-cell h5 { font-size:13.5px; margin-bottom:8px; }
.cell-tl { background:linear-gradient(135deg,rgba(0,230,118,0.22),rgba(0,230,118,0.06)); border:1px solid rgba(0,230,118,0.4); }
.cell-tr { background:linear-gradient(135deg,rgba(255,171,64,0.22),rgba(255,171,64,0.06)); border:1px solid rgba(255,171,64,0.4); }
.cell-bl { background:linear-gradient(135deg,rgba(0,217,255,0.20),rgba(0,217,255,0.05)); border:1px solid rgba(0,217,255,0.35); }
.cell-br { background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.12); }
.matrix-axis { text-align:center; color:#8899aa; font-size:12px; margin-top:10px; }
.action-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; }
.action-card { background:rgba(255,255,255,0.04); border-radius:14px; padding:22px; border-top:3px solid; font-size:13.5px; }
.action-card h4 { margin:0 0 12px 0; font-size:15px; color:#fff; }
.action-validation { border-color:#ff5252; } .action-watch { border-color:#ffab40; } .action-stop { border-color:#00e676; }
.action-card li { font-size:13px; }
.data-table { width:100%; border-collapse:collapse; margin:15px 0; font-size:13.5px; }
.data-table th { background:rgba(0,217,255,0.15); color:#00d9ff; padding:11px 14px; text-align:left; font-weight:600; border-bottom:2px solid rgba(0,217,255,0.3); }
.data-table td { padding:10px 14px; border-bottom:1px solid rgba(255,255,255,0.08); color:#e8eef5; vertical-align:top; }
.data-table tr:hover td { background:rgba(255,255,255,0.05); }
.data-table tr:last-child td { border-bottom:none; }
.data-table td.highlight { color:#00e676; font-weight:600; }
.data-table td.warning { color:#ffab40; }
.data-table td.danger { color:#ff5252; }
.tag { display:inline-block; padding:3px 10px; border-radius:6px; font-size:12px; font-weight:600; margin:2px 4px 2px 0; }
.tag-p0 { background:rgba(255,82,82,0.2); color:#ff5252; }
.tag-p1 { background:rgba(255,171,64,0.2); color:#ffab40; }
.tag-p2 { background:rgba(105,240,174,0.2); color:#69f0ae; }
.tag-info { background:rgba(0,217,255,0.2); color:#00d9ff; }
.tag-dim { background:rgba(255,255,255,0.08); color:#8899aa; }
.blockquote { background:rgba(0,217,255,0.1); border-left:4px solid #00d9ff; padding:15px 20px; margin:15px 0; border-radius:0 8px 8px 0; color:#c7d3e0; }
.chart-card { background:rgba(255,255,255,0.045); border:1px solid rgba(255,255,255,0.09); border-radius:16px; padding:20px 20px 14px; margin:22px 0; }
.chart-title { font-size:16px; font-weight:600; color:#fff; margin-bottom:8px; }
.chart-meta { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; }
.chip { font-size:11.5px; color:#a9bccf; background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.1); border-radius:999px; padding:2px 10px; }
.chart-legend { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:6px; align-items:center; }
.legend-item { display:inline-flex; align-items:center; gap:6px; font-size:12px; color:#e8eef5; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); border-radius:999px; padding:4px 12px; cursor:pointer; }
.legend-item:hover,.legend-item:focus { border-color:#00d9ff; outline:none; }
.legend-item.off { opacity:0.4; text-decoration:line-through; }
.legend-sw { width:14px; height:14px; border-radius:4px; display:inline-block; }
.legend-note { font-size:11.5px; color:#8899aa; margin-left:4px; }
.chart-wrap svg { width:100%; height:auto; display:block; }
.series-off { opacity:0.12; }
.chart-note { font-size:12.5px; color:#a9bccf; line-height:1.6; margin:10px 2px 4px; }
.chart-data summary { cursor:pointer; font-size:12.5px; color:#00d9ff; padding:6px 0; }
.chart-data summary:hover { color:#00e676; }
.source-link { display:inline-flex; align-items:center; gap:4px; margin:2px 4px 2px 0; padding:3px 8px; border:1px solid rgba(0,217,255,.35); border-radius:999px; color:var(--color-accent-blue); background:rgba(0,217,255,.08); font:inherit; font-size:12px; line-height:1.35; text-decoration:none; cursor:pointer; }
.source-link:hover,.source-link:focus { color:var(--color-accent-green); border-color:var(--color-accent-green); background:rgba(0,230,118,.10); text-decoration:none; }
.evidence-list li { scroll-margin-top:24px; }
.evidence-list { list-style:none; padding:0; }
.evidence-list > li { background:rgba(255,255,255,0.045); border:1px solid rgba(255,255,255,0.09); border-radius:14px; padding:18px 20px; margin-bottom:14px; }
.evidence-head { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:8px; }
.evidence-id { font-weight:700; color:#00d9ff; font-size:14px; background:rgba(0,217,255,0.12); border-radius:8px; padding:2px 10px; }
.evidence-title { font-size:14.5px; font-weight:600; }
.evidence-title a { color:#fff; }
.evidence-title a:hover { color:#00d9ff; }
.evidence-meta { font-size:12px; color:#8899aa; margin-bottom:8px; display:flex; flex-wrap:wrap; gap:6px 14px; }
.evidence-metric { font-size:13px; color:#c7d3e0; margin:6px 0; }
.evidence-sl { font-size:12px; color:#a9bccf; margin:4px 0; }
.cite-backs { margin-top:8px; font-size:12px; color:#8899aa; }
.drawer-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.55); z-index:998; }
.evidence-drawer { position:fixed; top:0; right:0; width:min(460px,94vw); height:100vh; background:#16213e; border-left:1px solid rgba(0,217,255,0.35); z-index:999; box-shadow:-12px 0 40px rgba(0,0,0,0.5); display:flex; flex-direction:column; }
.drawer-head { display:flex; align-items:center; justify-content:space-between; padding:16px 20px; border-bottom:1px solid rgba(255,255,255,0.1); }
.drawer-head h3 { font-size:16px; color:#00d9ff; margin:0; }
.drawer-close { background:none; border:1px solid rgba(255,255,255,0.2); color:#fff; width:32px; height:32px; border-radius:8px; font-size:18px; cursor:pointer; }
.drawer-close:hover { border-color:#00d9ff; color:#00d9ff; }
.drawer-body { flex:1; overflow-y:auto; padding:18px 20px; font-size:13px; }
.drawer-body .kv { margin-bottom:10px; }
.drawer-body .k { color:#8899aa; font-size:12px; margin-bottom:2px; }
.drawer-body .v { color:#e8eef5; line-height:1.55; }
.drawer-foot { padding:14px 20px; border-top:1px solid rgba(255,255,255,0.1); display:flex; flex-wrap:wrap; gap:8px; }
details.trace-card { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09); border-radius:14px; padding:14px 18px; margin-bottom:12px; }
details.trace-card summary { cursor:pointer; font-weight:600; color:#fff; font-size:15px; }
details.trace-card summary:hover { color:#00d9ff; }
.trace-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.judge-card { background:rgba(0,217,255,0.07); border-left:4px solid #00d9ff; border-radius:0 12px 12px 0; padding:16px 18px; margin:16px 0; }
.judge-card .jc-t { font-size:12px; color:#8899aa; margin-bottom:4px; }
.judge-card .jc-b { font-size:14.5px; color:#fff; line-height:1.6; }
.scenario-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin:18px 0; }
.scenario-card { border-radius:14px; padding:18px; font-size:13px; line-height:1.6; border:1px solid; }
.sc-base { background:rgba(0,217,255,0.08); border-color:rgba(0,217,255,0.4); }
.sc-bull { background:rgba(0,230,118,0.08); border-color:rgba(0,230,118,0.4); }
.sc-bear { background:rgba(255,82,82,0.08); border-color:rgba(255,82,82,0.4); }
.scenario-card h4 { margin:0 0 8px; font-size:14.5px; }
.disclaimer { font-size:12.5px; color:#8899aa; }
@media (max-width:1200px){ .key-metrics{grid-template-columns:repeat(3,1fr);} .main-content{grid-template-columns:1fr;} .trace-grid{grid-template-columns:1fr;} }
@media (max-width:768px){
  body{padding:18px;} .key-metrics{grid-template-columns:repeat(2,1fr);} .action-grid{grid-template-columns:1fr;}
  .scenario-grid{grid-template-columns:1fr;} .report-title{font-size:26px;} .content-section{padding:20px;}
}
@media (max-width:480px){ .key-metrics{grid-template-columns:1fr;} .matrix-wrap{grid-template-columns:1fr;} }
@media print {
  body { background:#fff; color:#111; padding:10px; }
  .content-section,.metric-card,.chart-card,.section-card,.action-card { background:#fff; border:1px solid #ccc; break-inside:avoid; }
  .report-title,.verdict { -webkit-text-fill-color:#0f3460; background:none; color:#0f3460; }
  .content-section h2,.content-section h3,.section-title { color:#0f3460; }
  .content-section p,.content-section li,.data-table td { color:#222; }
  .evidence-drawer,.drawer-overlay { display:none !important; }
  .chart-data { display:block; }
  a { color:#0f3460; }
}
"""

JS_TEMPLATE = r"""
(function(){
  var EVIDENCE = __EVIDENCE_JSON__;
  var drawer = document.getElementById('evidence-drawer');
  var overlay = document.getElementById('drawer-overlay');
  var body = document.getElementById('drawer-body');
  var title = document.getElementById('drawer-title');
  var gotoIndex = document.getElementById('drawer-goto-index');
  var gotoCite = document.getElementById('drawer-goto-cite');
  var gotoUrl = document.getElementById('drawer-goto-url');
  var lastAnchor = null;
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function row(k,v){return '<div class="kv"><div class="k">'+esc(k)+'</div><div class="v">'+v+'</div></div>';}
  function openDrawer(eid, anchorId){
    var ev = EVIDENCE[eid]; if(!ev){return;}
    lastAnchor = anchorId;
    title.textContent = '证据详情 · ' + eid;
    var urlHtml = ev.url ? '<a class="source-link" href="'+esc(ev.url)+'" target="_blank" rel="noopener noreferrer">公开原文入口 ↗</a>' : '<span class="tag tag-dim">无公开链接 · '+esc(ev.access||'')+'</span>';
    body.innerHTML =
      row('来源标题', esc(ev.title)) +
      row('发布机构', esc(ev.publisher)) +
      row('来源类型', esc(ev.type)) +
      row('发布/统计时间', esc(ev.publishedAt)) +
      row('本轮查询时间', esc(ev.queriedAt)) +
      row('地域', esc(ev.region)) +
      row('对象 / 口径 / 单位', esc(ev.metric)) +
      row('证据强度', esc(ev.strength)) +
      row('局限（不能证明什么）', esc(ev.limitation)) +
      row('访问权限', esc(ev.access)) +
      row('原文入口', urlHtml);
    gotoIndex.setAttribute('href','#evidence-'+eid);
    if(ev.url){ gotoUrl.style.display=''; gotoUrl.setAttribute('href',ev.url); } else { gotoUrl.style.display='none'; }
    drawer.hidden = false; overlay.hidden = false;
  }
  function closeDrawer(){ drawer.hidden = true; overlay.hidden = true; }
  document.querySelectorAll('.evidence-button').forEach(function(btn){
    btn.addEventListener('click', function(){
      var anchor = btn.previousElementSibling;
      openDrawer(btn.getAttribute('data-evidence-id'), anchor && anchor.id ? anchor.id : null);
    });
  });
  document.getElementById('drawer-close').addEventListener('click', closeDrawer);
  overlay.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', function(e){ if(e.key==='Escape'){ closeDrawer(); } });
  gotoIndex.addEventListener('click', function(){ closeDrawer(); });
  gotoCite.addEventListener('click', function(){
    closeDrawer();
    if(lastAnchor){
      var el = document.getElementById(lastAnchor);
      if(el){ el.scrollIntoView({behavior:'smooth', block:'center'}); }
    }
  });
  document.querySelectorAll('.legend-item').forEach(function(btn){
    btn.addEventListener('click', function(){
      var key = btn.getAttribute('data-series');
      var off = btn.classList.toggle('off');
      btn.setAttribute('aria-pressed', off ? 'false' : 'true');
      document.querySelectorAll('[data-series-group="'+key+'"]').forEach(function(g){
        g.classList.toggle('series-off', off);
      });
    });
  });
})();
"""

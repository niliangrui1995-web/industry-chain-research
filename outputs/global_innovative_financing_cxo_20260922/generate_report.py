import html
import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
PACKAGE_PATH = WORKSPACE / "frozen_delivery_package.json"
CONTRACT_PATH = WORKSPACE / "artifact-contract.json"
OUTPUT_PATH = WORKSPACE / "决策看板_全球创新药融资周期与CXO传导.html"

pkg = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
content = pkg["content"]
contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
evidence = {item["id"]: item for item in pkg["evidence"]}
tokens = contract["tokens"]


def esc(value):
    return html.escape(str(value), quote=True)


def badge(value):
    ids = [part.strip() for part in str(value).split(",") if part.strip()]
    return " ".join(f'<a class="evidence-badge" href="#evidence-{esc(item)}">{esc(item)}</a>' for item in ids)


def paragraph(text):
    return f"<p>{esc(text)}</p>"


def metric_block(item):
    return f'<div class="metric"><div class="metric-label">{esc(item["label"])}</div><strong>{esc(item["value"])}</strong><div class="metric-note">{esc(item["note"])}</div></div>'


def historical_section(section):
    rows = []
    for row in section["table"]["rows"]:
        cells = "".join(f"<td>{esc(cell) if not (isinstance(cell, str) and cell.startswith('E-')) else badge(cell)}</td>" for cell in row)
        rows.append(f"<tr>{cells}</tr>")
    headers = "".join(f"<th>{esc(item)}</th>" for item in section["table"]["headers"])
    metrics = "".join(metric_block(item) for item in section["blocks"] if item["type"] == "metric")
    return f'''<section id="{esc(section["id"])}" class="section section-fact">
      <div class="section-heading"><span>{esc(section["kicker"])}</span><h2>{esc(section["title"])}</h2><p>{esc(section["lead"])}</p></div>
      <div class="metric-grid">{metrics}</div>
      <div class="table-wrap"><table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>
    </section>'''


def forecast_section(section):
    s = section["scenario"]
    signal_rows = []
    for signal in section["signals"]:
        signal_rows.append(f'''<article class="signal signal-forward"><div class="signal-top"><span class="signal-name">{esc(signal["signal"])}</span><span class="tag orange">{esc(signal["lead_lag"])}</span></div><p><b>观察：</b>{esc(signal["observe"])}</p><p><b>含义：</b>{esc(signal["meaning"])}</p><p class="stop"><b>停止条件：</b>{esc(signal["stop"])}</p></article>''')
    return f'''<section id="{esc(section["id"])}" class="section section-forward-section">
      <div class="section-heading"><span>{esc(section["kicker"])}</span><h2>{esc(section["title"])}</h2><p>{esc(section["lead"])}</p></div>
      <div class="scenario-band"><div><span class="eyebrow">前瞻假设</span><p>{esc(s["assumption"])}</p></div><div class="window"><span class="eyebrow">情景窗口</span><strong>{esc(s["window"])}</strong><small>置信度：{esc(s["confidence"])}</small></div></div>
      <div class="two-column"><div class="note-panel"><h3>复苏的支持证据</h3>{paragraph(s["evidence_for_recovery"])}</div><div class="note-panel caution"><h3>反方情景</h3>{paragraph(s["countercase"])}</div></div>
      <div class="signal-grid">{"".join(signal_rows)}</div>
      <div class="rule-box"><b>顶部组合判据：</b>{esc(section["top_rule"])}</div>
    </section>'''


def chain_section(section):
    segment_cards = []
    for seg in section["segments"]:
        segment_cards.append(f'''<article class="segment"><div class="segment-name">{esc(seg["name"])}</div><p><b>代表公司：</b>{esc(seg["examples"])}</p><p><b>集中度：</b><span class="na">{esc(seg["concentration"])}</span></p><p><b>进入壁垒：</b>{esc(seg["barriers"])}</p><p><b>竞争：</b>{esc(seg["competition"])}</p><p class="leading"><b>先行指标：</b>{esc(seg["leading"])}</p></article>''')
    rows = []
    for row in section["transmission"]:
        cells = "".join(f"<td>{esc(value)}</td>" for value in [row["segment"], row["demand"], row["elasticity"], row["pricing"], row["utilization"], row["pace"]])
        rows.append(f"<tr>{cells}</tr>")
    headers = ["环节", "需求传导", "订单恢复弹性", "议价能力", "产能利用率", "受益节奏"]
    return f'''<section id="{esc(section["id"])}" class="section section-chain">
      <div class="section-heading"><span>{esc(section["kicker"])}</span><h2>{esc(section["title"])}</h2><p>{esc(section["lead"])}</p></div>
      <div class="segment-grid">{"".join(segment_cards)}</div>
      <div class="table-wrap"><table class="transmission"><thead><tr>{"".join(f"<th>{esc(item)}</th>" for item in headers)}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>
      <div class="winner-strip"><div><span class="winner-label">最快受益</span><strong>上游工具与材料</strong><p>预算恢复后即可触发采购，收入确认短，订单和复购较早可见。</p></div><div><span class="winner-label">最大弹性</span><strong>CDMO / CRDMO</strong><p>阶段升级、技术转移和利用率改善叠加，金额与利润弹性最大，但确认最慢。</p></div></div>
    </section>'''


def company_section(section):
    cards = []
    for item in section["checks"]:
        cards.append(f'''<article class="company-check"><div class="company-head"><h3>{esc(item["company"])}</h3><span>{badge(item["evidence"])}</span></div><p><b>事实：</b>{esc(item["facts"])}</p><p><b>解读：</b>{esc(item["interpretation"])}</p><p class="risk"><b>风险：</b>{esc(item["risk"])}</p></article>''')
    return f'''<section id="{esc(section["id"])}" class="section section-checks"><div class="section-heading"><span>{esc(section["kicker"])}</span><h2>{esc(section["title"])}</h2><p>融资、订单、收入、利润和现金流必须按顺序验证。单一订单增速或单季利润不能替代经营穿透。</p></div><div class="company-grid">{"".join(cards)}</div></section>'''


def dashboard_section(section):
    cols = []
    for column in section["columns"]:
        items = "".join(f"<li>{esc(item)}</li>" for item in column["items"])
        cols.append(f'<article class="dashboard-col"><h3>{esc(column["title"])}</h3><ul>{items}</ul></article>')
    return f'''<section id="{esc(section["id"])}" class="section section-dashboard"><div class="section-heading"><span>{esc(section["kicker"])}</span><h2>{esc(section["title"])}</h2><p>用组合信号确认周期状态，不用单点交易叙事替代证据链。</p></div><div class="dashboard-grid">{"".join(cols)}</div></section>'''


def limitations_section(section):
    items = "".join(f"<li>{esc(item)}</li>" for item in section["items"])
    return f'''<section id="{esc(section["id"])}" class="section section-limitations"><div class="section-heading"><span>{esc(section["kicker"])}</span><h2>{esc(section["title"])}</h2></div><ul class="limitations">{items}</ul></section>'''


def evidence_section():
    cards = []
    for item in evidence.values():
        url = item["url"]
        source_link = f'<a href="{esc(url)}" target="_blank" rel="noopener">打开来源</a>' if url.startswith("http") else f'<span class="local-source">{esc(url)}</span>'
        cards.append(f'''<article class="evidence-item" id="evidence-{esc(item["id"])}"><div class="evidence-head"><span class="evidence-id">{esc(item["id"])}</span><span class="tag">{esc(item["type"])}</span><span class="confidence">置信度：{esc(item["confidence"])}</span></div><h3>{esc(item["source"])}</h3><p><b>发布日期：</b>{esc(item["published"])}　<b>统计截止：</b>{esc(item["as_of"])}　<b>地域：</b>{esc(item["region"])}</p><p><b>对象：</b>{esc(item["object"])}　<b>口径：</b>{esc(item["scope"])}　<b>单位：</b>{esc(item["unit"])}</p><p>{esc(item["note"])}</p><div class="source-link">{source_link}</div></article>''')
    return f'''<section id="evidence" class="section section-evidence"><div class="section-heading"><span>APPENDIX / 证据台账</span><h2>证据、口径与来源</h2><p>每条记录保留来源类型、发布日期、统计截止期、地域、对象、口径、单位和置信度；不同统计口径不做简单平均。</p></div><div class="evidence-list">{"".join(cards)}</div></section>'''


sections = content["sections"]
section_html = "".join(
    historical_section(sections[0])
    + forecast_section(sections[1])
    + chain_section(sections[2])
    + company_section(sections[3])
    + dashboard_section(sections[4])
    + limitations_section(sections[5])
)

nav_items = [("historical", "01 历史复盘"), ("forecast", "02 前瞻预警"), ("chain", "03 CXO 传导"), ("company_checks", "04 经营验证"), ("dashboard", "05 跟踪看板"), ("limitations", "06 边界限制"), ("evidence", "证据台账")]
nav = "".join(f'<a href="#{anchor}">{esc(label)}</a>' for anchor, label in nav_items)
headline = content["headline"]

html_doc = f'''<!doctype html>
<html lang="zh-CN" data-moss-artifact-mode="{esc(contract["artifact_mode"])}" data-moss-visual-baseline="{esc(contract["visual_baseline"])}" data-moss-render-seed="{esc(contract["render_seed"])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(content["title"])}</title>
<style>
:root {{
  --moss-color-primary: {tokens["--moss-color-primary"]};
  --moss-color-secondary: {tokens["--moss-color-secondary"]};
  --moss-color-accent: {tokens["--moss-color-accent"]};
  --moss-color-surface: {tokens["--moss-color-surface"]};
  --moss-color-text: {tokens["--moss-color-text"]};
  --moss-font-display: {tokens["--moss-font-display"]};
  --moss-font-body: {tokens["--moss-font-body"]};
  --moss-type-ratio: {tokens["--moss-type-ratio"]};
  --moss-space-unit: {tokens["--moss-space-unit"]};
  --moss-radius: {tokens["--moss-radius"]};
  --moss-shadow: {tokens["--moss-shadow"]};
  --moss-motion-duration: {tokens["--moss-motion-duration"]};
  --moss-motion-easing: {tokens["--moss-motion-easing"]};
  --moss-tone: {tokens["--moss-tone"]};
  --moss-density: {tokens["--moss-density"]};
  --ink-soft: #566071;
  --line: #D9D7D0;
  --paper: #F7F4EE;
  --fact: #17213D;
  --forward: #E4572E;
  --ok: #2E6B57;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; background: var(--paper); }}
body {{ margin: 0; color: var(--moss-color-text); background: var(--paper); font-family: var(--moss-font-body); line-height: 1.62; }}
a {{ color: inherit; }}
.topbar {{ position: sticky; top: 0; z-index: 20; background: rgba(247,244,238,.94); backdrop-filter: blur(12px); border-bottom: 1px solid var(--line); }}
.nav {{ max-width: 1240px; margin: 0 auto; padding: 12px 28px; display: flex; gap: 18px; overflow-x: auto; white-space: nowrap; }}
.nav a {{ text-decoration: none; color: var(--ink-soft); font-size: 12px; font-weight: 700; letter-spacing: .02em; }}
.nav a:hover, .nav a:focus {{ color: var(--forward); }}
.hero {{ background: var(--moss-color-primary); color: #FFFDF8; padding: 76px max(28px, calc((100vw - 1240px)/2)) 68px; position: relative; overflow: hidden; }}
.hero:after {{ content: ""; position: absolute; width: 440px; height: 440px; right: -100px; top: -170px; border: 1px solid rgba(255,255,255,.17); border-radius: 50%; box-shadow: 0 0 0 38px rgba(255,255,255,.045), 0 0 0 76px rgba(255,255,255,.03); }}
.hero-grid {{ display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(280px, .7fr); gap: 56px; align-items: end; position: relative; z-index: 1; }}
.eyebrow, .section-heading > span {{ color: var(--forward); font-size: 11px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }}
.hero h1 {{ font-family: var(--moss-font-display); font-size: clamp(40px, 6vw, 78px); line-height: 1.02; margin: 20px 0 22px; max-width: 900px; font-weight: 700; }}
.hero .subtitle {{ max-width: 720px; margin: 0; color: #D9DEEA; font-size: 17px; }}
.hero-meta {{ border-left: 1px solid rgba(255,255,255,.32); padding-left: 24px; color: #D9DEEA; font-size: 13px; }}
.hero-meta strong {{ color: #FFFDF8; font-size: 20px; display: block; margin-top: 4px; }}
.wrap {{ max-width: 1240px; margin: 0 auto; padding: 0 28px; }}
.thesis {{ margin: -28px auto 72px; position: relative; z-index: 2; display: grid; grid-template-columns: 1.25fr .75fr .75fr; gap: 1px; background: var(--line); box-shadow: var(--moss-shadow); }}
.thesis > div {{ background: var(--moss-color-surface); padding: 26px; min-height: 166px; }}
.thesis .label {{ display: block; color: var(--ink-soft); font-size: 11px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-bottom: 12px; }}
.thesis strong {{ display: block; font-family: var(--moss-font-display); font-size: 22px; line-height: 1.22; color: var(--moss-color-primary); }}
.thesis p {{ margin: 10px 0 0; color: var(--ink-soft); font-size: 13px; }}
.section {{ padding: 76px 0; border-top: 1px solid var(--line); scroll-margin-top: 54px; }}
.section-heading {{ max-width: 890px; margin-bottom: 34px; }}
.section-heading h2 {{ font-family: var(--moss-font-display); color: var(--moss-color-primary); font-size: clamp(32px, 4vw, 52px); line-height: 1.1; margin: 12px 0 16px; }}
.section-heading p {{ margin: 0; color: var(--ink-soft); font-size: 16px; max-width: 800px; }}
.metric-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--line); margin: 28px 0 36px; }}
.metric {{ background: var(--moss-color-surface); padding: 22px; min-height: 144px; }}
.metric-label {{ font-size: 12px; color: var(--ink-soft); font-weight: 700; }}
.metric strong {{ display: block; color: var(--moss-color-primary); font-family: var(--moss-font-display); font-size: 34px; margin: 10px 0 6px; }}
.metric-note {{ color: var(--ink-soft); font-size: 12px; }}
.table-wrap {{ overflow-x: auto; border: 1px solid var(--line); background: var(--moss-color-surface); }}
table {{ width: 100%; border-collapse: collapse; min-width: 880px; font-size: 13px; }}
th {{ text-align: left; color: var(--moss-color-primary); background: var(--moss-color-secondary); padding: 13px 14px; font-size: 11px; letter-spacing: .05em; white-space: nowrap; }}
td {{ padding: 14px; border-top: 1px solid var(--line); vertical-align: top; min-width: 130px; }}
tr:hover td {{ background: #FCFAF5; }}
.evidence-badge {{ display: inline-block; margin: 2px 4px 2px 0; padding: 2px 6px; border: 1px solid #C9C6BD; color: var(--moss-color-primary); background: #FFFDF8; border-radius: 3px; font-size: 10px; font-weight: 800; text-decoration: none; }}
.evidence-badge:hover {{ border-color: var(--forward); color: var(--forward); }}
.scenario-band {{ display: grid; grid-template-columns: 1fr 280px; background: var(--moss-color-primary); color: #FFFDF8; margin: 32px 0; border-left: 7px solid var(--forward); }}
.scenario-band > div {{ padding: 26px; }}
.scenario-band p {{ margin: 10px 0 0; color: #E7E9F0; }}
.window {{ border-left: 1px solid rgba(255,255,255,.2); display: flex; flex-direction: column; justify-content: center; }}
.window .eyebrow {{ color: #F4A88F; }}
.window strong {{ font-family: var(--moss-font-display); font-size: 28px; margin: 6px 0; }}
.window small {{ color: #D9DEEA; }}
.two-column {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 28px; }}
.note-panel {{ padding: 22px; border: 1px solid var(--line); border-top: 3px solid var(--moss-color-primary); background: var(--moss-color-surface); }}
.note-panel.caution {{ border-top-color: var(--forward); }}
.note-panel h3 {{ margin: 0 0 9px; font-family: var(--moss-font-display); color: var(--moss-color-primary); }}
.note-panel p {{ margin: 0; color: var(--ink-soft); font-size: 13px; }}
.signal-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }}
.signal {{ background: var(--moss-color-surface); border: 1px solid var(--line); border-top: 3px solid var(--forward); padding: 18px; min-height: 280px; }}
.signal-top {{ display: flex; justify-content: space-between; gap: 8px; align-items: start; }}
.signal-name {{ font-weight: 800; color: var(--moss-color-primary); line-height: 1.2; }}
.signal p {{ color: var(--ink-soft); font-size: 12px; margin: 15px 0 0; }}
.signal .stop {{ color: #8A3B27; border-top: 1px dashed #E7B0A1; padding-top: 12px; }}
.tag {{ display: inline-block; padding: 3px 7px; background: #E8E7E1; color: var(--ink-soft); font-size: 10px; font-weight: 800; border-radius: 2px; white-space: nowrap; }}
.tag.orange {{ background: #FBE4DC; color: #9B3C25; }}
.rule-box {{ margin-top: 22px; border: 1px dashed var(--forward); padding: 18px 20px; color: #7B3A28; background: #FFF8F5; font-size: 13px; }}
.segment-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 28px; }}
.segment {{ padding: 20px; background: var(--moss-color-surface); border-top: 4px solid var(--moss-color-primary); border-bottom: 1px solid var(--line); }}
.segment-name {{ font-family: var(--moss-font-display); color: var(--moss-color-primary); font-size: 23px; line-height: 1.15; margin-bottom: 15px; }}
.segment p {{ color: var(--ink-soft); font-size: 12px; margin: 10px 0 0; }}
.na {{ color: var(--forward); font-weight: 800; }}
.leading {{ color: var(--ok) !important; border-top: 1px dashed #A9C7BA; padding-top: 12px; }}
.transmission {{ min-width: 1040px; }}
.winner-strip {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: var(--line); margin-top: 28px; }}
.winner-strip > div {{ background: var(--moss-color-primary); color: #FFFDF8; padding: 28px; }}
.winner-strip > div + div {{ background: var(--forward); }}
.winner-label {{ display: block; font-size: 11px; letter-spacing: .12em; font-weight: 800; opacity: .8; margin-bottom: 9px; }}
.winner-strip strong {{ font-family: var(--moss-font-display); font-size: 30px; display: block; }}
.winner-strip p {{ color: #F7EDE8; font-size: 13px; margin-bottom: 0; }}
.company-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }}
.company-check {{ background: var(--moss-color-surface); border: 1px solid var(--line); padding: 22px; }}
.company-head {{ display: flex; justify-content: space-between; gap: 14px; align-items: start; border-bottom: 1px solid var(--line); padding-bottom: 14px; }}
.company-head h3 {{ margin: 0; color: var(--moss-color-primary); font-family: var(--moss-font-display); font-size: 22px; }}
.company-check p {{ font-size: 13px; color: var(--ink-soft); margin: 14px 0 0; }}
.company-check .risk {{ color: #8A3B27; }}
.dashboard-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--line); }}
.dashboard-col {{ background: var(--moss-color-surface); padding: 24px; min-height: 220px; }}
.dashboard-col:nth-child(2) {{ background: #F0F4F2; }}
.dashboard-col:nth-child(3) {{ background: #F5F0E9; }}
.dashboard-col:nth-child(4) {{ background: #FFF1EB; }}
.dashboard-col h3 {{ color: var(--moss-color-primary); font-family: var(--moss-font-display); font-size: 22px; margin: 0 0 15px; }}
.dashboard-col ul, .limitations {{ padding-left: 19px; margin: 0; color: var(--ink-soft); font-size: 13px; }}
.dashboard-col li, .limitations li {{ margin: 9px 0; }}
.section-limitations {{ background: #EFECE5; }}
.limitations {{ max-width: 860px; font-size: 14px; }}
.section-evidence {{ padding-bottom: 100px; }}
.evidence-list {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.evidence-item {{ background: var(--moss-color-surface); border: 1px solid var(--line); padding: 20px; scroll-margin-top: 60px; }}
.evidence-head {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
.evidence-id {{ color: var(--forward); font-weight: 900; letter-spacing: .06em; }}
.confidence {{ color: var(--ink-soft); font-size: 11px; margin-left: auto; }}
.evidence-item h3 {{ color: var(--moss-color-primary); font-size: 16px; line-height: 1.3; margin: 12px 0 9px; }}
.evidence-item p {{ color: var(--ink-soft); font-size: 12px; margin: 7px 0; }}
.source-link {{ margin-top: 12px; color: var(--forward); font-size: 12px; font-weight: 800; }}
.source-link a {{ text-decoration: none; }}
.local-source {{ color: var(--ink-soft); font-weight: 600; }}
.footer {{ background: var(--moss-color-primary); color: #D9DEEA; padding: 26px 28px; font-size: 12px; }}
.footer-inner {{ max-width: 1240px; margin: 0 auto; display: flex; justify-content: space-between; gap: 20px; }}
@media (max-width: 980px) {{
  .hero-grid, .thesis, .two-column, .winner-strip {{ grid-template-columns: 1fr; }}
  .hero-meta, .window {{ border-left: 0; border-top: 1px solid rgba(255,255,255,.2); }}
  .metric-grid, .segment-grid, .dashboard-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .signal-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .evidence-list, .company-grid {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 640px) {{
  .hero {{ padding: 54px 20px 48px; }}
  .wrap {{ padding: 0 20px; }}
  .nav {{ padding-left: 20px; }}
  .hero h1 {{ font-size: 43px; }}
  .section {{ padding: 54px 0; }}
  .metric-grid, .segment-grid, .signal-grid, .dashboard-grid {{ grid-template-columns: 1fr; }}
  .thesis {{ margin-top: -18px; }}
  .footer-inner {{ display: block; }}
}}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} * {{ animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }} }}
</style>
</head>
<body>
<header class="topbar"><nav class="nav" aria-label="章节导航">{nav}</nav></header>
<header class="hero"><div class="hero-grid"><div><span class="eyebrow">投资研究 / GLOBAL BIOTECH FINANCING × CHINA CXO</span><h1>{esc(content["title"])}</h1><p class="subtitle">{esc(content["subtitle"])}。截至 {esc(content["as_of"])}，严格区分已发生的历史事实与基于假设的前瞻判断。</p></div><div class="hero-meta"><div>研究范围</div><strong>{esc(content["scope"])}</strong><div style="margin-top:18px">决策场景</div><strong>{esc(content["decision_context"])}</strong></div></div></header>
<main class="wrap">
<section class="thesis" aria-label="核心判断"><div><span class="label">核心结论</span><strong>{esc(headline["conclusion"])}</strong><p>{esc(headline["confidence"])}</p></div><div><span class="label">前瞻窗口</span><strong>{esc(headline["forecast"])}</strong><p>仅在融资、退出和宏观条件满足时成立。</p></div><div><span class="label">传导排序</span><strong>最快：{esc(headline["fastest_beneficiary"])}</strong><p>最大弹性：{esc(headline["highest_elasticity"])}</p></div></section>
{section_html}
{evidence_section()}
</main>
<footer class="footer"><div class="footer-inner"><span>产业链投研 · 全球创新药融资周期与中国 CXO</span><span>研究时点：{esc(content["as_of"])} · 仅作研究参考，不构成个性化投资建议</span></div></footer>
</body>
</html>
'''
OUTPUT_PATH.write_text(html_doc, encoding="utf-8")
print(f"wrote {OUTPUT_PATH}")

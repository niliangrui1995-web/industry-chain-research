# -*- coding: utf-8 -*-
"""重写为「明日盯盘视角」：生成新的 HTML body + md 报告。"""
import os, json, html

OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921'
OUT = r'D:/vcp_hunter/产业链投研/deliverables/technical-analyst/2026-09-21'
NX = json.load(open(os.path.join(OUTDIR, 'nextday.json'), encoding='utf-8'))
LAB = json.load(open(os.path.join(OUTDIR, 'labeled.json'), encoding='utf-8'))
rows = {r['full']: r for r in LAB['rows']}
byblk = {}
for r in LAB['rows']:
    byblk.setdefault(r['block'], []).append(r)
for k in byblk:
    byblk[k].sort(key=lambda x: x['full'])

AS_OF = '2026-09-21'
E = lambda s: html.escape(str(s))
TREND = {'up': '多头', 'down': '空头', 'range': '震荡', 'n/a': '不足'}
WTXT = {'up': '周线多头', 'down': '周线空头', 'range': '周线震荡', 'n/a': '周线不足'}

# ===== 明日盯盘名单（人工复核后定稿）=====
PICK = {
    '关注个股': {
        '明日核心盯盘': ['SZ002653', 'SH688617', 'SH688331'],
        '次日次级观察': ['SZ300298', 'SH601699', 'SH688235'],
        '煤炭组同步临界': ['SH600188', 'SH601225', 'SH601898'],
    },
    'AI硬件': {
        '明日核心盯盘': ['SH600487', 'SZ002463', 'SZ300408'],
        '次日次级观察': ['SZ300308', 'SH601208', 'SH688008'],
    },
}
RISK = {
    '关注个股': [('SZ000504', '南华生物', '一字涨停 + 向上跳空 + 20 日新高，但 60 日区间 100%、J 112.1，已是极端读数，明日只有"连板或炸板"两种结果'),
                 ('SH688621', '阳光诺和', '压力位前的十字星（+长下影），pos60 98.6% 贴顶，属高位犹豫信号'),
                 ('SZ000739', '普洛药业', '距压力仅 +0.12% 但 pos60 99.3%，连涨 4 日，临界与透支并存')],
    'AI硬件': [('BJ920045', '蘅东光', '高位看跌吞没 + KDJ 临界死叉（K−D=−6.9）+ 距压力仅 +0.32%，明日向下概率信号'),
               ('SZ002415', '海康威视', '距支撑 32.21 仅 −1.15%，看跌吞没，pos60 6.8%，是破位临界'),
               ('SZ002080', '中材科技', '+10.00% 大阳 + 连涨 9 日 + BIAS20 25.38%，透支最严重')],
}
REASON = {
    'SZ002653': ('昨日 +6.07% 并留下向上跳空（缺口 0.08%，64.09 未回补），量比 2.01 放量，'
                 'MACD 柱已收敛到绝对值占比 0.014 的临界值——明日柱体翻正即为确认；'
                 '上方压力 68.5（+1.63%）、下方支撑 67.38（−0.03%）贴身，是明日最可能给出方向的一只。'),
    'SH688617': ('昨日收出孕线（变盘 K 线）＋量比 1.62 放量，KDJ 的 K−D 仅 2.7 处于金叉/死叉临界，'
                 '且距支撑 240.04 仅 −1.44%。关键在 MA20 245.19 就在头顶（现价 243.49）——'
                 '明日能否收复 MA20 是这只票最直接的方向判据。'),
    'SH688331': ('昨日 +8.85% 大阳、量比 1.95，MACD 已零下金叉；收盘 125.00 恰好卡在双重临界上：'
                 '压力 125.66（+0.53%）与 MA60 125.14（+0.11%）几乎重合——明日站上即同时突破压力位与年线级别的 MA60，'
                 '位置仍在 60 日区间 35.6% 的低位，代价可控。'),
    'SZ300298': ('连涨 6 日、昨日大阳 +5.18%、量比 1.86，距压力 16.53 仅 +0.55%；'
                 '优点是 ATR 仅 2.31%（波动最小），风险是连涨 6 日后回踩概率上升。'),
    'SH601699': ('煤炭组代表：日线空头动能收敛，距压力 15.67 仅 +0.38%，KDJ 的 K−D 仅 2.1 处金叉临界，J 值 18.8 在低位。'),
    'SH688235': ('量比 1.78 放量、MACD 柱收敛至占比 0.005 的临界（随时可能翻正），连涨 3 日；'
                 '上下各有约 1.7% 空间（压 272.24 / 支 263.11），属区间中枢待方向。'),
    'SH600188': ('昨日看涨吞没，KDJ 的 K−D 仅 1.0 处金叉临界，J 值 19.5 低位；BIAS20 −4.66% 已在均线下方——'
                 '煤炭组 4 只同步出现该结构。'),
    'SH601225': ('昨日看涨吞没，K−D 仅 0.2（几乎重合，临界度最高），J 值 29.2；MACD 空头动能收敛。'),
    'SH601898': ('昨日看涨吞没但收放量下跌，K−D 1.3 处临界，J 值 20.2 低位；方向尚未确认，需次日验证。'),
    'SH600487': ('昨日留下向上跳空（缺口 0.34%，70.94 未回补）＋收出十字星带长上影——'
                 '跳空后的十字星是最典型的"次日方向选择"信号；距压力 72.21 仅 +0.64%，'
                 '且位置仍在 60 日区间 38.5% 的低位，量能趋势 1.25 温和放大。'),
    'SZ002463': ('距压力 126.18 仅 +0.14%，为全板块最贴身的临界位；昨日收十字星＋长下影＋孕线（三重变盘形态），'
                 'KDJ 的 K 已在 D 下方（K−D=−6.5）——形态与指标同时处于临界，明日必给方向。'),
    'SZ300408': ('昨日放量（量比 1.29）却收跌 −0.86%，距压力 131.23 仅 +1.07%，KD−D 差 −1.1 处死叉临界——'
                 '放量不涨＋指标临界，是明日最需要验证的一只；支撑 120.02 与 MA60 重合。'),
    'SZ300308': ('昨日十字星带长上影，距压力 949.73 仅 +0.93%，BOLL 位置 94.5% 已贴上轨，连涨 2 日；'
                 '位置低（60 日区间 28.3%）是优势，贴上轨是代价。'),
    'SH601208': ('昨日长上影＋孕线，距压力 52.89 仅 +0.27%，量能趋势 1.3 温和放大，K−D 差 4.3 接近临界。'),
    'SH688008': ('昨日向上跳空（缺口 0.66%，205.50 未回补）＋十字星带长下影，连涨 2 日，'
                 '位置极低（60 日区间 19.6%），是低位跳空待确认的结构。'),
}


def card(code):
    d = NX[code]
    c = d['candle']
    ctxt = '＋'.join(c) if c else '无特殊形态'
    gap = f"{d['gap'][0]} {d['gap'][2]}（{d['gap'][1]}%）" if d['gap'] else '无缺口'
    up = '看多' if d['chg1'] > 0 else ('看空' if d['chg1'] < 0 else '中性')
    chips = [
        ('收盘', f"{d['close']}"), ('昨日', f"{d['chg1']}%"), ('距压力', f"+{d['res_space']}%"),
        ('距支撑', f"-{d['sup_space']}%"), ('量比5', f"{d['vr5']}"), ('量比20', f"{d['vr20']}"),
        ('K−D', f"{d['kd_gap']}"), ('J值', f"{d['j']}"), ('BOLL位置', f"{d['boll_pos']}%"),
        ('RSI14', f"{d['rsi14']}"), ('ATR%', f"{d['atr_pct']}%"), ('60日位置', f"{d['pos60']}%"),
    ]
    chip_html = ''.join(
        f'<span class="chip{"warn" if k in ("距压力","ATR%","BOLL位置") else ("good" if k in ("距支撑","量比5") else "")}">'
        f'{E(k)} <b>{E(v)}</b></span>' for k, v in chips)
    return f'''<div class="dim">
  <div class="idxnum">{E(code[2:])}</div>
  <div class="dimmain">
    <div class="dimrow"><span class="dot r"></span><span class="dn">{E(d['name'])}</span>
      <span class="code" style="font-size:12px;color:var(--text-muted);font-family:ui-monospace,monospace">{E(code)}</span>
      <span class="pill {'r' if up=='看多' else ('g' if up=='看空' else 'n')}">{E(up)}</span>
      <span class="pill n">{E(ctxt)}</span>
      <span class="pill n">{E(gap)}</span></div>
    <div class="dd"><b>明日判据：{E('站上 ' + str(d['res_near']) if d['res_space'] and d['res_space'] < 2 else '守 ' + str(d['sup_near']))}
      是方向确认点；破 {E(str(d['sup_near']))} 则信号失效</b></div>
    <div class="data">{chip_html}</div>
    <div class="dd">{E(REASON.get(code, ''))}</div>
    <div class="dd" style="color:var(--text-muted)">连续：涨 {d['consec_up']} 日 / 跌 {d['consec_dn']} 日｜
      MA20 {d['ma20']}｜{E(d['mom_d'])}｜{E(d['volprice'])}</div>
  </div>
</div>'''


def table_for(blk):
    head = ('<tr style="background:var(--bg-elevated)">'
            '<th style="padding:6px 8px;text-align:left">代码</th><th style="padding:6px 8px;text-align:left">名称</th>'
            '<th style="padding:6px 8px;text-align:right">收盘</th><th style="padding:6px 8px;text-align:right">5日%</th>'
            '<th style="padding:6px 8px;text-align:right">20日%</th><th style="padding:6px 8px;text-align:left">趋势</th>'
            '<th style="padding:6px 8px;text-align:left">量价</th><th style="padding:6px 8px;text-align:left">MACD</th>'
            '<th style="padding:6px 8px;text-align:left">周线</th><th style="padding:6px 8px;text-align:right">60日位置</th>'
            '<th style="padding:6px 8px;text-align:right">BIAS20</th><th style="padding:6px 8px;text-align:right">RSI</th>'
            '<th style="padding:6px 8px;text-align:right">J</th><th style="padding:6px 8px;text-align:right">量比5</th>'
            '<th style="padding:6px 8px;text-align:right">压力</th><th style="padding:6px 8px;text-align:right">支撑</th></tr>')
    trs = []
    for r in byblk[blk]:
        i, l = r['ind'], r['lab']
        clr = 'color:var(--up)' if (i['chg5'] or 0) > 0 else ('color:var(--dn)' if (i['chg5'] or 0) < 0 else '')
        trs.append(
            f'<tr style="border-top:1px solid var(--border)">'
            f'<td style="padding:5px 8px;font-family:ui-monospace,monospace;font-size:12px">{E(r["full"])}</td>'
            f'<td style="padding:5px 8px">{E(r["name"])}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{i["close"]}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums;{clr}">{i["chg5"]}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{i["chg20"]}</td>'
            f'<td style="padding:5px 8px;font-size:12px">{E(TREND[l["trend_d"]])}</td>'
            f'<td style="padding:5px 8px;font-size:12px">{E(l["volprice"])}</td>'
            f'<td style="padding:5px 8px;font-size:12px">{E(l["mom_d"])}</td>'
            f'<td style="padding:5px 8px;font-size:12px">{E(WTXT[l["trend_w"]])}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{i["pos60"]}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{l["bias20"]}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{i["rsi14"]}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{i["kdj"]["j"]}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{i["vr5"]}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{l["res_near"]}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{l["sup_near"]}</td></tr>')
    return (f'<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:13px">'
            f'<thead>{head}</thead><tbody>{"".join(trs)}</tbody></table></div>')


IDX = LAB['index']
idx_rows = ''.join(
    f'<tr style="border-top:1px solid var(--border)"><td style="padding:5px 8px">{E(k)}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["close"]}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["ma20"]}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["ma60"]}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["chg5"]}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["macd"][2]}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["vr5"]}</td></tr>'
    for k, v in IDX.items())


def risk_block(blk):
    return ''.join(
        f'<li style="margin:4px 0"><b>{E(n)}</b>（{E(c)}）：{E(t)}</li>' for c, n, t in RISK[blk])


BODY = f'''<div class="wrap">

<section class="hdr">
  <div class="hdr-row1">
    <span class="hero-tag">明日盯盘</span>
    <h1>关注个股 &amp; AI硬件 · 明日盯盘名单<span class="code">126 只 / {AS_OF} 收盘</span></h1>
  </div>
  <div class="hdr-row2">
    <span>数据源：通达信本地 vipdoc 日线（前复权处理）</span><span class="dot-sep"></span>
    <span>数据截至 {AS_OF} 收盘</span><span class="dot-sep"></span>
    <span>交易日历完整性校验：126/126 通过</span>
  </div>
</section>

<section id="conclusion" class="sec" data-nav="核心结论">
  <div class="sec-head"><div class="sec-num">01</div><div class="sec-t">核心结论（明日盯盘视角）</div>
    <div class="sec-q">本报告不预测"明天谁涨"，只挑出"明天最可能给出方向性信号"的标的</div></div>
  <div class="tags">
    <span class="tag">关注个股：海思科 / 惠泰医疗 三重临界</span>
    <span class="tag">AI硬件：亨通光电 跳空＋十字星</span>
    <span class="tag">煤炭 4 只同步临界（板块级）</span>
  </div>
  <div class="lead">
    <b>先说清楚一件事</b>：本项目此前的 IC 回测已证明，<b class="g">1 日维度上所有技术特征的预测力 |IC| 均 &lt; 0.06，属噪声级别</b>。
    所以"明日最值得关注"在这里的定义不是"预测明天涨得最多"，而是：<b class="r">明日最可能给出方向性信号（突破 / 破位 / 指标翻转）的标的</b>——
    即临界度最高、最值得盯盘的那一批。盯的是"信号是否出现"，不是"涨跌结果"。<br><br>
    <b>明日盯盘三条主线</b>：<br>
    ① <b>关注个股</b>——<b>海思科</b>（跳空＋放量＋MACD 柱临界翻正＋压力位贴身）、<b>惠泰医疗</b>（孕线＋放量＋KDJ 临界＋头顶 MA20）、
    <b>荣昌生物</b>（压力 125.66 与 MA60 125.14 双重临界重合）。<br>
    ② <b>AI硬件</b>——<b>亨通光电</b>（向上跳空未回补＋十字星长上影＋距压力 0.64%）、<b>沪电股份</b>（距压力仅 0.14%＋十字星孕线三重变盘形态）、
    <b>三环集团</b>（放量却收跌＋KDJ 临界死叉）。<br>
    ③ <b>板块级同步</b>——关注个股里的<b>煤炭 4 只（兖矿、陕煤、中煤、潞安）同日出现"看涨吞没＋KDJ 临界金叉"</b>，
    J 值均在 18–29 的低位，是本次扫描中唯一出现板块共振的临界信号。
  </div>
  <div class="q3" style="margin-top:14px">
    <div class="q"><div class="ttl">① 明日最该盯哪几只？</div><div class="ans">关注个股看海思科、惠泰医疗、荣昌生物；AI硬件看亨通光电、沪电股份、三环集团。</div></div>
    <div class="q"><div class="ttl">② 盯的具体是什么？</div><div class="ans">临界压力位能否站上、支撑能否守住，以及 MACD 柱 / KDJ 是否翻转。</div></div>
    <div class="q"><div class="ttl">③ 最大的陷阱是什么？</div><div class="ans">南华生物一字板（60日区间100%）、中材科技连涨9日（BIAS 25.4%）——临界不等于安全。</div></div>
  </div>
  <div class="verdict"><b>口径声明：</b>以下名单的排序依据是"临界度"（同时命中临界位、量能异动、指标临界、变盘 K 线、缺口等条件中的几项），
  <b>不是对明日涨幅的预测排名</b>，也不做任何综合评分。每只都列出了"明日确认点"与"失效位"，信号出现与否由盘面给出。</div>
</section>

<section id="market" class="sec" data-nav="大盘背景">
  <div class="sec-head"><div class="sec-num">02</div><div class="sec-t">大盘背景（同日收盘）</div>
    <div class="sec-q">主要指数处于中期调整后的修复反弹，成长风格本周领涨</div></div>
  <div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:13px">
    <thead><tr style="background:var(--bg-elevated)">
      <th style="padding:6px 8px;text-align:left">指数</th><th style="padding:6px 8px;text-align:right">收盘</th>
      <th style="padding:6px 8px;text-align:right">MA20</th><th style="padding:6px 8px;text-align:right">MA60</th>
      <th style="padding:6px 8px;text-align:right">5日%</th><th style="padding:6px 8px;text-align:right">MACD柱</th>
      <th style="padding:6px 8px;text-align:right">量比5</th></tr></thead>
    <tbody>{idx_rows}</tbody></table></div>
  <div class="note">五大指数全线站上 MA20；深成指、创业板指、科创50、中证1000 日线 MACD 柱已翻正（上证仍为负但收敛）。
  科创50 近 5 日 +8.45% 领涨，成长风格占优。</div>
</section>

<section id="pick-gz" class="sec" data-nav="关注个股·明日名单">
  <div class="sec-head"><div class="sec-num">03</div><div class="sec-t">「关注个股」明日盯盘名单</div>
    <div class="sec-q">排序依据＝临界度（命中条件数），非涨幅预测</div></div>
  <div class="dimlist">
    {card("SZ002653")}
    {card("SH688617")}
    {card("SH688331")}
  </div>
  <div style="font-size:13px;color:var(--text-muted);margin:14px 0 6px">次级观察（临界度 2 项）</div>
  <div class="dimlist">
    {card("SZ300298")}
    {card("SH688235")}
    {card("SH601699")}
  </div>
  <div style="font-size:13px;color:var(--text-muted);margin:14px 0 6px">煤炭组：4 只同步"看涨吞没＋KDJ 临界金叉"（板块级共振）</div>
  <div class="dimlist">
    {card("SH601225")}
    {card("SH600188")}
    {card("SH601898")}
  </div>
</section>

<section id="pick-ai" class="sec" data-nav="AI硬件·明日名单">
  <div class="sec-head"><div class="sec-num">04</div><div class="sec-t">「AI硬件」明日盯盘名单</div>
    <div class="sec-q">排序依据＝临界度（命中条件数），非涨幅预测</div></div>
  <div class="dimlist">
    {card("SH600487")}
    {card("SZ002463")}
    {card("SZ300408")}
  </div>
  <div style="font-size:13px;color:var(--text-muted);margin:14px 0 6px">次级观察（临界度 2 项）</div>
  <div class="dimlist">
    {card("SZ300308")}
    {card("SH601208")}
    {card("SH688008")}
  </div>
</section>

<section id="roadmap" class="sec" data-nav="明日盘中路标">
  <div class="sec-head"><div class="sec-num">05</div><div class="sec-t">明日盘中路标</div>
    <div class="sec-q">只描述"信号出现意味着什么"，不构成任何买卖建议</div></div>
  <div class="roadmap">
    <div class="road up"><div class="roadhd"><span class="roadtag up">向上确认</span></div>
      <div class="roadcond">若 <b>海思科站上 68.5</b>、<b>亨通光电站上 72.21</b>、<b>沪电股份站上 126.18</b></div>
      <div class="roadbody">意味着跳空/临界位被量能确认，属于形态层面的突破成立；
      下一观察位分别是 <b>海思科 70 一线、亨通 76 一线、沪电 130 一线</b>，并同步看 MACD 柱是否由负转正。</div></div>
    <div class="road down"><div class="roadhd"><span class="roadtag down">向下失效</span></div>
      <div class="roadcond">若 <b>海思科跌破 67.38</b>、<b>惠泰医疗跌破 240.04</b>、<b>沪电股份跌破 122.25</b></div>
      <div class="roadbody">意味着昨日形态（跳空 / 孕线 / 十字星）演变为假信号，临界突破失败；
      下一观察位看各自 MA20（<b>海思科 65.33、惠泰 245.19、沪电 122.64</b>）能否收复。</div></div>
  </div>
  <div class="roadtip">煤炭组共同判据：4 只的 KDJ 均已到金叉临界（K−D 分别 0.2 / 1.0 / 1.3 / 2.1），
  明日<b>任一只 KD 金叉成立</b>都可视作板块级信号的第一次验证；失效位看各自近期低点（潞安 14.40、兖矿 18.91、陕煤 25.26、中煤 13.74）。</div>
</section>

<section id="risk" class="sec" data-nav="明日风险观察">
  <div class="sec-head"><div class="sec-num">06</div><div class="sec-t">明日高风险观察位（临界 ≠ 安全）</div>
    <div class="sec-q">这几只明日必然给方向，但读数是极端或恶化的</div></div>
  <div style="margin-bottom:10px"><div style="font-weight:600;margin-bottom:4px">关注个股</div>
    <ul style="margin:0;padding-left:20px;font-size:13.5px">{risk_block('关注个股')}</ul></div>
  <div><div style="font-weight:600;margin-bottom:4px">AI硬件</div>
    <ul style="margin:0;padding-left:20px;font-size:13.5px">{risk_block('AI硬件')}</ul></div>
</section>

<section id="list-gz" class="sec" data-nav="关注个股·完整清单">
  <div class="sec-head"><div class="sec-num">07</div><div class="sec-t">「关注个股」完整清单（42 只）</div>
    <div class="sec-q">按代码排序，全部指标取自 2026-09-21 收盘的本地日线</div></div>
  {table_for("关注个股")}
</section>

<section id="list-ai" class="sec" data-nav="AI硬件·完整清单">
  <div class="sec-head"><div class="sec-num">08</div><div class="sec-t">「AI硬件」完整清单（84 只）</div>
    <div class="sec-q">含 1 只 ETF（SH515880 通信ETF国泰）与 1 只次新股（SH688825 长鑫科技，样本不足不参与筛选）</div></div>
  {table_for("AI硬件")}
</section>

<section id="method" class="sec" data-nav="口径与方法">
  <div class="sec-head"><div class="sec-num">09</div><div class="sec-t">数据口径与方法说明</div></div>
  <div class="lead" style="font-size:14px">
    <b>数据来源</b>：通达信安装目录 D:\\HT 的本地日线（vipdoc\\sh|sz|bj\\lday\\*.day，32 字节定长二进制），
    共 126 只全部读取成功，最后交易日均为 2026-09-21；板块成分取自 T0002\\blocknew\\GZGG.blk（关注个股）与 AIYJ.blk（AI硬件），
    名称取自 T0002\\hq_cache 的 shs/szs/bjs.tnf。<br><br>
    <b>复权处理</b>：本地日线为不复权数据，已逐只检测超过各板块涨跌幅限制的跳空（主板10.5%、科创创业20.5%、北交所30.5%）并做前复权，
    共 16 只检测到除权事件。<br><br>
    <b>完整性校验</b>：以全市场并集交易日历为基准比对最近 130 个交易日，126 只中仅 5 只缺数且均为真实停牌或次新
    （有研硅停牌 10 日、长鑫科技上市不足半年样本仅 40 根等），非取数缺陷。<br><br>
    <b>明日临界度的六个条件</b>：① 距压力或支撑 ≤1.5%；② 量比5 ≥1.5 或 ≤0.6；③ KDJ 的 K−D 绝对值 ≤3 或 MACD 柱绝对值占比 ≤3%；
    ④ 出现变盘 K 线（十字星 / 吞没 / 孕线 / 长影线）；⑤ 存在未回补跳空缺口；⑥ 创 20 日新高或新低。命中越多，明日越可能给方向。<br><br>
    <b>指标参数</b>：MA5/10/20/30/60/120/250；MACD(12,26,9)，柱＝(DIF−DEA)×2；RSI(6/14) Wilder 平滑；KDJ(9,3,3)；
    BOLL(20,2)；ATR(14)；量比＝当日量 / 近 5 日均量。<br><br>
    <b>关于"不打分"</b>：本报告不做任何综合评分与分数排名，也不预测明日涨跌。入选依据是上述定性条件的临界度叠加，
    每只都给出"确认点"与"失效位"。<br><br>
    <b>已知局限</b>：本周仅 1 个交易日（周一），周线最后一根 K 线不完整，故周线量能指标不采用；
    不含换手率与筹码分布（本地数据无流通股本与成本分布）；不含资金流向（大单分类口径不可靠，不采用）。
  </div>
  <div class="verdict"><b>特别提示：</b>1 日维度的技术指标预测力已被本项目回测证伪（|IC| &lt; 0.06）。
  本报告只提供"明日最值得盯什么、盯到什么算数"，不提供涨跌判断。</div>
</section>

</div>'''

open(os.path.join(OUT, 'panel.body.html'), 'w', encoding='utf-8').write(BODY)
print('body written', len(BODY))

# ===== md =====
def md_table(blk):
    out = ['| 代码 | 名称 | 收盘 | 5日% | 20日% | 趋势 | 量价 | MACD | 周线 | 60日位置 | BIAS20 | RSI | J | 量比5 | 压力 | 支撑 |',
           '|---|---|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in byblk[blk]:
        i, l = r['ind'], r['lab']
        out.append(f"| {r['full']} | {r['name']} | {i['close']} | {i['chg5']} | {i['chg20']} | {TREND[l['trend_d']]} | "
                   f"{l['volprice']} | {l['mom_d']} | {WTXT[l['trend_w']]} | {i['pos60']} | {l['bias20']} | "
                   f"{i['rsi14']} | {i['kdj']['j']} | {i['vr5']} | {l['res_near']} | {l['sup_near']} |")
    return '\n'.join(out)


def md_card(code):
    d = NX[code]
    ctxt = '＋'.join(d['candle']) if d['candle'] else '无特殊形态'
    gap = f"{d['gap'][0]}（缺口位 {d['gap'][2]}，{d['gap'][1]}%）" if d['gap'] else '无缺口'
    return (f"**{d['name']}（{code}）** 收 {d['close']}｜昨日 {d['chg1']}%\n"
            f"- 临界位：压力 **{d['res_near']}**（+{d['res_space']}%）｜支撑 **{d['sup_near']}**（-{d['sup_space']}%）\n"
            f"- 昨日形态：{ctxt}｜缺口：{gap}｜连涨 {d['consec_up']} 日 / 连跌 {d['consec_dn']} 日\n"
            f"- 读数：量比5 **{d['vr5']}**｜量比20 {d['vr20']}｜KDJ K−D **{d['kd_gap']}**｜J {d['j']}｜"
            f"BOLL 位置 {d['boll_pos']}%｜RSI {d['rsi14']}｜ATR {d['atr_pct']}%｜60日位置 {d['pos60']}%\n"
            f"- 入选理由：{REASON.get(code, '')}\n")


def md_pick(blk):
    s = ''
    for tier in PICK[blk]:
        s += f'\n#### {tier}\n\n'
        for c in PICK[blk][tier]:
            s += md_card(c) + '\n'
    return s


idx_md = '\n'.join(f"| {k} | {v['close']} | {v['ma20']} | {v['ma60']} | {v['chg5']} | {v['macd'][2]} | {v['vr5']} |"
                   for k, v in IDX.items())
risk_md = ''
for blk in RISK:
    risk_md += f'\n**{blk}**\n' + '\n'.join(f'- **{n}**（{c}）：{t}' for c, n, t in RISK[blk]) + '\n'

MD = f"""# 关注个股 & AI硬件 · 明日盯盘名单（{AS_OF} 收盘）

> 数据源：通达信本地日线 `D:\\HT\\vipdoc`（前复权处理）｜板块成分：`T0002\\blocknew\\GZGG.blk`（关注个股）、`AIYJ.blk`（AI硬件）
> 覆盖 126 只，全部读取成功，最后交易日均为 {AS_OF}；交易日历完整性校验通过

---

## 一、核心结论（明日盯盘视角）

**先说清楚一件事**：本项目此前的 IC 回测已证明，**1 日维度上所有技术特征的预测力 |IC| 均 < 0.06，属噪声级别**。
所以"明日最值得关注"在这里的定义不是"预测明天涨得最多"，而是：**明日最可能给出方向性信号（突破 / 破位 / 指标翻转）的标的**——即临界度最高、最值得盯盘的那一批。盯的是"信号是否出现"，不是"涨跌结果"。

### 明日盯盘三条主线

1. **关注个股**：**海思科**（跳空＋放量＋MACD 柱临界翻正＋压力位贴身）、**惠泰医疗**（孕线＋放量＋KDJ 临界＋头顶 MA20）、**荣昌生物**（压力 125.66 与 MA60 125.14 双重临界重合）。
2. **AI硬件**：**亨通光电**（向上跳空未回补＋十字星长上影＋距压力 0.64%）、**沪电股份**（距压力仅 0.14%＋十字星/长下影/孕线三重变盘形态）、**三环集团**（放量却收跌＋KDJ 临界死叉）。
3. **板块级同步**：关注个股里的**煤炭 4 只（兖矿、陕煤、中煤、潞安）同日出现"看涨吞没＋KDJ 临界金叉"**，J 值均在 18–29 的低位——本次扫描中唯一出现板块共振的临界信号。

### 大盘背景（同日收盘）

| 指数 | 收盘 | MA20 | MA60 | 5日% | MACD柱 | 量比5 |
|---|---:|---:|---:|---:|---:|---:|
{idx_md}

五大指数全线站上 MA20；深成指、创业板指、科创50、中证1000 日线 MACD 柱已翻正（上证仍为负但收敛）。科创50 近 5 日 **+8.45%** 领涨。

---

## 二、「关注个股」明日盯盘名单
{md_pick('关注个股')}
---

## 三、「AI硬件」明日盯盘名单
{md_pick('AI硬件')}
---

## 四、明日盘中路标（只描述信号含义，不构成买卖建议）

| 情景 | 触发条件 | 意味着什么 | 下一观察位 |
|---|---|---|---|
| 向上确认 | **海思科站上 68.5**、**亨通光电站上 72.21**、**沪电股份站上 126.18** | 跳空/临界位被量能确认，形态层面的突破成立 | 海思科 70 一线、亨通 76 一线、沪电 130 一线，并看 MACD 柱是否由负转正 |
| 向下失效 | **海思科跌破 67.38**、**惠泰医疗跌破 240.04**、**沪电股份跌破 122.25** | 昨日形态（跳空/孕线/十字星）演变为假信号，临界突破失败 | 看各自 MA20（海思科 65.33、惠泰 245.19、沪电 122.64）能否收复 |
| 煤炭组验证 | 4 只 KDJ 已在金叉临界（K−D 分别 0.2 / 1.0 / 1.3 / 2.1） | 任一只 KD 金叉成立即为板块级信号的第一次验证 | 失效位：潞安 14.40、兖矿 18.91、陕煤 25.26、中煤 13.74 |

---

## 五、明日高风险观察位（临界 ≠ 安全）
{risk_md}
---

## 六、「关注个股」完整清单（42 只）

{md_table('关注个股')}

> 注：`XD皓元医`（SH688131）为除息日通达信名称前缀，即皓元医药。

---

## 七、「AI硬件」完整清单（84 只）

{md_table('AI硬件')}

> 注 1：`SH515880 通信ETF国泰` 为 ETF，非个股，不参与筛选。
> 注 2：`SH688825 长鑫科技` 上市不足半年，样本仅 40 根，MA60 与周线不可算，不参与筛选。
> 注 3：`XD柏诚股`（SH601133）为除息日名称前缀，即柏诚股份。

---

## 八、数据口径与方法

- **数据来源**：通达信安装目录 `D:\\HT` 的本地日线（`vipdoc\\sh|sz|bj\\lday\\*.day`，32 字节定长二进制）；板块成分取自 `T0002\\blocknew\\GZGG.blk` 与 `AIYJ.blk`；名称取自 `T0002\\hq_cache` 的 `shs/szs/bjs.tnf`。
- **复权处理**：本地日线为不复权数据，已逐只检测超过各板块涨跌幅限制的跳空（主板 10.5%、科创创业 20.5%、北交所 30.5%）并做前复权，共 16 只检测到除权事件。
- **完整性校验**：以全市场并集交易日历为基准比对最近 130 个交易日，126 只中仅 5 只缺数且均为真实停牌或次新，非取数缺陷。
- **明日临界度的六个条件**：① 距压力或支撑 ≤1.5%；② 量比5 ≥1.5 或 ≤0.6；③ KDJ 的 K−D 绝对值 ≤3 或 MACD 柱绝对值占比 ≤3%；④ 出现变盘 K 线（十字星/吞没/孕线/长影线）；⑤ 存在未回补跳空缺口；⑥ 创 20 日新高或新低。命中越多，明日越可能给方向。
- **指标参数**：MA5/10/20/30/60/120/250；MACD(12,26,9)，柱＝(DIF−DEA)×2；RSI(6/14) Wilder 平滑；KDJ(9,3,3)；BOLL(20,2)；ATR(14)；量比＝当日量÷近 5 日均量。
- **关于"不打分"**：本报告不做任何综合评分与分数排名，也不预测明日涨跌。入选依据是上述定性条件的临界度叠加，每只都给出"确认点"与"失效位"。
- **已知局限**：本周仅 1 个交易日（周一），周线最后一根 K 线不完整，故周线量能指标不采用；不含换手率与筹码分布；不含资金流向（大单分类口径不可靠，不采用）。

---

## 九、风险提示

1. **1 日预测无效**：本项目回测已证明 1 日口径下所有技术特征 |IC| < 0.06，本报告不预测明日涨跌，只标注"信号出现/失效"的观察位。
2. **临界不等于安全**：南华生物一字板后 60 日区间 100%、J 值 112；中材科技连涨 9 日、BIAS20 25.38%——这些标的明日必然给方向，但读数是极端的。
3. **量能不足**：AI硬件多只临界股处于缩量（沪电 0.95、中际旭创 0.91），无量突破的失败率偏高。
4. **波动风险**：入选标的中源杰科技、光智科技 ATR 分别 5.44%、8.37%，关键位易被瞬间穿越。
5. **口径风险**：本报告为纯技术面，未纳入基本面、消息面与政策面因素。

---

⚠️ 本分析由 AI 基于公开信息生成，仅依据价格、成交量等公开市场行为数据进行技术面研判，
不涉及基本面、消息面、政策面因素，不构成任何投资建议，不构成个股推荐。
技术分析有其固有局限性，过去的表现不代表未来走势。投资有风险，决策需谨慎。
"""

open(os.path.join(OUT, '关注个股与AI硬件-明日盯盘报告.md'), 'w', encoding='utf-8').write(MD)
print('md written', len(MD))

# -*- coding: utf-8 -*-
"""生成板块扫描看板的 body 片段（不含 html/head/style/nav/footer）。"""
import os, json, html

OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921'
OUT = r'D:/vcp_hunter/产业链投研/deliverables/technical-analyst/2026-09-21'
os.makedirs(OUT, exist_ok=True)

L = json.load(open(os.path.join(OUTDIR, 'labeled.json'), encoding='utf-8'))
PICKS = json.load(open(os.path.join(OUTDIR, 'final_picks.json'), encoding='utf-8'))
rows = L['rows']
byblk = {}
for r in rows:
    byblk.setdefault(r['block'], []).append(r)
for k in byblk:
    byblk[k].sort(key=lambda x: x['full'])

AS_OF = '2026-09-21'
E = lambda s: html.escape(str(s))

REASON = {
    'SH603259': 'MACD 在零轴上方新金叉、放量（量比1.4）配合，乖离仅6.8%未透支，是板块内形态最标准的趋势延续样本；压力 173.6 是下周唯一要盯的关口。',
    'SZ300759': '同为 MACD 零上金叉 + 放量，乖离 5.0% 为入选标的中最低，且距上方分形压力还有 13.7% 空间，位置与动量组合最优。',
    'SZ002821': '缩量回调（量比1.01）但价格守住 MA20 之上，属强势整理而非放量出逃；周线多头走强未被破坏。',
    'SZ300725': '放量上行、下方支撑 49.07 仅 2.55%（贴身支撑），上方空间 12.7%，风险收益结构清晰。',
    'SZ300298': '底部区域放量（量比1.86）且 MACD 日线、周线同步零下金叉，ATR 仅 2.31% 为本组最低，是小波动、低位置的反转型观察样本。',
    'SH688428': '日线 MACD 空头动能已收敛至临界、位置温和（乖离4.7%），同时放量1.77，属"动能待转正"的左侧观察位。',
    'SH688796': '趋势与动量俱佳，但 ATR 6.58%、乖离 11.3%，波动偏大，列备选。',
    'SZ301047': '动量与周线均好，但乖离 15.5%、ATR 7.19% 为入选组最高，波动风险最大，列备选。',
    'SH688131': '距压力仅 0.12% 的最临界位置，但已处 60 日区间 94% 高位，属"追临界"类型，列备选。',
    'SZ002463': '距上方分形压力仅 0.14%，为全板块最贴身的临界位；乖离 2.74%、KDJ-J 44.8 均处低位，属"低乖离 + 临界 + 指标未透支"的组合。',
    'SH600487': '位置仍在 60 日区间 38.5% 的低位，日线动能放大且距压力仅 0.64%，是"低位 + 临界突破"组合。',
    'SZ300408': '放量（量比1.29）上攻且距压力 1.07%，位置 47.8% 未透支，量价配合最扎实。',
    'SZ301205': 'MACD 零上金叉 + 周线多头走强，是 AI 硬件里少数周线已转多的标的，乖离 6.44% 温和。',
    'SZ300308': '处于 60 日区间 28.3% 的低位，日线动能放大且距压力 0.93%，属超跌后的临界修复。',
    'SH688498': '周线多头走强、日线动能放大，趋势结构完整；但已到 60 日区间 89.6%，需接受位置偏高的代价。',
    'SZ300476': '量比 1.83 为本组最大，属放量突破进行中；但上方压力还有 6.83%，需确认能否延续。',
    'SH688256': '位置极低（60日区间24.3%）、乖离仅 3.51%，属超跌修复类型；量能未放大，故列备选。',
    'SZ300489': 'MACD 零上金叉且位置居中，但 ATR 8.37% 为本组最高，波动过大，列备选。',
}

TREND_TXT = {'up': '日线多头', 'down': '日线空头', 'range': '日线震荡', 'n/a': '数据不足'}
WTXT = {'up': '周线多头', 'down': '周线空头', 'range': '周线震荡', 'n/a': '周线不足'}


def dot_pill(trend):
    return ('r', '看多') if trend == 'up' else (('g', '看空') if trend == 'down' else ('n', '中性'))


def pick_card(code):
    d = PICKS[code]
    dc, pc = dot_pill(d['trend_d'])
    chips = [
        ('收盘', f"{d['close']}"), ('MA20', f"{d['ma']['20']}"), ('MA60', f"{d['ma']['60']}"),
        ('压力', f"{d['res_near']} (+{d['res_space']}%)"), ('支撑', f"{d['sup_near']} (-{d['sup_space']}%)"),
        ('BIAS20', f"{d['bias20']}%"), ('RSI14', f"{d['rsi14']}"), ('KDJ-J', f"{d['kdj']['j']}"),
        ('量比5', f"{d['vr5']}"), ('ATR%', f"{d['atr_pct']}%"), ('60日位置', f"{d['pos60']}%"),
    ]
    chip_html = ''.join(
        f'<span class="chip{"warn" if k in ("压力","BIAS20","ATR%") else ("good" if k in ("支撑","量比5") else "")}">'
        f'{E(k)} <b>{E(v)}</b></span>' for k, v in chips)
    risks = '、'.join(d['risks']) if d['risks'] else '无极端读数'
    return f'''<div class="dim">
  <div class="idxnum">{E(code[2:])}</div>
  <div class="dimmain">
    <div class="dimrow"><span class="dot {dc}"></span><span class="dn">{E(d["name"])}</span>
      <span class="code" style="font-size:12px;color:var(--text-muted);font-family:ui-monospace,monospace">{E(code)}</span>
      <span class="pill {pc if pc!="看多" else "r"}">{E(pc)}</span>
      <span class="pill n">{E(d["mom_d"])}</span>
      <span class="pill n">{E(d["mom_w"])}</span></div>
    <div class="dd"><b>{E(d["volprice"])}，{E(TREND_TXT[d["trend_d"]])} / {E(WTXT[d["trend_w"]])}，{E(d["position"])}</b></div>
    <div class="data">{chip_html}</div>
    <div class="dd">{E(REASON.get(code, ""))}</div>
    <div class="dd" style="color:var(--text-muted)">风险标记：{E(risks)}｜周线 MACD 柱 {E(d["weekly"]["macd"]["hist"] if d["weekly"]["macd"] else "N/A")}</div>
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
            f'<td style="padding:5px 8px;font-size:12px">{E(TREND_TXT[l["trend_d"]])}</td>'
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


IDX = L['index']
idx_rows = ''.join(
    f'<tr style="border-top:1px solid var(--border)"><td style="padding:5px 8px">{E(k)}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["close"]}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["ma20"]}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["ma60"]}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["chg5"]}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["macd"][2]}</td>'
    f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{v["vr5"]}</td></tr>'
    for k, v in IDX.items())

AVOID = {
    '关注个股': [('SZ000504', '乖离MA20 27.6%、RSI 77、J 112，处60日区间最高点'),
                 ('SH688222', '乖离MA20 34.0%、RSI 76.4、J 111，四项超买读数叠加'),
                 ('SZ301080', '乖离MA20 30.6%、ATR 8.0%，透支最严重'),
                 ('SH688293', '乖离21.2%，贴60日高点(98.1%)'),
                 ('SZ000739', '60日区间99.3%，几乎无回旋空间'),
                 ('SH688621', '60日区间98.6%，贴顶'),
                 ('SH688758', '60日区间97.0%，贴顶'),
                 ('SH688271', '日线、周线双空头排列，60日区间14.8%'),
                 ('SH688578', '日线、周线双空头排列，60日区间10.5%'),
                 ('SH688016', '日线空头排列，MACD零下金叉未完成')],
    'AI硬件': [('SH688205', '乖离MA20 22.6%、60日区间99.4%，贴顶且超买'),
               ('SH688143', '60日区间97.7%、ATR 8.3%，波动与位置双高'),
               ('SZ002080', '乖离MA20 25.4%、RSI 72，短期拉升过快'),
               ('SZ002415', '日线周线双空头，RSI 34.7，60日区间6.8%')],
}
NAME = {r['full']: r['name'] for r in rows}
avoid_html = ''
for blk, items in AVOID.items():
    lis = ''.join(f'<li style="margin:4px 0"><b>{E(NAME[c])}</b>（{E(c)}）：{E(t)}</li>' for c, t in items)
    avoid_html += f'<div style="margin-bottom:10px"><div style="font-weight:600;margin-bottom:4px">{E(blk)}</div><ul style="margin:0;padding-left:20px;font-size:13.5px">{lis}</ul></div>'

BODY = f'''<div class="wrap">

<section class="hdr">
  <div class="hdr-row1">
    <span class="hero-tag">板块扫描</span>
    <h1>关注个股 &amp; AI硬件 · 技术面全景扫描<span class="code">126 只 / {AS_OF}</span></h1>
  </div>
  <div class="hdr-row2">
    <span>数据源：通达信本地 vipdoc 日线（前复权处理）</span><span class="dot-sep"></span>
    <span>数据截至 {AS_OF} 收盘</span><span class="dot-sep"></span>
    <span>交易日历完整性校验：126/126 通过</span>
  </div>
</section>

<section id="conclusion" class="sec" data-nav="核心结论">
  <div class="sec-head"><div class="sec-num">01</div><div class="sec-t">核心结论</div>
    <div class="sec-q">两个板块不在同一个中期阶段，策略含义完全不同</div></div>
  <div class="tags">
    <span class="tag">关注个股：中期多头延续期</span>
    <span class="tag">AI硬件：周线修复中的日线反弹</span>
    <span class="tag">共筛出 6+6 只重点观察</span>
  </div>
  <div class="lead">
    <b>「关注个股」</b>（42 只，医药 CXO 主导）：<b class="r">中期趋势最健康</b>——30 只日线多头、周线同步多头走强，
    日线 MACD 多头动能普遍放大，属趋势延续阶段；但隐患是<b class="r">位置普遍偏高</b>，7 只已贴 60 日区间最高点，短线追高代价大。<br><br>
    <b>「AI硬件」</b>（84 只）：<b class="g">周线仍未转多</b>——过半标的周线 MACD 仍在零下空头区收敛，日线却已普遍转为多头动能放大，
    属<b>周线级别调整中的日线反弹</b>；优势是位置普遍偏低（大量标的位于 60 日区间 20-40%），且 34 只已走到压力位 3% 以内的临界区，
    下周是"能否确认突破"的密集验证窗口。
  </div>
  <div class="q3" style="margin-top:14px">
    <div class="q"><div class="ttl">① 两个板块现在什么阶段？</div><div class="ans">关注个股＝趋势延续的中段；AI硬件＝周线修复的日线反弹初段。</div></div>
    <div class="q"><div class="ttl">② 下周最该盯什么？</div><div class="ans">关注个股盯"高位股回踩是否守住 MA20"；AI硬件盯"临界位能否放量突破"。</div></div>
    <div class="q"><div class="ttl">③ 最大的风险是什么？</div><div class="ans">关注个股是乖离透支（7 只贴顶）；AI硬件是周线未转多，日线反弹可能只是反抽。</div></div>
  </div>
  <div class="verdict"><b>矛盾裁决：</b>AI硬件日线动量普遍转正（看多）与周线仍处空头（看空）矛盾。按"长周期趋势 &gt; 量价 &gt; 形态 &gt; 指标"的优先级，
  <b>周线未转多前的日线信号只能定性为反弹而非反转</b>，故该板块入选标的以"低位 + 临界 + 低乖离"为筛选主轴，而非追最强动量。</div>
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
  <div class="note">五大指数全线站上 MA20；深成指、创业板指、科创50、中证1000 的日线 MACD 柱已翻正（金叉），上证仍为负但收敛。
  科创50 近 5 日 +8.45% 领涨，成长风格占优——这与"AI硬件周线待修复、日线先反弹"的板块读数一致。</div>
</section>

<section id="pick-gz" class="sec" data-nav="关注个股·名单">
  <div class="sec-head"><div class="sec-num">03</div><div class="sec-t">「关注个股」下周重点观察名单（6 只 + 3 只备选）</div>
    <div class="sec-q">筛选主轴：中期趋势不逆 + 动量向上 + 位置未透支 + 量价配合</div></div>
  <div class="dimlist">
    {pick_card("SH603259")}
    {pick_card("SZ300759")}
    {pick_card("SZ002821")}
    {pick_card("SZ300725")}
    {pick_card("SZ300298")}
    {pick_card("SH688428")}
  </div>
  <div style="font-size:13px;color:var(--text-muted);margin:14px 0 6px">备选（动量达标但波动或位置有代价）</div>
  <div class="dimlist">
    {pick_card("SH688796")}
    {pick_card("SZ301047")}
    {pick_card("SH688131")}
  </div>
</section>

<section id="pick-ai" class="sec" data-nav="AI硬件·名单">
  <div class="sec-head"><div class="sec-num">04</div><div class="sec-t">「AI硬件」下周重点观察名单（6 只 + 3 只备选）</div>
    <div class="sec-q">筛选主轴：低位 + 临界突破 + 低乖离（因周线未转多，不追最强动量）</div></div>
  <div class="dimlist">
    {pick_card("SZ002463")}
    {pick_card("SH600487")}
    {pick_card("SZ300408")}
    {pick_card("SZ301205")}
    {pick_card("SZ300308")}
    {pick_card("SH688498")}
  </div>
  <div style="font-size:13px;color:var(--text-muted);margin:14px 0 6px">备选（结构成立但量能或波动未确认）</div>
  <div class="dimlist">
    {pick_card("SZ300476")}
    {pick_card("SH688256")}
    {pick_card("SZ300489")}
  </div>
</section>

<section id="roadmap" class="sec" data-nav="情景路标">
  <div class="sec-head"><div class="sec-num">05</div><div class="sec-t">下周情景路标</div>
    <div class="sec-q">只描述"会发生什么"，不构成任何买卖建议</div></div>
  <div class="roadmap">
    <div class="road up"><div class="roadhd"><span class="roadtag up">向上情景</span></div>
      <div class="roadcond">若 <b>沪电股份站上 126.18</b>、<b>亨通光电站上 72.21</b></div>
      <div class="roadbody">意味着 AI 硬件的临界突破被量能确认，日线反弹升级为周线修复的起点；下一观察位看各自上方分形压力
      <b>沪电 130 一线、亨通 76 一线</b>，并观察周线 MACD 柱能否由负转正。</div></div>
    <div class="road down"><div class="roadhd"><span class="roadtag down">向下情景</span></div>
      <div class="roadcond">若 <b>沪电跌破 122.25</b>（MA20/MA60 粘合处）</div>
      <div class="roadbody">意味着临界突破失败、日线反弹结束，价格回到 60 日区间中部；下一观察位
      <b>118 一线</b>。对高位股同理：若<b>药明康德跌破 157.15</b>（MA20），则趋势延续的前提被破坏。</div></div>
  </div>
  <div class="roadtip">关注个股一侧：向上看<b>药明康德 173.6</b>、<b>康龙化成 51.3</b>；向下看<b>凯莱英 167.3</b>（MA60）与<b>药石科技 49.07</b>（贴身支撑）。</div>
</section>

<section id="list-gz" class="sec" data-nav="关注个股·完整清单">
  <div class="sec-head"><div class="sec-num">06</div><div class="sec-t">「关注个股」完整清单（42 只）</div>
    <div class="sec-q">按代码排序，全部指标取自 2026-09-21 收盘的本地日线</div></div>
  {table_for("关注个股")}
</section>

<section id="list-ai" class="sec" data-nav="AI硬件·完整清单">
  <div class="sec-head"><div class="sec-num">07</div><div class="sec-t">「AI硬件」完整清单（84 只）</div>
    <div class="sec-q">含 1 只 ETF（SH515880 通信ETF国泰）与 1 只次新股（SH688825 长鑫科技，样本不足不参与筛选）</div></div>
  {table_for("AI硬件")}
</section>

<section id="avoid" class="sec" data-nav="风险规避">
  <div class="sec-head"><div class="sec-num">08</div><div class="sec-t">本周明确规避 / 不宜追高的标的</div>
    <div class="sec-q">两类：乖离与位置极端透支、趋势已被破坏</div></div>
  {avoid_html}
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
    <b>指标参数</b>：MA5/10/20/30/60/120/250；MACD(12,26,9)，柱＝(DIF−DEA)×2；RSI(6/14) Wilder 平滑；KDJ(9,3,3)；
    BOLL(20,2)；ATR(14)；量比＝当日量 / 近 5 日均量；周线由日线按自然周聚合。<br><br>
    <b>关于"不打分"</b>：本报告不做任何综合评分与分数排名。入选依据是趋势、动量、位置、量价四类定性条件的共振，
    代价（波动、位置、量能不足）在每只卡片中单列，由读者自行权衡。<br><br>
    <b>已知局限</b>：本周仅 1 个交易日（周一），周线最后一根 K 线不完整，故周线量能指标不采用；
    不含换手率与筹码分布（本地数据无流通股本与成本分布）；不含资金流向（大单分类口径不可靠，不采用）。
  </div>
  <div class="verdict"><b>特别提示：</b>本轮扫描未纳入任何基本面、消息面与政策面因素，纯价格与成交量行为分析；
  技术指标对"下周谁涨"无可靠预测力，本报告只提供方向与关键位的观察框架。</div>
</section>

</div>'''

p = os.path.join(OUT, 'panel.body.html')
open(p, 'w', encoding='utf-8').write(BODY)
print('written', p, len(BODY))

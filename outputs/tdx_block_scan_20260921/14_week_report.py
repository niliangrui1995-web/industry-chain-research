# -*- coding: utf-8 -*-
"""本周剩余交易日视角：生成 HTML body + md 报告（第三版）。"""
import os, json, html

OUTDIR = r'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921'
OUT = r'D:/vcp_hunter/产业链投研/deliverables/technical-analyst/2026-09-21'
WK = json.load(open(os.path.join(OUTDIR, 'week_thresholds.json'), encoding='utf-8'))
NX = json.load(open(os.path.join(OUTDIR, 'nextday.json'), encoding='utf-8'))
LAB = json.load(open(os.path.join(OUTDIR, 'labeled.json'), encoding='utf-8'))
byblk = {}
for r in LAB['rows']:
    byblk.setdefault(r['block'], []).append(r)
for k in byblk:
    byblk[k].sort(key=lambda x: x['full'])

AS_OF = '2026-09-21'
E = lambda s: html.escape(str(s))
TREND = {'up': '多头', 'down': '空头', 'range': '震荡', 'n/a': '不足'}
WTXT = {'up': '周线多头', 'down': '周线空头', 'range': '周线震荡', 'n/a': '周线不足'}

PICK = {
    '关注个股': {
        '本周核心（周线转折决定型）': ['SH688271', 'SH601699', 'SH601225'],
        '次级（周线阈值可达）': ['SH601101', 'SH688235', 'SH600188'],
        '备选': ['SH600546', 'SH601088', 'SH603127'],
    },
    'AI硬件': {
        '本周核心（周线转折决定型）': ['SZ300308', 'SZ301205', 'SH688025'],
        '次级（周线阈值可达）': ['SH688008', 'SH688361', 'SH603893'],
        '备选': ['SZ301536', 'SH601869', 'SH601138'],
    },
}
RISK = {
    '关注个股': [('SZ301080', '百普赛斯', '周线柱翻正阈值低出现价 83%，即周线多头已充分展开；BIAS20 30.6%、ATR 8.0%，属过度延伸'),
                 ('SH688222', '成都先导', '阈值低于现价 34%，周内已涨 9.20%，BIAS20 34.0% 为全板块最高'),
                 ('SH688293', '奥浦迈', '阈值低于现价 55%，pos60 98.1% 贴顶'),
                 ('SZ000504', '南华生物', '阈值低于现价 40%，一字涨停后 pos60 100%、J 112.1')],
    'AI硬件': [('SZ002080', '中材科技', '周内已涨 12.25%，BIAS20 25.38%，连涨 9 日'),
               ('SH688205', '德科立', '周内 +10.01%，周线柱已正 4.963 且阈值低出现价 35%，pos60 99.4%'),
               ('BJ920045', '蘅东光', '周线柱 +25.613 为本板块最大值，已充分展开；高位看跌吞没'),
               ('SZ002415', '海康威视', '周线柱翻正需 +15.33% 且日线周线双空头，pos60 6.8%')],
}
REASON = {
    'SH688271': ('上周周线 MACD 柱 −0.078 已接近零，本周收盘只要站上 <b>104.2</b>，'
                 '就同时完成三重转强：柱翻正（103.77）＋站上周线 MA4（104.23）＋收复上周高点（103.88）——'
                 '三个阈值几乎重合在同一个价位带，是本周最清晰的一处周线转折。'
                 '位置只在 60 日区间 14.8%、BIAS20 −1.57%，不存在追高代价。'),
    'SH601699': ('本周站上 <b>15.91</b> 即同时收复上周高点（15.91）、站上周线 MA4（15.80）与 MA12（15.76），'
                 '三个阈值集中在 1.9% 以内；日线昨日已现看涨吞没、KDJ 的 K−D 仅 2.1 处金叉临界、J 值 18.8 低位——'
                 '日线临界与周线临界重合，是本周结构最紧凑的一只。'),
    'SH601225': ('站上周线 MA4 仅需 <b>25.83（+0.51%）</b>，收复上周高需 26.50（+3.11%）；'
                 '周线柱已为正（0.200），日线昨日看涨吞没且 K−D 仅 0.2 为全板块最临界的一只。'),
    'SH601101': ('已站上周线 MA4（13.34）与上周高点（13.39），本周只需<b>守住 13.39</b> 就能维持周线转强；'
                 '周线柱已正（0.121），周内已涨 5.30%，是煤炭组中唯一"临界已在脚下"的一只。'),
    'SH688235': ('站上周线 MA12 需 <b>269.88（+0.84%）</b>，上周高点 259.50 已收复；'
                 '日线 MACD 柱收敛至占比 0.005 的临界、量比 1.78，位置 37.7% 不高——周线均线争夺就在眼前。'),
    'SH600188': ('上周周线柱 −0.003 几乎为零，本周收 <b>21.62（+5.76%）</b> 柱即翻正；'
                 '周线 MA12（20.32）已站上，日线昨日看涨吞没、K−D 1.0 处金叉临界、J 值 19.5 低位。'),
    'SH600546': ('收复上周高点仅需 <b>13.68（+0.51%）</b>，周线 MA4（13.29）与 MA12（12.88）均已站上，'
                 '属"只需维持"型；周线柱已正。'),
    'SH601088': ('站上周线 MA4 需 <b>47.12（+0.68%）</b>，周线柱已正（0.459），收复上周高需 48.16（+2.91%）。'),
    'SH603127': ('本周收 <b>48.04（+2.77%）</b> 周线柱翻正（上周 −0.199）；周线 MA12（46.09）已站上，'
                 '日线昨日放量上涨（量比 1.32）且 5 日涨 9.21%。'),
    'SZ300308': ('<b>站上周线 MA12 仅需 941.15（+0.02%）</b>——这是全板块最极端的周线均线临界，'
                 '收复上周高点需 947.60（+0.70%）。日线昨日十字星带长上影、距压力 +0.93%，'
                 '位置 28.3% 低、BIAS20 7.44% 不透支。本周收盘站不站得上 941 就是答案。'),
    'SZ301205': ('按现价 321.00 计算，本周周线 MACD 柱<b>已经会翻正</b>（翻正阈值 319.87 已在现价之下）；'
                 '剩下的是收复上周高点 326.56（+1.73%）。日线 MACD 零上金叉、周线多头走强，'
                 '是本板块周线状态最健康的一只。'),
    'SH688025': ('本周收 <b>458.21（+2.51%）</b> 周线柱翻正（上周 −6.492），收复上周高需 454.97（+1.78%）；'
                 '两个阈值都落在 2% 出头的可达区间，日线量能趋势温和。'),
    'SH688008': ('站上周线 MA12 需 <b>210.31（+0.10%）</b>，为全板块第二极端的周线均线临界；'
                 '日线昨日向上跳空（缺口 205.50 未回补）＋十字星带长下影，位置 19.6% 极低。'),
    'SH688361': ('本周收 <b>391.59（+1.19%）</b> 周线柱翻正，收复上周高需 397.80（+2.79%）；'
                 '周内微跌 0.26%，属回调中的周线待确认结构。'),
    'SH603893': ('本周收 <b>204.94（+3.51%）</b> 周线柱翻正；周线 MA12（195.16）与上周高点（192.22）均已站上，'
                 '日线昨日放量上涨（量比 1.30），周内涨 4.19%。'),
    'SZ301536': ('本周收 <b>130.02（+3.26%）</b> 周线柱翻正；上周高点 125.77 已收复（距 −0.12%），'
                 '日线 MACD 零下金叉、量比 1.16。'),
    'SH601869': ('本周收 <b>476.71（+3.86%）</b> 周线柱翻正，收复上周高需 478.00（+4.14%）；'
                 '周线 MA4（435.93）已站上，周线柱 −6.330 待修复。'),
    'SH601138': ('站上周线 MA4 需 63.49（−0.17%，刚刚站上）、MA12 需 62.96（−1.01%，已站上），'
                 '收复上周高需 <b>63.95（+0.55%）</b>——本周只需小幅上行即可完成周线三连确认。'),
}


def fmt_threshold(v):
    """生成本周阈值说明文字"""
    parts = []
    if v['gap_macd0'] is not None:
        if not v['hist_pos_lastwk']:
            parts.append(f"柱翻正需 <b>{v['p_macd0']}</b>（{v['gap_macd0']:+.2f}%）")
        else:
            parts.append(f"柱维持为正的下限 <b>{v['p_macd0']}</b>（{v['gap_macd0']:+.2f}%）")
    parts.append(f"站上周线 MA4 需 <b>{v['p_ma4']}</b>（{v['gap_ma4']:+.2f}%）")
    parts.append(f"MA12 需 <b>{v['p_ma12']}</b>（{v['gap_ma12']:+.2f}%）")
    parts.append(f"收复上周高需 <b>{v['p_upper']}</b>（{v['gap_upper']:+.2f}%）")
    return '｜'.join(parts)


def card(code):
    v = WK[code]
    n = NX.get(code, {})
    chips = [
        ('现价', f"{v['close']}"), ('周内', f"{v['wk_chg']}%"),
        ('柱翻正需', f"{v['p_macd0']} ({v['gap_macd0']:+.1f}%)"),
        ('周线MA4需', f"{v['p_ma4']} ({v['gap_ma4']:+.1f}%)"),
        ('周线MA12需', f"{v['p_ma12']} ({v['gap_ma12']:+.1f}%)"),
        ('上周高', f"{v['p_upper']} ({v['gap_upper']:+.1f}%)"),
        ('上周周线柱', f"{v['macd_hist_lastwk']}"),
        ('60日位置', f"{v['pos60']}%"), ('BIAS20', f"{v['bias20']}%"), ('RSI14', f"{v['rsi14']}"),
        ('量比5', f"{v['vr5']}"), ('ATR%', f"{v['atr_pct']}%"),
    ]
    chip_html = ''.join(
        f'<span class="chip{"warn" if k in ("ATR%","BIAS20","周线MA4需","柱翻正需") else ("good" if k in ("60日位置","量比5") else "")}">'
        f'{E(k)} <b>{E(x)}</b></span>' for k, x in chips)
    dot = 'r' if v['wk_chg'] > 0 else ('g' if v['wk_chg'] < 0 else 'n')
    pill = '看多' if v['wk_chg'] > 0 else ('看空' if v['wk_chg'] < 0 else '中性')
    return f'''<div class="dim">
  <div class="idxnum">{E(code[2:])}</div>
  <div class="dimmain">
    <div class="dimrow"><span class="dot {dot}"></span><span class="dn">{E(v['name'])}</span>
      <span class="code" style="font-size:12px;color:var(--text-muted);font-family:ui-monospace,monospace">{E(code)}</span>
      <span class="pill {'r' if pill=='看多' else ('g' if pill=='看空' else 'n')}">{E(pill)}</span>
      <span class="pill n">周内 {E(v['wk_chg'])}%</span>
      <span class="pill n">{E('周线柱已正' if v['hist_pos_lastwk'] else '周线柱仍负')}</span></div>
    <div class="dd"><b>本周收盘阈值：{fmt_threshold(v)}</b></div>
    <div class="data">{chip_html}</div>
    <div class="dd">{REASON.get(code, '')}</div>
    <div class="dd" style="color:var(--text-muted)">日线：{E(v['mom_d'])}｜{E(v['volprice'])}｜{E(TREND[v['trend_d']])}趋势 / {E(WTXT[v['trend_w']])}｜
      压力 {E(v['res_near'])}（+{E(v['res_space'])}%）｜支撑 {E(v['sup_near'])}（-{E(v['sup_space'])}%）</div>
  </div>
</div>'''


def table_for(blk):
    head = ('<tr style="background:var(--bg-elevated)">'
            '<th style="padding:6px 8px;text-align:left">代码</th><th style="padding:6px 8px;text-align:left">名称</th>'
            '<th style="padding:6px 8px;text-align:right">收盘</th><th style="padding:6px 8px;text-align:right">周内%</th>'
            '<th style="padding:6px 8px;text-align:right">5日%</th><th style="padding:6px 8px;text-align:right">20日%</th>'
            '<th style="padding:6px 8px;text-align:left">趋势</th><th style="padding:6px 8px;text-align:left">量价</th>'
            '<th style="padding:6px 8px;text-align:left">MACD</th><th style="padding:6px 8px;text-align:left">周线</th>'
            '<th style="padding:6px 8px;text-align:right">60日位置</th><th style="padding:6px 8px;text-align:right">BIAS20</th>'
            '<th style="padding:6px 8px;text-align:right">RSI</th><th style="padding:6px 8px;text-align:right">J</th>'
            '<th style="padding:6px 8px;text-align:right">量比5</th>'
            '<th style="padding:6px 8px;text-align:right">压力</th><th style="padding:6px 8px;text-align:right">支撑</th></tr>')
    trs = []
    for r in byblk[blk]:
        i, l = r['ind'], r['lab']
        w = WK.get(r['full'], {})
        clr = 'color:var(--up)' if (i['chg5'] or 0) > 0 else ('color:var(--dn)' if (i['chg5'] or 0) < 0 else '')
        trs.append(
            f'<tr style="border-top:1px solid var(--border)">'
            f'<td style="padding:5px 8px;font-family:ui-monospace,monospace;font-size:12px">{E(r["full"])}</td>'
            f'<td style="padding:5px 8px">{E(r["name"])}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{i["close"]}</td>'
            f'<td style="padding:5px 8px;text-align:right;font-variant-numeric:tabular-nums">{w.get("wk_chg","")}</td>'
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
    return ''.join(f'<li style="margin:4px 0"><b>{E(n)}</b>（{E(c)}）：{E(t)}</li>' for c, n, t in RISK[blk])


BODY = f'''<div class="wrap">

<section class="hdr">
  <div class="hdr-row1">
    <span class="hero-tag">本周视角</span>
    <h1>关注个股 &amp; AI硬件 · 本周（剩余 4 个交易日）重点名单<span class="code">126 只 / {AS_OF}</span></h1>
  </div>
  <div class="hdr-row2">
    <span>数据源：通达信本地 vipdoc 日线（前复权处理）</span><span class="dot-sep"></span>
    <span>数据截至 {AS_OF} 收盘</span><span class="dot-sep"></span>
    <span>本周剩余交易日：9/22 – 9/25（周线将完整收出）</span>
  </div>
</section>

<section id="conclusion" class="sec" data-nav="核心结论">
  <div class="sec-head"><div class="sec-num">01</div><div class="sec-t">核心结论（本周视角）</div>
    <div class="sec-q">本周还剩 4 个交易日，真正有决定意义的是「本周周线收在哪里」</div></div>
  <div class="tags">
    <span class="tag">核心方法：周线收盘阈值</span>
    <span class="tag">关注个股：联影医疗 三重阈值重合</span>
    <span class="tag">AI硬件：中际旭创 周线MA12 差 0.02%</span>
  </div>
  <div class="lead">
    <b>为什么换方法</b>：4 个交易日的窗口比"明天"长，但比"下周"短——既不能用 1 日视角（预测力为噪声），
    也不能只看中期趋势（本周内不会走完）。本周恰好是<b>本周周线完整收出的一周</b>，
    所以真正可观察的是：<b class="r">本周收盘价能否站上某个"周线信号阈值"</b>——
    比如周线 MACD 柱翻正、周线收盘站上 MA4 / MA12、收复上周最高点。<br><br>
    这些阈值可以<b>精确算出来</b>（周线 MACD 关于本周收盘价是线性的，可直接解出翻正所需价格），
    于是"本周该关注谁"就变成了："<b>谁的周线阈值离现价最近、且本周内够得着</b>"。<br><br>
    <b>两类标的必须分开看</b>：<br>
    ① <b>本周决定型</b>——周线阈值在现价 0–3% 内，本周收盘价直接决定周线是否转强（如联影医疗、中际旭创、潞安环能）；<br>
    ② <b>已充分展开型</b>——周线柱翻正阈值远低于现价（如百普赛斯 −83%、奥浦迈 −55%），
    说明周线多头早已确立、价格已充分反映，<b class="g">本项目回测显示本池（高β动量股）"过度延伸"的 IC 恒为负，追高是负向因素</b>，这类应列为风险而非关注。
  </div>
  <div class="q3" style="margin-top:14px">
    <div class="q"><div class="ttl">① 本周该盯谁？</div><div class="ans">关注个股看联影医疗、潞安环能、陕西煤业；AI硬件看中际旭创、联特科技、杰普特。</div></div>
    <div class="q"><div class="ttl">② 盯的具体数字？</div><div class="ans">每只都给了"本周收盘需站上的价位"，到周五收盘即可验证。</div></div>
    <div class="q"><div class="ttl">③ 和"明天"名单为何不同？</div><div class="ans">明天盯临界位（1日方向选择）；本周盯周线收盘（结构是否转强）。视角不同，名单必然不同。</div></div>
  </div>
  <div class="verdict"><b>口径声明</b>：本项目 5 日窗口 IC 回测（非重叠采样 n=14）未达 t&gt;2 显著，只能谈符号一致性；
  方向性读数为"<b>量能确认与低 RSI 为正、趋势过度延伸为负</b>"。因此本周名单<b>偏向"低位 + 周线转折临界 + 量能配合"</b>，
  而非追最强的动量。本报告不预测涨跌，只给出可周五收盘验证的阈值。</div>
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
  科创50 近 5 日 +8.45% 领涨。本周剩余 4 个交易日同样将决定这些指数的周线收盘形态。</div>
</section>

<section id="pick-gz" class="sec" data-nav="关注个股·本周名单">
  <div class="sec-head"><div class="sec-num">03</div><div class="sec-t">「关注个股」本周重点名单</div>
    <div class="sec-q">排序依据＝周线阈值与现价的距离（越近、越够得着，本周越关键）</div></div>
  <div class="dimlist">
    {card("SH688271")}
    {card("SH601699")}
    {card("SH601225")}
  </div>
  <div style="font-size:13px;color:var(--text-muted);margin:14px 0 6px">次级（周线阈值可达）</div>
  <div class="dimlist">
    {card("SH601101")}
    {card("SH688235")}
    {card("SH600188")}
  </div>
  <div style="font-size:13px;color:var(--text-muted);margin:14px 0 6px">备选</div>
  <div class="dimlist">
    {card("SH600546")}
    {card("SH601088")}
    {card("SH603127")}
  </div>
</section>

<section id="pick-ai" class="sec" data-nav="AI硬件·本周名单">
  <div class="sec-head"><div class="sec-num">04</div><div class="sec-t">「AI硬件」本周重点名单</div>
    <div class="sec-q">排序依据＝周线阈值与现价的距离（越近、越够得着，本周越关键）</div></div>
  <div class="dimlist">
    {card("SZ300308")}
    {card("SZ301205")}
    {card("SH688025")}
  </div>
  <div style="font-size:13px;color:var(--text-muted);margin:14px 0 6px">次级（周线阈值可达）</div>
  <div class="dimlist">
    {card("SH688008")}
    {card("SH688361")}
    {card("SH603893")}
  </div>
  <div style="font-size:13px;color:var(--text-muted);margin:14px 0 6px">备选</div>
  <div class="dimlist">
    {card("SZ301536")}
    {card("SH601869")}
    {card("SH601138")}
  </div>
</section>

<section id="roadmap" class="sec" data-nav="本周验证路标">
  <div class="sec-head"><div class="sec-num">05</div><div class="sec-t">本周验证路标</div>
    <div class="sec-q">到周五收盘即可逐条验证，不构成任何买卖建议</div></div>
  <div class="roadmap">
    <div class="road up"><div class="roadhd"><span class="roadtag up">周线转强成立</span></div>
      <div class="roadcond">周五收盘 <b>联影医疗 ≥ 104.2</b>、<b>中际旭创 ≥ 941.15</b>、<b>潞安环能 ≥ 15.91</b></div>
      <div class="roadbody">意味着周线层面的转强被确认：联影同时完成柱翻正＋站上周线 MA4＋收复上周高；
      中际旭创收复周线 MA12；潞安环能同时收复上周高与周线 MA4/MA12。下一观察位是各自日线的上方分形压力。</div></div>
    <div class="road down"><div class="roadhd"><span class="roadtag down">周线转强落空</span></div>
      <div class="roadcond">周五收盘 <b>联影医疗 &lt; 103.0</b>、<b>中际旭创 &lt; 920</b>、<b>潞安环能 &lt; 15.4</b></div>
      <div class="roadbody">意味着本周反弹未能在周线级别兑现，周线柱与均线压制继续有效，
      这几只回到"周线待修复"状态；下一观察位是各自的周线 MA12 与 60 日区间下沿。</div></div>
  </div>
  <div class="roadtip">煤炭组共同验证：陕西煤业 ≥ 25.83、昊华能源守住 13.39、山煤国际 ≥ 13.68、中国神华 ≥ 47.12——
  四只同属"周线阈值就在脚下"，本周可作为一组同步观察。</div>
</section>

<section id="risk" class="sec" data-nav="过度延伸警示">
  <div class="sec-head"><div class="sec-num">06</div><div class="sec-t">过度延伸警示（周线已充分展开）</div>
    <div class="sec-q">判据：周线柱翻正阈值远低于现价 ⇒ 多头已充分反映，本池回测显示追高为负向</div></div>
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
    <b>完整性校验</b>：以全市场并集交易日历为基准比对最近 130 个交易日，126 只中仅 5 只缺数且均为真实停牌或次新，非取数缺陷。<br><br>
    <b>周线阈值的算法（本报告核心）</b>：<br>
    ① <b>周线 MACD 柱翻正价</b>：周线 MACD 的 DIF、DEA 关于本周收盘价 P 均为线性函数，故 hist(P) 也是线性的——
    取 P=0 与 P=1 两点求 hist，直接线性解出 hist(P*)=0 的价格 P*。<br>
    ② <b>周线 MA4 / MA12 站上价</b>：周线 MA4＝(前三周收盘和＋P)/4，要求 P &gt; MA4 ⇒ P &gt; 前三周和 ÷ 3；
    同理 MA12 ⇒ P &gt; 前 11 周和 ÷ 11。均为闭式解。<br>
    ③ <b>收复上周高点</b>：P &gt; 上一完整周的最高价。<br><br>
    <b>指标参数</b>：MA5/10/20/30/60/120/250；MACD(12,26,9)，柱＝(DIF−DEA)×2；RSI(6/14) Wilder 平滑；KDJ(9,3,3)；
    BOLL(20,2)；ATR(14)；量比＝当日量 / 近 5 日均量；周线由日线按自然周聚合。<br><br>
    <b>关于"不打分"</b>：本报告不做任何综合评分与分数排名，也不预测涨跌。入选依据是周线阈值与现价的距离、
    以及位置与量能是否配合；每只都给出可在本周五收盘验证的具体价位。<br><br>
    <b>已知局限</b>：本周仅 1 个交易日（周一），周线最后一根 K 线不完整，故周线量能指标不采用；
    不含换手率与筹码分布；不含资金流向（大单分类口径不可靠，不采用）；
    4 日窗口的预测力介于 1 日（噪声）与 5 日（弱）之间，本项目 5 日 IC 回测未达显著，结论只能作符号一致性参考。
  </div>
  <div class="verdict"><b>特别提示</b>：本报告为纯技术面，未纳入基本面、消息面与政策面因素。
  "周线阈值"是价格层面的可验证锚点，不代表公司层面的任何变化。</div>
</section>

</div>'''

open(os.path.join(OUT, 'panel.body.html'), 'w', encoding='utf-8').write(BODY)
print('body written', len(BODY))

# ===== md =====
def md_table(blk):
    out = ['| 代码 | 名称 | 收盘 | 周内% | 5日% | 20日% | 趋势 | 量价 | MACD | 周线 | 60日位置 | BIAS20 | RSI | J | 量比5 | 压力 | 支撑 |',
           '|---|---|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in byblk[blk]:
        i, l = r['ind'], r['lab']
        w = WK.get(r['full'], {})
        out.append(f"| {r['full']} | {r['name']} | {i['close']} | {w.get('wk_chg','')} | {i['chg5']} | {i['chg20']} | "
                   f"{TREND[l['trend_d']]} | {l['volprice']} | {l['mom_d']} | {WTXT[l['trend_w']]} | {i['pos60']} | "
                   f"{l['bias20']} | {i['rsi14']} | {i['kdj']['j']} | {i['vr5']} | {l['res_near']} | {l['sup_near']} |")
    return '\n'.join(out)


def md_card(code):
    v = WK[code]
    th = []
    if v['gap_macd0'] is not None:
        th.append(f"柱翻正需 **{v['p_macd0']}**（{v['gap_macd0']:+.2f}%）")
    th.append(f"周线MA4需 **{v['p_ma4']}**（{v['gap_ma4']:+.2f}%）")
    th.append(f"周线MA12需 **{v['p_ma12']}**（{v['gap_ma12']:+.2f}%）")
    th.append(f"收复上周高需 **{v['p_upper']}**（{v['gap_upper']:+.2f}%）")
    return (f"**{v['name']}（{code}）** 现价 {v['close']}｜周内 {v['wk_chg']}%\n"
            f"- **本周收盘阈值**：{'｜'.join(th)}\n"
            f"- 读数：上周周线柱 {v['macd_hist_lastwk']}（{'已正' if v['hist_pos_lastwk'] else '仍负'}）｜"
            f"60日位置 {v['pos60']}%｜BIAS20 {v['bias20']}%｜RSI14 {v['rsi14']}｜量比5 {v['vr5']}｜ATR {v['atr_pct']}%\n"
            f"- 日线：{v['mom_d']}｜{v['volprice']}｜压力 {v['res_near']}（+{v['res_space']}%）｜支撑 {v['sup_near']}（-{v['sup_space']}%）\n"
            f"- 入选理由：{REASON.get(code,'')}\n")


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

MD = f"""# 关注个股 & AI硬件 · 本周（剩余 4 个交易日）重点名单（{AS_OF} 收盘）

> 数据源：通达信本地日线 `D:\\HT\\vipdoc`（前复权处理）｜板块成分：`T0002\\blocknew\\GZGG.blk`（关注个股）、`AIYJ.blk`（AI硬件）
> 覆盖 126 只，全部读取成功，最后交易日均为 {AS_OF}；本周剩余交易日 9/22 – 9/25，周线将完整收出

---

## 一、核心结论（本周视角）

**为什么换方法**：4 个交易日的窗口比"明天"长、比"下周"短——既不能用 1 日视角（预测力为噪声），也不能只看中期趋势（本周内走不完）。
但本周恰好是**本周周线完整收出的一周**，所以真正可观察的是：**本周收盘价能否站上某个"周线信号阈值"**——
周线 MACD 柱翻正、周线收盘站上 MA4 / MA12、收复上周最高点。

这些阈值可以**精确算出来**（周线 MACD 关于本周收盘价是线性的，可直接解出翻正所需价格）。
于是"本周该关注谁"变成：**谁的周线阈值离现价最近、且本周内够得着**。

### 两类标的必须分开看

| 类型 | 判据 | 本周含义 | 处理 |
|---|---|---|---|
| **本周决定型** | 周线阈值在现价 0–3% 内 | 本周收盘价直接决定周线是否转强 | **重点关注** |
| **已充分展开型** | 周线柱翻正阈值远低于现价（如 −83%、−55%） | 周线多头早已确立、价格已充分反映 | **列为风险，不追** |

> 本项目回测显示本池（高β动量股）"**过度延伸**"的 IC 恒为负，追高是负向因素；"量能确认"与"低 RSI"为正向。
> 因此本周名单偏向"**低位 + 周线转折临界 + 量能配合**"，而非追最强动量。

### 大盘背景（同日收盘）

| 指数 | 收盘 | MA20 | MA60 | 5日% | MACD柱 | 量比5 |
|---|---:|---:|---:|---:|---:|---:|
{idx_md}

五大指数全线站上 MA20；深成指、创业板指、科创50、中证1000 日线 MACD 柱已翻正（上证仍为负但收敛）。科创50 近 5 日 **+8.45%** 领涨。

---

## 二、「关注个股」本周重点名单
{md_pick('关注个股')}
---

## 三、「AI硬件」本周重点名单
{md_pick('AI硬件')}
---

## 四、本周验证路标（周五收盘即可逐条验证）

| 情景 | 触发条件 | 意味着什么 |
|---|---|---|
| 周线转强成立 | 周五收盘 **联影医疗 ≥ 104.2**、**中际旭创 ≥ 941.15**、**潞安环能 ≥ 15.91** | 联影同时完成柱翻正＋站上周线MA4＋收复上周高；中际旭创收复周线MA12；潞安同时收复上周高与周线MA4/MA12 |
| 周线转强落空 | 周五收盘 **联影医疗 < 103.0**、**中际旭创 < 920**、**潞安环能 < 15.4** | 本周反弹未能在周线级别兑现，回到"周线待修复"状态 |
| 煤炭组同步验证 | 陕西煤业 ≥ 25.83、昊华能源守住 13.39、山煤国际 ≥ 13.68、中国神华 ≥ 47.12 | 四只同属"周线阈值就在脚下"，可作为一组同步观察 |

---

## 五、过度延伸警示（周线已充分展开）
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
- **周线阈值的算法（本报告核心）**：
  1. **周线 MACD 柱翻正价**：DIF、DEA 关于本周收盘价 P 均为线性函数 ⇒ hist(P) 线性 ⇒ 取 P=0 与 P=1 两点求 hist，线性解出 hist(P*)=0 的价格。
  2. **周线 MA4 / MA12 站上价**：周线 MA4＝(前三周收盘和＋P)/4，要求 P > MA4 ⇒ **P > 前三周和 ÷ 3**；MA12 ⇒ **P > 前 11 周和 ÷ 11**。均为闭式解。
  3. **收复上周高点**：P > 上一完整周的最高价。
- **指标参数**：MA5/10/20/30/60/120/250；MACD(12,26,9)，柱＝(DIF−DEA)×2；RSI(6/14) Wilder 平滑；KDJ(9,3,3)；BOLL(20,2)；ATR(14)；量比＝当日量÷近 5 日均量；周线由日线按自然周聚合。
- **关于"不打分"**：不做任何综合评分与分数排名，也不预测涨跌。入选依据是周线阈值与现价的距离、以及位置与量能是否配合。
- **已知局限**：本周仅 1 个交易日（周一），周线最后一根 K 线不完整，故周线量能指标不采用；不含换手率与筹码分布；不含资金流向（大单分类口径不可靠，不采用）；4 日窗口的预测力介于 1 日（噪声）与 5 日（弱）之间，本项目 5 日 IC 回测未达显著，结论只能作符号一致性参考。

---

## 九、风险提示

1. **窗口预测力有限**：4 日窗口介于 1 日（噪声）与 5 日（弱）之间；本项目 5 日 IC 回测非重叠采样 n=14，未达 t>2 显著，只能谈符号一致性，不能声称显著。
2. **追高为负向**：本池"过度延伸"IC 恒为负。百普赛斯（周线阈值低于现价 83%）、奥浦迈（−55%）、成都先导（−34%）等属周线已充分展开，本周不应作为关注对象。
3. **阈值是价格锚点、非保证**：周线阈值只说明"收在什么价位之上才会形成什么技术状态"，不保证价格会走到那里。
4. **波动风险**：寒武纪、光智科技、中船特气 ATR 分别为 5.12%、8.37%、6.98%，周内大幅波动会使周线收盘远离阈值。
5. **口径风险**：本报告为纯技术面，未纳入基本面、消息面与政策面因素。

---

⚠️ 本分析由 AI 基于公开信息生成，仅依据价格、成交量等公开市场行为数据进行技术面研判，
不涉及基本面、消息面、政策面因素，不构成任何投资建议，不构成个股推荐。
技术分析有其固有局限性，过去的表现不代表未来走势。投资有风险，决策需谨慎。
"""

open(os.path.join(OUT, '关注个股与AI硬件-本周重点名单.md'), 'w', encoding='utf-8').write(MD)
print('md written', len(MD))

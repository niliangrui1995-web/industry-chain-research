# -*- coding: utf-8 -*-
"""
合并 9-22 收盘技术面快照(blocknew_gzgg_aiyj_snapshot.csv) + 9-23 午盘实时行情(rt_quotes_20260923_1130.json),
生成「关注个股 / AI硬件」两自建板块完整个股清单 + 技术面筛选报告 HTML。
"""
import csv, json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r'D:\vcp_hunter\产业链投研\deliverables\technical-analyst\20260923'
SNAP = os.path.join(OUT_DIR, 'blocknew_gzgg_aiyj_snapshot.csv')
RT = os.path.join(OUT_DIR, 'rt_quotes_20260923_1130.json')
HTML = os.path.join(OUT_DIR, 'blocknew_gzgg_aiyj_report.html')

with open(RT, encoding='utf-8') as f:
    rt = json.load(f)['quotes']

rows = []
with open(SNAP, encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        rows.append(r)

NAME_FIX = {'515880': '通信ETF'}
for r in rows:
    if r.get('name') in ('N/A', '', None) and r['code'] in NAME_FIX:
        r['name'] = NAME_FIX[r['code']]

def rtq(r):
    key = r['mkt'] + r['code']
    return rt.get(key, [None]*5)

def fmt(v, suf='', na='N/A'):
    if v is None or v == '':
        return na
    try:
        return f"{float(v):g}{suf}"
    except (ValueError, TypeError):
        return na

def pct_cls(v):
    try:
        x = float(v)
    except (ValueError, TypeError):
        return 'na'
    return 'up' if x > 0 else ('dn' if x < 0 else 'fl')

TREND_ORDER = {'强多头': 0, '多头': 1, '震荡': 2, '空头': 3, '数据不足': 4}

def build_table(block):
    grp = [r for r in rows if r['block'] == block]
    grp.sort(key=lambda r: (TREND_ORDER.get(r['trend'], 9), -(float(r['chg20']) if r['chg20'] else -999)))
    tr = []
    for r in grp:
        price, chg, lb, hs, zf = rtq(r)
        macd_state = r.get('macd_cross5') or ('红柱' if r.get('dif_above0') == 'True' else '绿柱')
        err = r.get('error')
        row_note = ''
        if err:
            row_note = f"<span class='na'>数据不足({err})</span>"
        tr.append(
            f"<tr><td class='c'>{r['mkt']}{r['code']}</td><td class='nm'>{r['name']}</td>"
            f"<td class='c'>{r['trend']}</td>"
            f"<td class='c'>{fmt(r['close'])}</td>"
            f"<td class='c {pct_cls(r['pct_chg'])}'>{fmt(r['pct_chg'], '%')}</td>"
            f"<td class='c {pct_cls(r['chg5'])}'>{fmt(r['chg5'], '%')}</td>"
            f"<td class='c {pct_cls(r['chg20'])}'>{fmt(r['chg20'], '%')}</td>"
            f"<td class='c {pct_cls(r['vs_ma20'])}'>{fmt(r['vs_ma20'], '%')}</td>"
            f"<td class='c {pct_cls(r['from_hi60'])}'>{fmt(r['from_hi60'], '%')}</td>"
            f"<td class='c'>{fmt(r['rsi6'])}</td>"
            f"<td class='c'>{fmt(r['kdj_j'])}</td>"
            f"<td class='c'>{fmt(r['macd_bar'])}<span class='sub'>{macd_state}</span></td>"
            f"<td class='c'>{fmt(r['vol_ratio'])}</td>"
            f"<td class='c {pct_cls(chg)}'>{fmt(chg, '%')}</td>"
            f"<td class='c'>{fmt(lb)}</td>"
            f"<td class='c'>{fmt(hs, '%')}</td>"
            f"{('<td class=\"c na\">上市不足70日, 指标不适用</td>') if err else ''}"
            f"</tr>")
    if err_cols := any(r.get('error') for r in grp):
        head_extra = "<th>备注</th>"
    else:
        head_extra = ""
    head = ("<tr><th>代码</th><th>名称</th><th>趋势</th><th>收盘<br>09-22</th>"
            "<th>昨涨幅</th><th>5日</th><th>20日</th><th>MA20<br>偏离</th>"
            "<th>距60日<br>新高</th><th>RSI6</th><th>KDJ<br>J值</th>"
            "<th>MACD柱<br>状态</th><th>量比<br>昨日</th>"
            "<th>今日<br>涨幅</th><th>今日<br>量比</th><th>今日<br>换手</th>" + head_extra + "</tr>")
    return f"<table>{head}{''.join(tr)}</table>"

def stats_block(block):
    grp = [r for r in rows if r['block'] == block and not r.get('error')]
    dist = {}
    for r in grp:
        dist[r['trend']] = dist.get(r['trend'], 0) + 1
    up_today = sum(1 for r in grp if (rtq(r)[1] or 0) > 0)
    return dist, len(grp), up_today

gz_dist, gz_n, gz_up = stats_block('关注个股')
ai_dist, ai_n, ai_up = stats_block('AI硬件')

CSS = """
body{font-family:'Microsoft YaHei',system-ui,sans-serif;margin:0;background:#f5f6f8;color:#1c1e21;font-size:13px;}
.wrap{max-width:1180px;margin:0 auto;padding:24px 16px 60px;}
h1{font-size:22px;margin:8px 0 4px;}
h2{font-size:17px;margin:28px 0 10px;padding-left:10px;border-left:4px solid #c0392b;}
h3{font-size:14px;margin:16px 0 8px;}
.meta{color:#667;font-size:12px;line-height:1.7;margin-bottom:12px;}
table{width:100%;border-collapse:collapse;background:#fff;font-size:12px;margin:8px 0 4px;}
th{background:#eef1f5;padding:6px 5px;border:1px solid #dde2e8;font-weight:600;white-space:nowrap;}
td{padding:5px 6px;border:1px solid #e7ebef;text-align:right;}
td.c{text-align:center;white-space:nowrap;}
td.nm{text-align:left;font-weight:600;white-space:nowrap;}
.up{color:#c0392b;font-weight:600;}
.dn{color:#0e8a4a;font-weight:600;}
.fl{color:#555;}
.na{color:#999;}
.sub{display:block;font-size:10px;color:#889;font-weight:400;}
.card{background:#fff;border:1px solid #e2e6ec;border-radius:8px;padding:14px 16px;margin:10px 0;}
.card h3{margin:0 0 6px;}
.card .tick{font-weight:700;color:#c0392b;}
.card p{margin:4px 0;line-height:1.75;}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
@media(max-width:900px){.grid2{grid-template-columns:1fr;}}
.tag{display:inline-block;background:#eef4ff;color:#2456a6;border-radius:4px;padding:1px 7px;font-size:11px;margin-left:6px;}
.warn{background:#fff7f0;border:1px solid #f0d9c8;border-radius:8px;padding:12px 14px;margin:14px 0;}
.warn b{color:#b3541e;}
ul{line-height:1.9;}
.foot{color:#889;font-size:11px;margin-top:30px;border-top:1px solid #dde;padding-top:10px;line-height:1.7;}
"""

gz_dist_s = ' / '.join(f"{k}{v}只" for k, v in [('强多头', gz_dist.get('强多头', 0)), ('多头', gz_dist.get('多头', 0)), ('震荡', gz_dist.get('震荡', 0)), ('空头', gz_dist.get('空头', 0))])
ai_dist_s = ' / '.join(f"{k}{v}只" for k, v in [('强多头', ai_dist.get('强多头', 0)), ('多头', ai_dist.get('多头', 0)), ('震荡', ai_dist.get('震荡', 0)), ('空头', ai_dist.get('空头', 0))])

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>自建板块「关注个股 / AI硬件」全成分技术面快照与筛选 — 2026-09-23</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<h1>自建板块「关注个股」与「AI硬件」全成分技术面快照与筛选</h1>
<div class="meta">
板块来源：通达信自建板块 <b>D:\\HT\\T0002\\blocknew\\GZGG.blk（关注个股，42只）</b> 与 <b>AIYJ.blk（AI硬件，84只）</b>，名称映射 blocknew.cfg。<br>
历史行情：D:\\HT\\vipdoc 本地日线（不复权，经除权缺口识别 + 前复权近似处理），指标截至 <b>2026-09-22 收盘</b>；<br>
盘中动态：大智慧实时行情，<b>2026-09-23 11:30（午盘收盘快照）</b>。<br>
口径说明：收盘价/涨幅/均线/MACD/RSI/KDJ/量比均为 9-22 收盘口径（表格「昨日」列）；「今日」三列为 9-23 午盘实时口径。本地日线为不复权数据，除权识别为近似方法，仅供技术面参考。本文为纯技术面分析，不构成任何投资建议。
</div>

<h2>一、板块整体面貌（截至 9-23 午盘）</h2>
<div class="grid2">
<div class="card">
<h3>关注个股（42只）：CXO/创新药链主升，煤炭跛脚</h3>
<p>趋势分布：{gz_dist_s}。今日午盘上涨 <b class="tick">{gz_up}/{gz_n}</b> 只。</p>
<p>CXO/医疗板块呈<b>板块性主升</b>：奥浦迈 +12.0%、益诺思 +10.4%、百普赛斯 +9.4%、义翘神州 +8.7%、艾力斯 +8.6%、皓元医药 +7.7% 集体放量上攻，20 日涨幅普遍 +10%~+46%，MA 多头排列；煤炭 7 只全线走弱（-0.5%~-3.1%），量能萎缩，是板块内的拖累项。</p>
</div>
<div class="card">
<h3>AI硬件（84只）：高位分化，资金向 PCB/材料/设备扩散</h3>
<p>趋势分布：{ai_dist_s}。今日午盘上涨 <b class="tick">{ai_up}/{ai_n}</b> 只。</p>
<p>光模块双龙头<b>中际旭创 / 新易盛</b>高位缩量盘整（量比 0.71 / 0.77，未破 5 日线）；资金明显向<b>PCB（先导基电、沪电、胜宏）、材料（东材、沃特、联瑞）、设备/芯片（瑞芯微、有研硅、芯碁微装）</b>方向扩散，多只放量突破。前期热门股亨通光电 -3.1%、宏和科技 -2.2% 回落，寒武纪昨日放量长阴后缩量反抽。</p>
</div>
</div>

<h2>二、「关注个股」完整清单（42只，按趋势+20日涨幅排序）</h2>
{build_table('关注个股')}
<p class="foot">注：煤炭/能源类（昊华能源、山煤国际、陕西煤业、兖矿能源、中国神华、中煤能源、潞安环能）为空头/弱势，南华生物为连板情绪股（今日盘中最高触及涨停价后回落）。</p>

<h2>三、「AI硬件」完整清单（84只，按趋势+20日涨幅排序）</h2>
{build_table('AI硬件')}
<p class="foot">注：515880 为通信ETF（板块跟踪工具）；688825 上市不足 70 个交易日，长周期指标不适用；BJ920045 为北交所个股（蘅东光）。</p>

<h2>四、今日下午最值得关注（盘中动能 + 趋势突破延续）</h2>
<h3>关注个股</h3>
<div class="grid2">
<div class="card"><h3>1. 688293 奥浦迈 <span class="tag">+12.0% 量比2.0</span></h3>
<p>放量突破 60 日新高（昨收 75.4，今高 88.5），强多头排列，MACD 红柱 2.4 持续放大，CXO 板块情绪核心。突破后回踩均价线 82 元附近若企稳，动能有望延续。<b>风险：振幅 17.7%，RSI6=77，盘中追高风险大。</b></p></div>
<div class="card"><h3>2. 688710 益诺思 <span class="tag">+10.4% 量比3.7</span></h3>
<p>昨日 MACD 金叉后今日长阳加速，量比 3.7 为板块最强量能，距 60 日新高仍有 11.7% 空间、相对低位，量价配合健康。<b>风险：换手 5.8%，波动加剧。</b></p></div>
<div class="card"><h3>3. 688578 艾力斯 <span class="tag">+8.6% 量比3.3</span></h3>
<p>20 日回调 -9.8% 后首次放量反转，突破 20 日箱体，MACD 4 日前金叉、红柱连续放大，属「低位启动」形态而非高位加速，赔率较好。<b>风险：突破首日，需防冲高回落。</b></p></div>
<div class="card"><h3>4. 300363 博腾股份 / 000739 普洛药业 <span class="tag">+5.3% / +4.5%</span></h3>
<p>博腾放量（量比 2.1）突破近月平台，红柱放大；普洛沿 5 日线稳步主升（20日 +15%），量比 1.73 温和放大。两者均为趋势中继、乖离不高的补涨型选择。<b>风险：板块若冲高回落将同步回撤。</b></p></div>
</div>
<h3>AI硬件</h3>
<div class="grid2">
<div class="card"><h3>1. 600641 先导基电 <span class="tag">+6.6% 量比3.2</span></h3>
<p>昨日涨停后今日再度放量上攻（5日累计 +39.7%），PCB 设备方向情绪核心，外盘大于内盘、买盘占优。<b>风险：RSI6=89.6 严重超买，今日振幅已达 10%，尾盘注意分歧。</b></p></div>
<div class="card"><h3>2. 300684 中石科技 <span class="tag">+5.6% 量比2.6</span></h3>
<p>昨日 +12% 今日再涨 5.6%，MACD 昨日金叉、红柱转正加速，散热材料方向主升。<b>风险：换手 12.4% 偏高，RSI6=83.5。</b></p></div>
<div class="card"><h3>3. 603893 瑞芯微 <span class="tag">+3.1% 量比3.6</span></h3>
<p>昨日 +10% 今日续涨，量比 3.56 为板块最大，多头排列、距 60 日新高 -6.9% 处于突破区，AIoT SoC 主线中军。<b>风险：J 值 118 超买，短线乖离扩大。</b></p></div>
<div class="card"><h3>4. 601208 东材科技 / 002886 沃特股份 <span class="tag">+5.3% / +3.3%</span></h3>
<p>东材放量突破（20日 +17.8%，红柱放大）；沃特换手 15.1% 放量走强、MACD 绿柱收敛至金叉前夕。均为材料端「突破/临界」形态。<b>风险：材料端波动大于 PCB 中军，注意止损纪律。</b></p></div>
</div>

<h2>五、明日（9-24）最值得关注（蓄势 / 回踩企稳 / 启动初期）</h2>
<h3>关注个股</h3>
<div class="grid2">
<div class="card"><h3>1. 688428 诺诚健华 <span class="tag">昨日MACD金叉 今日+3.4%确认</span></h3>
<p>9-22 MACD 金叉、今日放量 3.4% 确认方向，距 60 日新高仅 -4%，突破在即。启动初期介入成本好于已加速个股。<b>关注 34 元上方突破有效性；跌破 32 元（今日低点）则形态失效。</b></p></div>
<div class="card"><h3>2. 688222 成都先导 <span class="tag">洗盘后修复 +3.4%</span></h3>
<p>5 日 +38% 后昨日 -2.4% 洗盘、今日放量（量比1.55）收复，红柱维持，强多头未破坏。回踩 5 日线企稳可跟踪延续。<b>关注 47.6 元（今日高点）突破；失守 43.5 元（今日低点）离场。</b></p></div>
<div class="card"><h3>3. 603259 药明康德 <span class="tag">龙头缩量蓄势</span></h3>
<p>CXO 龙头本轮明显滞涨（20日仅 +4.3% vs 板块 +15%~+46%），缩量横盘（量比0.97），若板块情绪延续存在补涨诉求；167 元（5日线附近）为多空观察位。<b>风险：若板块冲高回落，滞涨股可能补跌。</b></p></div>
<div class="card"><h3>4. 002821 凯莱英 / 601088 中国神华 <span class="tag">整理 / 防守</span></h3>
<p>凯莱英高位缩量整理（量比0.89），回踩 MA10（约182元）企稳可看延续；神华为空头趋势中的抗跌高股息防守位（今日仅 -0.5%，量比 0.83），47.5 元 MA60 上方盘整，作板块内对冲观察。</p></div>
</div>
<h3>AI硬件</h3>
<div class="grid2">
<div class="card"><h3>1. 688432 有研硅 <span class="tag">+4.7% 突破跟进</span></h3>
<p>半导体硅材料，今日放量突破 55 元平台，多头趋势、20日 +30.7% 但距 60 日新高仍有 13.5% 空间，红柱 1.49 放大。明日回踩 53 元（今日跳空缺口上沿）企稳则突破有效。</p></div>
<div class="card"><h3>2. 688300 联瑞新材 / 688630 芯碁微装 <span class="tag">金叉后加速</span></h3>
<p>联瑞 MACD 金叉 3 日、今日 +3.1% 放量（量比1.45）延续；芯碁微装今日 +3.1% 创阶段新高（红柱 5.3）。均为「金叉后第二波」形态，趋势健康、乖离可控。</p></div>
<div class="card"><h3>3. 002463 沪电股份 / 300476 胜宏科技 <span class="tag">PCB中军 沿5日线</span></h3>
<p>两只 PCB 核心均为多头排列稳步上行（20日 +27.6% / +14.6%），今日量比 1.33 / 1.18 温和放量、未过热。强趋势股回踩 5 日线不破即是关注点；跌破 10 日线再转谨慎。</p></div>
<div class="card"><h3>4. 中际旭创 / 新易盛（高位盘整观察）</h3>
<p>双龙头今日缩量盘整（+0.25% / -0.29%，量比 0.71 / 0.77），仍收于 5 日线上方、强多头未破坏。明日关注能否再度放量突破 930 / 460 平台——放量则板块情绪回归主线，缩量滞涨则注意高位钝化风险。<b>不作突破预判，以量能验证为准。</b></p></div>
</div>

<div class="warn">
<b>风险与排除提示：</b>
<ul>
<li><b>000504 南华生物</b>：连板情绪股，今日最高触及涨停价后炸板（收 +7.3%），量比 20.15、换手 28.2%，纯资金博弈，技术面体系不适用，不建议按趋势逻辑参与。</li>
<li><b>688256 寒武纪</b>：9-22 放量长阴 -9.84% 跌破 20 日线（趋势转空头），今日仅缩量反抽 +0.95%，属破位反抽而非反转，趋势标的剔除，仅作超跌反弹博弈观察。</li>
<li><b>600487 亨通光电 / 603256 宏和科技 / 688205 德科立</b>：近日连续放量回落，短线量价转弱，先观察企稳信号再介入。</li>
<li><b>688825 长鑫科技</b>：上市不足 70 个交易日，60 日均线等长周期指标不适用，不参与筛选。</li>
<li>今日涨幅前列的多只个股（百普赛斯、义翘神州、皓元医药、南华生物）RSI6 已达 84~92 的超买区，短线乖离大，若参与只宜轻仓且以当日均价线/前一日收盘为参照设纪律。</li>
<li>本报告为纯技术面定性分析，不预测具体点位与概率；所有「关注位/失效位」为基于趋势与量价的客观参照，非操作指令，不构成投资建议。</li>
</ul>
</div>

<div class="foot">
数据与产物：deliverables/technical-analyst/20260923/ 下 blocknew_gzgg_aiyj_snapshot.csv（126只全指标快照）、rt_quotes_20260923_1130.json（9-23午盘实时行情）、roster_关注个股.csv、roster_AI硬件.csv、本报告 HTML。<br>
生成脚本：scripts/scan_blocknew_technicals.py（可复用，改 BLOCKS 即可扫描其他自建板块）。生成时间：2026-09-23。
</div>
</div>
</body>
</html>"""

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print('HTML ->', HTML)

# 校验
with open(HTML, encoding='utf-8') as f:
    content = f.read()
assert content.count('<tr>') == content.count('</tr>'), 'tr mismatch'
assert '%s' not in content and 'None</td>' not in content
print('rows in tables:', content.count('<tr>') - content.count('<th>'))
print('check OK')

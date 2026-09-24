# -*- coding: utf-8 -*-
"""
基于 2026-09-24 收盘双周期(日线+周线)快照, 生成「关注个股 / AI硬件」两自建板块
完整个股清单 + 下周(2026-09-28~10-02)技术面关注名单与入选理由。
"""
import csv, os, html, sys

sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r'D:\vcp_hunter\产业链投研\deliverables\technical-analyst\20260924'
SNAP = os.path.join(OUT_DIR, 'blocknew_gzgg_aiyj_weekly_snapshot.csv')
REPORT = os.path.join(OUT_DIR, 'blocknew_gzgg_aiyj_weekly_report.html')

rows = list(csv.DictReader(open(SNAP, encoding='utf-8-sig')))
for r in rows:
    if r['code'] == '515880' and r['name'] == 'N/A':
        r['name'] = '通信ETF'

def f(r, k):
    try: return float(r[k])
    except: return None

def s(r, k, d=1, na='N/A'):
    v = f(r, k)
    return na if v is None else f'{v:.{d}f}'

def cls(r, k):
    v = f(r, k)
    return 'up' if (v or 0) > 0 else ('dn' if (v or 0) < 0 else 'flat')

def esc(x): return html.escape(str(x if x not in (None, '') else 'N/A'))

def row_html(r):
    cells = [
        f"<td class='code'>{esc(r['mkt']+r['code'])}</td>",
        f"<td class='name'>{esc(r['name'])}</td>",
        f"<td class='res'>{esc(r['resonance'])}</td>",
        f"<td>{esc(r['trend'])}</td><td>{esc(r['w_trend'])}</td>",
        f"<td>{esc(r['close'])}</td>",
        f"<td class='{cls(r,'pct_chg')}'>{s(r,'pct_chg',2)}%</td>",
        f"<td class='{cls(r,'chg5')}'>{s(r,'chg5')}%</td>",
        f"<td class='{cls(r,'chg20')}'>{s(r,'chg20')}%</td>",
        f"<td class='{cls(r,'vs_ma20')}'>{s(r,'vs_ma20')}%</td>",
        f"<td>{esc(r['ma5'])}</td><td>{esc(r['ma10'])}</td><td>{esc(r['ma20'])}</td><td>{esc(r['ma60'])}</td>",
        f"<td>{s(r,'macd_bar',3)}<small>{esc(r['macd_cross5'])}</small></td>",
        f"<td>{s(r,'rsi6')}</td><td>{s(r,'kdj_j')}</td>",
        f"<td>{s(r,'vol_ratio',2)}</td>",
        f"<td>{esc(r['lo20'])}</td><td>{esc(r['hi20'])}</td>",
        f"<td>{s(r,'w_vs_ma10')}%</td>",
        f"<td>{s(r,'w_pos20',0)}%</td>",
        f"<td class='{cls(r,'w_from_hi20')}'>{s(r,'w_from_hi20')}%</td>",
        f"<td>{s(r,'w_macd_bar',2)}<small>{esc(r['w_macd_cross5'])}</small></td>",
        f"<td>{esc(r['w_sup'])}</td><td>{esc(r['w_res'])}</td>",
    ]
    if r.get('error'):
        cells.append(f"<td class='na'>样本不足({esc(r['error'])})</td>")
    else:
        cells.append('<td></td>')
    return '<tr>' + ''.join(cells) + '</tr>'

HEAD = ('<tr><th>代码</th><th>名称</th><th>日周共振</th><th>日线趋势</th><th>周线趋势</th><th>收盘</th>'
        '<th>日涨跌</th><th>5日</th><th>20日</th><th>MA20偏离</th>'
        '<th>MA5</th><th>MA10</th><th>MA20</th><th>MA60</th><th>日MACD柱/交叉</th>'
        '<th>RSI6</th><th>KDJ-J</th><th>量比</th><th>日支撑<br>20日低</th><th>日压力<br>20日高</th>'
        '<th>周MA10<br>偏离</th><th>周位置<br>20周</th><th>距20周高</th><th>周MACD柱/交叉</th>'
        '<th>周支撑</th><th>周压力</th><th>备注</th></tr>')

def table(block):
    grp = [r for r in rows if r['block'] == block]
    order = {'日周共振向上':0, '日强周平':1, '周多日震(回踩确认)':2, '日多周空(反弹性质)':3,
             '周多日空(深度回调)':4, '双周期震荡':5, '双周期偏弱':6, '样本不足':7}
    grp.sort(key=lambda r: (order.get(r['resonance'], 9), -(f(r, 'chg20') or -999)))
    return f"<table><thead>{HEAD}</thead><tbody>{''.join(row_html(r) for r in grp)}</tbody></table>"

def find(code): return next(r for r in rows if r['code'] == code)

def line(code):
    r = find(code)
    return (f"收盘 {esc(r['close'])}｜日线{r['trend']}／{r['w_trend']}｜日周共振：<b>{esc(r['resonance'])}</b><br>"
            f"日线：日涨跌 {s(r,'pct_chg',2)}%，5日 {s(r,'chg5')}%，20日 {s(r,'chg20')}%，MA20偏离 {s(r,'vs_ma20')}%，"
            f"RSI6 {s(r,'rsi6')}，量比 {s(r,'vol_ratio',2)}，日支撑 {esc(r['lo20'])} / 日压力 {esc(r['hi20'])}<br>"
            f"周线：周MA10偏离 {s(r,'w_vs_ma10')}%，20周区间位置 {s(r,'w_pos20',0)}%，距20周高 {s(r,'w_from_hi20')}%，"
            f"周MACD柱 {s(r,'w_macd_bar',2)}{esc(r['w_macd_cross5'])}，周支撑 {esc(r['w_sup'])} / 周压力 {esc(r['w_res'])}")

PICK_GZ = [
 ('603259', '药明康德', '板块中军：回调中最稳、位置不过热',
  'CXO 板块今日普遍回吐，该股跌幅小于板块多数个股且量能未放大，日线仍为多头、周线维持多头，日线 MA20 偏离仅约 2.7%，RSI6 约 51.7 处于中性区。周线位置约 87%、周 MACD 红柱为正，中期结构未被破坏。下周若回踩周支撑 151.52 一带缩量企稳，属于"周多日震"中的健康回踩；跌破该位则周线多头结构转弱。'),
 ('300347', '泰格医药', '缩量回踩：量能萎缩是本次入选的核心',
  '今日下跌但量比仅约 0.56，属于明显缩量回踩而非放量出逃；日线为震荡、周线为多头，20 周区间位置约 89%，RSI6 约 52.6，未进入超买。周支撑 52.85 与日支撑 48.51 构成两级观察位。下周重点：能否在缩量基础上止跌并收复日线 MA20。'),
 ('688621', '阳光诺和', '强势整理：贴近周压力但回撤温和',
  '今日随板块回落但量比约 0.56 缩量，周线多头、20 周区间位置约 94%、距 20 周高仅 -2.3%，说明中期仍处高位区但尚未失控；RSI6 约 49.9，短线热度已明显下降。周支撑 65.72 为下周关键，守稳则维持高位整理，跌破则视为周线见顶的第一信号。'),
 ('002821', '凯莱英', '超卖修复：回调至周支撑上方的低位候选',
  '今日跌幅较大但量比约 0.89 未放量，RSI6 约 43.7 已回落至偏低区，J 值约 60；日线震荡、周线多头，20 周区间位置约 77%，距 20 周高 -10.8%，不属于高位追涨。周支撑 167.80 是关键分水岭，下周不破则具备超卖修复的条件。'),
 ('601088', '中国神华', '逆势防守：板块内唯一逆势收红的周线多头',
  '在两板块普跌的今日逆势收红，量比约 1.02 温和，周线多头、20 周区间位置约 75%，RSI6 约 66.9。其走势与 CXO/AI 硬件主线相关性低，适合作为板块回调期的防守型观察；周支撑 46.35 为防守位。'),
]

PICK_AI = [
 ('688432', '有研硅', '双周期共振且今日抗跌，结构最完整',
  '在 AI 硬件板块今日普跌背景下逆势收红，日线强多头 + 周线多头形成共振；周 MA10 偏离约 24.5%，但 20 周区间位置约 88%、距 20 周高仍有 -9.3%，即处于强势区但尚未创新高，避免了追高乖离。RSI6 约 65.2、量比约 1.00，量价平稳。周支撑 44.28 / 日支撑 37.66 为两级观察位。'),
 ('603893', '瑞芯微', '周线刚金叉 + 日线多头，回踩确认型',
  '周线 MACD 于 1 周前金叉，日线维持多头，周 MA10 偏离约 12.0%、20 周区间位置约 80%、距 20 周高 -6.3%，位置适中；今日随板块回落约 -1.78%，量比约 1.17 未见恐慌放量。RSI6 约 78.8 偏热是主要约束，下周以回踩周支撑 195.50 不破为确认条件。'),
 ('301536', '星宸科技', '周线金叉初期 + 缩量回踩',
  '周线 MACD 于 1 周前金叉，属趋势启动早期；今日回落但量比约 0.73 明显缩量，周 MA10 偏离约 7.9%、20 周区间位置约 78%、距 20 周高 -10.9%，乖离可控；RSI6 约 66.8 未过热。周支撑 121.06 为下周确认位。'),
 ('688025', '杰普特', '周线偏多、位置适中，回调温和',
  '周线偏多、日线多头，20 周区间位置约 77%、距 20 周高 -11.5%，上方仍有空间；今日小幅回落、量比约 1.19，RSI6 约 64.3 处于中性偏强区。周支撑 380.50 与日支撑 357.04 构成观察带，回踩不破则周线偏多结构延续。'),
 ('603228', '景旺电子', '缩量回踩周支撑，未破坏周线多头',
  '今日下跌但量比约 0.63 为明显缩量，周线维持多头、20 周区间位置约 81%、距 20 周高 -8.8%，RSI6 约 44.1 已回到偏低区。周支撑 94.51 与日支撑 85.60 是两级防线，下周缩量止跌可视为回踩完成。'),
]

def cards(items):
    out = []
    for code, name, title, reason in items:
        out.append(f"<div class='card'><h3>{code} {name} <span>{esc(title)}</span></h3>"
                   f"<p class='m'>{line(code)}</p><p>{esc(reason)}</p></div>")
    return '\n'.join(out)

gz = [r for r in rows if r['block'] == '关注个股']
ai = [r for r in rows if r['block'] == 'AI硬件']
def updown(rs):
    up = sum(1 for r in rs if (f(r, 'pct_chg') or 0) > 0)
    dn = sum(1 for r in rs if (f(r, 'pct_chg') or 0) < 0)
    return up, dn
gz_up, gz_dn = updown(gz)
ai_up, ai_dn = updown(ai)
gz_avg = sum(f(r, 'pct_chg') or 0 for r in gz if f(r, 'pct_chg') is not None) / max(1, len([r for r in gz if f(r, 'pct_chg') is not None]))
ai_avg = sum(f(r, 'pct_chg') or 0 for r in ai if f(r, 'pct_chg') is not None) / max(1, len([r for r in ai if f(r, 'pct_chg') is not None]))

def dist(rs):
    d = {}
    for r in rs: d[r['resonance']] = d.get(r['resonance'], 0) + 1
    return '、'.join(f'{k} {v}只' for k, v in sorted(d.items(), key=lambda x: -x[1]))

doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>关注个股与AI硬件 双周期技术面报告（2026-09-24收盘）</title><style>
*{{box-sizing:border-box}}
body{{margin:0;background:#f4f6f8;color:#20242b;font:13px/1.7 "Microsoft YaHei",Arial,sans-serif}}
.wrap{{max-width:1560px;margin:auto;padding:24px 18px 64px}}
h1{{font-size:23px;margin:0 0 6px}}
h2{{font-size:18px;border-left:4px solid #b52b2b;padding-left:10px;margin:30px 0 12px}}
h3{{font-size:15px;margin:0 0 6px}}
.meta{{color:#69727e;font-size:12px;line-height:1.85;background:#fff;border:1px solid #e1e5ea;border-radius:8px;padding:12px 15px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.card{{background:#fff;border:1px solid #e2e6eb;border-radius:8px;padding:12px 14px;margin:8px 0}}
.card h3 span{{font-size:12px;color:#245b9c;margin-left:6px}}
.card p{{margin:6px 0}}
.card p.m{{color:#5a6472;font-size:12px}}
.summary{{background:#fff;border-radius:8px;border:1px solid #e1e5ea;padding:13px 15px}}
.up{{color:#c62828;font-weight:600}}
.dn{{color:#087f45;font-weight:600}}
.flat{{color:#555}}
.na{{color:#999}}
table{{width:100%;border-collapse:collapse;background:#fff;font-size:11px;white-space:nowrap;display:block;overflow-x:auto}}
th,td{{border:1px solid #dfe4ea;padding:5px 6px;text-align:right}}
th{{background:#edf1f5;text-align:center;position:sticky;top:0}}
td.code,td.name,td.res{{text-align:left}}
td.name{{font-weight:600}}
td.res{{font-size:11px;color:#245b9c}}
small{{display:block;color:#8a929c;font-size:10px}}
.warn{{background:#fff7ef;border:1px solid #efd6bd;border-radius:8px;padding:12px 15px}}
li{{margin:5px 0}}
.foot{{border-top:1px solid #dfe4ea;margin-top:30px;padding-top:10px;color:#7a838e;font-size:11px}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><div class="wrap">
<h1>通达信自建板块「关注个股」与「AI硬件」双周期技术面报告</h1>
<div class="meta">
成分文件：<b>D:\\HT\\T0002\\blocknew\\GZGG.blk</b>（关注个股 42 只）与 <b>AIYJ.blk</b>（AI硬件 84 只），合计 126 只。<br>
行情来源：通达信本地日线 <b>D:\\HT\\vipdoc</b>，最新交易日 <b>2026-09-24 收盘</b>；日线原始为不复权，脚本对异常除权缺口作前复权近似处理，并按自然周聚合生成周线。<br>
周期定义：日线用于定位短期结构与支撑压力，周线用于判断跨周方向；<b>下周指 2026-09-28 至 2026-10-02 交易周</b>。<br>
口径限制：本周为 9/21-9/24 的<b>不完整周（仅 4 个交易日）</b>，周成交量与前 8 个完整周不可直接比较，故周线量能仅作方向参考、不用于结论；本报告不使用基本面、估值与消息面，仅作技术面结构分析。
</div>

<h2>一、结论先行：下周关注名单</h2>
<div class="grid">
<div class="summary"><h3>关注个股（CXO/医疗 + 煤炭）</h3>
<p>今日板块回吐：上涨 {gz_up} 只 / 下跌 {gz_dn} 只，平均涨跌 {gz_avg:.2f}%。共振分布：{dist(gz)}。</p>
<p><b>下周关注：</b>603259 药明康德、300347 泰格医药、688621 阳光诺和、002821 凯莱英、601088 中国神华。</p>
<p class="m">主线逻辑：CXO 中期周线仍多头，但日线今日普遍回吐，筛选重点从"追强势"转为"周线多头 + 日线缩量回踩 + 位置不过热"。</p></div>
<div class="summary"><h3>AI硬件（光模块/PCB/材料/设备）</h3>
<p>今日板块回吐：上涨 {ai_up} 只 / 下跌 {ai_dn} 只，平均涨跌 {ai_avg:.2f}%。共振分布：{dist(ai)}。</p>
<p><b>下周关注：</b>688432 有研硅、603893 瑞芯微、301536 星宸科技、688025 杰普特、603228 景旺电子。</p>
<p class="m">主线逻辑：板块内部分化显著，光模块龙头（中际旭创等）已落入双周期偏弱，资金结构更偏好周线刚金叉、位置未极端且回踩缩量的设备与材料标的。</p></div>
</div>

<h2>二、下周关注名单与入选理由：关注个股</h2>
{cards(PICK_GZ)}

<h2>三、下周关注名单与入选理由：AI硬件</h2>
{cards(PICK_AI)}

<h2>四、风险排除与失效条件</h2>
<div class="warn"><ul>
<li><b>600641 先导基电</b>：今日逆势大涨但 RSI6 约 94.4、量比约 2.20、5 日涨幅约 40%，周距 20 周高 +1.1% 已创新高，属极端过热，下周追高风险最大，不纳入。</li>
<li><b>000504 南华生物</b>：RSI6 约 94.7、量比约 6.87、5 日涨幅约 50.9%，为纯情绪博弈，技术趋势框架不适用。</li>
<li><b>301080 百普赛斯、301047 义翘神州</b>：周线虽多头，但周 MA10 偏离分别约 46.6%、41.2%，且已站上 20 周高，乖离过大，列入强势观察而非下周首选。</li>
<li><b>688293 奥浦迈</b>：周线多头但今日放量回落约 -8.88%，存在周线级别冲高回落风险，需先确认周支撑 61.66。</li>
<li><b>300308 中际旭创、688256 寒武纪、688146 中船特气、002384 东山精密、300476 胜宏科技</b>：周线偏空且 20 周区间位置偏低（多数低于 25%），属双周期偏弱，下周不作为多头候选。</li>
<li><b>688825 长鑫科技</b>：本地日线样本不足（44 根），周线指标不适用，不参与排序。<b>515880 通信ETF</b> 为板块跟踪工具，非个股。</li>
<li>统一失效条件：任一入选标的若下周跌破其对应周支撑且放量，则共振判断失效，应下调优先级；跌破周支撑后反弹未收复，视为中期结构转弱。</li>
</ul></div>

<h2>五、关注个股完整清单（42 只，按日周共振分层）</h2>
{table('关注个股')}

<h2>六、AI硬件完整清单（84 只，按日周共振分层）</h2>
{table('AI硬件')}

<div class="foot">
产物：blocknew_gzgg_aiyj_weekly_report.html（本报告）、blocknew_gzgg_aiyj_weekly_snapshot.csv（126 只日线+周线指标快照）、roster_关注个股.csv、roster_AI硬件.csv。
脚本：scripts/scan_blocknew_technicals_weekly.py（双周期扫描）、scripts/build_blocknew_weekly_report.py（本报告生成）。数据时间：2026-09-24 收盘；生成时间：2026-09-24。
字段说明：日周共振 = 日线趋势与周线趋势的组合标签；周位置 = 当前价在近 20 周高低区间中的百分位；周支撑 = max(周MA10, 20周低)，周压力 = 20 周高。
</div>
</div></body></html>'''

open(REPORT, 'w', encoding='utf-8').write(doc)
t = open(REPORT, encoding='utf-8').read()
assert t.count('<tr>') == t.count('</tr>'), 'tr 不匹配'
assert t.count('<table>') == t.count('</table>'), 'table 不匹配'
assert 'None' not in t and '%s' not in t and '\ufffd' not in t
print(REPORT)
print('rows', t.count('<tr>'), 'bytes', os.path.getsize(REPORT))

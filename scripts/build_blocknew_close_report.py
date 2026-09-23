# -*- coding: utf-8 -*-
import csv, os, html

OUT_DIR = r'D:\vcp_hunter\产业链投研\deliverables\technical-analyst\20260923'
SNAP = os.path.join(OUT_DIR, 'blocknew_gzgg_aiyj_snapshot.csv')
REPORT = os.path.join(OUT_DIR, 'blocknew_gzgg_aiyj_close_report.html')

rows = list(csv.DictReader(open(SNAP, encoding='utf-8-sig')))
for r in rows:
    if r['code'] == '515880' and r['name'] == 'N/A':
        r['name'] = '通信ETF'

def num(r, k):
    try: return float(r.get(k, ''))
    except: return None

def fval(r, k, suffix=''):
    x = num(r, k)
    return 'N/A' if x is None else f'{x:g}{suffix}'

def cls(x):
    return 'up' if x > 0 else ('dn' if x < 0 else 'flat')

def row_html(r):
    vals = [num(r,k) for k in ('pct_chg','chg5','chg20','vs_ma20','vs_ma60','macd_bar')]
    cells = [
        f"<td class='code'>{html.escape(r['mkt']+r['code'])}</td>",
        f"<td class='name'>{html.escape(r['name'])}</td>",
        f"<td>{html.escape(r['trend'])}</td>",
        f"<td>{fval(r,'close')}</td>",
        f"<td class='{cls(vals[0] or 0)}'>{fval(r,'pct_chg','%')}</td>",
        f"<td class='{cls(vals[1] or 0)}'>{fval(r,'chg5','%')}</td>",
        f"<td class='{cls(vals[2] or 0)}'>{fval(r,'chg20','%')}</td>",
        f"<td class='{cls(vals[3] or 0)}'>{fval(r,'vs_ma20','%')}</td>",
        f"<td>{fval(r,'ma5')}</td><td>{fval(r,'ma10')}</td><td>{fval(r,'ma20')}</td><td>{fval(r,'ma60')}</td>",
        f"<td>{fval(r,'macd_bar')}<small>{html.escape(r.get('macd_cross5') or '')}</small></td>",
        f"<td>{fval(r,'rsi6')}</td><td>{fval(r,'kdj_j')}</td><td>{fval(r,'boll_pos','%')}</td>",
        f"<td>{fval(r,'vol_ratio')}</td><td>{fval(r,'vol5_vs20')}</td>",
        f"<td class='{cls(vals[4] or 0)}'>{fval(r,'vs_ma60','%')}</td>",
        f"<td>{fval(r,'hi20')}</td><td>{fval(r,'lo20')}</td>",
        f"<td>{fval(r,'hi60')}</td><td>{fval(r,'lo60')}</td>",
        f"<td>{fval(r,'from_hi60','%')}</td>",
        f"<td>{fval(r,'limitups_20')}</td>",
    ]
    if r.get('error'):
        cells.append(f"<td class='na'>数据不足：{html.escape(r['error'])}</td>")
    else:
        cells.append("<td></td>")
    return '<tr>' + ''.join(cells) + '</tr>'

def table(block):
    grp = [r for r in rows if r['block'] == block]
    order = {'强多头':0,'多头':1,'震荡':2,'空头':3,'数据不足':4}
    grp.sort(key=lambda r:(order.get(r['trend'],9), -(num(r,'chg20') or -999)))
    head = '''<tr><th>代码</th><th>名称</th><th>趋势</th><th>收盘价</th><th>日涨跌</th><th>5日涨跌</th><th>20日涨跌</th><th>MA20偏离</th><th>MA5</th><th>MA10</th><th>MA20</th><th>MA60</th><th>MACD柱/交叉</th><th>RSI6</th><th>KDJ-J</th><th>BOLL位置</th><th>量比</th><th>5日量/20日量</th><th>MA60偏离</th><th>20日高</th><th>20日低</th><th>60日高</th><th>60日低</th><th>距60日高</th><th>20日涨停次数</th><th>备注</th></tr>'''
    return '<table><thead>'+head+'</thead><tbody>'+''.join(row_html(r) for r in grp)+'</tbody></table>'

def find(code):
    return next(r for r in rows if r['code'] == code)

def metrics(code):
    r = find(code)
    return f"收盘 {fval(r,'close')}，趋势{r['trend']}，5日 {fval(r,'chg5','%')}，20日 {fval(r,'chg20','%')}，MA20偏离 {fval(r,'vs_ma20','%')}，MACD柱 {fval(r,'macd_bar')}，RSI6 {fval(r,'rsi6')}，量比 {fval(r,'vol_ratio')}。"

cards_gz = [
 ('688796','百奥赛图','趋势最稳的低过热候选', '20日上涨而距离60日高点仍有空间，RSI6明显低于板块极端值；若回踩MA5/MA10缩量企稳，技术结构优于追涨股。'),
 ('002821','凯莱英','强趋势中的低量整理', '强多头排列、MACD红柱为正，短期量能未明显失控；明日重点看MA5附近承接，放量突破20日高点才算重新加速。'),
 ('300347','泰格医药','趋势延续型', '强多头且20日涨幅适中，RSI6处于可观察区间；相较CXO高位加速股，短线乖离较低。'),
 ('688428','诺诚健华','金叉后的确认标的', 'MACD近5日金叉、价格站上MA20/MA60，若明日不跌破短期均线并维持量能，趋势确认度提升。'),
 ('688621','阳光诺和','温和修复型', '多头结构、20日涨幅适中，量能未明显过热；适合观察回踩支撑后的再启动，不宜追击高开。'),
]
cards_ai = [
 ('688205','德科立','高位强趋势回踩', '20日涨幅较大但RSI6尚未极端，收盘仍在中长期均线之上；明日关注MA5/MA10附近缩量止跌，失守则降级。'),
 ('688432','有研硅','放量突破后确认', '强多头、20日涨幅较高但距60日高点仍有空间，MACD红柱为正；明日需要价格守住突破区域，防止假突破。'),
 ('688025','杰普特','趋势中继', '强多头、MACD红柱较强，RSI6约70但未极端；若沿MA5运行且量能温和，仍有趋势跟踪价值。'),
 ('300570','太辰光','金叉后趋势延续', 'MACD近期金叉，20日涨幅为正，RSI6处于中性偏强区；重点看回踩MA10是否获得承接。'),
 ('688630','芯碁微装','底部抬升观察', '强多头且MACD红柱较强，20日涨幅相对不高，属于高位板块中相对低乖离候选；需等待放量突破近期压力。'),
]

def cards(items):
    out=[]
    for code,name,title,reason in items:
        out.append(f"<div class='card'><h3>{code} {name} <span>{title}</span></h3><p>{metrics(code)}</p><p>{reason}</p></div>")
    return '\n'.join(out)

gz = [r for r in rows if r['block']=='关注个股']
ai = [r for r in rows if r['block']=='AI硬件']
def dist(rs):
    d={}
    for r in rs:d[r['trend']]=d.get(r['trend'],0)+1
    return ' / '.join(f'{k}{d.get(k,0)}只' for k in ['强多头','多头','震荡','空头','数据不足'])

html_doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>关注个股与AI硬件收盘技术面报告</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f6f8;color:#20242b;font:13px/1.65 "Microsoft YaHei",Arial,sans-serif}}.wrap{{max-width:1500px;margin:auto;padding:24px 18px 60px}}h1{{font-size:23px;margin:0 0 6px}}h2{{font-size:18px;border-left:4px solid #b52b2b;padding-left:10px;margin:28px 0 12px}}h3{{font-size:15px;margin:0 0 5px}}.meta{{color:#69727e;font-size:12px;line-height:1.8;background:#fff;border:1px solid #e1e5ea;border-radius:8px;padding:12px 15px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.card{{background:#fff;border:1px solid #e2e6eb;border-radius:8px;padding:12px 14px;margin:8px 0}}.card h3 span{{font-size:12px;color:#245b9c;margin-left:6px}}.card p{{margin:5px 0}}.summary{{background:#fff;border-radius:8px;border:1px solid #e1e5ea;padding:13px 15px}}.up{{color:#c62828;font-weight:600}}.dn{{color:#087f45;font-weight:600}}.flat{{color:#555}}.na{{color:#999}}table{{width:100%;border-collapse:collapse;background:#fff;font-size:11px;white-space:nowrap;display:block;overflow-x:auto}}th,td{{border:1px solid #dfe4ea;padding:5px 6px;text-align:right}}th{{background:#edf1f5;text-align:center;position:sticky;top:0}}td.code,td.name{{text-align:left}}td.name{{font-weight:600}}small{{display:block;color:#8a929c;font-size:10px}}.note{{color:#68727e;font-size:12px}}.warn{{background:#fff7ef;border:1px solid #efd6bd;border-radius:8px;padding:12px 15px}}li{{margin:4px 0}}.foot{{border-top:1px solid #dfe4ea;margin-top:30px;padding-top:10px;color:#7a838e;font-size:11px}}@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><div class="wrap">
<h1>通达信自建板块「关注个股」与「AI硬件」收盘技术面报告</h1>
<div class="meta">成分文件：<b>D:\\HT\\T0002\\blocknew\\GZGG.blk</b>（关注个股，42只）与 <b>AIYJ.blk</b>（AI硬件，84只）；名称来自 blocknew 名称映射。<br>行情来源：通达信本地日线 <b>D:\\HT\\vipdoc</b>，最新交易日为 <b>2026-09-23 收盘</b>；日线原始为不复权，脚本对异常除权缺口作前复权近似。技术指标为派生结果：MA、MACD、RSI、KDJ、BOLL、量比、区间高低点及趋势标签。<br>本文只做纯技术面筛选，不使用基本面、消息面和估值，也不预测次日具体价格或概率。<b>明日</b>指 2026-09-24 交易日。</div>
<h2>一、收盘结论</h2><div class="grid"><div class="summary"><h3>关注个股：CXO强势但过热分化</h3><p>趋势分布：{dist(gz)}。强多头数量较多，但百普赛斯、义翘神州、奥浦迈、南华生物等RSI6已进入高位，明日优先观察低过热、回踩承接和金叉确认标的。</p><p><b>明日优先：</b>688796 百奥赛图、002821 凯莱英、300347 泰格医药、688428 诺诚健华、688621 阳光诺和。</p></div><div class="summary"><h3>AI硬件：强趋势扩散，追高与回踩并存</h3><p>趋势分布：{dist(ai)}。设备、硅材料、光学器件方向强于部分高位光模块；德科立、有研硅等趋势强但需观察支撑，芯碁微装属于相对低乖离观察。</p><p><b>明日优先：</b>688205 德科立、688432 有研硅、688025 杰普特、300570 太辰光、688630 芯碁微装。</p></div></div>
<h2>二、明日关注名单与入选理由：关注个股</h2>{cards(cards_gz)}
<h2>三、明日关注名单与入选理由：AI硬件</h2>{cards(cards_ai)}
<h2>四、风险排除与观察条件</h2><div class="warn"><ul><li><b>000504 南华生物</b>：虽为强多头，但5日/20日涨幅和RSI6均处极端高位，属于情绪加速，不纳入明日稳健候选。</li><li><b>301080 百普赛斯、301047 义翘神州、688293 奥浦迈、688222 成都先导</b>：趋势很强但乖离和超买明显，列入“强势观察”而非首选；明日若高开冲高而量价背离，优先等待回踩。</li><li><b>688256 寒武纪</b>：收盘技术面仍属空头/弱势反抽逻辑，未纳入。</li><li><b>688825 长鑫科技</b>：本地日线不足70根，长周期指标不适用，未纳入排序。</li><li>所有关注位均为技术结构观察条件，不构成买卖指令；若明日跌破对应短期均线且放量，候选优先级应下调。</li></ul></div>
<h2>五、关注个股完整清单（42只）</h2>{table('关注个股')}
<h2>六、AI硬件完整清单（84只）</h2>{table('AI硬件')}
<div class="foot">产物：blocknew_gzgg_aiyj_close_report.html（本报告）、blocknew_gzgg_aiyj_snapshot.csv（126只指标快照）、roster_关注个股.csv、roster_AI硬件.csv。生成脚本：scripts/scan_blocknew_technicals.py；生成时间：2026-09-23。数据缺口：688825 日线样本不足；515880 为通信ETF，不是普通个股。</div>
</div></body></html>'''

open(REPORT,'w',encoding='utf-8').write(html_doc)
text=open(REPORT,encoding='utf-8').read()
assert text.count('<tr>') == text.count('</tr>')
assert text.count('<table>') == text.count('</table>')
assert 'None' not in text and '%s' not in text and '\ufffd' not in text
print(REPORT)
print('rows', text.count('<tr>'), 'bytes', os.path.getsize(REPORT))

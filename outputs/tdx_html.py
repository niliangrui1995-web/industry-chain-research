# -*- coding: utf-8 -*-
"""生成 HTML 多周期共振卡片报告（light theme）。"""
import json, os

OUT = r'D:\vcp_hunter\产业链投研\outputs'
DEL = r'D:\vcp_hunter\产业链投研\deliverables'
DATE = '2026-09-21'
DATEC = DATE.replace('-', '')

raw = json.load(open(os.path.join(OUT, 'resonance_raw.json'), encoding='utf-8'))
XDNAME = {'688131': '皓元医药', '601133': '柏诚股份'}

D = {}
ARR = {}
for bk, info in raw.items():
    ARR.setdefault(bk, [])
    for it in info['members']:
        nm = XDNAME.get(it['code'], it['name'])
        ARR[bk].append((it['code'], nm))
        if not it.get('ok'):
            continue
        d, w, m = it['daily'], it['weekly'], it['monthly']
        D[it['code']] = {'name': nm, 'bk': bk, 'c': d['close'],
                         'rsi': d['rsi14'], 'b20': d['bias']['ma20'],
                         'vr5': d['vol']['vr5'], 'v520': d['vol']['v5_over_v20'],
                         'dd': d['range250']['drawdown'], 'pos': d['range250']['pos'],
                         'm1': d['ret']['m1'], 'm3': d['ret']['m3'], 'd1': d['ret']['d1'],
                         'dma': d['mas'], 'wma': w['mas'], 'mma': m['mas'],
                         'dm': d.get('macd') or {}, 'wm': w.get('macd') or {}, 'mm': m.get('macd') or {},
                         'atp': d['atr_pct'], 'div': (d.get('divergence') or {}).get('type'),
                         'adj': it.get('adj'), 'etf': it.get('is_etf'), 'xd': it.get('xd_flag')}


def cd(t):
    return '↑' if t in ('bull', 'bull_pull') else ('↓' if t in ('bear', 'bear_bounce') else '→')


def tcls(t):
    return {'bull': 'up', 'bull_pull': 'up', 'cross': 'osc', 'bear': 'dn', 'bear_bounce': 'dn'}.get(t, 'osc')


for bk in ARR:
    for it in raw[bk]['members']:
        if it.get('ok'):
            D[it['code']]['trend'] = (tcls(it['daily']['trend_class']), tcls(it['weekly']['trend_class']),
                                      tcls(it['monthly']['trend_class']))

PICKS = {
    '关注个股': [('603259', '日 MACD 今日刚金叉'), ('301047', '回撤充分 + 位置不高'),
               ('688046', '日/周/月 MACD 三线同步'), ('688690', '月线级别确认最扎实'),
               ('002821', '中期动能最强，待放量')],
    'AI硬件': [('688432', '唯一共振且未超买'), ('300548', '周线 MACD 刚金叉'),
              ('688313', '周线刚金叉 + 温和放量'), ('300570', '量能配合最明确'),
              ('603228', '中期强、短线待企稳')],
}
REASONS = {
    '603259': '日 MACD <b>今日刚形成金叉</b>（DIF 3.163 / DEA 2.982），日 / 周 / 月三周期共振向上，周线 DIF 16.35、月线 DIF 19.24 深度多头。<b>BIAS20 仅 +6.8%</b>，是全部共振股中偏离最小者，追高风险最低；VR5 <b>1.40</b> 当日成交明显放大配合。结构最完整、最干净的启动型标的。',
    '301047': '三周期共振向上，周线 MACD 金叉（DIF 10.78），月线 DIF 虽为负但已收敛向上。<b>距 52 周高点仍有 -15.9% 空间</b>，52 周位置 72.8%，在共振股中回撤最充分者之一；RSI 69.5 未进超买区，VR5 1.32 温和放量。属「趋势已成、位置不高」的组合。',
    '688046': '三周期共振向上，周线 MACD 金叉（DIF 4.32）、月线 MACD 金叉（DIF 3.47）同步确认。<b>回撤 -15.4%，52 周位置 78.1%</b>，上方仍有修复空间；量比 5/20 = 1.11，量能温和放大而非脉冲；RSI 70.0、BIAS20 +12.9% 均未过热。',
    '688690': '三周期共振向上，<b>日、周、月三线 MACD 全部金叉</b>（月 DIF 2.27 为正），是名单中月线级别确认最扎实者；VR5 1.20，周 MA 排列 41.86 &gt; 40.77 &gt; 39.68 标准多头。需注意 RSI 76.5 与 52 周位置 94.7% 已偏高，属「强但需盯回撤」。',
    '002821': '三周期共振向上，周线 DIF <b>17.05</b>、月线 DIF <b>13.03</b>，两线均处大幅正值，中期趋势动能最强；BIAS20 仅 +10.8%、回撤 -4.5%，位置相对温和；ATR% 4.7 波动可控。短板是 VR5 1.01 量能未明显放大，属「趋势明确但需等待放量确认」。',
    '688432': '板块内<b>唯一三周期共振向上且 RSI 未超买</b>的标的（RSI 仅 <b>57.0</b>，其余共振股普遍 70+）。日 / 周 / 月 MACD 三线同步金叉。近 3 月上涨 159.9% 但当前回撤 -10.2%，说明高位已充分换手消化。<br><b>⚠ 风险：ATR% 高达 10.8%，全池波动最剧烈，须严格控制仓位。</b>',
    '300548': '<b>周线 MACD 今日刚形成金叉</b>（DIF 8.74），日线标准多头排列（230.87 &gt; 220.76 &gt; 212.71），月线维持金叉（DIF 48.19）。<b>回撤 -21.3%、52 周位置 69.9%</b>，在 AI 硬件里属修复空间较充足者；量比 5/20 = 1.06 基本持平。属「周线转折初现」的观察位。',
    '688313': '<b>周线 MACD 刚金叉</b>（DIF 11.41），日线多头排列 + 日 MACD 金叉（DIF 5.69 &gt; DEA 4.05 且开口扩大）；回撤 -17.0%、52 周位置 77.0%；量比 5/20 = <b>1.16</b> 温和放大。',
    '300570': '周线（DIF 17.42）、月线（DIF 34.82）MACD 均为扎实的正值金叉，日线重回多头排列；<b>回撤 -21.7%</b>，有较充分的调整垫；量比 5/20 = <b>1.20</b>，是 AI 硬件候选中量能配合最明确的一只。',
    '603228': '日线虽为均线交织，但<b>周线（DIF 10.28）与月线（DIF 15.23）MACD 均为多头金叉</b>，周 MA20 = 84.83 远低于现价，中期结构完好；回撤仅 -3.0%，月度涨幅 +20.2%。<br><b>⚠ 注意：日线 MACD 处于死叉状态（DIF 5.195 &lt; DEA 5.284），短线仍在调整中，属「中期强、短线待企稳」，需待日线重新金叉确认。</b>',
}
CUTS = {
    '关注个股': [('688222', 'BIAS20 <b>+34.0%</b> 严重偏离，RSI 83.0 深度超买，日线<b>顶背离</b>，KDJ J 值 111.1'),
               ('301080', 'BIAS20 <b>+30.6%</b>，近 3 月涨 <b>+143.3%</b>，日线<b>顶背离</b>，KDJ J 92.5'),
               ('688293', '52 周位置 <b>98.4%</b>、回撤仅 -0.9%，贴顶状态；RSI 76.1'),
               ('000739', '52 周位置 <b>99.4%</b>、回撤 -0.2%，几乎正处 52 周最高点；RSI 76.2'),
               ('688710', '量比 5/20 = <b>0.78</b> 明显萎缩；月线 MACD 因上市时长不足不可算，缺月线级确认'),
               ('688758', '52 周位置 97.5%、回撤 -1.3% 偏贴顶；月线 MACD 不可算；KDJ J 105.3'),
               ('688131', '今日为<b>除息日（XD）</b>，当日价格已扣股息，短期序列存在一次性扰动')],
    'AI硬件': [('688498', '同为三周期共振向上，但 <b>RSI 84.9 深度超买</b>、52 周位置 92.6%，VR5 0.99 / 量比 0.95 量能未跟进'),
              ('603186', '同为三周期共振向上，但收盘 231.70 <b>跌破 MA5（238.81）</b>，KDJ 呈 J(47.4) &lt; K(64.6) 走弱形态，VR5 <b>0.77</b> 显著缩量'),
              ('688205', 'BIAS20 +22.6%、RSI 77.4 偏高，月涨 +55.9% 短期涨幅过大，量比 0.79 缩量'),
              ('688025', '周线 MACD <b>死叉</b>（DIF 37.69），VR5 0.83 缩量，周线级别尚未修复')],
}


def fnum(v, p=2, s=''):
    return ('%.*f%s' % (p, v, s)) if v is not None else 'N/A'


def clsx(v):
    if v is None:
        return ''
    return 'up' if v > 0 else ('dn' if v < 0 else '')


H = []
H.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">')
H.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
H.append('<title>通达信自选板块 · 多周期共振技术面分析 %s</title>' % DATE)
H.append('''<style>
*{box-sizing:border-box}
body{margin:0;background:#f4f5f7;font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;color:#1f2329;line-height:1.6}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 60px}
header{background:linear-gradient(135deg,#5b4bd6,#7c4dff);color:#fff;border-radius:14px;padding:26px 28px;box-shadow:0 4px 16px rgba(92,75,214,.18)}
header h1{margin:0 0 6px;font-size:23px;letter-spacing:.5px}
header p{margin:0;font-size:13px;opacity:.88}
.meta{margin-top:12px;font-size:12px;opacity:.8;line-height:1.8}
h2{font-size:19px;margin:34px 0 14px;padding-left:11px;border-left:4px solid #5b4bd6}
h3{font-size:16px;margin:22px 0 12px;color:#3d4450}
.card{background:#fff;border:1px solid #e6e8eb;border-radius:12px;padding:20px 22px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.warn{background:#fff8e6;border:1px solid #f5d98a;border-radius:10px;padding:14px 18px;font-size:13px;color:#7a5b00;margin:14px 0}
.warn b{color:#8a6100}
.sum{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0}
.stat{flex:1;min-width:150px;background:#fff;border:1px solid #e6e8eb;border-radius:10px;padding:14px 16px}
.stat .lb{font-size:12px;color:#8a9099}
.stat .vl{font-size:24px;font-weight:700;margin-top:3px}
.stat .sub{font-size:11px;color:#a0a6ad;margin-top:2px}
.up{color:#d93025}.dn{color:#12a15c}.osc{color:#8a9099}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}
.pick{background:#fff;border:1px solid #e6e8eb;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.pick .hd{background:linear-gradient(135deg,#5b4bd6,#7c4dff);color:#fff;padding:12px 16px;display:flex;justify-content:space-between;align-items:baseline}
.pick .hd .nm{font-size:15px;font-weight:600}
.pick .hd .cd{font-size:12px;opacity:.85;font-family:ui-monospace,Consolas,monospace}
.pick .bd{padding:14px 16px}
.pick .px{font-size:22px;font-weight:700;margin-bottom:8px}
.pick .px small{font-size:12px;font-weight:400;color:#8a9099;margin-left:6px}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th,td{padding:7px 8px;border-bottom:1px solid #eef0f2;text-align:right}
th{background:#f8f9fb;color:#5b6169;font-weight:600;text-align:right;font-size:12px}
th:first-child,td:first-child{text-align:left}
td.c,th.c{text-align:center}
tbody tr:hover{background:#fafbff}
.tag{display:inline-block;padding:1px 6px;border-radius:4px;font-size:11px;margin-left:4px}
.t-red{background:#fdeceb;color:#c9302c}.t-grn{background:#e8f6ef;color:#0f8b52}
.t-gry{background:#f0f1f3;color:#6b7178}.t-pur{background:#f0ecff;color:#5b4bd6}
.reason{font-size:12.5px;color:#4a5058;border-top:1px dashed #e6e8eb;margin-top:10px;padding-top:10px}
ol.rs{margin:6px 0 0;padding-left:20px;font-size:12.5px;color:#4a5058}
ol.rs li{margin-bottom:7px}
details{margin-top:10px}
summary{cursor:pointer;font-size:13px;color:#5b4bd6;padding:8px 0;font-weight:600}
details table{margin-top:6px}
footer{margin-top:34px;text-align:center;font-size:11.5px;color:#98a0a8;line-height:1.9}
.mono{font-family:ui-monospace,Consolas,monospace}
.res3{display:inline-block;letter-spacing:2px;font-weight:700;font-size:15px}
</style></head><body><div class="wrap">''')

H.append('<header><h1>📊 通达信自选板块 · 多周期共振技术面分析</h1>')
H.append('<p>关注个股 + AI硬件 两板块 · 日 / 周 / 月三周期趋势一致性研判</p>')
H.append('<div class="meta">数据基准：通达信本地日线 <span class="mono">D:\\HT\\vipdoc\\*.day</span>，最新交易日 <b>%s</b>（今日收盘）<br>'
         '板块来源：<span class="mono">D:\\HT\\T0002\\blocknew\\</span>｜关注个股 → GZGG.blk（42 只）｜AI硬件 → AIYJ.blk（84 只）</div></header>' % DATE)

# 核心结论
H.append('<h2>一、核心结论</h2><div class="card">')
H.append('<div class="sum">')
H.append('<div class="stat"><div class="lb">关注个股 · 三周期共振向上</div><div class="vl up">13 <span style="font-size:14px;color:#8a9099">/ 42</span></div><div class="sub">占比 31%，技术结构最强一极</div></div>')
H.append('<div class="stat"><div class="lb">AI硬件 · 三周期共振向上</div><div class="vl dn">3 <span style="font-size:14px;color:#8a9099">/ 84</span></div><div class="sub">占比 4%，多数仍在休整</div></div>')
H.append('<div class="stat"><div class="lb">AI硬件 · 周期错位</div><div class="vl osc">77 <span style="font-size:14px;color:#8a9099">只</span></div><div class="sub">月线多头但周/日线未修复</div></div>')
H.append('<div class="stat"><div class="lb">三周期共振向下（回避）</div><div class="vl dn">3 <span style="font-size:14px;color:#8a9099">只</span></div><div class="sub">开立医疗 / 联影医疗 / 心脉医疗</div></div>')
H.append('</div>')
H.append('<ul style="font-size:13.5px;color:#4a5058;margin:6px 0 0;padding-left:20px">')
H.append('<li><b>「关注个股」板块</b>（创新药 / CXO 主线）：13 只三周期共振向上，日、周、月三线同向多头且多数已完成 MACD 三周期同步。</li>')
H.append('<li><b>「AI硬件」板块</b>（光模块 / PCB / 材料 / 算力）：2026 年 7 月经历极端杀跌后，多数标的自高点回撤 20%~57%，月线虽维持多头，但周线与日线尚未修复，属<b>大周期向上、中短期休整</b>形态。</li>')
H.append('</ul></div>')

# 明日关注
H.append('<h2>二、明日重点关注名单</h2>')
H.append('<div class="warn"><b>⚠ 重要前置说明：本报告不做「明日涨跌幅」预测。</b><br>'
         '本项目已做过 IC 回测验证——在 1 日维度下，所有技术指标的信息系数 |IC| &lt; 0.06，与随机噪声无异。'
         '下列名单的含义是：<b>技术结构与量价配合当下最健康、多周期共振最完整、且尚未出现过热透支的标的</b>，'
         '属于「值得盯盘关注」而非「判定会涨」。任何隔日走势仍受大盘、消息面与个股事件主导。</div>')

for bk in ['关注个股', 'AI硬件']:
    H.append('<h3>▍%s 板块 — 明日关注 Top 5</h3>' % bk)
    H.append('<div class="grid">')
    for i, (c, tagline) in enumerate(PICKS[bk], 1):
        r = D[c]
        tr = r['trend']
        H.append('<div class="pick"><div class="hd"><span class="nm">%d. %s</span><span class="cd">%s</span></div><div class="bd">' % (i, r['name'], c))
        H.append('<div class="px %s">%.2f <small>%s</small></div>' % (clsx(r['d1']), r['c'], fnum(r['d1'], 2, '%')))
        H.append('<table><tbody>')
        H.append('<tr><td>三周期共振</td><td class="c" colspan="3"><span class="res3 %s">%s</span> <span class="res3 %s">%s</span> <span class="res3 %s">%s</span> <span class="tag t-pur">共振向上</span></td></tr>'
                 % (tr[0], '↑' if tr[0] == 'up' else ('↓' if tr[0] == 'dn' else '→'),
                    tr[1], '↑' if tr[1] == 'up' else ('↓' if tr[1] == 'dn' else '→'),
                    tr[2], '↑' if tr[2] == 'up' else ('↓' if tr[2] == 'dn' else '→')))
        H.append('<tr><td>MACD 同步</td><td class="c" colspan="3">%s / %s / %s</td></tr>' % (r['dm'].get('state', 'N/A'), r['wm'].get('state', 'N/A'), r['mm'].get('state', 'N/A')))
        H.append('<tr><td>BIAS20</td><td class="c %s">%s</td><td>RSI14</td><td class="c %s">%s</td></tr>'
                 % (clsx(r['b20']), fnum(r['b20'], 1, '%'), 'up' if (r['rsi'] or 0) > 80 else '', fnum(r['rsi'], 1)))
        H.append('<tr><td>VR5 / 量比</td><td class="c">%s / %s</td><td>ATR%%</td><td class="c">%s</td></tr>'
                 % (fnum(r['vr5']), fnum(r['v520']), fnum(r['atp'], 1)))
        H.append('<tr><td>距 52 周高</td><td class="c dn">%s</td><td>52 周位置</td><td class="c">%s</td></tr>'
                 % (fnum(r['dd'], 1, '%'), fnum(r['pos'], 0, '%')))
        H.append('</tbody></table>')
        H.append('<div class="reason">%s</div>' % REASONS[c])
        H.append('</div></div>')
    H.append('</div>')

    H.append('<details><summary>同板块 · 因技术瑕疵被剔除者（点击展开）</summary><table><thead>'
             '<tr><th>代码</th><th>名称</th><th>剔除原因</th></tr></thead><tbody>')
    for c, rs in CUTS[bk]:
        H.append('<tr><td class="mono">%s</td><td>%s</td><td style="text-align:left;font-size:12px;color:#6b7178">%s</td></tr>' % (c, D[c]['name'], rs))
    H.append('</tbody></table></details>')

# 数据质量
H.append('<h2>三、数据质量核查（本次分析的关键前提）</h2><div class="card">')
H.append('<p style="font-size:13px;color:#4a5058;margin-top:0">本次分析在使用本地日线前完成三项校验，避免了既往踩过的坑。</p>')
H.append('<h3>1 · 跳空性质甄别（关键）</h3>')
H.append('<p style="font-size:12.5px;color:#4a5058">初检有 59 只出现单日跌幅超 11%，看似大量除权污染。经对照宽基指数后确认，<b>绝大多数并非除权，而是 2026 年 5-8 月的真实系统性暴跌</b>：</p>')
H.append('<table><thead><tr><th>日期</th><th class="c">上证指数</th><th class="c">创业板指</th><th class="c">科创50</th><th>市场性质</th></tr></thead><tbody>')
for dt, a, b, cc, note in [('2026-07-17', -3.05, -7.15, -7.12, '全市场暴跌，个股跌停潮'),
                           ('2026-07-20', 0.85, 0.42, 0.19, '指数企稳但 AI 板块二次崩盘'),
                           ('2026-07-21', None, 7.05, None, '报复性反弹'),
                           ('2026-07-28', -1.16, -7.35, -6.33, '二次杀跌'),
                           ('2026-08-19', -2.40, -6.26, -6.89, '再度杀跌')]:
    H.append('<tr><td class="mono">%s</td><td class="c %s">%s</td><td class="c %s">%s</td><td class="c %s">%s</td><td style="text-align:left;font-size:12px">%s</td></tr>'
             % (dt, clsx(a), fnum(a, 2, '%'), clsx(b), fnum(b, 2, '%'), clsx(cc), fnum(cc, 2, '%'), note))
H.append('</tbody></table>')
H.append('<p style="font-size:12.5px;color:#6b7178;margin-top:8px">例如太辰光 2026-07-20 高开 163.00 后崩至收盘 139.31（-11.87%）、德福科技当日跌停封死 -20.00%，均为真实成交而非除权跳空。</p>')
H.append('<h3>2 · 真除权股的精确定位与修正</h3>')
H.append('<p style="font-size:12.5px;color:#4a5058">改用「是否突破法定涨跌幅限制」作为硬判据（沪主板 ±10%、科创 / 创业 ±20%、北交所 ±30%），精确定位出 <b>11 只真实除权个股</b>，并通过通达信 MCP 取前复权基准价计算出复权因子完成修正：</p>')
H.append('<table><thead><tr><th>代码</th><th>名称</th><th class="c">除权日</th><th class="c">前复权因子</th><th>推算方案</th></tr></thead><tbody>')
for c, dt, f, sch in [('688498', '2026-05-18', 0.689, '约 10 转 4.5 股'), ('688256', '2026-05-08', 0.671, '约 10 转 4.9 股'),
                      ('300394', '2026-06-12', 0.712, '约 10 转 4 股'), ('300502', '2026-06-11', 0.713, '约 10 转 4 股'),
                      ('688195', '2026-05-29', 0.714, '约 10 转 4 股'), ('301128', '2026-05-19', 0.711, '约 10 转 4 股'),
                      ('688167', '2026-06-10', 0.690, '约 10 转 4.5 股'), ('688800', '2026-06-17', 0.713, '约 10 转 4 股'),
                      ('002975', '2026-05-11', 0.769, '约 10 转 3 股'), ('002837', '2026-06-01', 0.768, '约 10 转 3 股'),
                      ('301591', '2026-05-27', 0.767, '约 10 转 3 股')]:
    H.append('<tr><td class="mono">%s</td><td>%s</td><td class="c mono">%s</td><td class="c">%.3f</td><td style="text-align:left;font-size:12px">%s</td></tr>'
             % (c, D[c]['name'], dt, f, sch))
H.append('</tbody></table>')
H.append('<p style="font-size:12.5px;color:#6b7178;margin-top:8px">若不修正，源杰科技的 MA / MACD / KDJ 会因 5 月的伪跳空而系统性失真。修正后其 K 线恢复连续，仍判定为三周期共振向上。</p>')
H.append('<h3>3 · 数据可用性排除</h3>')
H.append('<table><thead><tr><th>代码</th><th>名称</th><th>状态</th></tr></thead><tbody>')
H.append('<tr><td class="mono">688825</td><td>长鑫科技</td><td style="text-align:left;font-size:12px;color:#6b7178">次新股，仅 41 根日线，MA60 / 月线不可算 → <b>已排除出筛选</b></td></tr>')
H.append('<tr><td class="mono">515880</td><td>通信ETF国泰</td><td style="text-align:left;font-size:12px;color:#6b7178">基金 / ETF，2026-07-06 曾发生份额折算（-52.06%），不参与个股技术面筛选</td></tr>')
H.append('<tr><td class="mono">688432 / 688143 / 688146 / 000504</td><td>有研硅 / 长盈通 / 中船特气 / 南华生物</td><td style="text-align:left;font-size:12px;color:#6b7178">存在停牌导致的交易日缺失（非数据缺陷），已逐一核实</td></tr>')
H.append('</tbody></table>')
H.append('<p style="font-size:12px;color:#8a9099;margin-top:10px"><b>残余不确定项：</b>小额现金分红（单日跌幅 &lt; 5%）无法通过跳空阈值自动识别，对价格序列影响通常在 1%~2% 量级，属可接受误差。</p>')
H.append('</div>')

# 完整清单
H.append('<h2>四、两板块个股完整清单（126 只）</h2>')
for bk in ['关注个股', 'AI硬件']:
    n = len(ARR[bk])
    H.append('<details%s><summary>%s（%d 只）— 点击查看完整清单</summary>' % (' open' if bk == '关注个股' else '', bk, n))
    H.append('<table><thead><tr><th>#</th><th>代码</th><th>名称</th><th class="c">收盘</th><th class="c">当日%</th>'
             '<th class="c">日/周/月</th><th class="c">BIAS20</th><th class="c">RSI14</th>'
             '<th class="c">日MACD</th><th class="c">周MACD</th><th class="c">月MACD</th>'
             '<th class="c">VR5</th><th class="c">距高点</th><th>备注</th></tr></thead><tbody>')
    for i, (c, nm) in enumerate(ARR[bk], 1):
        if c not in D:
            H.append('<tr><td class="c">%d</td><td class="mono">%s</td><td>%s</td><td class="c" colspan="10">数据不足，不可参与分析</td></tr>' % (i, c, nm))
            continue
        r = D[c]
        tr = r['trend']
        sy = lambda t: ('↑' if t == 'up' else ('↓' if t == 'dn' else '→'))
        nt = []
        if r['etf']:
            nt.append('<span class="tag t-gry">ETF</span>')
        if r['xd']:
            nt.append('<span class="tag t-gry">今日除息</span>')
        if r['adj']:
            nt.append('<span class="tag t-pur">已复权</span>')
        if r['div']:
            nt.append('<span class="tag t-red">%s</span>' % r['div'])
        H.append('<tr><td class="c">%d</td><td class="mono">%s</td><td>%s</td><td class="c">%s</td><td class="c %s">%s</td>'
                 '<td class="c"><span class="%s">%s</span><span class="%s">%s</span><span class="%s">%s</span></td>'
                 '<td class="c %s">%s</td><td class="c">%s</td><td class="c">%s</td><td class="c">%s</td><td class="c">%s</td>'
                 '<td class="c">%s</td><td class="c dn">%s</td><td style="text-align:left">%s</td></tr>'
                 % (i, c, r['name'], fnum(r['c']), clsx(r['d1']), fnum(r['d1'], 2, '%'),
                    tr[0], sy(tr[0]), tr[1], sy(tr[1]), tr[2], sy(tr[2]),
                    clsx(r['b20']), fnum(r['b20'], 1, '%'), fnum(r['rsi'], 1),
                    r['dm'].get('state', 'N/A'), r['wm'].get('state', 'N/A'), r['mm'].get('state', 'N/A'),
                    fnum(r['vr5']), fnum(r['dd'], 1, '%'), ''.join(nt)))
    H.append('</tbody></table></details>')

# 风险
H.append('<h2>五、风险提示</h2><div class="card"><ol class="rs">')
H.append('<li><b>本报告不构成买卖建议，且不包含任何隔日涨跌预测。</b>本项目 IC 回测已证实：1 日维度下技术指标的预测力与噪声无异。</li>')
H.append('<li>「明日关注名单」筛选逻辑为：<b>三周期共振结构完整 + 未过度延伸（BIAS20 ≤ 25%、RSI ≤ 80）+ 未贴顶 + 量能未萎缩</b>，属结构健康度排序，不是收益预测。</li>')
H.append('<li>本池 historically 呈高 β 动量特征，回测显示<b>追高是负向行为</b>——名单中已据此剔除多只过热标的。</li>')
H.append('<li>关注个股集中在创新药 / CXO 主线，AI 硬件集中在光模块 / PCB / 算力链，<b>两条线内部高度同涨同跌，分散效应有限</b>。</li>')
H.append('<li>有研硅 ATR% 达 10.8%，单日振幅常态 10% 以上，仓位需相应压缩。</li>')
H.append('<li>皓元医药（688131）、柏诚股份（601133）今日为除息日，价格序列存在一次性扰动。</li>')
H.append('</ol></div>')
H.append('<footer>数据来源：通达信本地行情数据 <span class="mono">D:\\HT\\vipdoc</span>（截至 %s 收盘）｜板块构成：<span class="mono">GZGG.blk</span> / <span class="mono">AIYJ.blk</span><br>'
         '分析日期：%s｜本报告由通达信 AI 智能体生成，仅供技术分析参考，不构成投资建议。投资有风险，入市需谨慎。</footer>' % (DATE, DATE))
H.append('</div></body></html>')

hp = os.path.join(DEL, '多周期共振_%s.html' % DATEC)
open(hp, 'w', encoding='utf-8').write('\n'.join(H))
print('HTML:', hp, len('\n'.join(H)), 'chars')

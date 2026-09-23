# -*- coding: utf-8 -*-
"""生成 光通信880670 / CPO概念880656 技术面扫描 HTML 报告。"""
import os, csv, html, sys

sys.stdout.reconfigure(encoding='utf-8')
OUT_DIR = r'D:\vcp_hunter\产业链投研\deliverables\technical-analyst\2026-09-23'

snap = list(csv.DictReader(open(os.path.join(OUT_DIR, 'gxt_cpo_technical_snapshot.csv'), encoding='utf-8-sig')))

def f(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d

def td(x, cls=''):
    return f'<td class="{cls}">{html.escape(str(x)) if x not in (None, "") else "—"}</td>'

def pct_cls(x):
    v = f(x)
    if v is None:
        return ''
    return 'up' if v > 0 else ('dn' if v < 0 else '')

def roster_table(block):
    grp = [r for r in snap if r['block'] == block]
    rows = []
    for i, r in enumerate(grp, 1):
        if r.get('error'):
            cells = [td(i), td(r['mkt']), td(r['code']), td(r['name'])] + [td('数据不足', 'warn')] * 8
        else:
            cells = [td(i), td(r['mkt']), td(r['code']), td(r['name']),
                     td(r['close']), td(r['pct_chg'], pct_cls(r['pct_chg'])),
                     td(r['chg5'], pct_cls(r['chg5'])), td(r['chg20'], pct_cls(r['chg20'])),
                     td(r['trend']), td(r['vol_ratio']),
                     td(r['rsi6']), td(r['from_hi60'])]
            if r.get('stale') == 'True':
                cells[3] = td(r['name'] + ' ⚠️滞后', 'warn')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    head = ('<tr><th>#</th><th>市场</th><th>代码</th><th>名称</th><th>收盘</th>'
            '<th>日涨跌%</th><th>5日%</th><th>20日%</th><th>趋势</th><th>量比</th>'
            '<th>RSI6</th><th>距60日高%</th></tr>')
    return f'<table class="grid"><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'

PICKS = {
'光通信': [
 ('300516','久之洋','83','强多头；昨日 MACD 零轴上方金叉(1 日前)；收盘站上全部均线且 MA20 偏离仅 +5.4%，位置低；9/21 放量 1.16 倍突破 20 日平台上沿 36.99 附近','支撑 35.20(昨日低/MA10≈35.15)；失效位 34.70(MA20)；压力 37.50(昨日高)→38.20(60 日高)','量能仅平量(0.98)，突破确认需补量；军工属性占比高，板块联动性一般'),
 ('300603','立昂技术','79','强多头；昨日 MACD 金叉(1 日前)且柱体转正；股价贴 MA20(偏离仅 +2.2%)启动，位置低、20 日仅 +8.2% 未拥挤；RSI6=64.6、J=73 动能适中；近两日温和放量(量比 1.19)','支撑 8.10(MA20≈8.09)；失效位 7.85(MA60)；压力 8.60→9.64(60 日高)','低价股弹性大但趋势级别尚浅，金叉有效性待确认；若跌回 MA20 下方则突破失败'),
 ('300570','太辰光','79','强多头；MACD 4 日前金叉且 DIF 在零轴上方；9/18 放量 1.59 倍大阳突破 213 平台上沿，三日站稳 220 上方；5 日 +17%、20 日 +12.2%，量价齐升无背离','支撑 220.6(MA5)/213(前平台上沿)；失效位 210(MA10)；压力 243(9/18 高)→251.8(60 日高)','绝对价位高、单日振幅大；若回踩 213 失守说明假突破'),
 ('300504','天邑股份','79','强多头；MACD 2 日前金叉；昨日放量 1.75 倍涨 5.75%，创阶段新高，距 60 日高仅 -1.8%；均线多头排列刚发散','支撑 18.30(昨日低)/MA5=18.19；失效位 17.60(MA10)；压力 19.85(60 日高)，突破后看 20.5 整数关口','RSI6=85.7、J=103 短线偏热，追高需控制仓位；缩量回踩 18.3 不破为健康'),
 ('301041','金百泽','76','强多头；连续 6 日量价齐升(5 日均量/20 日=1.70)，9/16 放量 1.93 倍突破平台上沿 33.91 后沿 MA5 上行；距 60 日新高仅 -0.8%','支撑 36.15(昨日低)/MA5=35.87；失效位 34.00(MA10)；压力 37.75(60 日高)→40 整数关口','20 日累计 +40.4% 涨幅已大，J=97，存在高位放量兑现风险；跌破 MA5 应减仓观察'),
],
'CPO概念': [
 ('300684','中石科技','79','强多头；昨日放量 1.34 倍大涨 +12.02% 并 MACD 金叉(1 日前)，一举收复 MA5/10/20；距 60 日高仅 -4.2%；散热件方向，平台 78.5~106.7 突破在即','支撑 101.80(昨日低)/MA5=99.40；失效位 97.00；压力 116.66(昨日高=60 日高)','单日脉冲式放量(5 日均量仅 0.80 倍)，需后续补量确认；J=106 过热，高开过多不宜追'),
 ('603328','依顿电子','76','强多头；9/16 放量 1.87 倍涨停式大阳后，高位 13.0~14.31 平台整理 5 日未破 13 元，量能维持 1.4 倍；RSI6=66 不热，平台突破蓄势形态','支撑 13.00~13.10(平台下沿)；失效位 12.80；压力 14.31(60 日高)，放量突破则打开空间','若跌破 13 元平台下沿且放量，说明 9/16 突破资金撤退，应离场'),
 ('301085','亚康股份','71','强多头；昨日放量 1.37 倍 +11.57% 大阳逼近前高(距 60 日高 -2.1%)；均线多头排列且 MA20 偏离 +23.9% 显示强趋势','支撑 76.50~77(昨日低/缺口)；失效位 74.00；压力 87.50(昨日高=60 日高)','RSI6=87.7 接近极值，单日大阳后追高风险大；若高开低走收阴则短线见顶概率大'),
 ('300698','万马科技','69','多头排列；MACD 2 日前金叉；9/18 起三连阳逐级放量(1.37→1.49→1.47)推升，距 60 日新高仅 -0.6%，面临 28.90 前高突破窗口','支撑 28.10(昨日低)；失效位 27.10(MA5)/26.55(MA10)；压力 28.90(60 日高)','J=113 严重超买，前高附近若放量滞涨(长上影)需防假突破；突破 28.90 站稳方可看高一线'),
 ('301205','联特科技','65','多头；9/15 缩量回踩 269(20 日低点)后三连阳修复，MACD 2 日前金叉、DIF 零轴上方；RSI6=69.8 适中；光模块核心弹性标的，5 日 +20.4%','支撑 317(昨日低)/MA5=313；失效位 300(MA10/MA20≈302.8)；压力 335(昨日高)→359.6(60 日高)','昨日量比 0.91 缩量上涨，持续性待补量；高价股波动剧烈，破位 300 整数关口需止损'),
],
}

def pick_table(block):
    rows = []
    for i, (code, name, sc, reason, levels, risk) in enumerate(PICKS[block], 1):
        rows.append(
            f'<tr><td>{i}</td><td><b>{code}</b></td><td>{name}</td><td>{sc}</td>'
            f'<td class="l">{reason}</td><td class="l">{levels}</td><td class="l warn">{risk}</td></tr>')
    head = ('<tr><th>排名</th><th>代码</th><th>名称</th><th>综合分</th>'
            '<th>入选技术依据</th><th>支撑/失效位/压力</th><th>风险提示</th></tr>')
    return f'<table class="grid picks"><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'

n1 = sum(1 for r in snap if r['block'] == '光通信')
n2 = sum(1 for r in snap if r['block'] == 'CPO概念')

html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>光通信880670 / CPO概念880656 板块技术面扫描 — 2026-09-23</title>
<style>
body{{font-family:"Microsoft YaHei",sans-serif;max-width:1280px;margin:24px auto;padding:0 16px;color:#1a1a1a;background:#fafafa}}
h1{{font-size:22px;border-left:5px solid #c0392b;padding-left:10px}}
h2{{font-size:18px;margin-top:32px;border-bottom:2px solid #ddd;padding-bottom:6px}}
table.grid{{border-collapse:collapse;width:100%;font-size:12.5px;background:#fff}}
table.grid th{{background:#2c3e50;color:#fff;padding:6px 8px;text-align:left;white-space:nowrap}}
table.grid td{{border:1px solid #e0e0e0;padding:4px 8px;white-space:nowrap}}
table.picks td{{white-space:normal;vertical-align:top}}
td.l{{text-align:left}}
tr:nth-child(even){{background:#f5f7fa}}
.up{{color:#c0392b;font-weight:600}}
.dn{{color:#1e8449;font-weight:600}}
.warn{{color:#b9770e}}
.note{{background:#fff8e1;border:1px solid #f0d98c;padding:10px 14px;font-size:13px;border-radius:4px;line-height:1.7}}
.meta{{color:#666;font-size:12.5px}}
</style></head><body>
<h1>光通信(880670) / CPO概念(880656) 板块个股技术面扫描</h1>
<p class="meta">数据基准日：2026-09-22(最近完整交易日) ｜ 板块成分来源：D:\\HT\\T0002\\hq_cache\\infoharbor_block.dat
(光通信更新至 20260921、CPO概念更新至 20260918) ｜ 行情：D:\\HT\\vipdoc 本地日线(不复权→除权缺口识别+前复权近似) ｜
报告生成：2026-09-23 02:00，目标观察窗口为 9/23(周三)、9/24(周四)两个交易日</p>

<div class="note"><b>数据与口径说明：</b>① 通达信概念板块成分不以 .blk 文件存储，两个板块成分均取自
hq_cache\\infoharbor_block.dat(市场前缀 0=深/1=沪/2=北，已还原为 6 位代码)；blocknew 目录下自建板块(指数/关注个股/AI硬件/防守一波/创新药/半导体设备/黄金概念等)无光通信相关板块。
② 本地日线为不复权数据，脚本以"跳空超涨跌停幅度"近似识别除权并做前复权，个股层面可能与真实复权价存在偏差。
③ 综合分(0–100)为纯技术面规则打分：趋势 30 + MACD 12/8 + 量比 10 + RSI6 10 + 距 60 日高位置 12 + KDJ-J 6，另有过热/放量下跌惩罚；规则全文见 scripts/score_gxt_cpo_detail.py。
④ 301689(两板块均在列)上市仅 9 个交易日，数据不足；920157(仅 CPO 概念)本地无日线文件，数据不足；002860 星帅尔本地数据止于 20260921，疑停牌，已标注。
⑤ 本报告仅为技术面筛选，不构成投资建议。</div>

<h2>一、板块概览</h2>
<p>光通信 880670：去重后 <b>{n1}</b> 只；CPO概念 880656：去重后 <b>{n2}</b> 只；两板块交集 66 只(仅光通信 88 只、仅 CPO 145 只)。
趋势分布——光通信：强多头 30 / 多头 54 / 震荡 61 / 空头 8 / 数据不足 1；CPO概念：强多头 47 / 多头 79 / 震荡 72 / 空头 11 / 数据不足 2。
光通信与 CPO 当前均处强势区(强多头+多头占比 55%/60%)，但 CPO 板块内部分化剧烈，20 日涨幅超 60% 的 PCB 类个股(澳弘电子+98%、满坤科技+90%、崇达技术+89%、威尔高+83%)已处情绪极值区，本筛选主动回避此类累计涨幅过大标的。</p>

<h2>二、明后两日(9/23–9/24)重点关注名单 — 光通信 880670</h2>
<p class="meta">注：打分第 1 的中电鑫龙(84 分)经人工复核剔除——9/21 巨量 2.97 倍冲高回落收长上影(H9.60/C9.20)、9/22 缩量下跌 -2.5%，高位滞涨派筹迹象明显；汇创达(83 分)因 RSI6=87.3 短线过热让位于同分但位置更低的立昂技术。名单按综合分排序。</p>
{pick_table('光通信')}

<h2>三、明后两日(9/23–9/24)重点关注名单 — CPO概念 880656</h2>
<p class="meta">注：太辰光(300570)同时位列 CPO 概念打分第 1(79 分)，已在光通信名单中给出分析，此处不重复列入。克来机电(79 分)因 J=114.8、5 日 +24% 短线过热剔除；ST 得润(76 分)因 ST 属性剔除。</p>
{pick_table('CPO概念')}

<h2>四、光通信 880670 完整个股清单(去重后 {n1} 只)</h2>
{roster_table('光通信')}

<h2>五、CPO概念 880656 完整个股清单(去重后 {n2} 只)</h2>
{roster_table('CPO概念')}

<p class="meta">附：全量 34 项指标快照见同目录 gxt_cpo_technical_snapshot.csv；板块成分清单见 roster_光通信.csv / roster_CPO概念.csv。</p>
</body></html>"""

out = os.path.join(OUT_DIR, '光通信_CPO_板块技术面扫描_20260923.html')
open(out, 'w', encoding='utf-8').write(html_doc)

# 校验
doc = open(out, encoding='utf-8').read()
assert '%s' not in doc and 'None<' not in doc and '>nan<' not in doc
print('HTML ->', out, len(doc), 'bytes')

# -*- coding: utf-8 -*-
"""输出候选完整档案（修正板块涨跌幅限制，剔除误判的“除权”）"""
import json, os

BASE = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260921/'
OUT = 'D:/vcp_hunter/产业链投研/outputs/tdx_block_scan_20260922/'

rec = json.load(open(OUT + 'recalc.json', encoding='utf-8'))
nd = json.load(open(BASE + 'nextday.json', encoding='utf-8'))
lab = {r['full']: r for r in json.load(open(BASE + 'labeled.json', encoding='utf-8'))['rows']}
R = json.load(open(BASE + 'bars_raw.json', encoding='utf-8'))
BARS = R['bars']


def board_limit(code):
    c = code[2:]
    if code.startswith('BJ'):
        return 0.305
    if c.startswith('688') or c.startswith('689'):
        return 0.205
    if c.startswith('300') or c.startswith('301'):
        return 0.205
    return 0.105


for code in ['SZ301205', 'SH688428', 'SH688690', 'SH600330', 'SH601225',
             'SH600546', 'SZ002821', 'SH601101', 'SH688313', 'SZ300548', 'SH688498']:
    r = rec[code]
    w = r['wk']
    t = r['today']
    n = nd[code]
    ind = lab[code]['ind']
    # 真·除权探测（按板块限）
    lim = board_limit(code)
    bars = BARS[code]
    div = []
    for i in range(max(1, len(bars) - 60), len(bars)):
        ch = bars[i]['close'] / bars[i - 1]['close'] - 1
        if abs(ch) > lim:
            div.append((bars[i]['date'], round(ch * 100, 2)))
    c = t['close']

    def gap(p):
        return 'N/A' if not p else '%+.2f%%' % ((p / c - 1) * 100)
    print('=' * 78)
    print('%s %s [%s]  现价 %.2f (%+.2f%%)  换手 %.2f%%  量比 %.2f' % (
        code, r['name'], r['block'], c, t['chg'], t['hsl'], t['liangbi']))
    print('  今日 OHLC: 开%.2f 高%.2f 低%.2f 收%.2f   昨收 %.2f   振幅 %.2f%%' % (
        t['open'], t['high'], t['low'], c, r['prev_close'],
        (t['high'] - t['low']) / r['prev_close'] * 100))
    print('  日均线: MA5=%.2f MA10=%.2f MA20=%.2f MA60=%s   价vsMA5 %+.2f%%' % (
        r['ma5'], r['ma10'], r['ma20'],
        ('%.2f' % r['ma60']) if r['ma60'] else 'N/A', (c / r['ma5'] - 1) * 100))
    print('  MACD: dif=%.2f dea=%.2f hist=%.2f(前%.2f)  RSI6=%.1f RSI14=%.1f  KDJ k=%.1f d=%.1f j=%.1f' % (
        r['macd']['dif'], r['macd']['dea'], r['macd']['hist'], r['macd']['hist_prev'],
        r['rsi6'], r['rsi14'], r['kdj']['k'], r['kdj']['d'], r['kdj']['j']))
    print('  BOLL: mid=%.2f up=%.2f dn=%.2f   vr5=%s vr20=%s' % (
        r['boll']['mid'], r['boll']['up'], r['boll']['dn'],
        ('%.2f' % r['vr5']) if r['vr5'] else 'N/A',
        ('%.2f' % r['vr20']) if r['vr20'] else 'N/A'))
    print('  周线: 柱(今)=%.3f 上周=%.3f  | 柱翻正P*=%.2f(%s) 周MA4阈值=%.2f(%s) 周MA12阈值=%s(%s) 上周高=%.2f(%s)' % (
        w['hist_now'], w['hist_last'], w['p_macd0'], gap(w['p_macd0']),
        w['p_ma4'], gap(w['p_ma4']),
        ('%.2f' % w['p_ma12']) if w['p_ma12'] else 'N/A', gap(w['p_ma12']),
        w['prev_high'], gap(w['prev_high'])))
    print('  位置(9/21): pos60=%.1f pos52=%.1f  支撑=%.2f(%.2f%%) 压力=%.2f(%.2f%%)' % (
        ind.get('pos60', 0), ind.get('pos52', 0),
        n.get('sup_near', 0), n.get('sup_space', 0),
        n.get('res_near', 0), n.get('res_space', 0)))
    print('  真·除权(近60日, 板块限%.1f%%): %s' % (lim * 100, div if div else '无'))

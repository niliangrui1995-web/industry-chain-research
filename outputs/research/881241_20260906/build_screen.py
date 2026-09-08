from pathlib import Path
import json,csv

ROOT=Path(__file__).parent
members=json.loads((ROOT/'tdx_constituents.json').read_text(encoding='utf-8'))['members']
vals={r['ticker']:r for p in json.loads((ROOT/'vendor_valuations.json').read_text(encoding='utf-8')) for r in p['data']['item']}
fin={p['data']['thscode'].split('.')[0]:{i['index_id']:i['value'] for a in p['data']['abilities'] for i in a['indicators']} for p in json.loads((ROOT/'vendor_financials.json').read_text(encoding='utf-8')) if p.get('code')==0}
notes={
'300206':('优先候选','原始财报深研','估值较低、海外增长与盈利改善；Q2收入减速和研发费用下降须跟踪'),
'688617':('优先候选','原始财报深研','收入归母扣非现金流同步增长；当前估值溢价较高，需关注PFA推广和集采'),
'300677':('有条件第三候选','原始财报深研','扣非和现金流改善强；手套周期、原材料、汇兑衍生品及资本开支风险'),
'300760':('质量备选','原始财报深研','平台与海外业务质量较强，现金流改善；归母尚下降，增长性价比暂不优先'),
'002223':('观察','原始财报深研','家用品牌优势；呼吸业务和利润仍承压，等待修复'),
'688271':('观察','原始财报深研','设备收入增长但利润现金流承压，等待回款与盈利兑现'),
'300633':('暂不优先','原始财报深研','利润和现金流承压，不能以国产替代逻辑替代盈利证明'),
'688212':('暂不优先','原始财报深研','仍处亏损及投入期'),
'301367':('风险观察','原始财报与公告深研','FDA警告信事项尚待解决，销售费用扩张且归母下降'),
'300003':('暂不优先','原始财报深研','营收与归母仍承压'),
'300298':('观察','原始财报深研','CGM扩张需进一步兑现利润与成本效率'),
'688029':('观察','财报原文交叉阅读','海外收入增长但当期归母和现金流下滑'),
'688016':('观察','财报原文交叉阅读','已有成熟主动脉介入业务，扣非修复但当期增长较温和'),
'301033':('观察','财报原文交叉阅读','小规模植入器械增长，需提高现金转化与持续性'),
'688581':('观察','财报原文交叉阅读','估值较低，收入与归母尚未恢复增长'),
'002901':('观察','原始财报深研','骨科恢复，但需区分低基数修复与持续内生增长'),
'300529':('观察','原始财报深研','收入尚未回升，等待集采后的量价和新品兑现'),
'688085':('暂不优先','财报原文交叉阅读','收入恢复但扣非仍下降；调整利润不能代替报告扣非')
}
rows=[]
for m in members:
 c=m['ticker'];v=vals.get(c,{});f=fin.get(c,{})
 status,level,reason=notes.get(c,('仅初筛','厂商量化初筛','未完成公司级原始财报深研，不据此给买入结论'))
 if not m.get('latest_daily'):
  status,level,reason='行情缺口排除','分类与上市状态核对','无最近交易日日线；不按可交易股票推荐'
 rows.append(dict(ticker=c,market=m['market'],name=m.get('name') or v.get('name'),subindustry=m['subindustry'],price_date=(m.get('latest_daily') or {}).get('date'),close_cny=(m.get('latest_daily') or {}).get('close'),pe_ttm_vendor=v.get('pe_ttm'),pb_mrq_vendor=v.get('pb_mrq'),revenue_yoy_pct_vendor=f.get('calculate_operating_income_yoy_growth_ratio'),net_profit_yoy_pct_vendor=f.get('calculate_parent_holder_net_profit_yoy_growth_ratio'),roe_h1_pct_vendor=f.get('index_weighted_avg_roe'),debt_pct_vendor=f.get('assets_debt_ratio'),report_period='2026H1',decision=status,review_level=level,reason=reason))
with (ROOT/'universe_screen.csv').open('w',encoding='utf-8-sig',newline='') as fp:
 w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(ROOT/'universe_screen.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('rows',len(rows),'financial_coverage',len(fin),'reviewed',sum(r['review_level'] not in ['厂商量化初筛','分类与上市状态核对'] for r in rows))

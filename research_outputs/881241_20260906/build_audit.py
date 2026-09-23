from pathlib import Path
from decimal import Decimal
from datetime import datetime, timezone, timedelta
import json

ROOT=Path(__file__).parent
ASOF=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
CHECKED=ASOF
PRICE_AT='2026-09-04T15:00:00+08:00'
data={
 'edan': {'ticker':'300206','name':'理邦仪器','h1_url':'https://static.cninfo.com.cn/finalpage/2026-08-26/1225500907.PDF#page=7','date':'2026-08-26','fy_url':'https://static.cninfo.com.cn/finalpage/2026-03-31/1225051222.PDF#page=11','fy_date':'2026-03-31','fy_np':'305637857.53','shares':'579663346','shares_at':'2026-06-30T15:00:00+08:00','price':'11.79','h1':{'revenue':['1023518584.81','913807258.77'],'attributable_net_profit':['201841258.45','154451434.92'],'deducted_attributable_net_profit':['191217912.21','144826160.38'],'operating_cash_flow':['152901229.63','88515100.07']}},
 'apt': {'ticker':'688617','name':'惠泰医疗','h1_url':None,'date':None,'price':'251.41','h1':{'revenue':['1526351745.77','1213804906.53'],'attributable_net_profit':['537319119.80','425160981.21'],'deducted_attributable_net_profit':['528771505.05','410820730.61'],'operating_cash_flow':['549285182.90','444648652.93']}},
 'intco': {'ticker':'300677','name':'英科医疗','h1_url':'https://static.cninfo.com.cn/finalpage/2026-08-25/1225495115.PDF#page=11','date':'2026-08-25','price':'54.25','h1':{'revenue':['6909022700.33','4913439043.41'],'attributable_net_profit':['837340519.61','710439983.93'],'deducted_attributable_net_profit':['1060540163.36','400201229.00'],'operating_cash_flow':['1757744842.35','745482560.58']}},
 'mindray': {'ticker':'300760','name':'迈瑞医疗','h1_url':'https://static.cninfo.com.cn/finalpage/2026-08-29/1225529856.PDF#page=16','date':'2026-08-29','fy_url':'https://static.cninfo.com.cn/finalpage/2026-03-31/1225059012.PDF#page=20','fy_date':'2026-03-31','fy_np':'8135775409','shares':'1211799431','shares_at':'2026-08-07T15:00:00+08:00','shares_url':'https://static.cninfo.com.cn/finalpage/2026-08-11/1225466190.PDF','shares_date':'2026-08-11','price':'169.91','h1':{'revenue':['17746969604','16743003854'],'attributable_net_profit':['4796791800','5068767098'],'deducted_attributable_net_profit':['4784797726','4949323103'],'operating_cash_flow':['4876986709','3922092201']}}
}

# Verified source locators and further official figures are supplied explicitly.
override=ROOT/'audit_company_overrides.json'
if override.exists():
 for k,v in json.loads(override.read_text(encoding='utf-8')).items(): data[k].update(v)

sources=[];facts=[];checks=[]
def source(i,kind,origin,url,date):
 sources.append(dict(id=i,source_type=kind,origin_id=origin,locator=url,source_date=date,checked_at=CHECKED,status='accepted'))
def fact(i,metric,value,basis,source_ids,period,unit='currency',currency='CNY',available=None):
 f=dict(id=i,metric=metric,value=value,unit=unit,currency=currency,scale='1',basis=basis,source_refs=source_ids,period=period)
 if available: f['available_at']=available
 facts.append(f)
 return {'fact_id':i}
def gate(tier='official',n=1):return dict(min_independent_origins=n,counted_tier=tier,required_anchor_tier=tier)
def dur(year):return dict(kind='duration',start=f'{year}-01-01',end=f'{year}-06-30',frequency='half',label=f'{year}H1')
def instant(at=PRICE_AT):return dict(kind='instant',as_of=at)

source('V_PRICE','market_data_vendor','hithink:quote:20260904','mcp://hithink-finance-a-share/get_a_share_prices_snapshot?tickers=300206,688617,300677,300760','2026-09-06')
source('V_TDX','market_data_vendor','tdx:lday:20260904',str(ROOT/'tdx_constituents.json'),'2026-09-06')
# Bottom-level independence of vendor valuation feeds is not established.
# Assign one shared origin conservatively; this is a consistency check only.
source('V_PE','market_data_vendor','vendor-pe-20260904-underlying-independence-unverified',str(ROOT/'vendor_valuations.json'),'2026-09-06')
source('R_REPORT','report_under_audit','report:tdx881241:20260906',str(ROOT/'report.md'),'2026-09-06')
vals={s['ticker']:s for v in json.loads((ROOT/'vendor_valuations.json').read_text(encoding='utf-8')) for s in v['data']['item']}
cross=json.loads((ROOT/'valuation_cross.json').read_text(encoding='utf-8'))
members={s['ticker']:s for s in json.loads((ROOT/'tdx_constituents.json').read_text(encoding='utf-8'))['members']}
for key,c in data.items():
 h='S_'+key+'_H1';source(h,'official_filing',c['ticker']+':2026H1',c['h1_url'],c['date'])
 for metric,(cur,prev) in c['h1'].items():
  a=fact(key+'_'+metric+'_2026',metric,cur,'reported_consolidated_prc_gaap',[h],dur(2026),available=c['date'])
  b=fact(key+'_'+metric+'_2025',metric,prev,'reported_consolidated_prc_gaap',[h],dur(2025),available=c['date'])
  checks.append(dict(id=key+'_'+metric+'_yoy',kind='percentage',materiality='material',mode='change',current=a,base=b,period_relation='yoy',output_metric=metric+'_yoy_pct',output_basis='reported_consolidated_prc_gaap_yoy',source_gate=gate()))
 p=fact(key+'_price','close_price',c['price'],'unadjusted_close',['V_PRICE'],instant(),unit='currency_per_share')
 p2=fact(key+'_tdx_price','close_price',str(members[c['ticker']]['latest_daily']['close']),'unadjusted_close',['V_TDX'],instant(),unit='currency_per_share')
 checks.append(dict(id=key+'_price_cross',kind='cross_source',materiality='material',target=p,references=[p2],source_gate=gate('vendor_or_official'),tolerance={'relative_pct':'0','absolute_base':'0'}))
 sx='S_'+key+'_CFI';source(sx,'market_data_vendor','vendor-pe-20260904-underlying-independence-unverified',cross[key]['url'],'2026-09-04')
 v=fact(key+'_vendor_pe','pe_ttm',str(vals[c['ticker']]['pe_ttm']),'pe_ttm',['V_PE'],instant(),unit='multiple',currency=None)
 # The table claim is checked against the original vendor value. CFI remains a
 # documented corroborating page, without claiming an independent feed origin.
 v2=fact(key+'_report_pe','pe_ttm',cross[key]['pe'],'pe_ttm',['R_REPORT'],instant(),unit='multiple',currency=None)
 checks.append(dict(id=key+'_pe_report_rounding',kind='cross_source',materiality='material',target=v2,references=[v],source_gate=gate('vendor_or_official'),tolerance={'relative_pct':'0','absolute_base':'0.005'}))
 if 'shares' in c:
  ss='S_'+key+'_SHARES'
  share_origin=c['ticker']+':shares:'+c['shares_at'] if 'shares_url' in c else c['ticker']+':2026H1'
  source(ss,'official_filing',share_origin,c.get('shares_url',c['h1_url'].split('#')[0]+'#shares'),c.get('shares_date',c['date']))
  sh=fact(key+'_shares','total_shares',c['shares'],'total_shares_outstanding',[ss],instant(c['shares_at']),unit='share',currency=None)
  checks.append(dict(id=key+'_market_cap',kind='market_cap',materiality='material',price=p,shares=sh,capitalization_basis='total',max_share_age_days=120,source_gate={'min_independent_origins':2,'counted_tier':'vendor_or_official','required_anchor_tier':'official'}))
 if 'fy_np' in c and 'shares' in c:
  fs='S_'+key+'_FY';source(fs,'official_filing',c['ticker']+':2025FY',c['fy_url'],c['fy_date'])
  fy=fact(key+'_fy_np','attributable_net_profit',c['fy_np'],'fy_attributable_net_profit',[fs],dict(kind='duration',start='2025-01-01',end='2025-12-31',frequency='year',label='FY2025'),available=c['fy_date'])
  checks.append(dict(id=key+'_pe_fy2025',kind='valuation',materiality='material',metric='pe',numerator={'check_id':key+'_market_cap','output':'value'},denominator_low=fy,denominator_high=fy,valuation_basis='fy_attributable_net_profit',source_gate={'min_independent_origins':2,'counted_tier':'vendor_or_official','required_anchor_tier':'official'}))

payload=dict(schema_version='1.0',audit_id='tdx881241-20260906',as_of=ASOF,sources=sources,facts=facts,checks=checks)
(ROOT/'evidence_audit_input.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'core_company_facts.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('checks',len(checks),'facts',len(facts))

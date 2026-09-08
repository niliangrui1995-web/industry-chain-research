import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
raw = json.loads((ROOT / 'financial_inputs.json').read_text(encoding='utf-8'))
vendor = json.loads((ROOT / 'vendor_snapshots.json').read_text(encoding='utf-8'))
local = json.loads((ROOT / 'market_local.json').read_text(encoding='utf-8'))
tdx = json.loads((ROOT / 'tdx_valuation_crosscheck.json').read_text(encoding='utf-8'))
now = datetime.now(timezone.utc).isoformat()
package = {'schema_version': '1.0', 'audit_id': '880652-20260906', 'as_of': now, 'sources': [], 'facts': [], 'checks': []}

def source(sid, kind, origin, locator, date):
    package['sources'].append({'id': sid, 'source_type': kind, 'origin_id': origin, 'locator': locator, 'source_date': date, 'checked_at': now, 'status': 'accepted'})

def fact(fid, metric, value, unit, currency, scale, period, basis, sid, available=None):
    row = {'id': fid, 'metric': metric, 'value': str(value), 'unit': unit, 'currency': currency, 'scale': str(scale), 'period': period, 'basis': basis, 'source_refs': [sid]}
    if available:
        row['available_at'] = available
    package['facts'].append(row)
    return {'fact_id': fid}

def cross(cid, target, refs, tier, n=1, absolute='0', relative='0'):
    package['checks'].append({'id': cid, 'kind': 'cross_source', 'materiality': 'material', 'target': target, 'references': refs, 'source_gate': {'min_independent_origins': n, 'counted_tier': tier, 'required_anchor_tier': tier}, 'tolerance': {'relative_pct': relative, 'absolute_base': absolute}})

source('REPORT', 'report_under_audit', 'research:880652:20260906', str(ROOT / 'research_report.md'), now)
for company in raw['companies']:
    code, date = company['code'], company['date']
    sid = 'OFF_' + code
    source(sid, 'official_filing', code + ':2026H1', company['source'], date)
    for metric, current, prior, rounded in company['metrics']:
        refs = []
        for year, value in [('2026', current), ('2025', prior)]:
            period = {'kind': 'duration', 'start': year + '-01-01', 'end': year + '-06-30', 'frequency': 'half', 'label': year + 'H1'}
            refs.append(fact(code + '_' + metric + '_' + year, metric, value, 'currency', 'CNY', company['scale'], period, 'reported_consolidated_prc_gaap', sid, date))
        period = {'kind': 'duration', 'start': '2026-01-01', 'end': '2026-06-30', 'frequency': 'half', 'label': '2026H1'}
        claim = fact('CLAIM_' + code + '_' + metric, metric, rounded, 'currency', 'CNY', '100000000', period, 'reported_consolidated_prc_gaap', 'REPORT', date)
        cross('ROUND_' + code + '_' + metric, claim, [refs[0]], 'official', absolute='500000')
        package['checks'].append({'id': 'YOY_' + code + '_' + metric, 'kind': 'percentage', 'materiality': 'material', 'mode': 'change', 'current': refs[0], 'base': refs[1], 'period_relation': 'yoy', 'output_metric': metric + '_yoy_pct', 'output_basis': 'reported_consolidated_prc_gaap_yoy', 'source_gate': {'min_independent_origins': 1, 'counted_tier': 'official', 'required_anchor_tier': 'official'}})

instant = {'kind': 'instant', 'as_of': '2026-09-04T15:00:00+08:00'}
source('THS_PRICE', 'market_data_vendor', 'ths:prices:20260904', 'mcp:hithink-finance:prices-snapshot:950cf02c29474c028c189d6a853cebac', now)
source('THS_VAL', 'market_data_vendor', 'ths:valuation:20260904', 'mcp:hithink-finance:valuations-snapshot:32f16aa951b142c78befc1d18ea8f0be', now)
source('TDX_LOCAL', 'market_data_vendor', 'tdx:daily:20260904', str(ROOT / 'market_local.json'), now)
prices = {x['ticker']: x for x in vendor['prices']['data']['item']}
vals = {x['ticker']: x for x in vendor['valuations']['data']['item']}
for item in local['quotes']:
    code = item['ticker'][2:]
    if code not in prices:
        continue
    ths_price = fact('P_' + code, 'close_price', prices[code]['last_price'], 'currency_per_share', 'CNY', '1', instant, 'unadjusted_close', 'THS_PRICE')
    tdx_price = fact('L_' + code, 'close_price', item['close'], 'currency_per_share', 'CNY', '1', instant, 'unadjusted_close', 'TDX_LOCAL')
    cross('PRICE_' + code, ths_price, [ths_price, tdx_price], 'vendor_or_official', n=2)
for item in tdx.values():
    headers, row = item['headers'], item['data'][0]
    code = row[headers.index('sec_code')]
    sid = 'TDX_' + code
    source(sid, 'market_data_vendor', 'tdx:fundamental:20260904', str(ROOT / 'tdx_valuation_crosscheck.json') + '#' + code, now)
    pe = row[next(i for i, h in enumerate(headers) if h.startswith('市盈(TTM)'))]
    ths_ref = fact('PE_THS_' + code, 'pe_ttm', vals[code]['pe_ttm'], 'multiple', None, '1', instant, 'vendor_ttm_attributable_net_profit', 'THS_VAL')
    tdx_ref = fact('PE_TDX_' + code, 'pe_ttm', pe, 'multiple', None, '1', instant, 'vendor_ttm_attributable_net_profit', sid)
    cross('PE_' + code, ths_ref, [ths_ref, tdx_ref], 'vendor_or_official', n=2, relative='0.1')
    if code == '688578':
        shares = fact('ALLIST_SHARES', 'total_shares', '450000000', 'share', None, '1', {'kind': 'instant', 'as_of': '2026-06-30T23:59:59+08:00'}, 'total_shares_outstanding', 'OFF_688578')
        marketcap = row[next(i for i, h in enumerate(headers) if h.startswith('最新总市值'))]
        expected = fact('ALLIST_MARKET_CAP', 'total_market_cap', marketcap, 'currency', 'CNY', '1', instant, 'total_market_cap', sid)
        package['checks'].append({'id': 'MCAP_688578', 'kind': 'market_cap', 'materiality': 'material', 'price': {'fact_id': 'P_688578'}, 'shares': shares, 'expected': expected, 'capitalization_basis': 'total', 'max_share_age_days': 90, 'source_gate': {'min_independent_origins': 2, 'counted_tier': 'vendor_or_official', 'required_anchor_tier': 'official'}, 'tolerance': {'relative_pct': '0.001', 'absolute_base': '0'}})

source('DIZAL_CONTRACT', 'official_filing', '688192:20260901:license-effective', 'https://static.cninfo.com.cn/finalpage/2026-09-01/1225539616.PDF', '2026-09-01')
source('AZ_CONTRACT', 'official_customer_supplier', 'AZ:20260901:license-completion', 'https://www.astrazeneca-us.com/content/az-us/media/press-releases/2026/AstraZeneca-completes-global-license-agreement-for-oral-EGFR-inhibitor-ZEGFROVY-sunvozertinib-for-lung-cancer.html', '2026-09-01')
contract_period = {'kind': 'instant', 'as_of': '2026-08-31T23:59:59+08:00'}
contract_refs = [fact('DIZAL_UPFRONT', 'contractual_upfront_payment', '600', 'currency', 'USD', '1000000', contract_period, 'contractually_payable_not_cash_received', 'DIZAL_CONTRACT'), fact('AZ_UPFRONT', 'contractual_upfront_payment', '600', 'currency', 'USD', '1000000', contract_period, 'contractually_payable_not_cash_received', 'AZ_CONTRACT')]
contract_claim = fact('CLAIM_UPFRONT', 'contractual_upfront_payment', '6', 'currency', 'USD', '100000000', contract_period, 'contractually_payable_not_cash_received', 'REPORT')
cross('DIZAL_UPFRONT_AMOUNT', contract_claim, contract_refs, 'official', n=2)

(ROOT / 'evidence_audit.json').write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'sources': len(package['sources']), 'facts': len(package['facts']), 'checks': len(package['checks'])}, ensure_ascii=False))

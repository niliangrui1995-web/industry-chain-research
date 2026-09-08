from pathlib import Path
from decimal import Decimal
import json
import subprocess
import sys

ROOT = Path(__file__).parent
AUDITOR = Path('.agents/skills/financial-evidence-audit/scripts/financial_evidence_audit.py')
facts = json.loads((ROOT / 'core_company_facts.json').read_text(encoding='utf-8'))
vendors = {r['ticker']: r for batch in json.loads((ROOT / 'vendor_valuations.json').read_text(encoding='utf-8')) for r in batch['data']['item']}

def calc(expression):
    completed = subprocess.run([sys.executable, str(AUDITOR), 'calc', '--expr', expression], check=True, capture_output=True, text=True, encoding='utf-8')
    return {'expression': expression, **json.loads(completed.stdout)}

result = {'as_of': '2026-09-06', 'price_as_of': '2026-09-04T15:00:00+08:00', 'method': '官方FY2025归母+官方2026H1归母-官方2025H1归母；当前未复权价*最近官方总股本。calc仅作补充算术，不计入正式审计的verified_count。', 'companies': {}}
for key, c in facts.items():
    cur, prev = c['h1']['attributable_net_profit']
    profit_expr = f"{c['fy_np']} + {cur} - {prev}"
    pe_expr = f"({c['price']} * {c['shares']}) / ({profit_expr})"
    pe = calc(pe_expr)
    vendor = str(vendors[c['ticker']]['pe_ttm'])
    difference = abs(Decimal(pe['result']) - Decimal(vendor))
    assert difference <= Decimal('0.00001'), (key, pe, vendor)
    result['companies'][key] = {'ticker': c['ticker'], 'fy_source': c['fy_url'], 'h1_source': c['h1_url'], 'shares_source': c.get('shares_url', c['h1_url']), 'ttm_net_profit': calc(profit_expr), 'reconstructed_pe_ttm': pe, 'vendor_pe_ttm': vendor, 'absolute_difference': str(difference)}

result['valuation_preferences'] = {
    'notice': '以下PE区间是研究者主观要求的估值纪律，非历史分位、市场共识或目标价；固定2026H1末TTM利润及当前股本，不含未来分红、送转、稀释。盈利变化后必须重新计算。',
    'edan': {'pe_low_assumption': '18', 'pe_high_assumption': '20', 'low_price': calc('11.79 / 19.358909 * 18'), 'high_price': calc('11.79 / 19.358909 * 20')},
    'apt': {'pe_low_assumption': '33', 'pe_high_assumption': '35', 'low_price': calc('251.41 / 38.14542 * 33'), 'high_price': calc('251.41 / 38.14542 * 35')}
}
result['sensitivity'] = {
    'notice': '未来TTM利润和终点估值的假设组合，无概率权重、非预测。价格变动率=(1+假设利润增速)*假设终点PE/当前PE-1；未计分红与股本变化。',
    'edan_downside': {'earnings_change_assumption': '-10%', 'terminal_pe_assumption': '16', 'price_change_pct': calc('(0.9 * 16 / 19.358909 - 1) * 100')},
    'apt_growth_with_derating': {'earnings_change_assumption': '+25%', 'terminal_pe_assumption': '35', 'price_change_pct': calc('(1.25 * 35 / 38.14542 - 1) * 100')},
    'apt_downside': {'earnings_change_assumption': '0%', 'terminal_pe_assumption': '30', 'price_change_pct': calc('(30 / 38.14542 - 1) * 100')}
}
(ROOT / 'valuation_reconciliation_and_scenarios.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'ttm_reconciled': len(result['companies']), 'valuation_preferences': result['valuation_preferences'], 'sensitivity': result['sensitivity']}, ensure_ascii=False, indent=2))

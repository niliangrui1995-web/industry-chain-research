"""Build reproducible source and arithmetic checks for the Medicilon research note."""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE = Path(__file__).resolve().parent
ASOF = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
sources = [
    {"id": "H1", "source_type": "official_filing", "origin_id": "medicilon:2026H1:report", "locator": "https://file.finance.sina.com.cn/211.154.219.97%3A9494/MRGG/CNSESH_STOCK/2026/2026-8/2026-08-25/12526632.PDF", "source_date": "2026-08-25", "checked_at": ASOF, "status": "accepted"},
    {"id": "FY", "source_type": "official_filing", "origin_id": "medicilon:2025FY:report", "locator": "https://stockmc.xueqiu.com/202604/688202_20260423_0X7V.pdf", "source_date": "2026-04-23", "checked_at": ASOF, "status": "accepted"},
    {"id": "Q1", "source_type": "official_filing", "origin_id": "medicilon:2026Q1:report", "locator": "https://static.cninfo.com.cn/finalpage/2026-04-30/1225260265.PDF", "source_date": "2026-04-30", "checked_at": ASOF, "status": "accepted"},
    {"id": "PRICE", "source_type": "market_data_vendor", "origin_id": "hithink:688202:20260908:unadjusted", "locator": "market_snapshots.json#hithink_1", "source_date": "2026-09-08T15:00:00+08:00", "checked_at": ASOF, "status": "accepted"},
    {"id": "FORECAST", "source_type": "market_data_vendor", "origin_id": "ths:688202:20260908:forecasts", "locator": "https://basic.10jqka.com.cn/688202/worth.html", "source_date": "2026-09-08T15:00:00+08:00", "checked_at": ASOF, "status": "accepted"},
    {"id": "DRAFT", "source_type": "report_under_audit", "origin_id": "medicilon:research:20260909", "locator": "美迪西688202_深度研究.md", "source_date": ASOF, "checked_at": ASOF, "status": "accepted"},
]
facts, checks = [], []
gate = {"min_independent_origins": 1, "counted_tier": "official", "required_anchor_tier": "official"}
vendor_gate = {"min_independent_origins": 1, "counted_tier": "vendor_or_official", "required_anchor_tier": "vendor_or_official"}

def period(year, half=False):
    return {"kind": "duration", "start": f"{year}-01-01", "end": f"{year}-06-30" if half else f"{year}-12-31", "frequency": "half" if half else "year", "label": f"{year}H1" if half else f"FY{year}"}

def fact(fid, metric, value, source, when, basis="reported_consolidated_prc_gaap", unit="currency", scale="1"):
    record = {"id": fid, "metric": metric, "value": value, "unit": unit, "currency": "CNY" if unit in ("currency", "currency_per_share") else None, "scale": scale, "period": when, "basis": basis, "source_refs": [source]}
    if when["kind"] == "duration":
        record["available_at"] = next(s["source_date"] for s in sources if s["id"] == source)
    facts.append(record)
    return fid

def rounded(fid, shown, scale="100000000", absolute="500000", credible_gate=None):
    raw = next(f for f in facts if f["id"] == fid)
    claim = dict(raw, id=f"D_{fid}", value=shown, scale=scale, source_refs=["DRAFT"])
    facts.append(claim)
    checks.append({"id": f"VERIFY_{fid}", "kind": "cross_source", "materiality": "material", "target": {"fact_id": claim["id"]}, "references": [{"fact_id": fid}], "source_gate": credible_gate or gate, "tolerance": {"relative_pct": "0", "absolute_base": absolute}})

history = {
    2023: ("1365630883.93", "-33210603.10", "-57616135.66", "33318579.17"),
    2024: ("1037745730.63", "-330845821.97", "-347713168.25", "-22747595.87"),
    2025: ("1163062463.78", "-167828221.44", "-181156917.56", "105174424.03"),
}
display = {2023: ("13.66", "-0.33", "-0.58", "0.33"), 2024: ("10.38", "-3.31", "-3.48", "-0.23"), 2025: ("11.63", "-1.68", "-1.81", "1.05")}
metrics = ("revenue", "attributable_net_profit", "deducted_attributable_net_profit", "operating_cash_flow")
for year, values in history.items():
    for metric, value, shown in zip(metrics, values, display[year]):
        fid = fact(f"{metric}_{year}", metric, value, "FY", period(year))
        rounded(fid, shown)

half_values = {
    2025: ("540407246.88", "-12898356.21", "-26730367.14", "74666392.49"),
    2026: ("761474155.85", "51602435.50", "43026810.95", "134795299.53"),
}
half_display = {2025: ("5.40", "-0.1290", "-0.2673", "0.7467"), 2026: ("7.61", "0.5160", "0.4303", "1.3480")}
for year, values in half_values.items():
    for metric, value, shown in zip(metrics, values, half_display[year]):
        fid = fact(f"{metric}_{year}H1", metric, value, "H1", period(year, True))
        rounded(fid, shown, absolute="500000" if metric == "revenue" else "5000")

for metric in ("revenue", "operating_cash_flow"):
    checks.append({"id": f"YOY_{metric}_H1", "kind": "percentage", "materiality": "material", "mode": "change", "current": {"fact_id": f"{metric}_2026H1"}, "base": {"fact_id": f"{metric}_2025H1"}, "period_relation": "yoy", "output_metric": f"{metric}_yoy_pct", "output_basis": "reported_consolidated_prc_gaap_yoy", "source_gate": gate})
for metric, output in (("attributable_net_profit", "attributable_net_margin_pct"), ("deducted_attributable_net_profit", "deducted_attributable_net_margin_pct")):
    checks.append({"id": f"MARGIN_{metric}", "kind": "percentage", "materiality": "material", "mode": "ratio", "numerator": {"fact_id": f"{metric}_2026H1"}, "denominator": {"fact_id": "revenue_2026H1"}, "period_relation": "same", "output_metric": output, "output_basis": "reported_consolidated_prc_gaap_over_reported_consolidated_prc_gaap", "source_gate": gate})

for fid, metric, value, shown, basis, unit in [
    ("gross_margin_H1", "gross_margin_pct", "31.60", "31.60", "issuer_reported_gross_margin_prc_gaap", "percent"),
    ("new_orders_H1", "new_contract_value", "12.33", "12.33", "issuer_defined_new_orders", "currency"),
    ("new_orders_growth_H1", "new_orders_yoy_pct", "104.74", "104.74", "issuer_defined_new_orders_yoy", "percent"),
    ("overseas_share_H1", "overseas_revenue_share_pct", "45.70", "45.70", "issuer_reported_revenue_share", "percent"),
    ("double_filing_revenue_H1", "dual_filing_revenue", "1.67", "1.67", "issuer_reported_dual_filing_revenue", "currency"),
]:
    scale = "100000000" if unit == "currency" else "1"
    fact(fid, metric, value, "H1", period(2026, True), basis, unit, scale)
    rounded(fid, shown, scale=scale, absolute="0")

for fid, metric, value, shown in [
    ("cash_H1", "cash_and_cash_equivalents_reported_balance", "288528432.95", "2.8853"),
    ("cash_available_H1", "cash_available_on_demand", "228552588.45", "2.2855"),
    ("receivables_H1", "accounts_receivable_net", "445786733.85", "4.4579"),
    ("inventory_H1", "inventory", "208130607.42", "2.0813"),
    ("advances_H1", "contract_liabilities", "187418579.56", "1.8742"),
    ("advances_FY", "contract_liabilities", "79091953.90", "0.7909"),
    ("notes_payable_H1", "notes_payable", "150966660.00", "1.5097"),
    ("notes_payable_FY", "notes_payable", "5200000.00", "0.0520"),
    ("equity_H1", "equity_attributable_to_parent", "2002728170.24", "20.0273"),
]:
    date = "2025-12-31" if fid.endswith("FY") else "2026-06-30"
    basis = "equity_attributable_to_parent" if fid == "equity_H1" else "reported_consolidated_prc_gaap"
    fact(fid, metric, value, "H1", {"kind": "instant", "as_of": date + "T23:59:59+08:00"}, basis)
    rounded(fid, shown, absolute="5000")

for fid, metric, value, shown in [
    ("credit_impairment_H1", "credit_impairment_loss", "25556950.47", "2555.70"),
    ("capex_H1", "cash_paid_to_acquire_long_lived_assets", "108019675.11", "10801.97"),
]:
    fact(fid, metric, value, "H1", period(2026, True), "reported_consolidated_prc_gaap_loss_positive" if fid.startswith("credit") else "reported_consolidated_prc_gaap")
    rounded(fid, shown, scale="10000", absolute="50")

for fid, metric, value, shown, scale, unit in [
    ("discovery_revenue_H1", "discovery_pharmaceutical_revenue", "347188608.26", "3.47", "100000000", "currency"),
    ("preclinical_revenue_H1", "preclinical_revenue", "414243064.17", "4.14", "100000000", "currency"),
    ("discovery_growth_H1", "discovery_pharmaceutical_revenue_yoy_pct", "29.42", "29.42", "1", "percent"),
    ("preclinical_growth_H1", "preclinical_revenue_yoy_pct", "52.26", "52.26", "1", "percent"),
    ("preclinical_orders_H1", "preclinical_new_orders", "8.20", "8.20", "100000000", "currency"),
    ("discovery_orders_H1", "discovery_pharmaceutical_new_orders", "4.14", "4.14", "100000000", "currency"),
]:
    raw_scale = scale if metric.endswith("new_orders") else "1"
    fact(fid, metric, value, "H1", period(2026, True), "issuer_reported_segment_metric", unit, raw_scale)
    rounded(fid, shown, scale=scale, absolute="500000" if metric.endswith("revenue") else "0")

for fid, metric, value, shown in [
    ("receivables_gross_H1", "accounts_receivable_gross", "688235056.04", "6.88"),
    ("receivables_allowance_H1", "accounts_receivable_allowance", "242448322.19", "2.42"),
    ("restricted_cash_H1", "restricted_cash", "59975844.50", "0.60"),
    ("litigation_claim_H1", "plaintiff_damage_claim_not_recognized_loss", "150000000", "1.50"),
]:
    fact(fid, metric, value, "H1", {"kind": "instant", "as_of": "2026-06-30T23:59:59+08:00"})
    rounded(fid, shown)

fact("price", "close_price", "93.70", "PRICE", {"kind": "instant", "as_of": "2026-09-08T15:00:00+08:00"}, "unadjusted_close", "currency_per_share")
fact("shares", "total_shares", "134352184", "H1", {"kind": "instant", "as_of": "2026-06-30T23:59:59+08:00"}, "total_shares_outstanding", "share")
checks.append({"id": "MARKET_CAP", "kind": "market_cap", "materiality": "material", "price": {"fact_id": "price"}, "shares": {"fact_id": "shares"}, "capitalization_basis": "total", "max_share_age_days": 80, "source_gate": {"min_independent_origins": 2, "counted_tier": "vendor_or_official", "required_anchor_tier": "official"}})
checks.append({"id": "PB_H1", "kind": "valuation", "materiality": "material", "metric": "pb", "numerator": {"check_id": "MARKET_CAP", "output": "value"}, "denominator_low": {"fact_id": "equity_H1"}, "denominator_high": {"fact_id": "equity_H1"}, "valuation_basis": "equity_attributable_to_parent", "source_gate": {"min_independent_origins": 2, "counted_tier": "vendor_or_official", "required_anchor_tier": "official"}})
for year, mean in [(2026, "1.04"), (2027, "2.24"), (2028, "3.56")]:
    when = {"kind": "estimate", "expectation_as_of": "2026-09-08T15:00:00+08:00", "target_start": f"{year}-01-01", "target_end": f"{year}-12-31", "frequency": "year", "label": f"FY{year}E current vendor aggregate"}
    fid = fact(f"forecast_{year}", "attributable_net_profit", mean, "FORECAST", when, "fy_attributable_net_profit", scale="100000000")
    rounded(fid, mean, absolute="0", credible_gate=vendor_gate)
    checks.append({"id": f"FORWARD_PE_{year}", "kind": "valuation", "materiality": "material", "metric": "pe", "numerator": {"check_id": "MARKET_CAP", "output": "value"}, "denominator_low": {"fact_id": fid}, "denominator_high": {"fact_id": fid}, "valuation_basis": "fy_attributable_net_profit", "source_gate": {"min_independent_origins": 2, "counted_tier": "vendor_or_official", "required_anchor_tier": "official"}})

payload = {"schema_version": "1.0", "audit_id": "medicilon-688202-20260909", "as_of": ASOF, "sources": sources, "facts": facts, "checks": checks}
(BASE / "evidence-audit.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"facts": len(facts), "checks": len(checks)}, ensure_ascii=False))

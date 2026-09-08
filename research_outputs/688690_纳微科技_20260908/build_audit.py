"""Build 688690 financial evidence audit from retained original filings.

TTM and single-quarter values are explicitly deterministic derived records,
not amounts presented by the issuer. Their full formulas, input fact IDs,
scales and inherited origins are retained in external_derived_provenance.
The engine has no general addition/subtraction check; this script separately
asserts period reconciliation. Its arithmetic does not increase verified_count.
"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from decimal import Decimal, getcontext
import json
import re
from pathlib import Path

getcontext().prec = 50
ROOT = Path(__file__).resolve().parent
AS_OF = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
PRICE_AT = "2026-09-08T15:00:00+08:00"
OFF = {"min_independent_origins": 1, "counted_tier": "official", "required_anchor_tier": "official"}
MIX = {"min_independent_origins": 2, "counted_tier": "vendor_or_official", "required_anchor_tier": "official"}
PRC = "reported_consolidated_prc_gaap"
payload = {"schema_version": "1.0", "audit_id": "688690-20260908", "as_of": AS_OF, "sources": [], "facts": [], "checks": []}
ledger = []


def source(sid, kind, origin, locator, source_date):
    payload["sources"].append({"id": sid, "source_type": kind, "origin_id": origin, "locator": locator, "source_date": source_date, "checked_at": AS_OF, "status": "accepted"})


source("FY", "official_filing", "issuer:688690:2025:annual-report", "https://stockmc.xueqiu.com/202604/688690_20260416_FX2T.pdf", "2026-04-16")
source("H1", "official_filing", "issuer:688690:2026:half-year-report", "https://file.finance.sina.com.cn/211.154.219.97:9494/MRGG/CNSESH_STOCK/2026/2026-8/2026-08-27/12545796.PDF", "2026-08-27")
source("Q1", "official_filing", "issuer:688690:2026:first-quarter-report", "https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12213934", "2026-04-28")
source("QUOTE", "market_data_vendor", "ths:688690:unadjusted-daily-kline:20260908", str(ROOT / "quote_history.json"), PRICE_AT)
source("FORECAST", "market_data_vendor", "ths:688690:rolling-estimate:20260908", "https://basic.10jqka.com.cn/688690/worth.html", "2026-09-08")
source("IR", "company_ir", "issuer:688690:IR:2026-007", str(ROOT / "sources" / "IR_20260828.pdf"), "2026-08-28")
source("DRAFT", "report_under_audit", "working-paper:688690:20260908", str(ROOT / "financial_audit_input.json") + "#working-claims", AS_OF)


def duration(year, freq="year"):
    endings = {"year": "12-31", "half": "06-30", "quarter": "03-31"}
    return {"kind": "duration", "start": f"{year}-01-01", "end": f"{year}-{endings[freq]}", "frequency": freq, "label": f"{year}-{freq}"}


def locate_amount(sid, value):
    filename = {"FY": "2025FY", "H1": "2026H1"}[sid]
    content = (ROOT / "sources" / (filename + ".txt")).read_text(encoding="utf-8-sig")
    token = format(Decimal(value), ",f")
    pos = content.index(token)
    pages = re.findall(r"--- PAGE (\d+) ---", content[:pos])
    assert pages, f"Missing page locator for {sid}/{value}"
    return filename + ".pdf#page=" + pages[-1]


def fact(fid, metric, value, period, sid, basis=PRC, unit="currency", scale="10000", available=None, location=None):
    record = {"id": fid, "metric": metric, "value": str(value), "unit": unit, "currency": "CNY" if unit in ("currency", "currency_per_share") else None, "scale": scale, "period": period, "basis": basis, "source_refs": [sid] if isinstance(sid, str) else sid}
    if period["kind"] == "duration":
        record["available_at"] = available or ("2026-04-16" if sid == "FY" else "2026-08-27" if sid == "H1" else "2026-04-28")
    if location:
        record["original_document_locator"] = location
    payload["facts"].append(record)
    return record


def cross(record, absolute="0", gate=OFF):
    target = deepcopy(record)
    target["id"] = record["id"] + "_CLAIM"
    target["source_refs"] = ["DRAFT"]
    payload["facts"].append(target)
    payload["checks"].append({"id": "VERIFY_" + record["id"], "kind": "cross_source", "materiality": "material", "target": {"fact_id": target["id"]}, "references": [{"fact_id": record["id"]}], "source_gate": gate, "tolerance": {"relative_pct": "0", "absolute_base": absolute}})


annual = {
    2023: ["58686.51", "6856.63", "3158.65", "12553.05"],
    2024: ["78245.67", "8284.34", "6587.37", "13305.52"],
    2025: ["92468.96", "13600.91", "11761.48", "16832.91"],
}
metrics = ["revenue", "attributable_net_profit", "deducted_attributable_net_profit", "operating_cash_flow"]
for year, values in annual.items():
    for metric, value in zip(metrics, values):
        cross(fact(f"FY{year}_{metric}", metric, value, duration(year), "FY", location="2025FY.pdf#page=10"))
for year, values in {2025: ["41362.54", "6330.56", "5528.04", "2417.16"], 2026: ["56783.37", "13680.78", "12740.22", "10922.76"]}.items():
    for metric, value in zip(metrics, values):
        cross(fact(f"H1{year}_{metric}", metric, value, duration(year, "half"), "H1", location="2026H1.pdf#page=9"))

for metric, value in zip(metrics, ["25277.53", "6813.47", "6165.37", "1490.50"]):
    cross(fact(f"Q12026_{metric}", metric, value, duration(2026, "quarter"), "Q1", location="Q1 webpage main financial indicators; CNY 10000"))

by_id = lambda fid: next(f for f in payload["facts"] if f["id"] == fid)


def percentage(cid, current, base, relation="yoy"):
    cur = by_id(current)
    payload["checks"].append({"id": cid, "kind": "percentage", "materiality": "material", "mode": "change", "current": {"fact_id": current}, "base": {"fact_id": base}, "period_relation": relation, "output_metric": cur["metric"] + "_" + relation + "_pct", "output_basis": cur["basis"] + "_" + relation, "source_gate": OFF})


for metric in metrics:
    percentage("H1_YOY_" + metric, "H12026_" + metric, "H12025_" + metric)
for year in (2025, 2026):
    payload["checks"].append({"id": f"H1{year}_deducted_margin", "kind": "percentage", "materiality": "material", "mode": "ratio", "numerator": {"fact_id": f"H1{year}_deducted_attributable_net_profit"}, "denominator": {"fact_id": f"H1{year}_revenue"}, "period_relation": "same", "output_metric": "deducted_attributable_net_margin_pct", "output_basis": PRC + "_over_" + PRC, "source_gate": OFF})

# Exact statement amounts where available; deduction is disclosed rounded to CNY 10000 x 0.01.
for fid, metric, value, year, freq, sid, page in [
    ("FY2025_profit_exact", "attributable_net_profit", "136009139.99", 2025, "year", "FY", 130),
    ("H12026_profit_exact", "attributable_net_profit", "136807753.73", 2026, "half", "H1", 81),
    ("H12025_profit_exact", "attributable_net_profit", "63305644.09", 2025, "half", "H1", 81),
    ("H12026_revenue_exact", "revenue", "567833685.63", 2026, "half", "H1", 80),
    ("Q12026_revenue_exact", "revenue", "252775299.49", 2026, "quarter", "Q1", 0),
    ("Q12026_profit_exact", "attributable_net_profit", "68134676.89", 2026, "quarter", "Q1", 0),
]:
    cross(fact(fid, metric, value, duration(year, freq), sid, scale="1", location=locate_amount(sid, value) if sid != "Q1" else "Q1 original filing webpage financial statements"))


def derived(fid, metric, terms, period, basis):
    inputs = [by_id(x[1]) for x in terms]
    value = sum(Decimal(sign) * Decimal(rec["value"]) * Decimal(rec["scale"]) for (sign, _), rec in zip(terms, inputs))
    refs = sorted({s for rec in inputs for s in rec["source_refs"]})
    rec = fact(fid, metric, value, period, refs, basis, scale="1", available="2026-08-27")
    formula = " + ".join(f"({sign}) * {iid}.value * {iid}.scale" for sign, iid in terms)
    rec["fact_nature"] = "deterministic_derived_not_issuer_reported"
    rec["derivation"] = {"formula": formula, "input_fact_ids": [x[1] for x in terms], "arithmetic": "Decimal precision 50"}
    ledger.append({"id": fid, "formula": formula, "inputs": [{"fact_id": x[1], "sign": x[0], "value": r["value"], "scale": r["scale"], "source_refs": r["source_refs"]} for x, r in zip(terms, inputs)], "value_base_cny": str(value), "is_official_reported_value": False, "inherit_source_refs": refs, "period": period, "limitation": "Addition/subtraction is reproducible script arithmetic; not a native audit check."})
    return rec


ttm_period = {"kind": "duration", "start": "2025-07-01", "end": "2026-06-30", "frequency": "ttm", "label": "TTM ended 2026-06-30"}
derived("TTM_profit", "attributable_net_profit", [("1", "FY2025_profit_exact"), ("1", "H12026_profit_exact"), ("-1", "H12025_profit_exact")], ttm_period, "ttm_attributable_net_profit")
derived("TTM_deducted", "deducted_attributable_net_profit", [("1", "FY2025_deducted_attributable_net_profit"), ("1", "H12026_deducted_attributable_net_profit"), ("-1", "H12025_deducted_attributable_net_profit")], ttm_period, "ttm_deducted_attributable_net_profit")
q2period = {"kind": "duration", "start": "2026-04-01", "end": "2026-06-30", "frequency": "quarter", "label": "Derived Q2 2026"}
for metric, h1, q1 in [
    ("revenue", "H12026_revenue_exact", "Q12026_revenue_exact"),
    ("attributable_net_profit", "H12026_profit_exact", "Q12026_profit_exact"),
    ("deducted_attributable_net_profit", "H12026_deducted_attributable_net_profit", "Q12026_deducted_attributable_net_profit"),
]:
    rec = derived("Q22026_" + metric, metric, [("1", h1), ("-1", q1)], q2period, PRC)
    assert Decimal(rec["value"]) + Decimal(by_id(q1)["value"]) * Decimal(by_id(q1)["scale"]) == Decimal(by_id(h1)["value"]) * Decimal(by_id(h1)["scale"])
    percentage("Q2_QOQ_" + metric, rec["id"], q1, "qoq")

quote = json.loads((ROOT / "quote_history.json").read_text(encoding="utf-8-sig"))["structuredContent"]
assert quote["code"] == 0 and quote["data"]["adjust"] == "none"
assert str(quote["data"]["item"][-1]["close_price"]) == "41.4"
fact("PRICE", "close_price", "41.4", {"kind": "instant", "as_of": PRICE_AT}, "QUOTE", "unadjusted_close", "currency_per_share", "1")
cross(fact("SHARES", "total_shares", "403814765", {"kind": "instant", "as_of": "2026-06-30T23:59:59+08:00"}, "H1", "total_shares_outstanding", "share", "1", location=locate_amount("H1", "403814765.00")))
payload["checks"].append({"id": "MARKET_CAP", "kind": "market_cap", "materiality": "material", "price": {"fact_id": "PRICE"}, "shares": {"fact_id": "SHARES"}, "capitalization_basis": "total", "max_share_age_days": 90, "source_gate": MIX})

fy_profit = deepcopy(by_id("FY2025_profit_exact"))
fy_profit["id"] = "FY2025_profit_valuation"
fy_profit["basis"] = "fy_attributable_net_profit"
payload["facts"].append(fy_profit)


def valuation(cid, denominator):
    rec = by_id(denominator)
    payload["checks"].append({"id": cid, "kind": "valuation", "metric": "pe", "materiality": "material", "numerator": {"check_id": "MARKET_CAP", "output": "value"}, "denominator_low": {"fact_id": denominator}, "denominator_high": {"fact_id": denominator}, "valuation_basis": rec["basis"], "source_gate": MIX})


valuation("PE_FY2025", "FY2025_profit_valuation")
valuation("PE_TTM_profit", "TTM_profit")
valuation("PE_TTM_deducted", "TTM_deducted")
for year, value in [(2026, "2.51"), (2027, "3.54")]:
    period = {"kind": "estimate", "expectation_as_of": "2026-09-08", "target_start": f"{year}-01-01", "target_end": f"{year}-12-31", "frequency": "year", "label": f"Current vendor rolling FY{year} forecast, not PIT consensus"}
    fact(f"FY{year}E", "attributable_net_profit", value, period, "FORECAST", "fy_attributable_net_profit", scale="100000000", location="THS rolling page 2026-09-08; aggregate 4 firms, detail 3 visible firms; attribution checked against historical series matching issuer attributable profit")
    valuation(f"PE_FY{year}E", f"FY{year}E")

for fid, metric, value, year, freq, sid, basis, unit, scale, page in [
    ("H1_CORE_REVENUE", "core_microsphere_revenue", "37376.51", 2026, "half", "H1", PRC, "currency", "10000", 9),
    ("H1_CORE_YOY_DISCLOSED", "core_microsphere_revenue_yoy_pct", "56.84", 2026, "half", "H1", "issuer_disclosed_yoy", "percent", "1", 9),
    ("H1_ADJ_ATTRIB_YOY", "adjusted_attributable_net_profit_yoy_pct", "65.02", 2026, "half", "H1", "issuer_adjusted_excluding_share_based_payment", "percent", "1", 18),
    ("FULI_REVENUE_2026", "fuli_consolidated_revenue", "8379.51", 2026, "half", "H1", PRC, "currency", "10000", 206),
    ("FULI_REVENUE_2025", "fuli_consolidated_revenue", "8246.77", 2025, "half", "H1", PRC, "currency", "10000", 206),
    ("FULI_PROFIT_2026", "fuli_consolidated_net_profit", "519.77", 2026, "half", "H1", PRC, "currency", "10000", 206),
    ("FULI_PROFIT_2025", "fuli_consolidated_net_profit", "617.79", 2025, "half", "H1", PRC, "currency", "10000", 206),
    ("FULI_OCF_2026", "fuli_consolidated_operating_cash_flow", "-920.79", 2026, "half", "H1", PRC, "currency", "10000", 206),
    ("INVENTORY_IMPAIRMENT_CHARGE", "inventory_impairment_charge", "23287144.39", 2026, "half", "H1", PRC, "currency", "1", 152),
    ("FY_CORE_REVENUE", "core_chromatographic_media_revenue", "55229.12", 2025, "year", "FY", PRC, "currency", "10000", 42),
    ("FY_CORE_GROSS_MARGIN", "core_chromatographic_media_gross_margin_pct", "81.81", 2025, "year", "FY", PRC, "percent", "1", 42),
    ("FY_COLUMN_REVENUE", "chromatography_column_and_sample_preparation_revenue", "9694.63", 2025, "year", "FY", PRC, "currency", "10000", 42),
    ("FY_COLUMN_GROSS_MARGIN", "chromatography_column_and_sample_preparation_gross_margin_pct", "78.19", 2025, "year", "FY", PRC, "percent", "1", 42),
]:
    cross(fact(fid, metric, value, duration(year, freq), sid, basis, unit, scale, location=f"{'2025FY' if sid == 'FY' else '2026H1'}.pdf#page={page}"))

for fid, metric, value, date in [
    ("INVENTORY_GROSS_H1", "inventory_gross", "449422530.15", "2026-06-30"),
    ("INVENTORY_GROSS_FY", "inventory_gross", "425763481.85", "2025-12-31"),
    ("INVENTORY_ALLOWANCE_H1", "inventory_impairment_allowance", "80682462.10", "2026-06-30"),
    ("INVENTORY_ALLOWANCE_FY", "inventory_impairment_allowance", "58420402.02", "2025-12-31"),
]:
    cross(fact(fid, metric, value, {"kind": "instant", "as_of": date + "T23:59:59+08:00"}, "H1", scale="1", location="2026H1.pdf#page=152"))
percentage("FULI_REVENUE_YOY", "FULI_REVENUE_2026", "FULI_REVENUE_2025")
percentage("FULI_PROFIT_YOY", "FULI_PROFIT_2026", "FULI_PROFIT_2025")

for fid, metric, value, unit, scale, qualifier in [
    ("IR_PEPTIDE_REVENUE", "peptide_glp1_revenue", "9000", "currency", "10000", "near; management disclosure"),
    ("IR_PEPTIDE_YOY", "peptide_glp1_revenue_yoy_pct", "15", "percent", "1", "approximately; management disclosure"),
    ("IR_OLIGO_REVENUE", "oligonucleotide_chromatographic_media_revenue", "6700", "currency", "10000", "approximately; management disclosure"),
    ("IR_OLIGO_YOY", "oligonucleotide_chromatographic_media_revenue_yoy_pct", "170", "percent", "1", "approximately; management disclosure"),
    ("IR_COLUMN_REVENUE", "chromatography_analytical_consumable_revenue", "5565", "currency", "10000", "management disclosure; rounded CNY 10000"),
    ("IR_COLUMN_YOY", "chromatography_analytical_consumable_revenue_yoy_pct", "29", "percent", "1", "approximately; management disclosure"),
    ("IR_CORE_GROSS_MARGIN", "core_microsphere_gross_margin_pct", "78.94", "percent", "1", "management disclosure"),
    ("IR_COLUMN_GROSS_MARGIN", "chromatography_analytical_consumable_gross_margin_pct", "77.91", "percent", "1", "management disclosure"),
]:
    record = fact(fid, metric, value, duration(2026, "half"), "IR", "issuer_defined_segment_disclosure", unit, scale, available="2026-08-28", location="IR_20260828.pdf#page=1" if fid == "IR_CORE_GROSS_MARGIN" else "IR_20260828.pdf#page=2")
    record["disclosure_qualifier"] = qualifier
    cross(record)

payload["numeric_conflicts"] = [{
    "status": "resolved_for_report", "metric": "H12026_deducted_attributable_net_profit",
    "accepted_fact_id": "H12026_deducted_attributable_net_profit", "accepted_value_cny": "127402200",
    "excluded_claim": {"source_id": "IR", "locator": "IR_20260828.pdf#page=2", "value_cny": "109000000", "original_text": "实现扣非归母净利润1.09亿元，同比增长130%"},
    "reason": "IR narrative amount conflicts with formal H1 financial indicators; the research adopts the formal half-year report. Exclusion is field-specific; other IR operational disclosures remain accepted. No issuer correction was identified.",
}]
payload["sources"].append({
    "id": "IR_DEDUCTED_FIELD_EXCLUDED", "source_type": "company_ir", "origin_id": "issuer:688690:IR:2026-007",
    "locator": str(ROOT / "sources" / "IR_20260828.pdf") + "#page=2&field=H12026_deducted_attributable_net_profit",
    "source_date": "2026-08-28", "checked_at": AS_OF, "status": "excluded",
    "exclusion_code": "conflicts_with_formal_financial_table",
    "exclusion_reason": "Only the IR narrative deducted-profit amount CNY109000000 is excluded; formal H1 table reports CNY127402200. All other IR fields remain independently assessed.",
})
ledger.append({
    "id": "H1_deducted_margin_change_pp", "is_official_reported_value": False,
    "formula": "(12740.22 / 56783.37 - 5528.04 / 41362.54) * 100",
    "input_fact_ids": ["H12026_deducted_attributable_net_profit", "H12026_revenue", "H12025_deducted_attributable_net_profit", "H12025_revenue"],
    "value_percentage_points": str((Decimal("12740.22") / Decimal("56783.37") - Decimal("5528.04") / Decimal("41362.54")) * 100),
    "limitation": "Both component margin checks are audited; their difference is separately reproducible Decimal arithmetic, not an additional native audit check.",
})

payload["external_derived_provenance"] = ledger
payload["research_context"] = {
    "issuer": "苏州纳微科技股份有限公司", "ticker": "688690.SH",
    "formal_surprise_status": "N/A", "formal_surprise_reason": "No verifiable pre-event consensus snapshot; rolling forecasts are not event-time consensus.",
    "amount_precision": "Main financial indicators in CNY 10000 are rounded to 0.01; derived deducted profits inherit at most CNY 100 rounding for H1-Q1 and CNY 150 for TTM.",
    "forward_forecast_caution": "Vendor aggregate claims 4 institutions but detail renders 3; some reports precede H1. Values are current rolling vendor estimates, not independently reconstructed 4-firm means or formal surprise evidence.",
    "source_identity": "H1 and FY are issuer original PDFs retained from mirrors; mirror domains do not create independent origins. Q1 original announcement text was checked on Sina. H1 is unaudited.",
    "source_locator_correction": "Exact profit/revenue facts identify statements; the report text retained alongside PDFs is the authoritative local locating aid.",
}
(ROOT / "financial_audit_input.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"as_of": AS_OF, "facts": len(payload["facts"]), "checks": len(payload["checks"]), "derived": ledger}, ensure_ascii=False, indent=2))

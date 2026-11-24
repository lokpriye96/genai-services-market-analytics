"""
Data and analysis tests. Run:  python tests/test_data.py   (or pytest -q)
Each test pins a number that appears in the README, dashboard or slide, so a silent
change in the data or code fails loudly.
"""
import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
COS = {"Accenture", "TCS", "Infosys", "HCLTech", "Cognizant", "Capgemini", "Wipro", "Tech Mahindra"}


def _d():
    return json.loads((ROOT / "docs" / "data" / "dashboard_data.json").read_text())


def test_every_row_is_sourced():
    src = set(pd.read_csv(P / "sources.csv").source_id)
    for f in ["company_quarterly.csv", "ai_timeseries.csv", "market_estimates.csv", "revenue_reference.csv"]:
        df = pd.read_csv(P / f)
        for cell in df.source_id.dropna():
            for sid in str(cell).split(";"):
                assert sid.strip() in src, f"{f}: unknown source {sid}"
        assert df.source_id.notna().all(), f"{f}: unsourced row"


def test_sources_have_urls():
    s = pd.read_csv(P / "sources.csv")
    assert s.url.str.startswith("http").all()
    assert s.source_id.is_unique


def test_eight_companies_complete():
    m = pd.read_csv(P / "company_metrics.csv")
    assert set(m.company) == COS and len(m) == 8
    assert m[["revenue_q_usd_m", "revenue_q_prior_usd_m", "headcount", "headcount_prior"]].notna().all().all()


def test_revenue_pool_and_growth():
    m = pd.read_csv(P / "company_metrics.csv")
    assert round(m.revenue_runrate_usd_m.sum() / 1000, 1) == 207.8
    assert round((m.revenue_q_usd_m.sum() / m.revenue_q_prior_usd_m.sum() - 1) * 100, 1) == 5.1


def test_ai_pool_range_and_order():
    a = pd.read_csv(P / "ai_pool.csv")
    assert (a.ai_runrate_low_usd_m <= a.ai_runrate_mid_usd_m).all()
    assert (a.ai_runrate_mid_usd_m <= a.ai_runrate_high_usd_m).all()
    assert round(a.ai_runrate_mid_usd_m.sum() / 1000, 1) == 15.8
    assert round(a.ai_runrate_low_usd_m.sum() / 1000, 1) == 13.2
    assert round(a.ai_runrate_high_usd_m.sum() / 1000, 1) == 18.9
    # disclosers carry no range; estimates do
    for c in ["TCS", "HCLTech", "Infosys"]:
        r = a[a.company == c].iloc[0]
        assert r.ai_runrate_low_usd_m == r.ai_runrate_high_usd_m
    assert set(a[a.evidence_grade == "C"].company) == {"Capgemini", "Cognizant", "Wipro", "Tech Mahindra"}


def test_core_shrinks_at_indian_disclosers():
    c = {r["company"]: r for r in _d()["core_vs_ai"]}
    assert c["Infosys"]["core_growth_annualised_pct"] == -5.9
    assert c["TCS"]["core_growth_annualised_pct"] == -3.6
    assert c["HCLTech"]["core_growth_annualised_pct"] < 0
    assert c["Accenture"]["core_growth_annualised_pct"] > 0
    for r in c.values():  # core = revenue - AI at both ends
        assert abs(r["revenue_start_usd_m"] - r["ai_start_usd_m"] - r["core_start_usd_m"]) < 1
        assert abs(r["revenue_end_usd_m"] - r["ai_end_usd_m"] - r["core_end_usd_m"]) < 1


def test_project1_join():
    e = pd.read_csv(P / "p1_ci_events.csv")
    v = e[e.validation_status == "Verified"]
    assert len(v) == 80 and set(v.company) == COS


def test_scenarios():
    s = pd.DataFrame(_d()["scenarios"])
    start = s[s.year == 2026]
    assert start.total_usd_bn.nunique() == 1  # all scenarios start from the same run-rate
    t30 = s[s.year == 2030].set_index("scenario").total_usd_bn.round(1).to_dict()
    assert t30 == {"Bear": 205.2, "Base": 233.3, "Bull": 264.1}
    assert (abs(s.ai_usd_bn + s.core_usd_bn - s.total_usd_bn) < 0.05).all()


def test_sql_quality_checks_all_pass():
    q = pd.read_csv(ROOT / "outputs" / "sql_results" / "07_data_quality_checks.csv")
    assert len(q) >= 20 and (q.status == "PASS").all(), q[q.status != "PASS"]


def test_db_matches_processed():
    con = sqlite3.connect(ROOT / "db" / "genai_services.db")
    n = con.execute("SELECT COUNT(*) FROM fact_company_metrics").fetchone()[0]
    assert n == 8


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn(); print("PASS", name)
            except AssertionError as e:
                fails += 1; print("FAIL", name, e)
    print(f"{'ALL PASS' if not fails else str(fails) + ' FAILED'}")
    raise SystemExit(1 if fails else 0)

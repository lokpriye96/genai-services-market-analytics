"""
Step 3 - Analysis layer:
  * market sizing - three lenses (analyst top-down, management view, vendor-disclosed bottom-up)
  * hypothesis tests H1-H5 with an explicit test and verdict each (incl. rank correlations)
  * 2027-2030 scenarios for the eight firms: AI growth vs core-services deflation
  * bundle for the web dashboard (docs/data/dashboard_data.json)

Run:  python src/analysis.py   (after clean.py and build_db.py)
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "db" / "genai_services.db"
RES = ROOT / "outputs" / "sql_results"
OUT = ROOT / "outputs" / "analysis"
WEB = ROOT / "docs" / "data"
OUT.mkdir(parents=True, exist_ok=True)
WEB.mkdir(parents=True, exist_ok=True)

YEARS = [2027, 2028, 2029, 2030]
# Scenario levers (annual growth rates). Stated and justified in the README; editable in Excel.
SCENARIOS = {
    "Bear": {"ai_growth": [0.35, 0.22, 0.15, 0.12], "core_growth": [-0.010, -0.030, -0.035, -0.035],
             "story": "Renewal repricing passes the full ~3.5%/yr AI deflation to clients (Kotak base case) with no volume offset; AI growth fades fast as pilots stall."},
    "Base": {"ai_growth": [0.50, 0.35, 0.25, 0.20], "core_growth": [0.005, -0.010, -0.015, -0.015],
             "story": "Core drifts from today's ~+1% organic to -1.5%/yr as large contracts renew at AI-adjusted prices; AI growth halves from today's ~70-80% and keeps decelerating."},
    "Bull": {"ai_growth": [0.65, 0.45, 0.35, 0.28], "core_growth": [0.015, 0.010, 0.005, 0.005],
             "story": "Clients reinvest about half of AI savings in new work (Kotak's offset), so core stays slightly positive; agentic AI programmes scale quickly."},
}


def q(con, sql):
    return pd.read_sql_query(sql, con)


def spearman(a: pd.Series, b: pd.Series) -> float:
    return round(a.rank().corr(b.rank()), 2)


# ---------------------------------------------------------------------------
def sizing(con) -> pd.DataFrame:
    pool = pd.read_csv(RES / "02_ai_pool.csv")
    share = pd.read_csv(RES / "01_market_share.csv")
    est = q(con, "SELECT * FROM market_estimates").set_index("estimate_id")
    pmid, plo, phi = pool.pool_mid_usd_bn.iloc[0], pool.pool_low_usd_bn.iloc[0], pool.pool_high_usd_bn.iloc[0]
    eight_share = share.share_of_gartner_it_services_pct.sum() / 100
    its26 = est.loc["GARTNER_ITS_2026", "value_usd_m"] / 1000
    g26 = est.loc["GARTNER_AI_SVC_2026", "value_usd_m"] / 1000
    rev8 = share.revenue_runrate_usd_bn.sum()
    rows = [
        ("A. Analyst top-down", "Gartner: worldwide AI services spending, 2026", g26, None, None,
         "Broadest definition: includes 'indirect' AI services where AI is embedded in ordinary projects.", "GARTNER_AI_SEP26"),
        ("B. Management view", "Infosys management: AI services market", 350, 300, 400,
         "Stated as $300-400 bn; no year or definition given.", "INFY_MKT"),
        ("C. Bottom-up (this project)", "Eight firms' AI revenue run-rate, CY Q3 2026 x 4", pmid, plo, phi,
         f"Disclosed (TCS, HCLTech), derived (Infosys, Accenture) and estimated (others) - {pool.pool_pct_company_based.iloc[0]:.0f}% of the mid value rests on company figures.", "02_ai_pool.sql"),
        ("C. Bottom-up (this project)", "Implied vendor-labelled AI services market", pmid / eight_share, plo / eight_share, phi / eight_share,
         f"Eight-firm pool / their {eight_share * 100:.1f}% share of Gartner's ${its26:,.0f} bn IT services market. Assumes the rest of the market has the same AI intensity.", "derived"),
    ]
    df = pd.DataFrame(rows, columns=["lens", "measure", "value_usd_bn", "low_usd_bn", "high_usd_bn", "reading", "source"])
    df["value_usd_bn"] = df.value_usd_bn.round(1)
    implied = pmid / eight_share
    notes = {
        "eight_firm_revenue_runrate_usd_bn": round(rev8, 1),
        "eight_firm_share_of_gartner_it_services_pct": round(eight_share * 100, 1),
        "eight_firm_ai_intensity_pct": round(pmid / rev8 * 100, 1),
        "gartner_to_vendor_labelled_ratio": round(g26 / implied, 1),
        "eight_firm_share_of_gartner_ai_services_pct": round(pmid / g26 * 100, 1),
    }
    return df.round(1), notes


# ---------------------------------------------------------------------------
def hypotheses(con) -> tuple[pd.DataFrame, dict]:
    pool = pd.read_csv(RES / "02_ai_pool.csv").set_index("company")
    core = pd.read_csv(RES / "03_core_vs_ai.csv").set_index("company")
    prod = pd.read_csv(RES / "04_productivity.csv").set_index("company")
    mom = pd.read_csv(RES / "05_momentum_vs_money.csv").set_index("company")
    share = pd.read_csv(RES / "01_market_share.csv")

    rho_ai_growth = spearman(mom.ai_share_of_revenue_pct, mom.revenue_yoy_cc_pct)
    rho_mom_ai = spearman(mom.p1_events, mom.ai_share_of_revenue_pct)
    rho_mom_growth = spearman(mom.p1_events, mom.revenue_yoy_cc_pct)
    disclosed = mom[mom.ai_disclosure_grade.isin(["A", "B"])]
    rho_ai_growth_disclosed = spearman(disclosed.ai_share_of_revenue_pct, disclosed.revenue_yoy_cc_pct)
    from scipy.stats import spearmanr
    p_ai_growth = spearmanr(mom.ai_share_of_revenue_pct, mom.revenue_yoy_cc_pct).pvalue
    p_mom_ai = spearmanr(mom.p1_events, mom.ai_share_of_revenue_pct).pvalue
    p_mom_growth = spearmanr(mom.p1_events, mom.revenue_yoy_cc_pct).pvalue
    stats = {
        "spearman_ai_intensity_vs_growth_all8": rho_ai_growth,
        "spearman_ai_intensity_vs_growth_disclosers": rho_ai_growth_disclosed,
        "spearman_p1_events_vs_ai_intensity": rho_mom_ai,
        "spearman_p1_events_vs_growth": rho_mom_growth,
        "p_value_ai_intensity_vs_growth_all8": round(p_ai_growth, 2),
        "p_value_p1_events_vs_ai_intensity": round(p_mom_ai, 2),
        "p_value_p1_events_vs_growth": round(p_mom_growth, 2),
        "median_decoupling_gap_pp": round(prod.decoupling_gap_pp.median(), 2),
        "eight_firm_yoy_usd_pct": share.eight_firm_yoy_usd_pct.iloc[0],
        "gartner_it_services_growth_2026_pct": share.gartner_it_services_growth_2026_pct.iloc[0],
    }
    pool_mid = pool.pool_mid_usd_bn.iloc[0]
    rows = [
        {"id": "H1", "hypothesis": "GenAI is now material revenue, not a pilot-stage side line.",
         "test": "AI share of revenue at disclosing firms; size of the eight-firm AI pool.",
         "evidence": (f"TCS {pool.loc['TCS','ai_share_of_revenue_pct']:.1f}% and Infosys {pool.loc['Infosys','ai_share_of_revenue_pct']:.1f}% of revenue (company-disclosed); "
                      f"eight-firm AI run-rate ~${pool_mid:.1f} bn (range ${pool.pool_low_usd_bn.iloc[0]:.1f}-{pool.pool_high_usd_bn.iloc[0]:.1f} bn), "
                      f"~{pool_mid / share.revenue_runrate_usd_bn.sum() * 100:.1f}% of their combined revenue. TCS's AI run-rate rose 72% in three quarters ($1.8 bn to $3.1 bn)."),
         "verdict": "Supported",
         "so_what": "AI is now big enough to move the P&L. The open question has shifted from 'is AI real?' to 'is AI net-additive?'."},
        {"id": "H2", "hypothesis": "AI revenue growth is arriving alongside a shrinking core business (AI deflation).",
         "test": "Split revenue into AI and non-AI at two points for every firm with an AI time series; annualise each.",
         "evidence": (f"Core (non-AI) revenue shrank at all three Indian disclosers: Infosys {core.loc['Infosys','core_growth_annualised_pct']:+.1f}%/yr, "
                      f"TCS {core.loc['TCS','core_growth_annualised_pct']:+.1f}%/yr, HCLTech {core.loc['HCLTech','core_growth_annualised_pct']:+.1f}%/yr, "
                      f"while total revenue grew only {core.loc['HCLTech','total_growth_annualised_pct']:.1f}-{core.loc['TCS','total_growth_annualised_pct']:.1f}%. "
                      f"Accenture's core still grew {core.loc['Accenture','core_growth_annualised_pct']:+.1f}% (FY24-FY25)."),
         "verdict": "Directionally supported for TCS and Infosys (upper bound; TCS core rests on two data points); weaker for HCLTech; not for Accenture",
         "so_what": "At TCS and Infosys, AI growth is so far replacing core revenue, not adding to it. That fits the 2-3.5%/yr deflation analysts cite. Part of the shift may be existing work relabelled as AI, which no firm discloses."},
        {"id": "H3", "hypothesis": "The firms with the most AI revenue are not the ones growing fastest.",
         "test": "Spearman rank correlation between AI share of revenue and constant-currency revenue growth (8 firms; and the 4 company-based disclosers).",
         "evidence": (f"Rank correlation {rho_ai_growth:+.2f} across all eight (p={p_ai_growth:.2f}) and {rho_ai_growth_disclosed:+.2f} across the four disclosers (n=4, not testable). "
                      f"Five of the eight AI shares are estimates or peer benchmarks. Infosys (10.5% AI) grew 1.5%; "
                      f"TCS (10.1%) 2.8%; Capgemini (est. 8%) 11.7% incl. WNS; Tech Mahindra (est. 5%) 7.2%."),
         "verdict": "Weak: no positive link in this sample (n=8, not significant)",
         "so_what": "'AI revenue' is not yet a growth KPI. For CI and investor work, track core growth and book-to-bill next to the AI number."},
        {"id": "H4", "hypothesis": "AI has decoupled revenue from headcount.",
         "test": "Revenue growth minus headcount growth (YoY), and revenue per employee.",
         "evidence": (f"Median gap only {stats['median_decoupling_gap_pp']:+.1f}pp. Six of eight show weak or no decoupling. Revenue per employee rose 0.5-1.7% at most firms; "
                      f"Tech Mahindra is the outlier (+{prod.loc['Tech Mahindra','rev_per_employee_yoy_pct']:.1f}%, headcount down). "
                      f"Capgemini's headcount jumped {prod.loc['Capgemini','headcount_yoy_pct']:.0f}% with the WNS acquisition."),
         "verdict": "Weak - mostly not yet",
         "so_what": "Productivity gains are being passed to clients as price, not kept as margin or non-linear growth. That is the deflation mechanism in H2 seen from the people side."},
        {"id": "H5", "hypothesis": "Announcement momentum (Project 1's CI events) predicts AI monetisation.",
         "test": "Spearman rank correlation of verified Project 1 events per firm against AI share of revenue and against growth.",
         "evidence": (f"Rank correlations (n=8): events vs AI share {rho_mom_ai:+.2f} (p={p_mom_ai:.2f}); events vs growth {rho_mom_growth:+.2f} (p={p_mom_growth:.2f}, not significant). "
                      f"HCLTech and Cognizant lead on event count (12 each), with TCS and Wipro on 11. "
                      f"Wipro's revenue is flat and it discloses no AI revenue; Capgemini has no frontier-lab ties and the fastest growth (11.7% incl. WNS)."),
         "verdict": "No evidence of a link (n=8, not significant)",
         "so_what": "Partnership press releases are a weak lead indicator. A CI programme should weight disclosed AI revenue, core growth and bookings above announcement counts - the main design lesson carried back to Project 1."},
    ]
    return pd.DataFrame(rows), stats


# ---------------------------------------------------------------------------
def scenarios() -> tuple[pd.DataFrame, dict]:
    pool = pd.read_csv(RES / "02_ai_pool.csv")
    share = pd.read_csv(RES / "01_market_share.csv")
    ai0 = pool.ai_runrate_mid_usd_bn.sum()
    rev0 = share.revenue_runrate_usd_bn.sum()
    core0 = rev0 - ai0
    rows = []
    for name, s in SCENARIOS.items():
        ai, core = ai0, core0
        rows.append({"scenario": name, "year": 2026, "ai_usd_bn": ai, "core_usd_bn": core, "total_usd_bn": ai + core})
        for i, y in enumerate(YEARS):
            ai *= 1 + s["ai_growth"][i]
            core *= 1 + s["core_growth"][i]
            rows.append({"scenario": name, "year": y, "ai_usd_bn": ai, "core_usd_bn": core, "total_usd_bn": ai + core})
    df = pd.DataFrame(rows)
    df["ai_share_pct"] = df.ai_usd_bn / df.total_usd_bn * 100
    df["total_growth_pct"] = df.groupby("scenario").total_usd_bn.pct_change() * 100
    # AI growth required to hold total revenue flat, given that year's core growth
    req = []
    for _, r in df.iterrows():
        if r.year == 2026:
            req.append(None)
            continue
        prev = df[(df.scenario == r.scenario) & (df.year == r.year - 1)].iloc[0]
        cg = SCENARIOS[r.scenario]["core_growth"][YEARS.index(r.year)]
        req.append(max(0.0, -cg * prev.core_usd_bn / prev.ai_usd_bn) * 100)
    df["ai_growth_needed_for_flat_total_pct"] = req
    cagr = {n: ((g.total_usd_bn.iloc[-1] / g.total_usd_bn.iloc[0]) ** (1 / 4) - 1) * 100 for n, g in df.groupby("scenario")}
    df["cagr_2026_2030_pct"] = df.scenario.map(cagr)
    calib = {
        "start_ai_usd_bn": round(ai0, 2), "start_total_usd_bn": round(rev0, 1), "start_core_usd_bn": round(core0, 1),
        "observed_ai_growth": "TCS +72% in three quarters; HCLTech +78% YoY CC; Accenture tripled in FY25",
        "observed_core_growth": "Infosys -5.9%/yr, TCS -3.6%/yr, HCLTech -0.5%/yr (2025-26); Accenture +4.7% (FY25)",
        "deflation_benchmarks": "Kotak 3-3.5%/yr through FY29; HCLTech 2-3%; analysts 10-15% cumulative over 3-5 years",
        "gartner_it_services_growth_2026_pct": share.gartner_it_services_growth_2026_pct.iloc[0],
    }
    return df.round(2), calib


# ---------------------------------------------------------------------------
def main() -> None:
    con = sqlite3.connect(DB)
    size_df, size_notes = sizing(con)
    hyp, stats = hypotheses(con)
    scen, calib = scenarios()
    size_df.to_csv(OUT / "market_sizing.csv", index=False)
    hyp.to_csv(OUT / "hypotheses.csv", index=False)
    scen.to_csv(OUT / "scenarios.csv", index=False)
    (OUT / "stats.json").write_text(json.dumps({**stats, **size_notes, "scenario_calibration": calib}, indent=2))

    sql = {p.stem: pd.read_csv(p) for p in RES.glob("*.csv")}
    bundle = {
        "as_of": "2026-11-12",
        "market_share": sql["01_market_share"].to_dict("records"),
        "ai_pool": sql["02_ai_pool"].to_dict("records"),
        "core_vs_ai": sql["03_core_vs_ai"].to_dict("records"),
        "productivity": sql["04_productivity"].to_dict("records"),
        "momentum": sql["05_momentum_vs_money"].to_dict("records"),
        "scorecard": sql["06_scorecard"].to_dict("records"),
        "ai_timeseries": q(con, "SELECT * FROM fact_ai_timeseries").to_dict("records"),
        "ai_assumptions": q(con, "SELECT company, method, evidence_grade, rationale FROM fact_ai_pool").to_dict("records"),
        "sizing": size_df.to_dict("records"),
        "sizing_notes": size_notes,
        "hypotheses": hyp.to_dict("records"),
        "stats": stats,
        "scenarios": scen.to_dict("records"),
        "scenario_levers": SCENARIOS,
        "scenario_calibration": calib,
        "p1_events": q(con, "SELECT event_id, company, event_date, event_type, counterparty, counterparty_type, headline, source_url FROM p1_ci_events WHERE validation_status='Verified' ORDER BY event_date DESC").to_dict("records"),
        "sources": q(con, "SELECT * FROM sources").to_dict("records"),
    }
    (WEB / "dashboard_data.json").write_text(json.dumps(bundle, indent=1, default=str).replace("NaN", "null"))

    pd.set_option("display.width", 220)
    print(size_df[["measure", "value_usd_bn", "low_usd_bn", "high_usd_bn"]].to_string(index=False))
    print(json.dumps({**stats, **size_notes}, indent=1))
    print(scen[scen.year == 2030][["scenario", "ai_usd_bn", "core_usd_bn", "total_usd_bn", "ai_share_pct", "cagr_2026_2030_pct"]].to_string(index=False))
    print(scen[scen.scenario == "Base"][["year", "total_growth_pct", "ai_growth_needed_for_flat_total_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()

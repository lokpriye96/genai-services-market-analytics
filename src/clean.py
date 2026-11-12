"""
Step 1 - Clean and normalise the hand-collected raw files into analysis-ready tables.

The hard part of this project is that every company discloses AI differently:
TCS gives annualised AI revenue, Infosys a share of revenue, HCLTech a quarterly figure,
Accenture stopped quarterly disclosure after Q1 FY26, Capgemini gives a share of bookings,
and Cognizant, Wipro and Tech Mahindra give no AI revenue at all.

This script puts all of it on ONE basis - annualised USD run-rate for the latest quarter
(calendar Q3 2026) - and keeps an evidence grade on every number:
  A = company-reported figure      B = derived from a company-reported figure
  C = analyst estimate (stated assumption, low / mid / high range)

It also aggregates Project 1's verified competitive-intelligence events per company so the
two projects can be joined ("announcement momentum" vs "monetisation").

Run:  python src/clean.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

COMPANIES = ["Accenture", "TCS", "Infosys", "HCLTech", "Cognizant", "Capgemini", "Wipro", "Tech Mahindra"]
HQ = {"Accenture": "Global (Ireland/US)", "Cognizant": "Global (US)", "Capgemini": "Global (France)",
      "TCS": "India", "Infosys": "India", "HCLTech": "India", "Wipro": "India", "Tech Mahindra": "India"}


def company_metrics() -> pd.DataFrame:
    q = pd.read_csv(RAW / "company_quarterly.csv")
    latest = q[q.is_latest == 1].set_index("company")
    prior = q[q.is_latest == 0].set_index("company")
    df = pd.DataFrame(index=COMPANIES)
    df["hq_group"] = df.index.map(lambda c: "Global" if HQ[c].startswith("Global") else "India-heritage")
    df["latest_period"] = latest["period_label"]
    df["revenue_q_usd_m"] = latest["revenue_usd_m"]
    df["revenue_q_prior_usd_m"] = prior["revenue_usd_m"]
    df["revenue_runrate_usd_m"] = df["revenue_q_usd_m"] * 4
    df["revenue_yoy_usd_pct"] = (df["revenue_q_usd_m"] / df["revenue_q_prior_usd_m"] - 1) * 100
    df["revenue_yoy_cc_pct"] = latest["yoy_growth_cc_pct"]
    df["headcount"] = latest["headcount"]
    df["headcount_prior"] = prior["headcount"]
    df["headcount_yoy_pct"] = (df["headcount"] / df["headcount_prior"] - 1) * 100
    df["rev_per_employee_k_usd"] = df["revenue_runrate_usd_m"] * 1000 / df["headcount"]
    df["rev_per_employee_prior_k_usd"] = df["revenue_q_prior_usd_m"] * 4 * 1000 / df["headcount_prior"]
    df["rev_per_employee_yoy_pct"] = (df["rev_per_employee_k_usd"] / df["rev_per_employee_prior_k_usd"] - 1) * 100
    df["bookings_q_usd_m"] = latest["bookings_usd_m"]
    df["bookings_basis"] = latest["bookings_basis"]
    df["book_to_bill"] = df["bookings_q_usd_m"] / df["revenue_q_usd_m"]
    df["source_id"] = latest["source_id"]
    df.index.name = "company"
    return df.round(3).reset_index()


def ai_timeseries() -> pd.DataFrame:
    """Every disclosure converted to annualised USD where possible."""
    d = pd.read_csv(RAW / "ai_disclosures.csv")
    q = pd.read_csv(RAW / "company_quarterly.csv")
    rev = {("Infosys", "2025-12-31"): 5099, ("Infosys", "2026-09-30"): 5145}   # Q3 FY26 from INFY_Q3FY26_PR
    rows = []
    for _, r in d.iterrows():
        ann = None
        if r.metric == "ai_revenue_annualised":
            ann = r.value
        elif r.metric == "ai_revenue_quarter":
            ann = r.value * 4
        elif r.metric == "ai_share_of_revenue" and (r.company, r.quarter_end) in rev:
            ann = r.value / 100 * rev[(r.company, r.quarter_end)] * 4
        elif r.metric == "ai_revenue_fy":
            ann = r.value
        rows.append({**r.to_dict(), "ai_annualised_usd_m": None if ann is None else round(ann, 1)})
    return pd.DataFrame(rows)


def ai_pool(cm: pd.DataFrame) -> pd.DataFrame:
    """Latest AI revenue run-rate per company (low / mid / high) with evidence grade."""
    a = pd.read_csv(RAW / "ai_estimation_assumptions.csv").set_index("company")
    cm = cm.set_index("company")
    rows = []
    for c in COMPANIES:
        r = a.loc[c]
        rr = cm.loc[c, "revenue_runrate_usd_m"]
        if r.unit == "USD m":
            vals = [r.low, r.mid, r.high]
        else:
            vals = [rr * r.low / 100, rr * r.mid / 100, rr * r.high / 100]
        grade = {"TCS": "A", "HCLTech": "A", "Infosys": "B", "Accenture": "B"}.get(c, "C")
        rows.append({
            "company": c, "method": r.method, "evidence_grade": grade,
            "ai_runrate_low_usd_m": round(vals[0], 1), "ai_runrate_mid_usd_m": round(vals[1], 1),
            "ai_runrate_high_usd_m": round(vals[2], 1),
            "revenue_runrate_usd_m": rr,
            "ai_intensity_mid_pct": round(vals[1] / rr * 100, 2),
            "rationale": r.rationale,
        })
    return pd.DataFrame(rows)


def p1_momentum() -> pd.DataFrame:
    """Aggregate Project 1 verified events per company."""
    e = pd.read_csv(RAW / "p1_ci_events.csv")
    e = e[e.validation_status == "Verified"]
    g = e.groupby("company")
    out = pd.DataFrame({
        "p1_events_verified": g.size(),
        "p1_partnerships": g.apply(lambda x: (x.event_type == "Partnership").sum(), include_groups=False),
        "p1_frontier_lab_events": g.apply(lambda x: (x.counterparty_type == "Frontier model lab").sum(), include_groups=False),
        "p1_hyperscaler_events": g.apply(lambda x: (x.counterparty_type == "Hyperscaler").sum(), include_groups=False),
        "p1_acquisitions": g.apply(lambda x: (x.event_type == "Acquisition").sum(), include_groups=False),
        "p1_deals_gcc": g.apply(lambda x: (x.event_type == "Deal / GCC").sum(), include_groups=False),
        "p1_disclosed_acq_value_usd_m": g.apply(lambda x: x.loc[x.event_type == "Acquisition", "deal_value_usd_m"].sum(), include_groups=False),
        "p1_first_event": g["event_date"].min(),
        "p1_last_event": g["event_date"].max(),
    }).reindex(COMPANIES).fillna(0)
    out.index.name = "company"
    return out.reset_index()


def main() -> None:
    cm = company_metrics()
    files = {
        "company_metrics.csv": cm,
        "ai_timeseries.csv": ai_timeseries(),
        "ai_pool.csv": ai_pool(cm),
        "p1_momentum.csv": p1_momentum(),
        "market_estimates.csv": pd.read_csv(RAW / "market_estimates.csv"),
        "sources.csv": pd.read_csv(RAW / "sources.csv"),
        "company_quarterly.csv": pd.read_csv(RAW / "company_quarterly.csv"),
        "revenue_reference.csv": pd.read_csv(RAW / "revenue_reference.csv"),
        "p1_ci_events.csv": pd.read_csv(RAW / "p1_ci_events.csv"),
    }
    for name, df in files.items():
        df.to_csv(OUT / name, index=False)
        print(f"wrote data/processed/{name:24s} {len(df):3d} rows")


if __name__ == "__main__":
    main()

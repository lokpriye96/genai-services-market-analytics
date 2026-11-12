"""
Step 8 - Export a clean star schema for Power BI Desktop (powerbi/*.csv).
Build steps: guides/POWERBI_GUIDE.md

Run:  python src/export_powerbi.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "powerbi"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    con = sqlite3.connect(ROOT / "db" / "genai_services.db")
    q = lambda sql: pd.read_sql_query(sql, con)
    tables = {
        "dim_company": q("SELECT * FROM dim_company ORDER BY sort_order"),
        "fact_company_metrics": q("SELECT * FROM fact_company_metrics"),
        "fact_ai_pool": q("SELECT company, method, evidence_grade, ai_runrate_low_usd_m, ai_runrate_mid_usd_m, "
                          "ai_runrate_high_usd_m, revenue_runrate_usd_m FROM fact_ai_pool"),
        "fact_ai_timeseries": q("SELECT company, period_label, quarter_end, metric, value, unit, evidence_grade, "
                                "ai_annualised_usd_m, source_id FROM fact_ai_timeseries ORDER BY company, quarter_end"),
        "fact_p1_events": q("SELECT event_id, company, event_date, event_type, counterparty, counterparty_type, "
                            "headline, strategic_theme, deal_value_usd_m, source_url FROM p1_ci_events "
                            "WHERE validation_status = 'Verified' ORDER BY company, event_date"),
        "market_estimates": q("SELECT * FROM market_estimates"),
        "sources": q("SELECT * FROM sources"),
    }
    sr, ana = ROOT / "outputs" / "sql_results", ROOT / "outputs" / "analysis"
    tables["fact_core_vs_ai"] = pd.read_csv(sr / "03_core_vs_ai.csv")
    tables["fact_scenarios"] = pd.read_csv(ana / "scenarios.csv")
    tables["market_sizing"] = pd.read_csv(ana / "market_sizing.csv")
    tables["hypotheses"] = pd.read_csv(ana / "hypotheses.csv")
    # disconnected slicer tables (used by DAX SELECTEDVALUE)
    tables["dim_ai_case"] = pd.DataFrame({"case": ["Low", "Mid", "High"], "sort": [1, 2, 3]})
    tables["dim_scenario"] = pd.DataFrame({"scenario": ["Bear", "Base", "Bull"], "sort": [1, 2, 3]})
    for name, df in tables.items():
        df.to_csv(OUT / f"{name}.csv", index=False)
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.csv"))))


if __name__ == "__main__":
    main()

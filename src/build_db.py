"""
Step 2 - Load the cleaned tables (and Project 1's event database) into SQLite
(db/genai_services.db), then run every analysis query in sql/01-07 and save results to
outputs/sql_results/. The build stops if any data-quality check fails.

Run:  python src/build_db.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
SQL = ROOT / "sql"
DB = ROOT / "db" / "genai_services.db"
RES = ROOT / "outputs" / "sql_results"

TABLES = {
    "fact_company_quarter": "company_quarterly.csv",
    "fact_company_metrics": "company_metrics.csv",
    "fact_ai_timeseries": "ai_timeseries.csv",
    "fact_ai_pool": "ai_pool.csv",
    "fact_revenue_reference": "revenue_reference.csv",
    "p1_ci_events": "p1_ci_events.csv",
    "market_estimates": "market_estimates.csv",
    "sources": "sources.csv",
}


def build(con: sqlite3.Connection) -> None:
    con.executescript((SQL / "00_schema.sql").read_text())
    m = pd.read_csv(PROC / "company_metrics.csv")
    dim = m[["company", "hq_group"]].copy()
    dim["sort_order"] = range(1, len(dim) + 1)
    dim.to_sql("dim_company", con, if_exists="append", index=False)
    for table, f in TABLES.items():
        df = pd.read_csv(PROC / f)
        cols = [r[1] for r in con.execute(f"PRAGMA table_info({table})")]
        df[[c for c in cols if c in df.columns]].to_sql(table, con, if_exists="append", index=False)
    con.commit()


def run_queries(con: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    RES.mkdir(parents=True, exist_ok=True)
    out = {}
    for f in sorted(SQL.glob("0[1-9]_*.sql")):
        df = pd.read_sql_query(f.read_text(), con)
        df.to_csv(RES / f"{f.stem}.csv", index=False)
        out[f.stem] = df
        print(f"ran sql/{f.name:30s} -> {len(df):2d} rows")
    return out


def main() -> None:
    DB.parent.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()
    with sqlite3.connect(DB) as con:
        build(con)
        res = run_queries(con)
    chk = res["07_data_quality_checks"]
    bad = chk[chk.status != "PASS"]
    print(f"data-quality checks: {len(chk) - len(bad)}/{len(chk)} PASS")
    if len(bad):
        print(bad.to_string(index=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()

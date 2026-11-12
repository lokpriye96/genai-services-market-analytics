-- Data model for the GenAI services market analysis (SQLite).
-- Built by src/build_db.py from data/processed/*.csv into db/genai_services.db.

DROP TABLE IF EXISTS dim_company;
CREATE TABLE dim_company (
    company     TEXT PRIMARY KEY,
    hq_group    TEXT,              -- Global | India-heritage
    sort_order  INTEGER
);

DROP TABLE IF EXISTS fact_company_quarter;     -- raw latest + year-ago quarter per company
CREATE TABLE fact_company_quarter (
    company TEXT REFERENCES dim_company(company), period_label TEXT, quarter_end TEXT,
    calendar_quarter TEXT, is_latest INTEGER, revenue_usd_m REAL, revenue_basis TEXT,
    revenue_local_m REAL, local_currency TEXT, yoy_growth_cc_pct REAL, bookings_usd_m REAL,
    bookings_basis TEXT, headcount INTEGER, source_id TEXT, note TEXT
);

DROP TABLE IF EXISTS fact_company_metrics;     -- one row per company, latest quarter (CY Q3 2026)
CREATE TABLE fact_company_metrics (
    company TEXT PRIMARY KEY REFERENCES dim_company(company), hq_group TEXT, latest_period TEXT,
    revenue_q_usd_m REAL, revenue_q_prior_usd_m REAL, revenue_runrate_usd_m REAL,
    revenue_yoy_usd_pct REAL, revenue_yoy_cc_pct REAL, headcount INTEGER, headcount_prior INTEGER,
    headcount_yoy_pct REAL, rev_per_employee_k_usd REAL, rev_per_employee_prior_k_usd REAL,
    rev_per_employee_yoy_pct REAL, bookings_q_usd_m REAL, bookings_basis TEXT, book_to_bill REAL,
    source_id TEXT
);

DROP TABLE IF EXISTS fact_ai_timeseries;       -- every AI disclosure, as reported + annualised USD
CREATE TABLE fact_ai_timeseries (
    company TEXT, period_label TEXT, quarter_end TEXT, metric TEXT, value REAL, unit TEXT,
    company_definition TEXT, evidence_grade TEXT, source_id TEXT, note TEXT, ai_annualised_usd_m REAL
);

DROP TABLE IF EXISTS fact_ai_pool;             -- latest AI run-rate per company, low / mid / high
CREATE TABLE fact_ai_pool (
    company TEXT PRIMARY KEY, method TEXT, evidence_grade TEXT,
    ai_runrate_low_usd_m REAL, ai_runrate_mid_usd_m REAL, ai_runrate_high_usd_m REAL,
    revenue_runrate_usd_m REAL, ai_intensity_mid_pct REAL, rationale TEXT
);

DROP TABLE IF EXISTS fact_revenue_reference;   -- extra revenue points needed for the core-vs-AI test
CREATE TABLE fact_revenue_reference (
    company TEXT, period_label TEXT, period_end TEXT, revenue_usd_m REAL, basis TEXT, source_id TEXT, note TEXT
);

DROP TABLE IF EXISTS p1_ci_events;             -- Project 1 event database, joined as-is
CREATE TABLE p1_ci_events (
    event_id TEXT PRIMARY KEY, company TEXT, event_date TEXT, date_precision TEXT, event_type TEXT,
    counterparty TEXT, counterparty_type TEXT, headline TEXT, summary TEXT, strategic_theme TEXT,
    industry_focus TEXT, deal_value_usd_m REAL, value_note TEXT, source_name TEXT, source_url TEXT,
    source_tier TEXT, validation_status TEXT, confidence TEXT
);

DROP TABLE IF EXISTS market_estimates;
CREATE TABLE market_estimates (
    estimate_id TEXT PRIMARY KEY, publisher TEXT, metric TEXT, year TEXT, value_usd_m REAL,
    low_usd_m REAL, high_usd_m REAL, definition TEXT, source_id TEXT, note TEXT
);

DROP TABLE IF EXISTS sources;
CREATE TABLE sources (
    source_id TEXT PRIMARY KEY, publisher TEXT, title TEXT, release_date TEXT, url TEXT, source_type TEXT
);

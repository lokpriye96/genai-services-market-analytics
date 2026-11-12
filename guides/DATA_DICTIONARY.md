# Data dictionary

All money is in **USD millions** unless a column ends in `_bn`.

- **Run-rate** = latest quarter × 4.
- **Latest quarter** = calendar Q3 2026 (Accenture: Q4 FY26, Jun–Aug 2026; the others Jul–Sep 2026).

## Evidence grades (used throughout)

| Grade | Meaning | Example |
|---|---|---|
| **A** | Company-reported figure, used as reported | TCS annualised AI services revenue $3.1 bn |
| **B** | Derived arithmetically from a company figure | Infosys AI share 10.5% × revenue; Accenture last quarterly AI revenue × 4 × uplift |
| **C** | Analyst estimate with a stated low / mid / high range | Cognizant, Wipro and Tech Mahindra peer benchmark of 3 / 5 / 8% of revenue |

## Raw inputs: `data/raw/` (hand-transcribed from sources)

| File | Grain | Key columns |
|---|---|---|
| `sources.csv` | one row per source (51) | `source_id`, `publisher`, `title`, `release_date`, `url`, `source_type` (primary / secondary) |
| `company_quarterly.csv` | company × quarter (latest and year-ago) | `revenue_usd_m`, `revenue_basis` (reported / derived and how), `revenue_local_m`, `yoy_growth_cc_pct`, `bookings_usd_m`, `bookings_basis`, `headcount`, `source_id` |
| `ai_disclosures.csv` | company × period × metric | `metric` (e.g. `ai_revenue_annualised`, `ai_share_of_revenue`, `ai_bookings_q`), `value`, `unit`, `company_definition`, `evidence_grade`, `source_id` |
| `ai_estimation_assumptions.csv` | one row per company | `method`, `low` / `mid` / `high`, `unit`, `rationale` |
| `revenue_reference.csv` | extra revenue points needed for the core-vs-AI split | `period_label`, `revenue_usd_m`, `basis` |
| `market_estimates.csv` | one row per published market estimate | `publisher`, `metric`, `year`, `value_usd_m`, `low_usd_m`, `high_usd_m`, `definition` |
| `p1_ci_events.csv` | one row per competitive-intelligence event (copy of Project 1) | `event_id`, `company`, `event_date`, `event_type`, `counterparty_type`, `validation_status` |

## Processed tables: `data/processed/` and SQLite `db/genai_services.db`

| Table | Grain | Notes |
|---|---|---|
| `dim_company` | company | `hq_group` (Global / India-heritage), `sort_order` |
| `fact_company_quarter` | company × quarter | the cleaned raw quarterly data |
| `fact_company_metrics` | company | run-rate, YoY growth (USD and CC), headcount growth, revenue per employee, `book_to_bill` = bookings ÷ revenue (in each firm's own bookings basis) |
| `fact_ai_timeseries` | company × period × metric | adds `ai_annualised_usd_m`, a common annualised USD basis where one can be computed |
| `fact_ai_pool` | company | `ai_runrate_low/mid/high_usd_m`, `ai_intensity_mid_pct`, `evidence_grade`, `rationale` |
| `fact_revenue_reference` | company × period | |
| `p1_ci_events` | event | only `validation_status = 'Verified'` rows (70) are used in the analysis |
| `market_estimates`, `sources` | as raw | |

## Key derived metrics

| Metric | Formula | Where |
|---|---|---|
| Share of eight | firm run-rate ÷ sum of the eight | `sql/01_market_share.sql` |
| Share of Gartner IT services | firm run-rate ÷ Gartner 2026 IT services spending | `sql/01` |
| AI share of revenue | AI run-rate ÷ revenue run-rate | `sql/02_ai_pool.sql` |
| AI share index | share of AI pool ÷ share of revenue (>1 = over-indexes on AI) | `sql/02` |
| Core revenue | total revenue − AI revenue | `sql/03_core_vs_ai.sql` |
| Annualised growth | `(end / start)^(12 / months) − 1`, via `POWER()` | `sql/03` |
| Decoupling gap | revenue growth YoY − headcount growth YoY, in pp | `sql/04_productivity.sql` |
| Implied vendor-labelled AI market | eight-firm AI pool ÷ their share of Gartner IT services | `src/analysis.py` |
| AI growth needed for flat total | −core growth × core ÷ AI (prior year) | `src/analysis.py` |

## Outputs

| Path | What |
|---|---|
| `outputs/sql_results/*.csv` | result of each SQL file |
| `outputs/analysis/` | `market_sizing.csv`, `hypotheses.csv`, `scenarios.csv`, `stats.json` |
| `outputs/GenAI_Services_Market_Model.xlsx` | Excel model: inputs, live formulas, case / scenario dropdowns, checks |
| `outputs/Executive_Summary.pptx` / `.pdf` | one-slide executive summary |
| `outputs/charts/*.png` | static charts used in the README |
| `docs/index.html` | web dashboard (GitHub Pages) |
| `powerbi/*.csv` | star schema for Power BI (see `guides/POWERBI_GUIDE.md`) |

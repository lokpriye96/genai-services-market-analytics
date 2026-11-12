# Power BI build guide

Build the same analysis as the web dashboard in Power BI Desktop. It takes about 60–90 minutes. Every visual has an **expected value**, so you can check your build against the Python/SQL output.

All inputs are in `powerbi/`. Regenerate them with `python src/export_powerbi.py` (or `./run_all.sh`).

---

## 1. Load the data (10 min)

1. Open Power BI Desktop and choose **Get data → Text/CSV**.
2. Load every file in `powerbi/`.
3. In **Transform data** (Power Query), check these types and then click **Close & Apply**:

| Table | Column | Type |
|---|---|---|
| fact_company_metrics | revenue_*_usd_m, *_pct, book_to_bill, headcount | Decimal / Whole number |
| fact_ai_pool | ai_runrate_*_usd_m, revenue_runrate_usd_m | Decimal |
| fact_ai_timeseries | quarter_end | Date |
| fact_p1_events | event_date | Date |
| fact_scenarios | year | Whole number; all other columns Decimal |

> Locale tip: if decimals load as text, set **File → Options → Regional settings → Locale for import = English (United States)**.

## 2. Model: star schema (10 min)

Open the **Model** view and create these relationships. All are one-to-many, single direction, from the dimension to the fact table.

| From (1) | To (*) | Key |
|---|---|---|
| dim_company | fact_company_metrics | company |
| dim_company | fact_ai_pool | company |
| dim_company | fact_ai_timeseries | company |
| dim_company | fact_p1_events | company |
| dim_company | fact_core_vs_ai | company |

`dim_ai_case` and `dim_scenario` stay **disconnected**. They only drive slicers, which DAX reads with `SELECTEDVALUE`.

Sort `dim_company[company]` by `sort_order`, `dim_ai_case[case]` by `sort` and `dim_scenario[scenario]` by `sort` (**Column tools → Sort by column**).

## 3. Measures (15 min)

Create a table called `_Measures` (**Enter data**, one dummy column). Add the measures below, then hide the dummy column.

```DAX
Revenue Run-rate ($bn) = SUM ( fact_company_metrics[revenue_runrate_usd_m] ) / 1000

Revenue YoY USD % =
VAR cur = SUM ( fact_company_metrics[revenue_q_usd_m] )
VAR pri = SUM ( fact_company_metrics[revenue_q_prior_usd_m] )
RETURN DIVIDE ( cur, pri ) - 1

Share of Eight % =
DIVIDE ( [Revenue Run-rate ($bn)],
         CALCULATE ( [Revenue Run-rate ($bn)], ALL ( dim_company ) ) )

Selected AI Case = SELECTEDVALUE ( dim_ai_case[case], "Mid" )

AI Run-rate ($bn) =
SWITCH ( [Selected AI Case],
    "Low",  SUM ( fact_ai_pool[ai_runrate_low_usd_m] ),
    "High", SUM ( fact_ai_pool[ai_runrate_high_usd_m] ),
            SUM ( fact_ai_pool[ai_runrate_mid_usd_m] ) ) / 1000

AI Share of Revenue % = DIVIDE ( [AI Run-rate ($bn)], [Revenue Run-rate ($bn)] )

Share of AI Pool % =
DIVIDE ( [AI Run-rate ($bn)], CALCULATE ( [AI Run-rate ($bn)], ALL ( dim_company ) ) )

AI Share Index = DIVIDE ( [Share of AI Pool %], [Share of Eight %] )

Company-based AI % =
DIVIDE (
    CALCULATE ( SUM ( fact_ai_pool[ai_runrate_mid_usd_m] ), fact_ai_pool[evidence_grade] IN { "A", "B" } ),
    CALCULATE ( SUM ( fact_ai_pool[ai_runrate_mid_usd_m] ), ALL ( fact_ai_pool[evidence_grade] ) ) )

Headcount YoY % =
DIVIDE ( SUM ( fact_company_metrics[headcount] ), SUM ( fact_company_metrics[headcount_prior] ) ) - 1

Decoupling Gap (pp) = ( [Revenue YoY USD %] - [Headcount YoY %] ) * 100

Book-to-bill =
DIVIDE ( SUM ( fact_company_metrics[bookings_q_usd_m] ), SUM ( fact_company_metrics[revenue_q_usd_m] ) )

P1 Events = COUNTROWS ( fact_p1_events )

Selected Scenario = SELECTEDVALUE ( dim_scenario[scenario], "Base" )

Scenario Total ($bn) =
CALCULATE ( SUM ( fact_scenarios[total_usd_bn] ), fact_scenarios[scenario] = [Selected Scenario] )

Scenario AI ($bn) =
CALCULATE ( SUM ( fact_scenarios[ai_usd_bn] ), fact_scenarios[scenario] = [Selected Scenario] )

Scenario Core ($bn) =
CALCULATE ( SUM ( fact_scenarios[core_usd_bn] ), fact_scenarios[scenario] = [Selected Scenario] )

Scenario 2030 Total ($bn) =
CALCULATE ( [Scenario Total ($bn)], fact_scenarios[year] = 2030 )
```

Formats:

- `%` measures: Percentage, 1 decimal.
- `$bn` measures: Decimal, 1 decimal (the AI measure at the firm level: 2 decimals).

## 4. Pages and visuals (40 min)

Use one theme colour per company, matching the web dashboard (**Format → Data colors**):

| Company | Colour | Company | Colour |
|---|---|---|---|
| Accenture | #2A78D6 | Cognizant | #E87BA4 |
| TCS | #EB6834 | Capgemini | #008300 |
| Infosys | #1BAF7A | Wipro | #6250D6 |
| HCLTech | #EDA100 | Tech Mahindra | #E34948 |

### Page 1: Market & AI pool

- **Slicer:** `dim_ai_case[case]` as tiles, single select.
- **Cards:** `Revenue Run-rate ($bn)`, `AI Run-rate ($bn)`, `AI Share of Revenue %`, `Company-based AI %`.
- **Clustered bar:** axis `dim_company[company]`, value `Revenue Run-rate ($bn)`; tooltips `Share of Eight %`, `Revenue YoY USD %`.
- **Clustered bar:** axis company, value `AI Run-rate ($bn)`, tooltip `fact_ai_pool[evidence_grade]`, sorted descending.
- **Table** (market sizing): `market_sizing[lens]`, `measure`, `value_usd_bn`, `low_usd_bn`, `high_usd_bn`.

### Page 2: Is AI adding or replacing?

- **Clustered column:** axis `fact_core_vs_ai[company]`, values `total_growth_annualised_pct` and `core_growth_annualised_pct` (set the summarisation to *Don't summarize* / Average).
- **Line chart:** x `fact_ai_timeseries[quarter_end]`, y `ai_annualised_usd_m` (Sum), legend company. Add a filter to drop rows where `ai_annualised_usd_m` is blank.
- **Text box** with the H2 finding (see the README).

### Page 3: Competitive positioning

- **Scatter:** values = company; x `AI Share of Revenue %`; y = Average of `fact_company_metrics[revenue_yoy_cc_pct]`; size `Revenue Run-rate ($bn)`.
- **Scatter:** x `P1 Events`; y = Average of `revenue_yoy_cc_pct`.
- **Clustered bar:** company × `Revenue YoY USD %` and `Headcount YoY %`.
- **Matrix scorecard:** company × `Revenue Run-rate ($bn)`, CC growth, `AI Run-rate ($bn)`, `AI Share of Revenue %`, evidence grade, `Book-to-bill`, `P1 Events`.

### Page 4: 2030 scenarios

- **Slicer:** `dim_scenario[scenario]`.
- **Line chart:** x `fact_scenarios[year]`, y Sum of `total_usd_bn`, legend `fact_scenarios[scenario]`.
- **Stacked column:** x `fact_scenarios[year]`, values `Scenario Core ($bn)` and `Scenario AI ($bn)`.
- **Card:** `Scenario 2030 Total ($bn)`.
- **Table:** `hypotheses` (id, hypothesis, verdict, so_what).

## 5. Check your build against the expected values

| Check | Expected |
|---|---|
| Revenue Run-rate ($bn), all firms | **207.8** |
| Revenue YoY USD %, all firms | **5.1%** |
| AI Run-rate ($bn): Low / Mid / High | **13.2 / 15.8 / 18.9** |
| AI Share of Revenue %, Mid | **7.6%** |
| Company-based AI %, Mid | **73.7%** |
| Share of Eight %, Accenture | **36.0%** |
| AI Run-rate, Mid: Accenture / TCS / Infosys | **5.50 / 3.10 / 2.16** |
| Core growth p.a.: Infosys / TCS / HCLTech / Accenture | **−5.9% / −3.6% / −0.5% / +4.7%** |
| Book-to-bill: TCS / Tech Mahindra | **1.26 / 0.60** |
| P1 Events (all) | **70** |
| Scenario 2030 Total: Bear / Base / Bull | **205.2 / 233.3 / 264.1** |

If any value differs, check the data types (step 1) and that the relationships run from `dim_company` (step 2).

## 6. Publish (optional)

- Save the file as `powerbi/GenAI_Services_Market.pbix`.
- **Publish to web** needs a Power BI Pro or Fabric licence and an admin setting. Otherwise, export the report to PDF (**File → Export → PDF**) and add screenshots to the README.

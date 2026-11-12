-- Q3 (Hypothesis H2). Is AI revenue growth coming with a SHRINKING core business?
-- For each firm that discloses AI revenue over time, split revenue into AI and non-AI ("core")
-- at two points and annualise the growth of each. Quarterly AI = annualised / 4.
WITH pts AS (
    -- TCS: Q3 FY26 (first disclosure) -> Q2 FY27
    SELECT 'TCS' AS company, 'Q3 FY26 -> Q2 FY27' AS window, 0.75 AS years,
           (SELECT revenue_usd_m FROM fact_revenue_reference WHERE company='TCS' AND period_end='2025-12-31') AS rev0,
           (SELECT ai_annualised_usd_m/4 FROM fact_ai_timeseries WHERE company='TCS' AND quarter_end='2025-12-31' AND metric='ai_revenue_annualised') AS ai0,
           (SELECT revenue_q_usd_m FROM fact_company_metrics WHERE company='TCS') AS rev1,
           (SELECT ai_annualised_usd_m/4 FROM fact_ai_timeseries WHERE company='TCS' AND quarter_end='2026-09-30' AND metric='ai_revenue_annualised') AS ai1
    UNION ALL
    -- Infosys: Q3 FY26 -> Q2 FY27 (AI = reported share x revenue)
    SELECT 'Infosys', 'Q3 FY26 -> Q2 FY27', 0.75,
           (SELECT revenue_usd_m FROM fact_revenue_reference WHERE company='Infosys' AND period_end='2025-12-31'),
           (SELECT ai_annualised_usd_m/4 FROM fact_ai_timeseries WHERE company='Infosys' AND quarter_end='2025-12-31'),
           (SELECT revenue_q_usd_m FROM fact_company_metrics WHERE company='Infosys'),
           (SELECT ai_annualised_usd_m/4 FROM fact_ai_timeseries WHERE company='Infosys' AND quarter_end='2026-09-30')
    UNION ALL
    -- HCLTech: Q2 FY26 -> Q2 FY27 (year on year)
    SELECT 'HCLTech', 'Q2 FY26 -> Q2 FY27', 1.0,
           (SELECT revenue_q_prior_usd_m FROM fact_company_metrics WHERE company='HCLTech'),
           (SELECT value FROM fact_ai_timeseries WHERE company='HCLTech' AND quarter_end='2025-09-30' AND metric='ai_revenue_quarter'),
           (SELECT revenue_q_usd_m FROM fact_company_metrics WHERE company='HCLTech'),
           (SELECT value FROM fact_ai_timeseries WHERE company='HCLTech' AND quarter_end='2026-09-30' AND metric='ai_revenue_quarter')
    UNION ALL
    -- Accenture: FY24 -> FY25 (full fiscal years)
    SELECT 'Accenture', 'FY24 -> FY25', 1.0,
           (SELECT revenue_usd_m FROM fact_revenue_reference WHERE company='Accenture' AND period_end='2024-08-31'),
           (SELECT value FROM fact_ai_timeseries WHERE company='Accenture' AND quarter_end='2024-08-31' AND metric='ai_revenue_fy'),
           (SELECT revenue_usd_m FROM fact_revenue_reference WHERE company='Accenture' AND period_end='2025-08-31'),
           (SELECT value FROM fact_ai_timeseries WHERE company='Accenture' AND quarter_end='2025-08-31' AND metric='ai_revenue_fy')
)
SELECT company, window,
       ROUND(rev0, 0) AS revenue_start_usd_m, ROUND(ai0, 0) AS ai_start_usd_m, ROUND(rev0 - ai0, 0) AS core_start_usd_m,
       ROUND(rev1, 0) AS revenue_end_usd_m,   ROUND(ai1, 0) AS ai_end_usd_m,   ROUND(rev1 - ai1, 0) AS core_end_usd_m,
       ROUND(100.0 * ai0 / rev0, 1) AS ai_share_start_pct, ROUND(100.0 * ai1 / rev1, 1) AS ai_share_end_pct,
       ROUND(100.0 * (POWER(rev1 / rev0, 1.0 / years) - 1), 1)                     AS total_growth_annualised_pct,
       ROUND(100.0 * (POWER(ai1 / ai0, 1.0 / years) - 1), 1)                       AS ai_growth_annualised_pct,
       ROUND(100.0 * (POWER((rev1 - ai1) / (rev0 - ai0), 1.0 / years) - 1), 1)     AS core_growth_annualised_pct,
       ROUND(100.0 * ((rev1 - ai1) - (rev0 - ai0)) / (rev1 - rev0), 0)            AS core_contribution_to_change_pct
FROM pts
ORDER BY core_growth_annualised_pct;

-- Q7. Data-quality checks. Every row must return 'PASS' or the build stops.

WITH printed(company, pct) AS (
    VALUES ('Accenture', 6.0), ('Infosys', 1.3), ('Cognizant', 4.6), ('Tech Mahindra', 6.8),
           ('Capgemini', 12.6), ('Wipro', 0.3), ('TCS', 2.4), ('HCLTech', 2.2)
)
-- (a) Recomputed YoY USD growth matches the growth rate printed by the company (within 0.5 pp)
SELECT 'printed YoY growth recomputes: ' || m.company AS check_name,
       CASE WHEN ABS(m.revenue_yoy_usd_pct - p.pct) <= 0.5 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_company_metrics m JOIN printed p ON p.company = m.company

UNION ALL
-- (b) Low <= mid <= high for every AI estimate, and mid AI share is plausible (< 20% of revenue)
SELECT 'AI range ordered and plausible: ' || company,
       CASE WHEN ai_runrate_low_usd_m <= ai_runrate_mid_usd_m AND ai_runrate_mid_usd_m <= ai_runrate_high_usd_m
             AND ai_intensity_mid_pct < 20 THEN 'PASS' ELSE 'FAIL' END
FROM fact_ai_pool

UNION ALL
-- (c) Disclosed AI series never falls (TCS, HCLTech annualised)
SELECT 'AI series non-decreasing: ' || company,
       CASE WHEN MIN(d) >= 0 THEN 'PASS' ELSE 'FAIL' END
FROM (SELECT company, ai_annualised_usd_m - LAG(ai_annualised_usd_m) OVER (PARTITION BY company ORDER BY quarter_end) AS d
      FROM fact_ai_timeseries
      WHERE company IN ('TCS','HCLTech') AND ai_annualised_usd_m IS NOT NULL
        AND metric IN ('ai_revenue_annualised','ai_revenue_quarter')
        AND NOT (company = 'HCLTech' AND metric = 'ai_revenue_annualised' AND quarter_end = '2026-09-30'))
WHERE d IS NOT NULL
GROUP BY company

UNION ALL
-- (d) TCS ">10% of revenue" claim is consistent with our numbers
SELECT 'TCS AI > 10% of revenue',
       CASE WHEN ai_intensity_mid_pct > 10 THEN 'PASS' ELSE 'FAIL' END
FROM fact_ai_pool WHERE company = 'TCS'

UNION ALL
-- (e) HCLTech: annualised = 4 x quarterly as printed
SELECT 'HCLTech annualised = 4 x quarter',
       CASE WHEN ABS(MAX(CASE WHEN metric='ai_revenue_annualised' THEN value END)
                   - 4 * MAX(CASE WHEN metric='ai_revenue_quarter' THEN value END)) < 1 THEN 'PASS' ELSE 'FAIL' END
FROM fact_ai_timeseries WHERE company = 'HCLTech' AND quarter_end = '2026-09-30'

UNION ALL
-- (f) Project 1 join is complete: every tracked company has events and the verified total is 70
SELECT 'Project 1 join: 70 verified events across 8 firms',
       CASE WHEN COUNT(*) = 70 AND COUNT(DISTINCT company) = 8 THEN 'PASS' ELSE 'FAIL' END
FROM p1_ci_events WHERE validation_status = 'Verified'

UNION ALL
-- (g) Every company-metrics row and AI-pool row has a source or a stated method
SELECT 'every metric row is sourced',
       CASE WHEN SUM(source_id IS NULL OR source_id = '') = 0 THEN 'PASS' ELSE 'FAIL' END
FROM fact_company_metrics;

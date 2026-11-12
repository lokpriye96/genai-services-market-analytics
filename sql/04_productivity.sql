-- Q4 (Hypothesis H4). Has revenue decoupled from headcount?
-- Decoupling gap = revenue growth (USD, YoY) minus headcount growth (YoY), in percentage points.
SELECT company, hq_group,
       ROUND(revenue_yoy_usd_pct, 2)        AS revenue_yoy_usd_pct,
       ROUND(headcount_yoy_pct, 2)          AS headcount_yoy_pct,
       ROUND(revenue_yoy_usd_pct - headcount_yoy_pct, 2) AS decoupling_gap_pp,
       headcount, headcount - headcount_prior AS net_adds,
       ROUND(rev_per_employee_k_usd, 1)     AS rev_per_employee_k_usd,
       ROUND(rev_per_employee_yoy_pct, 2)   AS rev_per_employee_yoy_pct,
       CASE WHEN revenue_yoy_usd_pct - headcount_yoy_pct >= 2 THEN 'Decoupling'
            WHEN revenue_yoy_usd_pct - headcount_yoy_pct >= 0 THEN 'Weak decoupling'
            ELSE 'Headcount outgrowing revenue' END AS pattern
FROM fact_company_metrics
ORDER BY decoupling_gap_pp DESC;

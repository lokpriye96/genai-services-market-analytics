-- Q2. How big is the AI revenue pool across the eight, and who is capturing it?
-- AI run-rate (annualised USD) per company with evidence grade and low / mid / high range.
-- "AI share index" > 1 means a firm captures more of the AI pool than its share of total revenue.
SELECT p.company,
       p.evidence_grade,
       ROUND(p.ai_runrate_mid_usd_m / 1000.0, 2)                                          AS ai_runrate_mid_usd_bn,
       ROUND(p.ai_runrate_low_usd_m / 1000.0, 2)                                          AS ai_runrate_low_usd_bn,
       ROUND(p.ai_runrate_high_usd_m / 1000.0, 2)                                         AS ai_runrate_high_usd_bn,
       ROUND(p.ai_intensity_mid_pct, 1)                                                   AS ai_share_of_revenue_pct,
       ROUND(100.0 * p.ai_runrate_mid_usd_m / SUM(p.ai_runrate_mid_usd_m) OVER (), 1)     AS share_of_ai_pool_pct,
       ROUND(100.0 * p.revenue_runrate_usd_m / SUM(p.revenue_runrate_usd_m) OVER (), 1)   AS share_of_revenue_pct,
       ROUND((p.ai_runrate_mid_usd_m / SUM(p.ai_runrate_mid_usd_m) OVER ())
           / (p.revenue_runrate_usd_m / SUM(p.revenue_runrate_usd_m) OVER ()), 2)         AS ai_share_index,
       ROUND(SUM(p.ai_runrate_mid_usd_m) OVER () / 1000.0, 2)                             AS pool_mid_usd_bn,
       ROUND(SUM(p.ai_runrate_low_usd_m) OVER () / 1000.0, 2)                             AS pool_low_usd_bn,
       ROUND(SUM(p.ai_runrate_high_usd_m) OVER () / 1000.0, 2)                            AS pool_high_usd_bn,
       ROUND(100.0 * SUM(CASE WHEN p.evidence_grade IN ('A','B') THEN p.ai_runrate_mid_usd_m ELSE 0 END) OVER ()
           / SUM(p.ai_runrate_mid_usd_m) OVER (), 1)                                      AS pool_pct_company_based
FROM fact_ai_pool p
ORDER BY p.ai_runrate_mid_usd_m DESC;

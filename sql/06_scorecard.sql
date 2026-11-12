-- Q6. Competitive positioning scorecard: scale, growth, AI monetisation, demand pipeline, productivity.
SELECT m.company,
       m.hq_group,
       ROUND(m.revenue_runrate_usd_m / 1000.0, 1)  AS revenue_runrate_usd_bn,
       m.revenue_yoy_cc_pct                        AS growth_cc_pct,
       ROUND(a.ai_runrate_mid_usd_m / 1000.0, 2)   AS ai_runrate_usd_bn,
       ROUND(a.ai_intensity_mid_pct, 1)            AS ai_share_pct,
       a.evidence_grade                            AS ai_grade,
       ROUND(m.book_to_bill, 2)                    AS book_to_bill,
       m.bookings_basis,
       ROUND(m.rev_per_employee_k_usd, 1)          AS rev_per_employee_k_usd,
       ROUND(m.headcount_yoy_pct, 1)               AS headcount_yoy_pct,
       p.p1_events, p.p1_frontier_lab_events
FROM fact_company_metrics m
JOIN fact_ai_pool a USING (company)
LEFT JOIN (SELECT company, COUNT(*) AS p1_events,
                  SUM(counterparty_type = 'Frontier model lab') AS p1_frontier_lab_events
           FROM p1_ci_events WHERE validation_status = 'Verified' GROUP BY company) p USING (company)
ORDER BY m.revenue_runrate_usd_m DESC;

-- Q5 (Hypothesis H5). Does announcement momentum (Project 1 CI events) translate into monetisation?
-- Joins Project 1's verified event database with this project's AI and growth metrics,
-- and ranks firms on each so a rank correlation can be computed in analysis.py.
WITH ev AS (
    SELECT company,
           COUNT(*)                                                       AS p1_events,
           SUM(CASE WHEN event_type = 'Partnership' THEN 1 ELSE 0 END)    AS partnerships,
           SUM(CASE WHEN counterparty_type = 'Frontier model lab' THEN 1 ELSE 0 END) AS frontier_lab_events,
           SUM(CASE WHEN event_type = 'Acquisition' THEN 1 ELSE 0 END)    AS acquisitions,
           SUM(CASE WHEN event_type = 'Deal / GCC' THEN 1 ELSE 0 END)     AS deals_gcc,
           GROUP_CONCAT(DISTINCT CASE WHEN counterparty_type = 'Frontier model lab' THEN counterparty END) AS frontier_labs
    FROM p1_ci_events
    WHERE validation_status = 'Verified'
    GROUP BY company
)
SELECT m.company,
       ev.p1_events, ev.partnerships, ev.frontier_lab_events, ev.acquisitions, ev.deals_gcc,
       COALESCE(ev.frontier_labs, '-')                           AS frontier_labs,
       a.evidence_grade                                          AS ai_disclosure_grade,
       ROUND(a.ai_intensity_mid_pct, 1)                          AS ai_share_of_revenue_pct,
       m.revenue_yoy_cc_pct,
       RANK() OVER (ORDER BY ev.p1_events DESC)                  AS rank_momentum,
       RANK() OVER (ORDER BY a.ai_intensity_mid_pct DESC)        AS rank_ai_intensity,
       RANK() OVER (ORDER BY m.revenue_yoy_cc_pct DESC)          AS rank_growth
FROM fact_company_metrics m
JOIN fact_ai_pool a USING (company)
LEFT JOIN ev USING (company)
ORDER BY ev.p1_events DESC, m.company;

-- Q1. How big are the eight firms, who holds what share, and are they keeping up with the market?
-- Annualised run-rate = latest quarter (calendar Q3 2026) x 4.
WITH base AS (
    SELECT m.company, m.hq_group, m.revenue_runrate_usd_m AS rr, m.revenue_yoy_usd_pct, m.revenue_yoy_cc_pct,
           m.revenue_q_usd_m AS q_now, m.revenue_q_prior_usd_m AS q_prior
    FROM fact_company_metrics m
),
mkt AS (
    SELECT MAX(CASE WHEN estimate_id = 'GARTNER_ITS_2026' THEN value_usd_m END) AS its_2026,
           MAX(CASE WHEN estimate_id = 'GARTNER_ITS_2025' THEN value_usd_m END) AS its_2025
    FROM market_estimates
)
SELECT b.company,
       b.hq_group,
       ROUND(b.rr / 1000.0, 2)                                       AS revenue_runrate_usd_bn,
       ROUND(100.0 * b.rr / SUM(b.rr) OVER (), 2)                   AS share_of_eight_pct,
       ROUND(100.0 * b.rr / mkt.its_2026, 2)                        AS share_of_gartner_it_services_pct,
       RANK() OVER (ORDER BY b.rr DESC)                             AS size_rank,
       ROUND(b.revenue_yoy_usd_pct, 2)                              AS yoy_usd_pct,
       b.revenue_yoy_cc_pct                                         AS yoy_cc_pct,
       ROUND(100.0 * (SUM(b.q_now) OVER () / SUM(b.q_prior) OVER () - 1), 2) AS eight_firm_yoy_usd_pct,
       ROUND(100.0 * (mkt.its_2026 / mkt.its_2025 - 1), 2)          AS gartner_it_services_growth_2026_pct
FROM base b CROSS JOIN mkt
ORDER BY b.rr DESC;

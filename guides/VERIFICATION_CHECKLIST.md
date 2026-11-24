# Manual verification checklist

**What the automated checks cover.** `sql/07_data_quality_checks.sql` (22 checks) and `tests/test_data.py` test internal consistency:

- printed growth rates recompute from the revenue figures;
- AI ranges are ordered low ≤ mid ≤ high;
- disclosed AI series never fall;
- annualised figures equal 4× the quarter;
- every row has a source;
- Project 1 joins with 80 verified events across the 8 firms.

**What they cannot catch.** A figure copied wrong *consistently* from its source. This list covers the headline figures: open each source, find the number, and tick the box. **Priority:** the rows marked ★ feed the headline finding (H2, core shrinking).

**Status (12 Nov 2026):** the 7 starred rows were checked against company documents (AI-assisted check; owner spot-check recommended). All matched. Unstarred rows are open.

| ✓ | Figure used | Value in repo | Where to check |
|---|---|---|---|
| ✅ ★ | TCS annualised AI services revenue, Q2 FY27 / Q3 FY26 | $3.1 bn / $1.8 bn | Matched: [TCS Q2 FY27 press release](https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/2026-27/q2/IFRS/Press%20Release%20-%20USD.pdf); [TCS Q3 FY26 press release](https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/2025-26/q3/IFRS/Press%20Release%20-%20USD.pdf) |
| ✅ ★ | TCS revenue Q2 FY27 / Q3 FY26 (USD) | $7,642 m / $7,509 m | Matched: same two TCS press releases (Q2 FY27 also: +2.4% YoY USD, workforce 598,056, TCV $9.6 bn) |
| ✅ ★ | Infosys AI share of revenue, Q2 FY27 / Q1 FY27 / Q3 FY26 | 10.5% / 8.2% / 5.5% | Matched: [Infosys Q2 FY27 call, SEC 6-K](https://www.sec.gov/Archives/edgar/data/0001067491/000106749126000044/exv99w05.htm) (10.5%, 8.2%); 5.5% stated by the CEO at Infosys Investor AI Day, Feb-2026 ([Reuters](https://www.dzrh.com.ph/post/infosys-reveals-ai-revenue-share-as-sector-faces-growing-disruption-fears)) |
| ✅ ★ | Infosys revenue Q2 FY27 / Q3 FY26 | $5,145 m / $5,099 m | Matched: Q2 FY27 coverage of the results; [Infosys Q3 FY26 press release, SEC 6-K](https://www.sec.gov/Archives/edgar/data/1067491/000106749126000004/exv99w01.htm) |
| ✅ ★ | HCLTech advanced AI revenue Q2 FY27 (annualised) | $876 m ($219 m quarter; +78% YoY CC) | Matched: [HCLTech Q2 FY27 release](https://www.hcltech.com/press-releases/hcltech-delivers-strong-q2-led-record-deal-bookings-33-billion) |
| ✅ | HCLTech Q2 FY26 advanced AI revenue | 123 m (derived) | Cross-checked: $219 m ÷ 1.78 (company-reported +78% YoY CC) = $123 m; consistent with Q3 FY26 $146 m being up ~20% QoQ |
| ✅ ★ | Accenture FY25 advanced AI revenue / bookings | $2.7 bn / $5.9 bn | Matched: [Q4 FY25 call transcript](https://www.investor.accenture.com/~/media/Files/A/Accenture-IR-V3/quarterly-earnings/2025/q4-fy-25/accenture-fourth-quarter-fiscal-2025-conference-call-transcript.pdf) and FY25 annual report |
| ✅ | Accenture Q1 FY26 AI revenue / bookings | ~$1.1 bn / $2.2 bn | Matched: [Q1 FY26 call transcript](https://investor.accenture.com/~/media/Files/A/accenture-v4/investors/earnings-reports/2026/accenture-first-quarter-fiscal-2026-conference-call-transcript.pdf). Accenture said this is the last quarter it discloses these metrics. Cumulative AI revenue to date of $4.8 bn is consistent with the repo's FY24 $0.9 bn + FY25 $2.7 bn + Q1 FY26 $1.1 bn |
| ☐ | Accenture Q4 FY26 revenue / bookings / CC growth | $18.68 bn / $22.17 bn / +7% | [Q4 FY26 8-K exhibit](https://www.sec.gov/Archives/edgar/data/0001467373/000146737326000037/q4fy26earnings8-kexhibit.htm) |
| ☐ | Cognizant Q3 2026 revenue / CC growth | $5,664 m / +4.8% | [Cognizant Q3 8-K](https://www.sec.gov/Archives/edgar/data/0001058290/000105829026000039/exhibit9919302026.htm) |
| ☐ | Wipro Q2 FY27 IT services revenue | $2,611.5 m | [Wipro 6-K](https://www.sec.gov/Archives/edgar/data/0001123799/000119312526426841/d188224dex991.htm) |
| ☐ | Capgemini Q3 2026 revenue / growth | €6,073 m / +11.7% | Capgemini Q3 release (`CAP_Q3_PR`); **upgrade to capgemini.com** |
| ☐ | Capgemini GenAI/agentic share of bookings | >11% (Q1 2026) | Capgemini Q1 release (`CAP_Q1_PR`) |
| ☐ | Tech Mahindra Q2 FY27 revenue / headcount | $1,693 m / 152,206 | Tech Mahindra Q2 FY27 fact sheet (`TECHM_Q2FY27`) |
| ☐ | Headcount, all eight (latest and year-ago) | see `data/raw/company_quarterly.csv` | Each firm's fact sheet |
| ☐ | Gartner AI services spending 2026 | $576.5 bn | [Gartner, 16-Sep-2026](https://gartner.com/en/newsroom/press-releases/2026-09-16-gartner-forecasts-worldwide-ai-spending-to-grow-49-point-5-percent-in-2026) |
| ☐ | Gartner IT services spending 2025 / 2026 | $1,717.6 bn / $1,866.9 bn | [Gartner, 3-Feb-2026](https://gcom.pdo.aws.gartner.com/en/newsroom/press-releases/2026-02-03-gartner-forecasts-worldwide-it-spending-to-grow-10-point-8-percent-in-2026-totaling-6-point-15-trillion-dollars) |
| ☐ | Kotak AI-deflation estimate | 3–3.5% per year | [Kotak Neo report](https://www.kotakneo.com/news/sectors/it-stocks-kotak-downgrades-infosys-tcs-to-add-ltm-to-sell-after-sharp-rally/) |

**Source mix.**

- 51 sources: 22 primary (company filings, releases and wires, Gartner, Project 1) and 29 secondary (press reporting of company figures).
- Every AI figure behind the headline finding (TCS, Infosys, HCLTech, Accenture) now traces to a company document. The remaining secondary sources mainly cover non-headline inputs (headcount, bookings, deflation estimates).

**If any figure differs:** correct it in `data/raw/`, then run `./run_all.sh`. The SQL checks, Excel model, dashboard, charts and slide all rebuild from it.

# Manual verification checklist

**What the automated checks cover.** `sql/07_data_quality_checks.sql` (22 checks) and `tests/test_data.py` test internal consistency:

- printed growth rates recompute from the revenue figures;
- AI ranges are ordered low ≤ mid ≤ high;
- disclosed AI series never fall;
- annualised figures equal 4× the quarter;
- every row has a source;
- Project 1 joins with 70 verified events across the 8 firms.

**What they cannot catch.** A figure copied wrong *consistently* from its source. This list covers the headline figures: open each source, find the number, and tick the box. **Priority:** the rows marked ★ feed the headline finding (H2, core shrinking).

**Status:** ☐ Not yet completed. Replace this line with the date when done.

| ✓ | Figure used | Value in repo | Where to check |
|---|---|---|---|
| ☐ ★ | TCS annualised AI services revenue, Q2 FY27 / Q3 FY26 | $3.1 bn / $1.8 bn | TCS Q2 FY27 results release and call (`TCS_Q2FY27_QUARTR`); Q3 FY26 release (`TCS_Q3FY26_PR`) |
| ☐ ★ | TCS revenue Q2 FY27 / Q3 FY26 (USD) | $7,642 m / $7,509 m | TCS investor releases (tcs.com/investor-relations) |
| ☐ ★ | Infosys AI share of revenue, Q2 FY27 / Q3 FY26 | 10.5% / 5.5% | [Infosys Q2 FY27 call, SEC 6-K](https://www.sec.gov/Archives/edgar/data/0001067491/000106749126000044/exv99w05.htm); Q3 FY26 (`INFY_Q3FY26_AI`) |
| ☐ ★ | Infosys revenue Q2 FY27 / Q3 FY26 | $5,145 m / $5,099 m | Infosys fact sheets (infosys.com/investors) |
| ☐ ★ | HCLTech advanced AI revenue Q2 FY27 (annualised) | $876 m ($219 m quarter) | [HCLTech Q2 FY27 release](https://www.hcltech.com/press-releases/hcltech-delivers-strong-q2-led-record-deal-bookings-33-billion) |
| ☐ | HCLTech Q2 FY26 advanced AI revenue | ">$100 m" (repo uses 123, derived) | HCLTech Q2 FY26 call (`HCL_Q2FY26_OB`); **upgrade if an exact figure is found** |
| ☐ ★ | Accenture FY25 advanced AI revenue / bookings | $2.7 bn / $5.9 bn | [Q4 FY25 call transcript](https://www.investor.accenture.com/~/media/Files/A/Accenture-IR-V3/quarterly-earnings/2025/q4-fy-25/accenture-fourth-quarter-fiscal-2025-conference-call-transcript.pdf) |
| ☐ | Accenture Q1 FY26 AI revenue / bookings | ~$1.1 bn / $2.2 bn | [Q1 FY26 call transcript](https://investor.accenture.com/~/media/Files/A/accenture-v4/investors/earnings-reports/2026/accenture-first-quarter-fiscal-2026-conference-call-transcript.pdf) |
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

- 51 sources: 21 primary (company filings, releases and wires, Gartner, Project 1) and 30 secondary (press reporting of company figures).
- Several AI figures were found only in press coverage of earnings calls. Replacing them with the company transcripts would make the register fully primary; this is the most valuable upgrade.

**If any figure differs:** correct it in `data/raw/`, then run `./run_all.sh`. The SQL checks, Excel model, dashboard, charts and slide all rebuild from it.

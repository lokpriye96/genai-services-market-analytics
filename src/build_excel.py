"""
Step 4 - Excel model with LIVE formulas (outputs/GenAI_Services_Market_Model.xlsx).
Blue = input as reported/assumed, black = formula, green = cross-sheet link, yellow = key lever.
Change an AI-estimate case, a scenario lever or a raw figure and everything recalculates.

Run:  python src/build_excel.py   (then recalculate in Excel or LibreOffice)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from analysis import SCENARIOS, YEARS  # noqa: E402

RAW = ROOT / "data" / "raw"
XLSX = ROOT / "outputs" / "GenAI_Services_Market_Model.xlsx"
F = "Arial"
BLUE, GREEN, BOLD = Font(name=F, color="0000FF"), Font(name=F, color="008000"), Font(name=F, bold=True)
TITLE, NOTE = Font(name=F, bold=True, size=14), Font(name=F, italic=True, color="52514E", size=9)
HDR, KEY = PatternFill("solid", fgColor="E1E0D9"), PatternFill("solid", fgColor="FFFF00")
USD = '#,##0;(#,##0);"-"'
USD1 = '#,##0.0;(#,##0.0);"-"'
PCT = '0.0%;(0.0%);"-"'
X2 = '0.00"x"'
COS = ["Accenture", "TCS", "Infosys", "HCLTech", "Cognizant", "Capgemini", "Wipro", "Tech Mahindra"]


def header(ws, row, labels, col=1):
    for i, lab in enumerate(labels):
        c = ws.cell(row, col + i, lab)
        c.font, c.fill = BOLD, HDR
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = Border(bottom=Side(style="thin", color="C3C2B7"))


def widths(ws, w):
    for i, x in enumerate(w, 1):
        ws.column_dimensions[get_column_letter(i)].width = x


def setf(c, value, font=None, fmt=None, fill=None):
    c.value = value
    if font is not None:
        c.font = font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def fontify(wb):
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.font.name != F:
                    c.font = Font(name=F, bold=c.font.bold, italic=c.font.italic, color=c.font.color, size=c.font.size or 10)


def main() -> None:
    q = pd.read_csv(RAW / "company_quarterly.csv")
    assum = pd.read_csv(RAW / "ai_estimation_assumptions.csv").set_index("company")
    ev = pd.read_csv(RAW / "p1_ci_events.csv")
    est = pd.read_csv(RAW / "market_estimates.csv").set_index("estimate_id")
    ref = pd.read_csv(RAW / "revenue_reference.csv")
    ai = pd.read_csv(RAW / "ai_disclosures.csv")
    src = pd.read_csv(RAW / "sources.csv")
    wb = Workbook()
    wb.properties.creator = "Utkarsh Saxena"
    wb.properties.lastModifiedBy = "Utkarsh Saxena"
    wb.properties.title = "GenAI Services Market Model"

    # ------------------------------------------------------------- README
    ws = wb.active
    ws.title = "README"
    lines = [
        ("GenAI Services Market Model: eight IT services firms, data to CY Q3 2026", TITLE),
        ("Companion to Project 1 (AI-Powered CI Tracker). Sizes the AI revenue pool, shares, growth, the AI-vs-core split and 2027-2030 scenarios.", None),
        ("", None),
        ("Legend: blue = reported or assumed input | black = formula | green = link to another sheet | yellow = key lever you can change", BOLD),
        ("", None),
        ("Inputs        - latest and year-ago quarter per firm (revenue USD m, growth, bookings, headcount) with source IDs.", None),
        ("Metrics       - run-rate, share, YoY growth, headcount growth, revenue per employee, book-to-bill (formulas).", None),
        ("AI_Pool       - AI revenue run-rate per firm. Choose Low / Mid / High in cell C2; evidence grade A/B/C per firm.", None),
        ("Core_vs_AI    - AI vs non-AI ('core') revenue growth for firms with an AI time series (hypothesis H2).", None),
        ("Sizing        - three market-sizing lenses and the definitional gap to Gartner.", None),
        ("Scenarios     - 2027-2030 projection: AI growth vs core deflation; pick a scenario in C2.", None),
        ("P1_Momentum   - Project 1 event counts per firm, computed live with COUNTIFS from the P1_Events sheet.", None),
        ("Checks        - every check should read TRUE.", None),
        ("", None),
        ("Evidence grades: A = company-reported figure | B = derived from a company figure | C = analyst estimate with stated range.", None),
        ("Run-rate = latest quarter x 4. Accenture's latest quarter is Q4 FY26 (Jun-Aug 2026); all others Jul-Sep 2026.", NOTE),
        ("Capgemini EUR converted at Reuters' $1 = 0.8957 EUR for both quarters (constant-FX comparison).", NOTE),
    ]
    for i, (t, f) in enumerate(lines, 1):
        c = ws.cell(i, 1, t)
        if f:
            c.font = f
    widths(ws, [150])

    # ------------------------------------------------------------- Inputs
    inp = wb.create_sheet("Inputs")
    inp["A1"] = "Company inputs as reported (USD m unless stated)"
    inp["A1"].font = TITLE
    cols = ["Company", "Latest period", "Revenue latest Q", "Revenue year-ago Q", "Growth YoY CC (reported)",
            "Bookings latest Q", "Bookings basis", "Headcount latest", "Headcount year-ago", "Revenue basis / note", "Source IDs"]
    header(inp, 3, cols)
    for i, co in enumerate(COS):
        r = 4 + i
        L = q[(q.company == co) & (q.is_latest == 1)].iloc[0]
        P = q[(q.company == co) & (q.is_latest == 0)].iloc[0]
        inp.cell(r, 1, co)
        inp.cell(r, 2, L.period_label)
        setf(inp.cell(r, 3), float(L.revenue_usd_m), BLUE, USD1)
        setf(inp.cell(r, 4), float(P.revenue_usd_m), BLUE, USD1)
        setf(inp.cell(r, 5), float(L.yoy_growth_cc_pct) / 100, BLUE, PCT)
        setf(inp.cell(r, 6), float(L.bookings_usd_m), BLUE, USD)
        inp.cell(r, 7, L.bookings_basis)
        setf(inp.cell(r, 8), int(L.headcount), BLUE, "#,##0")
        setf(inp.cell(r, 9), int(P.headcount), BLUE, "#,##0")
        inp.cell(r, 10, f"{L.revenue_basis} | prior: {P.revenue_basis}")
        inp.cell(r, 11, f"{L.source_id}; {P.source_id}")
    widths(inp, [14, 24, 12, 12, 11, 12, 30, 12, 12, 50, 50])
    inp.freeze_panes = "B4"
    R0, R1 = 4, 4 + len(COS) - 1

    # ------------------------------------------------------------- Metrics
    m = wb.create_sheet("Metrics")
    m["A1"] = "Derived metrics (formulas)"
    m["A1"].font = TITLE
    header(m, 3, ["Company", "Revenue run-rate (USD m)", "Share of eight", "Revenue YoY (USD)", "Growth YoY CC",
                  "Headcount YoY", "Decoupling gap (pp)", "Revenue / employee (USD k)", "Rev/employee YoY",
                  "Book-to-bill", "Share of Gartner IT services 2026"])
    for i in range(len(COS)):
        r, s = 4 + i, R0 + i
        setf(m.cell(r, 1), f"=Inputs!A{s}", GREEN)
        setf(m.cell(r, 2), f"=Inputs!C{s}*4", GREEN, USD)
        setf(m.cell(r, 3), f"=B{r}/SUM($B$4:$B${3 + len(COS)})", None, PCT)
        setf(m.cell(r, 4), f"=Inputs!C{s}/Inputs!D{s}-1", GREEN, PCT)
        setf(m.cell(r, 5), f"=Inputs!E{s}", GREEN, PCT)
        setf(m.cell(r, 6), f"=Inputs!H{s}/Inputs!I{s}-1", GREEN, PCT)
        setf(m.cell(r, 7), f"=(D{r}-F{r})*100", None, '+0.0;-0.0')
        setf(m.cell(r, 8), f"=B{r}*1000/Inputs!H{s}", GREEN, USD1)
        setf(m.cell(r, 9), f"=H{r}/(Inputs!D{s}*4*1000/Inputs!I{s})-1", GREEN, PCT)
        setf(m.cell(r, 10), f"=Inputs!F{s}/Inputs!C{s}", GREEN, X2)
        setf(m.cell(r, 11), f"=B{r}/Sizing!$C$5", GREEN, '0.00%')
    MT = 4 + len(COS)
    m.cell(MT, 1, "Eight firms").font = BOLD
    setf(m.cell(MT, 2), f"=SUM(B4:B{MT - 1})", BOLD, USD)
    setf(m.cell(MT, 4), f"=SUM(Inputs!C{R0}:C{R1})/SUM(Inputs!D{R0}:D{R1})-1", GREEN, PCT)
    setf(m.cell(MT, 11), f"=SUM(K4:K{MT - 1})", None, '0.0%')
    widths(m, [14] + [13] * 10)

    # ------------------------------------------------------------- AI_Pool
    p = wb.create_sheet("AI_Pool")
    p["A1"] = "AI revenue run-rate by firm (USD m, annualised)"
    p["A1"].font = TITLE
    p["A2"] = "Estimate case:"
    p["A2"].font = BOLD
    setf(p["C2"], "Mid", BLUE, None, KEY)
    dv = DataValidation(type="list", formula1='"Low,Mid,High"')
    p.add_data_validation(dv)
    dv.add("C2")
    header(p, 4, ["Company", "Grade", "Unit of assumption", "Low", "Mid", "High", "Revenue run-rate",
                  "AI run-rate (selected case)", "AI share of revenue", "Share of AI pool", "AI share index", "Method / rationale"])
    grade = {"TCS": "A", "HCLTech": "A", "Infosys": "B", "Accenture": "B"}
    for i, co in enumerate(COS):
        r = 5 + i
        a = assum.loc[co]
        p.cell(r, 1, co)
        p.cell(r, 2, grade.get(co, "C"))
        p.cell(r, 3, a.unit)
        is_pct = a.unit != "USD m"
        for j, v in enumerate([a.low, a.mid, a.high]):
            setf(p.cell(r, 4 + j), float(v) / 100 if is_pct else float(v), BLUE, PCT if is_pct else USD, KEY)
        setf(p.cell(r, 7), f"=Metrics!B{4 + i}", GREEN, USD)
        pick = 'INDEX(D{r}:F{r},MATCH($C$2,{{"Low","Mid","High"}},0))'.format(r=r)
        setf(p.cell(r, 8), f'=IF(C{r}="USD m",{pick},{pick}*G{r})', None, USD)
        setf(p.cell(r, 9), f"=H{r}/G{r}", None, PCT)
        setf(p.cell(r, 10), f"=H{r}/SUM($H$5:$H${4 + len(COS)})", None, PCT)
        setf(p.cell(r, 11), f"=J{r}/Metrics!C{4 + i}", GREEN, X2)
        p.cell(r, 12, f"{a.method}: {a.rationale}").font = NOTE
    PT = 5 + len(COS)
    p.cell(PT, 1, "Eight-firm pool").font = BOLD
    setf(p.cell(PT, 7), f"=SUM(G5:G{PT - 1})", BOLD, USD)
    setf(p.cell(PT, 8), f"=SUM(H5:H{PT - 1})", BOLD, USD)
    setf(p.cell(PT, 9), f"=H{PT}/G{PT}", BOLD, PCT)
    p.cell(PT + 1, 1, "Share of pool on company figures (grade A/B)")
    setf(p.cell(PT + 1, 8), f'=SUMIF(B5:B{PT - 1},"A",H5:H{PT - 1})+SUMIF(B5:B{PT - 1},"B",H5:H{PT - 1})', None, USD)
    setf(p.cell(PT + 1, 9), f"=H{PT + 1}/H{PT}", None, PCT)
    widths(p, [14, 7, 11, 10, 10, 10, 12, 14, 11, 11, 10, 110])

    # ------------------------------------------------------------- Core_vs_AI
    c = wb.create_sheet("Core_vs_AI")
    c["A1"] = "Is AI growth replacing core revenue? (USD m per quarter or fiscal year)"
    c["A1"].font = TITLE
    header(c, 3, ["Company", "Window", "Years", "Revenue start", "AI start", "Revenue end", "AI end",
                  "Core start", "Core end", "Total growth p.a.", "AI growth p.a.", "Core growth p.a.", "Note"])
    tcs_ai0 = ai[(ai.company == "TCS") & (ai.quarter_end == "2025-12-31")].value.iloc[0] / 4
    tcs_ai1 = ai[(ai.company == "TCS") & (ai.quarter_end == "2026-09-30")].value.iloc[0] / 4
    inf0 = ai[(ai.company == "Infosys") & (ai.quarter_end == "2025-12-31")].value.iloc[0] / 100
    inf1 = ai[(ai.company == "Infosys") & (ai.quarter_end == "2026-09-30")].value.iloc[0] / 100
    hcl0 = ai[(ai.company == "HCLTech") & (ai.quarter_end == "2025-09-30")].value.iloc[0]
    hcl1 = ai[(ai.company == "HCLTech") & (ai.quarter_end == "2026-09-30") & (ai.metric == "ai_revenue_quarter")].value.iloc[0]
    rr = lambda co, pe: float(ref[(ref.company == co) & (ref.period_end == pe)].revenue_usd_m.iloc[0])  # noqa: E731
    rows = [
        ("TCS", "Q3 FY26 -> Q2 FY27", 0.75, rr("TCS", "2025-12-31"), tcs_ai0, "=Inputs!C5", tcs_ai1, "AI = annualised / 4"),
        ("Infosys", "Q3 FY26 -> Q2 FY27", 0.75, rr("Infosys", "2025-12-31"), f"={inf0}*D5", "=Inputs!C6", f"={inf1}*F5", "AI = reported share x revenue (5.5% -> 10.5%)"),
        ("HCLTech", "Q2 FY26 -> Q2 FY27", 1.0, "=Inputs!D7", hcl0, "=Inputs!C7", hcl1, "Q2 FY26 AI derived (219 / 1.78)"),
        ("Accenture", "FY24 -> FY25", 1.0, rr("Accenture", "2024-08-31"), 900, rr("Accenture", "2025-08-31"), 2700, "Fiscal years; FY24 AI derived ('tripled')"),
    ]
    for i, (co, w, yrs, r0v, a0, r1v, a1, note) in enumerate(rows):
        r = 4 + i
        c.cell(r, 1, co)
        c.cell(r, 2, w)
        setf(c.cell(r, 3), yrs, BLUE, "0.00")
        for j, v in enumerate([r0v, a0, r1v, a1]):
            isf = isinstance(v, str)
            setf(c.cell(r, 4 + j), v, GREEN if isf and "!" in v else (None if isf else BLUE), USD)
        setf(c.cell(r, 8), f"=D{r}-E{r}", None, USD)
        setf(c.cell(r, 9), f"=F{r}-G{r}", None, USD)
        setf(c.cell(r, 10), f"=(F{r}/D{r})^(1/C{r})-1", None, PCT)
        setf(c.cell(r, 11), f"=(G{r}/E{r})^(1/C{r})-1", None, PCT)
        setf(c.cell(r, 12), f"=(I{r}/H{r})^(1/C{r})-1", None, PCT)
        c.cell(r, 13, note).font = NOTE
    widths(c, [12, 20, 7, 11, 10, 11, 10, 11, 11, 11, 11, 11, 44])

    # ------------------------------------------------------------- Sizing
    z = wb.create_sheet("Sizing")
    z["A1"] = "Market sizing - three lenses (USD m)"
    z["A1"].font = TITLE
    header(z, 3, ["Lens", "Measure", "Value", "Note"])
    lens = [
        ("A. Analyst top-down", "Gartner AI services spending 2026", float(est.loc["GARTNER_AI_SVC_2026", "value_usd_m"]), True, "GARTNER_AI_SEP26 (Sep-2026)"),
        ("Reference", "Gartner IT services spending 2026", float(est.loc["GARTNER_ITS_2026", "value_usd_m"]), True, "GARTNER_IT_FEB26 (Feb-2026)"),
        ("B. Management view", "Infosys: AI services market (mid of $300-400 bn)", 350000.0, True, "INFY_MKT"),
        ("C. Bottom-up", "Eight-firm AI run-rate (selected case)", f"=AI_Pool!H{PT}", False, "AI_Pool sheet"),
        ("C. Bottom-up", "Eight firms' share of Gartner IT services", f"=Metrics!B{MT}/C5", False, "Revenue run-rate / Gartner IT services 2026"),
        ("C. Bottom-up", "Implied vendor-labelled AI services market", "=C7/C8", False, "Assumes the rest of the market has the eight firms' AI intensity"),
        ("Gap", "Gartner AI services / implied vendor-labelled market", "=C4/C9", False, "Gartner counts AI embedded in ordinary projects"),
        ("Gap", "Eight firms' AI pool as % of Gartner AI services", "=C7/C4", False, ""),
    ]
    for i, (a, b, v, is_in, note) in enumerate(lens):
        r = 4 + i
        z.cell(r, 1, a)
        z.cell(r, 2, b)
        fmt = PCT if "share" in b.lower() or "%" in b else (X2 if "/" in b else USD)
        setf(z.cell(r, 3), v, BLUE if is_in else (GREEN if isinstance(v, str) and "!" in v else None), fmt)
        z.cell(r, 4, note).font = NOTE
    widths(z, [20, 52, 14, 60])

    # ------------------------------------------------------------- Scenarios
    s = wb.create_sheet("Scenarios")
    s["A1"] = "2027-2030 scenarios for the eight firms (USD m): AI growth vs core-services deflation"
    s["A1"].font = TITLE
    s["A2"] = "Selected scenario:"
    s["A2"].font = BOLD
    setf(s["C2"], "Base", BLUE, None, KEY)
    dv2 = DataValidation(type="list", formula1='"Bear,Base,Bull"')
    s.add_data_validation(dv2)
    dv2.add("C2")
    header(s, 4, ["Lever", "Scenario"] + [str(y) for y in YEARS])
    r = 5
    lever_rows = {}
    for lever in ["ai_growth", "core_growth"]:
        for sc in ["Bear", "Base", "Bull"]:
            s.cell(r, 1, "AI revenue growth" if lever == "ai_growth" else "Core (non-AI) growth")
            s.cell(r, 2, sc)
            for j, v in enumerate(SCENARIOS[sc][lever]):
                setf(s.cell(r, 3 + j), v, BLUE, PCT, KEY)
            lever_rows[(lever, sc)] = r
            r += 1
    s.cell(r + 1, 1, "Starting point (CY Q3 2026 run-rate)").font = BOLD
    s.cell(r + 2, 1, "AI revenue")
    setf(s.cell(r + 2, 3), f"=AI_Pool!H{PT}", GREEN, USD)
    s.cell(r + 3, 1, "Total revenue")
    setf(s.cell(r + 3, 3), f"=Metrics!B{MT}", GREEN, USD)
    s.cell(r + 4, 1, "Core revenue")
    setf(s.cell(r + 4, 3), f"=C{r + 3}-C{r + 2}", None, USD)
    AI0, CORE0 = r + 2, r + 4
    base = r + 6
    header(s, base, ["Scenario", "Line", "2026"] + [str(y) for y in YEARS] + ["CAGR 2026-30"])
    rr_ = base + 1
    out_rows = {}
    for sc in ["Bear", "Base", "Bull"]:
        ra, rc, rt, rs, rn = rr_, rr_ + 1, rr_ + 2, rr_ + 3, rr_ + 4
        for row, lab in [(ra, "AI revenue"), (rc, "Core revenue"), (rt, "Total revenue"), (rs, "AI share of total"), (rn, "AI growth needed to hold total flat")]:
            s.cell(row, 1, sc)
            s.cell(row, 2, lab)
        setf(s.cell(ra, 3), f"=$C${AI0}", None, USD)
        setf(s.cell(rc, 3), f"=$C${CORE0}", None, USD)
        for j in range(len(YEARS) + 1):
            col = get_column_letter(3 + j)
            if j:
                prev = get_column_letter(2 + j)
                lv = get_column_letter(2 + j)  # lever column for this year (C..F)
                setf(s.cell(ra, 3 + j), f"={prev}{ra}*(1+{lv}{lever_rows[('ai_growth', sc)]})", None, USD)
                setf(s.cell(rc, 3 + j), f"={prev}{rc}*(1+{lv}{lever_rows[('core_growth', sc)]})", None, USD)
                setf(s.cell(rn, 3 + j), f"=MAX(0,-{lv}{lever_rows[('core_growth', sc)]}*{prev}{rc}/{prev}{ra})", None, PCT)
            setf(s.cell(rt, 3 + j), f"={col}{ra}+{col}{rc}", BOLD, USD)
            setf(s.cell(rs, 3 + j), f"={col}{ra}/{col}{rt}", None, PCT)
        setf(s.cell(rt, 8), f"=(G{rt}/C{rt})^(1/4)-1", BOLD, PCT)
        out_rows[sc] = rt
        rr_ += 6
    sel = rr_ + 1
    s.cell(sel, 1, "Selected scenario").font = BOLD
    s.cell(sel + 1, 1, "Total revenue 2030")
    setf(s.cell(sel + 1, 3), f'=INDEX(G{out_rows["Bear"]}:G{out_rows["Bull"]},MATCH(C2,{{"Bear","Base","Bull"}},0)*6-5)', None, USD)
    s.cell(sel + 2, 1, "CAGR 2026-2030")
    setf(s.cell(sel + 2, 3), f'=INDEX(H{out_rows["Bear"]}:H{out_rows["Bull"]},MATCH(C2,{{"Bear","Base","Bull"}},0)*6-5)', None, PCT)
    s.cell(sel + 3, 1, "Gartner IT services growth 2026 (market benchmark)")
    setf(s.cell(sel + 3, 3), "=Sizing!C5/" + str(float(est.loc["GARTNER_ITS_2025", "value_usd_m"])) + "-1", GREEN, PCT)
    for i, sc in enumerate(["Bear", "Base", "Bull"]):
        s.cell(sel + 5 + i, 1, sc).font = BOLD
        s.cell(sel + 5 + i, 2, SCENARIOS[sc]["story"]).font = NOTE
    widths(s, [34, 22, 12, 12, 12, 12, 12, 12])
    SC_OUT = out_rows

    # ------------------------------------------------------------- P1_Events + P1_Momentum
    e = wb.create_sheet("P1_Events")
    ecols = ["event_id", "company", "event_date", "event_type", "counterparty", "counterparty_type", "headline",
             "deal_value_usd_m", "validation_status", "source_url"]
    header(e, 1, ecols)
    for i, rec in enumerate(ev[ecols].itertuples(index=False), 2):
        for j, v in enumerate(rec, 1):
            e.cell(i, j, None if (isinstance(v, float) and pd.isna(v)) else v)
    EN = len(ev) + 1
    widths(e, [10, 14, 11, 18, 18, 18, 60, 10, 12, 60])
    pm = wb.create_sheet("P1_Momentum")
    pm["A1"] = "Project 1 announcement momentum vs this project's monetisation metrics"
    pm["A1"].font = TITLE
    header(pm, 3, ["Company", "Verified events", "Partnerships", "Frontier-lab events", "Acquisitions", "AI share of revenue", "Growth YoY CC"])
    rng = lambda col: f"P1_Events!${col}$2:${col}${EN}"  # noqa: E731
    for i, co in enumerate(COS):
        r = 4 + i
        pm.cell(r, 1, co)
        V = f'{rng("I")},"Verified"'
        setf(pm.cell(r, 2), f'=COUNTIFS({rng("B")},A{r},{V})', GREEN, "0")
        setf(pm.cell(r, 3), f'=COUNTIFS({rng("B")},A{r},{rng("D")},"Partnership",{V})', GREEN, "0")
        setf(pm.cell(r, 4), f'=COUNTIFS({rng("B")},A{r},{rng("F")},"Frontier model lab",{V})', GREEN, "0")
        setf(pm.cell(r, 5), f'=COUNTIFS({rng("B")},A{r},{rng("D")},"Acquisition",{V})', GREEN, "0")
        setf(pm.cell(r, 6), f"=AI_Pool!I{5 + i}", GREEN, PCT)
        setf(pm.cell(r, 7), f"=Metrics!E{4 + i}", GREEN, PCT)
    pm.cell(13, 1, "Rank correlation (Spearman) is computed in src/analysis.py; see README H5.").font = NOTE
    widths(pm, [14, 12, 12, 14, 12, 14, 12])

    # ------------------------------------------------------------- Sources
    so = wb.create_sheet("Sources")
    header(so, 1, list(src.columns))
    for i, rec in enumerate(src.itertuples(index=False), 2):
        for j, v in enumerate(rec, 1):
            so.cell(i, j, v)
    widths(so, [18, 26, 60, 12, 60, 24])

    # ------------------------------------------------------------- Checks
    k = wb.create_sheet("Checks", 1)
    k["A1"] = "Model checks (all should be TRUE)"
    k["A1"].font = TITLE
    header(k, 3, ["Check", "Result"])
    checks = [
        ("Revenue shares sum to 100%", f"=ABS(SUM(Metrics!C4:C{MT - 1})-1)<0.0001"),
        ("AI pool shares sum to 100%", f"=ABS(SUM(AI_Pool!J5:J{PT - 1})-1)<0.0001"),
        ("Low <= Mid <= High for every AI estimate", f"=SUMPRODUCT(--(AI_Pool!D5:D{PT - 1}<=AI_Pool!E5:E{PT - 1}),--(AI_Pool!E5:E{PT - 1}<=AI_Pool!F5:F{PT - 1}))={len(COS)}"),
        ("TCS AI share > 10% (company says '>10% of revenue')", "=AI_Pool!I6>0.1"),
        ("Project 1 verified events = 79", f"=SUM(P1_Momentum!B4:B{3 + len(COS)})=79"),
        ("Bear <= Base <= Bull total revenue in 2030", f"=AND(Scenarios!G{SC_OUT['Bear']}<=Scenarios!G{SC_OUT['Base']},Scenarios!G{SC_OUT['Base']}<=Scenarios!G{SC_OUT['Bull']})"),
        ("Core shrinks at Infosys and TCS (H2)", "=AND(Core_vs_AI!L4<0,Core_vs_AI!L5<0)"),
    ]
    for i, (lab, f) in enumerate(checks):
        k.cell(4 + i, 1, lab)
        k.cell(4 + i, 2, f)
    widths(k, [60, 10])

    fontify(wb)
    XLSX.parent.mkdir(exist_ok=True)
    wb.save(XLSX)
    print("wrote", XLSX.relative_to(ROOT))


if __name__ == "__main__":
    main()

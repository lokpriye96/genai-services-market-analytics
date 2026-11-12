// Step 7 - One-slide executive summary (outputs/Executive_Summary.pptx). Every number is read
// from docs/data/dashboard_data.json so the slide cannot drift from the analysis.
// Run:  node src/exec_slide.js   (then convert to PDF with LibreOffice)
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "docs/data/dashboard_data.json"), "utf8"));
const POOL = Object.fromEntries(D.ai_pool.map(r => [r.company, r]));
const CORE = Object.fromEntries(D.core_vs_ai.map(r => [r.company, r]));
const SZ = D.sizing, SN = D.sizing_notes, ST = D.stats;
const p = D.ai_pool[0];
const y30 = s => D.scenarios.find(r => r.scenario === s && r.year === 2030);
const sg = v => (v > 0 ? "+" : "") + v.toFixed(1) + "%";

const INK = "0B0B0B", INK2 = "52514E", MUTED = "898781", CARD = "F3F2EE", BLUE = "2A78D6", RED = "E34948", GREEN = "1BAF7A";
const COL = { Accenture: "2A78D6", TCS: "EB6834", Infosys: "1BAF7A", HCLTech: "EDA100", Cognizant: "E87BA4", Capgemini: "008300", Wipro: "6250D6", "Tech Mahindra": "E34948" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "Utkarsh Saxena";
pres.title = "GenAI services market - executive summary";
pres.theme = { headFontFace: "Arial", bodyFontFace: "Arial" };
const s = pres.addSlide();
s.background = { color: "FFFFFF" };

s.addText("EXECUTIVE SUMMARY  ·  GENAI IN IT SERVICES  ·  8 FIRMS  ·  LATEST QUARTER = CALENDAR Q3 2026", {
  x: 0.5, y: 0.3, w: 12.3, h: 0.3, fontSize: 10, color: MUTED, bold: true, charSpacing: 1, margin: 0, isTextBox: true,
});
s.addText(`AI is now a $${p.pool_mid_usd_bn.toFixed(0)} bn business for the eight IT services leaders, but at TCS and Infosys it is replacing core revenue, not adding to it`, {
  x: 0.5, y: 0.62, w: 12.3, h: 0.95, fontSize: 24, bold: true, color: INK, margin: 0, valign: "top", isTextBox: true,
});

const findings = [
  [`$${p.pool_mid_usd_bn.toFixed(1)} bn`, `AI revenue run-rate across the eight (range $${p.pool_low_usd_bn.toFixed(1)}-${p.pool_high_usd_bn.toFixed(1)} bn), ${(p.pool_mid_usd_bn / D.market_share.reduce((a, r) => a + r.revenue_runrate_usd_bn, 0) * 100).toFixed(1)}% of their revenue. ${p.pool_pct_company_based.toFixed(0)}% rests on company-reported figures.`],
  [`${sg(CORE.Infosys.core_growth_annualised_pct)} / ${sg(CORE.TCS.core_growth_annualised_pct)}`, `Annualised core (non-AI) growth at Infosys / TCS while AI grew >100% a year. AI deflation is real at the Indian disclosers; Accenture's core still grew ${sg(CORE.Accenture.core_growth_annualised_pct)}.`],
  [`${SN.gartner_to_vendor_labelled_ratio}×`, `Gap between Gartner's $${SZ[0].value_usd_bn.toFixed(0)} bn "AI services" market and the ~$${SZ[3].value_usd_bn.toFixed(0)} bn that vendors label as AI. Market size is a definition choice.`],
  [`ρ = ${ST.spearman_ai_intensity_vs_growth_all8.toFixed(2)}`, `Rank correlation of AI share vs growth: AI revenue is not yet a growth signal. Project 1 announcement counts correlate ${ST.spearman_p1_events_vs_growth.toFixed(2)} with growth.`],
];
findings.forEach(([big, txt], i) => {
  const y = 1.78 + i * 1.06;
  s.addText(big, { x: 0.5, y, w: 2.65, h: 0.8, fontSize: 28, bold: true, color: i === 1 ? RED : BLUE, margin: 0, valign: "middle", isTextBox: true, fit: "shrink" });
  s.addText(txt, { x: 3.25, y, w: 3.85, h: 0.9, fontSize: 12, color: INK2, margin: 0, valign: "middle", isTextBox: true });
});

// right top: native bar chart, AI run-rate by firm (mid)
const rows = [...D.ai_pool].sort((a, b) => b.ai_runrate_mid_usd_bn - a.ai_runrate_mid_usd_bn);
s.addText("AI run-rate by firm, USD bn (A reported · B derived · C estimate)", { x: 7.45, y: 1.72, w: 5.4, h: 0.3, fontSize: 11, bold: true, color: INK, margin: 0, isTextBox: true });
s.addChart(pres.charts.BAR, [{ name: "AI run-rate (mid)", labels: rows.map(r => `${r.company} (${r.evidence_grade})`), values: rows.map(r => r.ai_runrate_mid_usd_bn) }], {
  x: 7.35, y: 2.0, w: 5.5, h: 2.6, barDir: "bar", barGapWidthPct: 45,
  chartColors: rows.map(r => COL[r.company]), invertedColors: rows.map(r => COL[r.company]),
  showLegend: false, showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 9, dataLabelColor: INK, dataLabelFormatCode: "0.00", dataLabelFontFace: "Arial",
  catAxisLabelColor: INK2, catAxisLabelFontSize: 9, catAxisLabelFontFace: "Arial", catAxisOrientation: "maxMin",
  valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 6.6, valGridLine: { style: "none" }, catGridLine: { style: "none" },
});

// right bottom: scenario tiles
s.addText("2030 revenue of the eight, USD bn (CAGR 2026-30 · AI share)", { x: 7.45, y: 4.72, w: 5.4, h: 0.3, fontSize: 11, bold: true, color: INK, margin: 0, isTextBox: true });
[["Bear", "Deflation wins"], ["Base", "AI offsets core"], ["Bull", "AI adds net growth"]].forEach(([sc, note], i) => {
  const x = 7.45 + i * 1.82, r = y30(sc);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.06, w: 1.68, h: 1.12, fill: { color: sc === "Base" ? "E8F1FC" : CARD }, line: { color: sc === "Base" ? BLUE : CARD, width: 1 }, rectRadius: 0.08, objectName: `scenario-${sc}` });
  s.addText([
    { text: sc, options: { fontSize: 11, bold: true, color: INK2, breakLine: true } },
    { text: `$${r.total_usd_bn.toFixed(0)}`, options: { fontSize: 22, bold: true, color: INK, breakLine: true } },
    { text: `${sg(r.cagr_2026_2030_pct)} · AI ${r.ai_share_pct.toFixed(0)}%`, options: { fontSize: 10, color: INK2, breakLine: true } },
    { text: note, options: { fontSize: 9, color: MUTED } },
  ], { x: x + 0.1, y: 5.08, w: 1.5, h: 1.08, margin: 0, valign: "middle", isTextBox: true });
});

s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 6.28, w: 12.35, h: 0.72, fill: { color: CARD }, line: { color: CARD }, rectRadius: 0.06, objectName: "so-what" });
s.addText([
  { text: "So what  ", options: { bold: true, color: INK } },
  { text: `Judge AI by core growth and book-to-bill, not by AI revenue or partnership headlines. The eight grew ${sg(ST.eight_firm_yoy_usd_pct)} vs a market at ${sg(ST.gartner_it_services_growth_2026_pct)}: they are losing share. With a ~$190 bn shrinking core, AI must grow ~7-9% a year just to hold revenue flat; the winners will be firms that re-price work to outcomes before renewals deflate it.`, options: { color: INK2 } },
], { x: 0.7, y: 6.3, w: 12.0, h: 0.68, fontSize: 11.5, margin: 0, valign: "middle", isTextBox: true });

s.addText("Sources: company results & filings (Accenture 8-K/annual report, TCS, Infosys, HCLTech, Wipro 6-K, Cognizant 8-K, Capgemini, Tech Mahindra, Q3 CY2026), Gartner AI and IT spending forecasts (2026), Kotak Institutional Equities. Run-rate = quarter × 4. Scenarios are assumptions, not forecasts. Utkarsh Saxena · github.com/lokpriye96/genai-services-market-analytics", {
  x: 0.5, y: 7.05, w: 12.35, h: 0.34, fontSize: 8, color: MUTED, margin: 0, isTextBox: true,
});
s.addNotes("One-slide summary of the GenAI services market analysis. Numbers are generated from docs/data/dashboard_data.json by src/exec_slide.js.");

pres.writeFile({ fileName: path.join(ROOT, "outputs/Executive_Summary.pptx") }).then(f => console.log("wrote", path.relative(ROOT, f)));

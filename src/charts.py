"""
Step 6 - Static charts (PNG) for the README and the executive slide.
Colours follow the entity (one fixed hue per company), validated categorical palette.

Run:  python src/charts.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "charts"
COL = {"Accenture": "#2a78d6", "TCS": "#eb6834", "Infosys": "#1baf7a", "HCLTech": "#eda100",
       "Cognizant": "#e87ba4", "Capgemini": "#008300", "Wipro": "#6250d6", "Tech Mahindra": "#e34948"}
INK, INK2, GRID, MUTED = "#0b0b0b", "#52514e", "#e1e0d9", "#898781"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150})


def _finish(fig, ax, name, title, sub=None):
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color=INK, pad=22 if sub else 8)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9, color=INK2)
    fig.tight_layout()
    fig.savefig(OUT / name, facecolor="white")
    plt.close(fig)


def ai_pool(d):
    rows = sorted(d["ai_pool"], key=lambda r: r["ai_runrate_mid_usd_bn"])
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    for i, r in enumerate(rows):
        est = r["evidence_grade"] == "C"
        ax.barh(i, r["ai_runrate_mid_usd_bn"], color=COL[r["company"]], alpha=.45 if est else 1, height=.6)
        if r["ai_runrate_high_usd_bn"] > r["ai_runrate_low_usd_bn"]:
            ax.errorbar(r["ai_runrate_mid_usd_bn"], i, xerr=[[r["ai_runrate_mid_usd_bn"] - r["ai_runrate_low_usd_bn"]],
                        [r["ai_runrate_high_usd_bn"] - r["ai_runrate_mid_usd_bn"]]], color=INK, capsize=3, lw=1)
        ax.text(r["ai_runrate_high_usd_bn"] + .1, i, f"${r['ai_runrate_mid_usd_bn']:.2f} bn  ·  {r['evidence_grade']}  ·  {r['ai_share_of_revenue_pct']:.1f}% of rev",
                va="center", fontsize=8.5, color=INK)
    ax.set_yticks(range(len(rows)), [r["company"] for r in rows])
    ax.set_xlim(0, 9.5); ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
    ax.set_xlabel("AI revenue run-rate, USD bn (mid case; whisker = low-high)")
    p = d["ai_pool"][0]
    _finish(fig, ax, "ai_pool.png", f"AI revenue pool: ${p['pool_mid_usd_bn']:.1f} bn across eight firms",
            f"Range ${p['pool_low_usd_bn']:.1f}-{p['pool_high_usd_bn']:.1f} bn; {p['pool_pct_company_based']:.0f}% rests on company figures. Light bars = grade C estimates.")


def core_vs_ai(d):
    rows = {r["company"]: r for r in d["core_vs_ai"]}
    cos = ["Infosys", "TCS", "HCLTech", "Accenture"]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    w = .36
    for i, c in enumerate(cos):
        t, k = rows[c]["total_growth_annualised_pct"], rows[c]["core_growth_annualised_pct"]
        ax.bar(i - w / 2 - .02, t, w, color=MUTED)
        ax.bar(i + w / 2 + .02, k, w, color="#e34948" if k < 0 else "#2a78d6")
        for x, v in [(i - w / 2 - .02, t), (i + w / 2 + .02, k)]:
            ax.text(x, v + (.3 if v >= 0 else -.3), f"{v:+.1f}%", ha="center", va="bottom" if v >= 0 else "top", fontsize=8.5, color=INK, fontweight="bold")
    ax.axhline(0, color="#c3c2b7", lw=1)
    ax.set_xticks(range(len(cos)), [f"{c}\nAI {rows[c]['ai_growth_annualised_pct']:+.0f}%" for c in cos], fontsize=9)
    ax.set_ylim(-8, 9.5); ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_ylabel("% per year")
    ax.bar(0, 0, color=MUTED, label="Total revenue growth"); ax.bar(0, 0, color="#e34948", label="Core (non-AI) growth")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    _finish(fig, ax, "core_vs_ai.png", "AI deflation: core revenue is shrinking at the Indian disclosers",
            "Annualised growth; core = total revenue minus disclosed AI revenue. Label under firm = AI growth p.a.")


def positioning(d):
    ms = {r["company"]: r for r in d["market_share"]}
    fig, ax = plt.subplots(figsize=(7.2, 4))
    for r in d["ai_pool"]:
        c, m = r["company"], ms[r["company"]]
        est = r["evidence_grade"] == "C"
        ax.scatter(r["ai_share_of_revenue_pct"], m["yoy_cc_pct"], s=m["revenue_runrate_usd_bn"] * 9,
                   facecolor="none" if est else COL[c], edgecolor=COL[c], lw=2, alpha=.85, zorder=3)
        off = {"Tech Mahindra": (-8, 0, "right"), "Infosys": (10, -2, "left"), "TCS": (12, 6, "left")}.get(c, (10, 0, "left"))
        ax.annotate(c, (r["ai_share_of_revenue_pct"], m["yoy_cc_pct"]), xytext=off[:2], textcoords="offset points",
                    ha=off[2], va="center", fontsize=8.5, fontweight="bold", color=INK)
    ax.set_xlim(0, 12.5); ax.set_ylim(-1, 13.5); ax.grid(True, color=GRID); ax.set_axisbelow(True)
    ax.set_xlabel("AI share of revenue (%)"); ax.set_ylabel("Revenue growth YoY, constant currency (%)")
    s = d["stats"]
    _finish(fig, ax, "positioning.png", "More AI revenue is not (yet) more growth",
            f"Spearman rho = {s['spearman_ai_intensity_vs_growth_all8']:+.2f} (all 8), {s['spearman_ai_intensity_vs_growth_disclosers']:+.2f} (4 disclosers). Bubble = revenue; hollow = estimate.")


def scenarios(d):
    col = {"Bear": "#e34948", "Base": "#2a78d6", "Bull": "#1baf7a"}
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for s in ["Bear", "Base", "Bull"]:
        pts = [r for r in d["scenarios"] if r["scenario"] == s]
        ax.plot([r["year"] for r in pts], [r["total_usd_bn"] for r in pts], marker="o", color=col[s], lw=2,
                ls="-" if s == "Base" else "--")
        l = pts[-1]
        ax.text(2030.08, l["total_usd_bn"], f"{s} ${l['total_usd_bn']:.0f} bn ({l['cagr_2026_2030_pct']:+.1f}% CAGR, AI {l['ai_share_pct']:.0f}%)",
                va="center", fontsize=8.5, color=INK, fontweight="bold")
    ax.set_xlim(2025.8, 2032.4); ax.set_xticks([2026, 2027, 2028, 2029, 2030], ["2026\n(run-rate)", "2027", "2028", "2029", "2030"])
    ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True); ax.set_ylabel("Total revenue, eight firms, USD bn")
    _finish(fig, ax, "scenarios.png", "2030 scenarios: AI growth vs core deflation",
            "Levers: AI growth and core (non-AI) growth per year, calibrated on 2025-26 data")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = json.loads((ROOT / "docs" / "data" / "dashboard_data.json").read_text())
    for fn in (ai_pool, core_vs_ai, positioning, scenarios):
        fn(d)
    print("charts ->", sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()

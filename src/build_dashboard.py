"""
Step 5 - Build the interactive web dashboard (docs/index.html, served by GitHub Pages).
Data from docs/data/dashboard_data.json is inlined so the page also works offline.

Run:  python src/build_dashboard.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    tpl = (ROOT / "src" / "dashboard_template.html").read_text(encoding="utf-8")
    data = (ROOT / "docs" / "data" / "dashboard_data.json").read_text(encoding="utf-8").replace("</", "<\\/")
    out = ROOT / "docs" / "index.html"
    out.write_text(tpl.replace("/*__DATA__*/null", data), encoding="utf-8")
    (ROOT / "docs" / ".nojekyll").write_text("")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

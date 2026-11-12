#!/usr/bin/env bash
# Rebuild everything from the raw transcribed data, in order.
set -euo pipefail
cd "$(dirname "$0")"
python src/clean.py            # raw -> data/processed (types, derived values, AI pool estimates)
python src/build_db.py         # processed -> db/genai_services.db, runs sql/01-07 (fails if a quality check fails)
python src/analysis.py         # sizing, hypotheses, scenarios -> outputs/analysis, docs/data
python src/build_excel.py      # Excel model with live formulas
python src/charts.py           # static PNG charts
python src/build_dashboard.py  # docs/index.html (GitHub Pages)
python src/export_powerbi.py   # powerbi/*.csv star schema
node src/exec_slide.js         # outputs/Executive_Summary.pptx (needs: npm i pptxgenjs)
# Optional: recalculate the workbook so cached values exist for viewers without Excel
# soffice --headless --convert-to xlsx --outdir outputs outputs/GenAI_Services_Market_Model.xlsx
python tests/test_data.py

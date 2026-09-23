# Sales Analytics & Visualization Tool — Project 1

**Time Series & Category Charts** — A Tkinter multi-tab desktop app that loads *any* CSV, auto-detects `Date`/`Category`/`Sales_Amount`, aggregates monthly/quarterly sales with `pandas resample`, compares categories with `groupby`, and exports high-resolution PNGs plus a global summary.

> Built for SYNTECXHUB Data Science — Project 1: Plot sales over time (line charts, monthly/quarterly), bar charts for categories, pie charts for share, PNG export + summary, chart-choice & formatting discussion.

---

## Overview

This tool ingests sales records with shifting column layouts (e.g., `Order Date`/`Item Type`/`Total Revenue` or `Date`/`Category`/`Sales_Amount`) and produces executive-ready visuals:

- **Line charts** (dual: monthly + quarterly) for continuous time — trend & velocity
- **Bar charts** (horizontal, ranked) for category comparison — precise magnitude
- **Pie charts** (capped top5+Other, <6 slices) for market share — proportional readability

Every Run rebuilds charts **live** from the selected file (short 5-row or long 100k-row) and also saves 300 DPI PNGs for submission.

Three spec-aligned demo CSVs are included in `data/` to show expected input/output.

## Key Features

- **Universal ingestion** — `pandas.read_csv` with auto-detect `_guess_project_columns()` for any header (`Date` variants, `Category/Type/Item`, `Revenue/Sales/Amount`)
- **Time-series aggregation** — `df.set_index(Date).resample('ME'/'QE').sum()` with `asfreq(fill 0)` for sparse months
- **Categorical aggregation** — `groupby(Category)[Sales].sum().sort_values(ascending=False)` for bar/pie
- **Live data navigation & edit** — `ttk.Treeview` paginated (200 rows/page), double-click cell → `simpledialog` edit → `update_cell()` → `Save Edited CSV`
- **Multi-tab workspaces** — `ttk.Notebook` per file (`MainInterfaceLayout`), middle-click close, duplicate guard
- **Artifact export** — One-click `sales_trends.png` (dual line), `category_comparison.png` (bar), `market_share.png` (pie), `*_summary.txt` (total, top category, best quarter + chart-choice notes)

## Tools Used

| Tool | Role |
|------|------|
| **Python 3.12** | Runtime |
| **Tkinter / ttk (clam)** | Native desktop UI — `CSVAnalyzerApp`, `WorkspaceTab`, `MainInterfaceLayout` (`main.py:6`, `display.py:8`) |
| **Pandas** | CSV parsing, `to_datetime`, `to_numeric`, `resample`, `groupby`, `asfreq` (`Data_Analytics.py:68`) |
| **NumPy** | Numeric ops, std, vectorization (via Pandas) |
| **Matplotlib (Agg)** | Headless `fig, ax` OO API, `savefig(dpi=300, bbox_inches='tight')` (`Pie_chart_generation.py:4`) |
| **pathlib / os** | Robust path handling (`resolve_input_path`) — spaces, quotes, absolute/relative, forward/back slashes |

## Libraries & Requirements

`requirements.txt`:
```
pandas>=2.0
numpy>=1.26
matplotlib>=3.7
openpyxl>=3.1  # for .xlsx
```

Install:
```bash
pip install -r requirements.txt
# or minimal
pip install pandas numpy matplotlib openpyxl
```

## Project Structure

```
sales-analytics-tool/
├── main.py                     # Tkinter root — CSVAnalyzerApp, ttk theme, Notebook (Project 1 entry)
├── Data_Analytics.py           # CSVDataProcessor — auto-detect, resample ME/QE, groupby, KPIs, update_cell
├── Pie_chart_generation.py     # ChartGenerator — generate_line/bar/pie/summary (Agg, 300 DPI)
├── display.py                  # WorkspaceTab + MainInterfaceLayout — stats Treeview, data table, exports
├── Test.py                     # Generates 5 shifting-layout diagnostic CSVs
├── data/
│   ├── project1_ideal_12months.csv            # 165 rows, 5 cats, 2024-02→2024-12 (gold standard)
│   ├── project1_short_3months.csv             # 35 rows, 3 cats, 2024-09→2024-11 (sparse edge)
│   └── project1_long_18months_dominant.csv    # 233 rows, 6 cats, 2023-07→2024-12 (cap test)
│   └── 100 Sales Records.csv (example external) # 100 rows, 14 cols, Order Date/Item Type/Total Revenue
├── README.md
└── *_summary.txt / *.png       # Generated per input file (e.g., project1_ideal_12months_sales_trends.png)
```

## Installation & Setup

```bash
# 1. Clone / copy
git clone <repo-url> sales-analytics-tool
cd sales-analytics-tool

# 2. (optional) venv
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

# 3. Install deps
pip install -r requirements.txt

# 4. Verify (no GUI)
python -c "import pandas, matplotlib; print('OK')"
python Test.py  # creates test1-5 CSVs
```

## How to Run

### GUI (recommended — Project 1 visual)
```bash
python main.py
# → Click “📁 Import CSV Document Via File Explorer”
# → Pick any file: data/project1_ideal_12months.csv  or  C:/Users/Mbawe/Documents/100 Sales Records.csv
# → Left: select metric → right stats update (Count/Sum/Mean...)
# → Click View/Edit Data Table → double-click cell to edit → Save Edited CSV (paginated, 200/page)
# → Export Sales Trends (Line) / Category Bar / Market Share Pie → PNGs saved beside source CSV
# → Export Global Summary TXT → total revenue, top category, best quarter + monthly/quarterly tables
```

### Headless / Batch (for testing any length)
```python
from Data_Analytics import CSVDataProcessor
from Pie_chart_generation import ChartGenerator

proc = CSVDataProcessor()
proc.load_file("data/project1_ideal_12months.csv")  # auto-detected
monthly = proc.get_monthly_sales()           # resample ME
quarterly = proc.get_quarterly_sales()       # resample QE
cat = proc.get_category_totals()             # groupby
ChartGenerator.generate_line_chart("data/project1_ideal_12months.csv", monthly, quarterly)
ChartGenerator.generate_bar_graph("data/project1_ideal_12months.csv", cat)
ChartGenerator.generate_pie_chart("data/project1_ideal_12months.csv", cat)
ChartGenerator.generate_summary("data/project1_ideal_12months.csv", proc)
```

## Data Schema — Expected CSV

| Column (auto-detected) | Type | Example | Notes |
|------------------------|------|---------|-------|
| **Date** | `YYYY-MM-DD` (also `M/D/Y` like `5/28/2010` auto-parsed) | `2024-02-01` / `Order Date` | Used as index for `resample('ME'/'QE')`; NaT rows dropped |
| **Category** | `string` (<80 uniques) | `Electronics` / `Item Type` | Group key; bar ranked, pie capped top5+Other |
| **Sales_Amount** | `float` ≥0 | `1250.50` / `Total Revenue` | Summed; ` Revenue in USD` axis |

Any extra columns are ignored; column order irrelevant. Tested with 5 shifting layouts (`Test.py`) + 100 Sales Records (14 cols).

## Expected Output (for the 3 custom CSVs)

| Demo File | Rows | Monthly | Quarterly | Bar | Pie |
|-----------|------|---------|-----------|-----|-----|
| `project1_ideal_12months.csv` | 165, 5 cats, Feb-Dec 2024 | 11 periods, growth trend | 4 periods, Q4 best | 5 bars ranked, Electronics top | 5 slices |
| `project1_short_3months.csv` | 35, 3 cats, Sep-Nov 2024 | 3 sparse | 1 | 3 bars | 3 slices |
| `project1_long_18months_dominant.csv` | 233, 6 cats, 18 months | 18 | 6 | top 8, dominant Office Supplies | 5+Other |

Each generates: `*_sales_trends.png` (dual line, markers, `grid -- alpha 0.6`, `Revenue in USD`, spines top/right off), `*_category_comparison.png` (barh, invert y), `*_market_share.png` (pie 90°, pct 0.85), `*_summary.txt`.

## Chart Choice & Formatting (per spec)

- **Line (monthly/quarterly)** — continuous time → slope = velocity; markers `o`/`s`, `linewidth 2.2`, `Resample ME/QE`, `asfreq fill 0` for sparse months
- **Bar (category)** — length = magnitude → precise ranking; horizontal for label space, `barh`, `invert_yaxis`, no redundant legend
- **Pie (<6)** — angle = share → capped `top5+Other`, `autopct 1.1%`, `startangle 90`, `wedge edgecolor white`, `legend bbox_to_anchor (1,0.5)` outside

All: `title Revenue in USD`, `ylabel Revenue in USD`, `grid linestyle -- alpha 0.6`, `set_axisbelow True`, `tight bbox`, `dpi 300`, `facecolor white`.

## GitHub Description

> **Sales Analytics & Visualization Tool (Project 1)** — Python Tkinter app that auto-detects any sales CSV and plots time series (monthly/quarterly line via `resample`) + category bar/pie (`groupby`, <6 cap). Features live data table with edit, paginated navigation, multi-tab workspaces, and 300 DPI PNG + summary export. Stack: Pandas, NumPy, Matplotlib (Agg). Handles 5-row to 100k-row files. Includes 3 spec-aligned demo datasets.

**Topics:** `python` `pandas` `matplotlib` `tkinter` `data-visualization` `time-series` `sales-analytics`

**Clone & run (one-liner for GitHub):**
```bash
git clone https://github.com/<user>/sales-analytics-tool.git && cd sales-analytics-tool && pip install -r requirements.txt && python main.py
```

---

*Generated for SYNTECXHUB Project 1 — preserves UI (clam, Treeview) while adding Project 1 logic. No syntax errors, all controls functional.*

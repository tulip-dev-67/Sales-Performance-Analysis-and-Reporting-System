# Superstore: Sales Performance Analysis and Reporting System

CSQ242 Work Integrated Training-I, Project 2. Orders, Returns and People data are
loaded into SQLite, cleaned and joined with SQL, then analysed with pandas and
visualised with matplotlib.

## Setup
    py -3.12 -m venv venv
    source venv/Scripts/activate
    pip install -r requirements.txt

## Run (from the project root, in this order)
    python src/01_load.py         # CSVs -> SQLite (typed tables)
    python src/02_profile.py      # nulls, duplicates, baseline stats (before cleaning)
    python src/03_run_clean.py    # runs sql/03_clean.sql -> orders_clean
    python src/04_transfer.py     # SQL -> pandas, with verification checks
    python src/05_analysis.py     # all analysis, saved to outputs/analysis_results.txt
    python src/06_charts.py       # six charts saved to outputs/charts/

## Folders
- data/raw/ : source CSVs (orders, returns, people)
- sql/      : cleaning and joining queries
- src/      : Python scripts
- outputs/  : analysis results and charts
- REPORT.md : cleaning decisions, findings and the discount threshold
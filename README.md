# Bluestock Mutual Fund Analytics Capstone

## Project Overview

This project builds an end-to-end analytics system for Indian mutual fund data. It covers data ingestion, cleaning, SQLite warehousing, exploratory data analysis, performance and risk analytics, investor cohort analysis, a simple fund recommender, and a Power BI dashboard.

## Objectives

- Clean and validate raw mutual fund datasets.
- Build a SQLite star schema for analysis.
- Perform EDA using Python notebooks and exported charts.
- Compute CAGR, Sharpe Ratio, Sortino Ratio, Alpha, Beta, Maximum Drawdown, VaR, and CVaR.
- Analyze investor cohorts, SIP continuity, geographic behavior, and sector concentration.
- Build a four-page Power BI dashboard.
- Package the final project with a PDF report, presentation, README, and GitHub tag.

## Dataset Description

The project uses 10 core CSV datasets:

- `01_fund_master.csv`: fund house, scheme name, AMFI code, category, plan, benchmark, risk category, and expense ratio.
- `02_nav_history.csv`: daily NAV history by AMFI code.
- `03_aum_by_fund_house.csv`: AUM by fund house and date.
- `04_monthly_sip_inflows.csv`: monthly SIP inflow, accounts, SIP AUM, and YoY growth.
- `05_category_inflows.csv`: monthly category-level net inflows.
- `06_industry_folio_count.csv`: industry folio count by category.
- `07_scheme_performance.csv`: return, risk, AUM, rating, and expense metrics.
- `08_investor_transactions.csv`: investor transactions, geography, demographics, payment mode, and KYC.
- `09_portfolio_holdings.csv`: fund holdings by stock and sector.
- `10_benchmark_indices.csv`: benchmark index close values.

## Folder Structure

```text
data/
  raw/           original downloaded files
  processed/     cleaned CSVs and analytics outputs
  db/            local SQLite database, ignored by Git
notebooks/       EDA, performance, and advanced analytics notebooks
scripts/         ETL, live NAV fetch, recommender, and pipeline runner
sql/             schema.sql and analytical queries
dashboard/       Power BI dashboard files or exports
reports/         final report, presentation, data dictionary, and charts
```

## Setup

```bash
pip install -r requirements.txt
```

If using the bundled Anaconda runtime on this machine:

```bash
/opt/anaconda3/bin/python scripts/run_pipeline.py
```

## How To Run The ETL

```bash
python scripts/run_pipeline.py
```

The pipeline fetches live NAV data, cleans the raw CSV files, creates processed CSVs, writes SQLite tables, and verifies row counts.

## Key Outputs

- Cleaned CSVs: `data/processed/`
- SQLite schema: `sql/schema.sql`
- Analytical SQL: `sql/queries.sql`
- EDA notebook: `notebooks/EDA_Analysis.ipynb`
- Performance notebook: `notebooks/Performance_Analytics.ipynb`
- Advanced analytics notebook: `notebooks/Advanced_Analytics.ipynb`
- Scorecard output: `data/processed/fund_scorecard.csv`
- Alpha/Beta output: `data/processed/alpha_beta.csv`
- VaR/CVaR output: `data/processed/var_cvar_report.csv`
- Recommender: `scripts/recommender.py`
- Dashboard screenshots and PDF: `reports/charts/`
- Final report: `reports/Final_Report.pdf`
- Presentation: `reports/Bluestock_MF_Presentation.pptx`

## Dashboard

The Power BI dashboard was built in Power BI Service because Power BI Desktop is not available natively on Mac.

Dashboard pages:

1. Industry Overview
2. Fund Performance
3. Investor Analytics
4. SIP & Market Trends

Exports are available in `reports/charts/`.

## Limitations

- `.pbix` creation requires Power BI Desktop on Windows.
- SQLite `.db` files are ignored in Git; `sql/schema.sql` and `sql/queries.sql` document the database.
- Analysis quality depends on the completeness and reliability of the provided source data.

## Author

Dhanistha Arora

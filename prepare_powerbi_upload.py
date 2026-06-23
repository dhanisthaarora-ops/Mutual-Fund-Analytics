import pandas as pd
from pathlib import Path

BASE_DIR = Path("/Users/dhanistha/mutual-fund-analytics")
PROCESSED_DIR = BASE_DIR / "data" / "processed"
POWERBI_DIR = BASE_DIR / "powerbi"

POWERBI_DIR.mkdir(exist_ok=True)

files = {
    "dim_fund": "01_fund_master_clean.csv",
    "fact_nav": "02_nav_history_clean.csv",
    "fact_aum": "03_aum_by_fund_house_clean.csv",
    "fact_sip": "04_monthly_sip_inflows_clean.csv",
    "fact_category": "05_category_inflows_clean.csv",
    "fact_folio": "06_industry_folio_count_clean.csv",
    "fact_performance": "07_scheme_performance_clean.csv",
    "fact_transactions": "08_investor_transactions_clean.csv",
    "fact_holdings": "09_portfolio_holdings_clean.csv",
    "fact_benchmark": "10_benchmark_indices_clean.csv",
    "fund_scorecard": "fund_scorecard.csv",
    "alpha_beta": "alpha_beta.csv",
    "tracking_error": "tracking_error.csv",
}

output_file = POWERBI_DIR / "bluestock_powerbi_dataset.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    for sheet_name, file_name in files.items():
        path = PROCESSED_DIR / file_name

        if path.exists():
            df = pd.read_csv(path)

            for col in df.columns:
                if "date" in col.lower() or col.lower() == "month":
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            print(f"Added {sheet_name}: {df.shape}")
        else:
            print(f"Missing file skipped: {file_name}")

print(f"\nPower BI upload file created:")
print(output_file)

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
SQL_DIR = Path("sql")
REPORTS_DIR = Path("reports")

DB_PATH = "bluestock_mf.db"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
SQL_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def clean_text_columns(df):
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": None, "None": None, "": None})
    return df


def to_numeric_columns(df, exclude=None):
    exclude = exclude or []
    for col in df.columns:
        if col not in exclude:
            try:
                df[col] = pd.to_numeric(df[col])
            except Exception:
                pass
    return df


def clean_fund_master():
    df = pd.read_csv(RAW_DIR / "01_fund_master.csv")
    df = clean_text_columns(df)

    df["amfi_code"] = pd.to_numeric(df["amfi_code"], errors="coerce").astype("Int64")
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")
    df["expense_ratio_pct"] = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
    df["exit_load_pct"] = pd.to_numeric(df["exit_load_pct"], errors="coerce")
    df["min_sip_amount"] = pd.to_numeric(df["min_sip_amount"], errors="coerce")
    df["min_lumpsum_amount"] = pd.to_numeric(df["min_lumpsum_amount"], errors="coerce")

    df = df.drop_duplicates(subset=["amfi_code"])
    df.to_csv(PROCESSED_DIR / "01_fund_master_clean.csv", index=False)
    return df


def clean_nav_history():
    df = pd.read_csv(RAW_DIR / "02_nav_history.csv")
    df = clean_text_columns(df)

    df["amfi_code"] = pd.to_numeric(df["amfi_code"], errors="coerce").astype("Int64")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    df = df.dropna(subset=["amfi_code", "date"])
    df = df[df["nav"] > 0]

    df = df.drop_duplicates(subset=["amfi_code", "date"], keep="last")
    df = df.sort_values(["amfi_code", "date"])

    cleaned_parts = []

    for amfi_code, group in df.groupby("amfi_code"):
        group = group.set_index("date").sort_index()
        full_dates = pd.date_range(group.index.min(), group.index.max(), freq="D")
        group = group.reindex(full_dates)
        group["amfi_code"] = amfi_code
        group["nav"] = group["nav"].ffill()
        group = group.reset_index().rename(columns={"index": "date"})
        cleaned_parts.append(group)

    df_clean = pd.concat(cleaned_parts, ignore_index=True)
    df_clean = df_clean[df_clean["nav"] > 0]
    df_clean.to_csv(PROCESSED_DIR / "02_nav_history_clean.csv", index=False)
    return df_clean


def clean_aum_by_fund_house():
    df = pd.read_csv(RAW_DIR / "03_aum_by_fund_house.csv")
    df = clean_text_columns(df)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["aum_lakh_crore"] = pd.to_numeric(df["aum_lakh_crore"], errors="coerce")
    df["aum_crore"] = pd.to_numeric(df["aum_crore"], errors="coerce")
    df["num_schemes"] = pd.to_numeric(df["num_schemes"], errors="coerce")

    df = df.drop_duplicates()
    df.to_csv(PROCESSED_DIR / "03_aum_by_fund_house_clean.csv", index=False)
    return df


def clean_monthly_sip_inflows():
    df = pd.read_csv(RAW_DIR / "04_monthly_sip_inflows.csv")
    df = clean_text_columns(df)

    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    numeric_cols = [
        "sip_inflow_crore",
        "active_sip_accounts_crore",
        "new_sip_accounts_lakh",
        "sip_aum_lakh_crore",
        "yoy_growth_pct",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates()
    df.to_csv(PROCESSED_DIR / "04_monthly_sip_inflows_clean.csv", index=False)
    return df


def clean_category_inflows():
    df = pd.read_csv(RAW_DIR / "05_category_inflows.csv")
    df = clean_text_columns(df)

    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    df["net_inflow_crore"] = pd.to_numeric(df["net_inflow_crore"], errors="coerce")

    df = df.drop_duplicates()
    df.to_csv(PROCESSED_DIR / "05_category_inflows_clean.csv", index=False)
    return df


def clean_industry_folio_count():
    df = pd.read_csv(RAW_DIR / "06_industry_folio_count.csv")
    df = clean_text_columns(df)

    df["month"] = pd.to_datetime(df["month"], errors="coerce")

    for col in df.columns:
        if col != "month":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates()
    df.to_csv(PROCESSED_DIR / "06_industry_folio_count_clean.csv", index=False)
    return df


def clean_scheme_performance():
    df = pd.read_csv(RAW_DIR / "07_scheme_performance.csv")
    df = clean_text_columns(df)

    df["amfi_code"] = pd.to_numeric(df["amfi_code"], errors="coerce").astype("Int64")

    numeric_cols = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["expense_ratio_valid"] = df["expense_ratio_pct"].between(0.1, 2.5)
    df["return_anomaly_flag"] = (
        (df["return_1yr_pct"].abs() > 100)
        | (df["return_3yr_pct"].abs() > 100)
        | (df["return_5yr_pct"].abs() > 100)
    )

    df = df.drop_duplicates(subset=["amfi_code"])
    df.to_csv(PROCESSED_DIR / "07_scheme_performance_clean.csv", index=False)
    return df


def clean_investor_transactions():
    df = pd.read_csv(RAW_DIR / "08_investor_transactions.csv")
    df = clean_text_columns(df)

    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["amfi_code"] = pd.to_numeric(df["amfi_code"], errors="coerce").astype("Int64")
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df["annual_income_lakh"] = pd.to_numeric(df["annual_income_lakh"], errors="coerce")

    transaction_map = {
        "sip": "SIP",
        "s.i.p": "SIP",
        "lumpsum": "Lumpsum",
        "lump sum": "Lumpsum",
        "redemption": "Redemption",
        "redeem": "Redemption",
    }

    df["transaction_type"] = (
        df["transaction_type"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(transaction_map)
        .fillna(df["transaction_type"])
    )

    valid_transaction_types = ["SIP", "Lumpsum", "Redemption"]
    valid_kyc_status = ["Verified", "Pending", "Rejected"]

    df["transaction_type_valid"] = df["transaction_type"].isin(valid_transaction_types)
    df["amount_valid"] = df["amount_inr"] > 0
    df["kyc_status_valid"] = df["kyc_status"].isin(valid_kyc_status)

    df = df[df["amount_valid"]]
    df = df.drop_duplicates()
    df.to_csv(PROCESSED_DIR / "08_investor_transactions_clean.csv", index=False)
    return df


def clean_portfolio_holdings():
    df = pd.read_csv(RAW_DIR / "09_portfolio_holdings.csv")
    df = clean_text_columns(df)

    df["amfi_code"] = pd.to_numeric(df["amfi_code"], errors="coerce").astype("Int64")
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce")

    numeric_cols = ["weight_pct", "market_value_cr", "current_price_inr"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates()
    df.to_csv(PROCESSED_DIR / "09_portfolio_holdings_clean.csv", index=False)
    return df


def clean_benchmark_indices():
    df = pd.read_csv(RAW_DIR / "10_benchmark_indices.csv")
    df = clean_text_columns(df)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")

    df = df.drop_duplicates()
    df.to_csv(PROCESSED_DIR / "10_benchmark_indices_clean.csv", index=False)
    return df


def create_schema_sql():
    schema = """
DROP TABLE IF EXISTS fact_benchmark_indices;
DROP TABLE IF EXISTS fact_portfolio_holdings;
DROP TABLE IF EXISTS fact_folio_count;
DROP TABLE IF EXISTS fact_category_inflows;
DROP TABLE IF EXISTS fact_sip_inflows;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;

CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT,
    scheme_name TEXT,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

CREATE TABLE dim_date (
    date TEXT PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    month_name TEXT,
    quarter INTEGER
);

CREATE TABLE fact_nav (
    amfi_code INTEGER,
    date TEXT,
    nav REAL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

CREATE TABLE fact_transactions (
    investor_id TEXT,
    transaction_date TEXT,
    amfi_code INTEGER,
    transaction_type TEXT,
    amount_inr REAL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    transaction_type_valid INTEGER,
    amount_valid INTEGER,
    kyc_status_valid INTEGER,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT,
    fund_house TEXT,
    category TEXT,
    plan TEXT,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating REAL,
    risk_grade TEXT,
    expense_ratio_valid INTEGER,
    return_anomaly_flag INTEGER,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_aum (
    date TEXT,
    fund_house TEXT,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER,
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

CREATE TABLE fact_sip_inflows (
    month TEXT,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

CREATE TABLE fact_category_inflows (
    month TEXT,
    category TEXT,
    net_inflow_crore REAL
);

CREATE TABLE fact_folio_count (
    month TEXT,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

CREATE TABLE fact_portfolio_holdings (
    amfi_code INTEGER,
    stock_symbol TEXT,
    stock_name TEXT,
    sector TEXT,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_benchmark_indices (
    date TEXT,
    index_name TEXT,
    close_value REAL,
    FOREIGN KEY (date) REFERENCES dim_date(date)
);
"""
    (SQL_DIR / "schema.sql").write_text(schema.strip())


def create_queries_sql():
    queries = """
-- 1. Top 5 funds by AUM
SELECT scheme_name, fund_house, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month
SELECT substr(date, 1, 7) AS month, ROUND(AVG(nav), 2) AS avg_nav
FROM fact_nav
GROUP BY substr(date, 1, 7)
ORDER BY month;

-- 3. SIP YoY growth
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip_inflows
ORDER BY month;

-- 4. Transactions by state
SELECT state, COUNT(*) AS transaction_count, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- 5. Funds with expense ratio below 1%
SELECT scheme_name, fund_house, expense_ratio_pct
FROM fact_performance
WHERE expense_ratio_pct < 1
ORDER BY expense_ratio_pct;

-- 6. Top 5 funds by 5-year return
SELECT scheme_name, fund_house, return_5yr_pct
FROM fact_performance
ORDER BY return_5yr_pct DESC
LIMIT 5;

-- 7. Total transaction amount by transaction type
SELECT transaction_type, COUNT(*) AS count_txn, SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount DESC;

-- 8. Monthly benchmark average close
SELECT substr(date, 1, 7) AS month, index_name, ROUND(AVG(close_value), 2) AS avg_close
FROM fact_benchmark_indices
GROUP BY substr(date, 1, 7), index_name
ORDER BY month, index_name;

-- 9. Portfolio exposure by sector
SELECT sector, ROUND(SUM(weight_pct), 2) AS total_weight_pct
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_weight_pct DESC;

-- 10. Funds with invalid or unusual performance flags
SELECT scheme_name, expense_ratio_pct, expense_ratio_valid, return_anomaly_flag
FROM fact_performance
WHERE expense_ratio_valid = 0 OR return_anomaly_flag = 1;
"""
    (SQL_DIR / "queries.sql").write_text(queries.strip())


def create_data_dictionary():
    dictionary = """
# Data Dictionary

## dim_fund
Source: 01_fund_master.csv

| Column | Type | Meaning |
|---|---|---|
| amfi_code | INTEGER | Unique AMFI scheme code |
| fund_house | TEXT | Mutual fund company |
| scheme_name | TEXT | Scheme name |
| category | TEXT | Main fund category |
| sub_category | TEXT | Sub-category such as Large Cap |
| plan | TEXT | Regular or Direct plan |
| launch_date | TEXT | Scheme launch date |
| benchmark | TEXT | Benchmark index |
| expense_ratio_pct | REAL | Annual expense ratio percentage |
| exit_load_pct | REAL | Exit load percentage |
| min_sip_amount | REAL | Minimum SIP investment |
| min_lumpsum_amount | REAL | Minimum lumpsum investment |
| fund_manager | TEXT | Fund manager name |
| risk_category | TEXT | Risk level |
| sebi_category_code | TEXT | SEBI category code |

## dim_date
Source: generated from date columns

| Column | Type | Meaning |
|---|---|---|
| date | TEXT | Calendar date |
| year | INTEGER | Year |
| month | INTEGER | Month number |
| month_name | TEXT | Month name |
| quarter | INTEGER | Quarter number |

## fact_nav
Source: 02_nav_history.csv

| Column | Type | Meaning |
|---|---|---|
| amfi_code | INTEGER | Fund code |
| date | TEXT | NAV date |
| nav | REAL | Net Asset Value |

## fact_transactions
Source: 08_investor_transactions.csv

| Column | Type | Meaning |
|---|---|---|
| investor_id | TEXT | Investor identifier |
| transaction_date | TEXT | Transaction date |
| amfi_code | INTEGER | Fund code |
| transaction_type | TEXT | SIP, Lumpsum, or Redemption |
| amount_inr | REAL | Transaction amount |
| state | TEXT | Investor state |
| city | TEXT | Investor city |
| city_tier | TEXT | T30 or B30 city type |
| age_group | TEXT | Investor age group |
| gender | TEXT | Investor gender |
| annual_income_lakh | REAL | Annual income in lakhs |
| payment_mode | TEXT | Payment method |
| kyc_status | TEXT | KYC status |
| transaction_type_valid | INTEGER | 1 if transaction type is valid |
| amount_valid | INTEGER | 1 if amount is positive |
| kyc_status_valid | INTEGER | 1 if KYC status is valid |

## fact_performance
Source: 07_scheme_performance.csv

| Column | Type | Meaning |
|---|---|---|
| amfi_code | INTEGER | Fund code |
| return_1yr_pct | REAL | 1-year return percentage |
| return_3yr_pct | REAL | 3-year return percentage |
| return_5yr_pct | REAL | 5-year return percentage |
| benchmark_3yr_pct | REAL | 3-year benchmark return |
| alpha | REAL | Fund alpha |
| beta | REAL | Fund beta |
| sharpe_ratio | REAL | Risk-adjusted return measure |
| sortino_ratio | REAL | Downside risk-adjusted return measure |
| std_dev_ann_pct | REAL | Annualised standard deviation |
| max_drawdown_pct | REAL | Maximum drawdown percentage |
| aum_crore | REAL | Assets under management in crore |
| expense_ratio_pct | REAL | Expense ratio percentage |
| morningstar_rating | REAL | Morningstar rating |
| risk_grade | TEXT | Risk grade |
| expense_ratio_valid | INTEGER | 1 if expense ratio is between 0.1 and 2.5 |
| return_anomaly_flag | INTEGER | 1 if return value is unusually large |

## Other Fact Tables
Sources: 03_aum_by_fund_house.csv, 04_monthly_sip_inflows.csv, 05_category_inflows.csv, 06_industry_folio_count.csv, 09_portfolio_holdings.csv, 10_benchmark_indices.csv

These tables store AUM, SIP inflow, category inflow, folio count, portfolio holding, and benchmark index values.
"""
    (REPORTS_DIR / "data_dictionary.md").write_text(dictionary.strip())


def create_dim_date(*dfs):
    date_values = []

    for df in dfs:
        for col in df.columns:
            if col in ["date", "month", "transaction_date", "portfolio_date"]:
                date_values.extend(pd.to_datetime(df[col], errors="coerce").dropna().tolist())

    dates = pd.DataFrame({"date": sorted(set(date_values))})
    dates["year"] = dates["date"].dt.year
    dates["month"] = dates["date"].dt.month
    dates["month_name"] = dates["date"].dt.month_name()
    dates["quarter"] = dates["date"].dt.quarter
    dates["date"] = dates["date"].dt.strftime("%Y-%m-%d")
    return dates


def format_dates_for_sql(df):
    for col in df.columns:
        if "date" in col or col == "month":
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
            except Exception:
                pass
    return df


def load_to_sqlite(tables):
    engine = create_engine(f"sqlite:///{DB_PATH}")

    schema_sql = (SQL_DIR / "schema.sql").read_text()

    with engine.begin() as conn:
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))

    for table_name, df in tables.items():
        df = format_dates_for_sql(df.copy())
        df.to_sql(table_name, engine, if_exists="append", index=False)

    with engine.connect() as conn:
        print("\nSQLite row counts:")
        for table_name, df in tables.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            db_count = result.scalar()
            print(f"{table_name}: source={len(df)}, sqlite={db_count}")


def main():
    fund_master = clean_fund_master()
    nav_history = clean_nav_history()
    aum = clean_aum_by_fund_house()
    sip = clean_monthly_sip_inflows()
    category_inflows = clean_category_inflows()
    folio = clean_industry_folio_count()
    performance = clean_scheme_performance()
    transactions = clean_investor_transactions()
    holdings = clean_portfolio_holdings()
    benchmarks = clean_benchmark_indices()

    dim_date = create_dim_date(
        nav_history,
        aum,
        sip,
        category_inflows,
        folio,
        transactions,
        holdings,
        benchmarks,
    )

    create_schema_sql()
    create_queries_sql()
    create_data_dictionary()

    tables = {
        "dim_fund": fund_master,
        "dim_date": dim_date,
        "fact_nav": nav_history,
        "fact_transactions": transactions,
        "fact_performance": performance,
        "fact_aum": aum,
        "fact_sip_inflows": sip,
        "fact_category_inflows": category_inflows,
        "fact_folio_count": folio,
        "fact_portfolio_holdings": holdings,
        "fact_benchmark_indices": benchmarks,
    }

    load_to_sqlite(tables)

    print("\nDay 2 complete.")
    print("Cleaned CSVs saved in data/processed/")
    print("SQLite DB saved as bluestock_mf.db")
    print("Schema saved as sql/schema.sql")
    print("Queries saved as sql/queries.sql")
    print("Data dictionary saved as reports/data_dictionary.md")


if __name__ == "__main__":
    main()


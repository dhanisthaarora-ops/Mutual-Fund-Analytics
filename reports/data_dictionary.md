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
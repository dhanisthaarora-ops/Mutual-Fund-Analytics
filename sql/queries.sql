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
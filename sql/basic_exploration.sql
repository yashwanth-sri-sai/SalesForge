-- ============================================================
-- RetailEdge Sales Intelligence Platform
-- File: basic_exploration.sql
-- Purpose: Initial data exploration and quality checks
-- ============================================================

-- ── 1. Overview of all tables ────────────────────────────────

-- All customers
SELECT * FROM customers;

-- All markets with their zone
SELECT * FROM markets;

-- All products
SELECT * FROM products;

-- Date dimension table
SELECT * FROM date LIMIT 20;

-- ── 2. Row counts ─────────────────────────────────────────────

SELECT 'customers'    AS table_name, COUNT(*) AS row_count FROM customers    UNION ALL
SELECT 'products',                   COUNT(*)              FROM products      UNION ALL
SELECT 'markets',                    COUNT(*)              FROM markets       UNION ALL
SELECT 'transactions',               COUNT(*)              FROM transactions  UNION ALL
SELECT 'date',                       COUNT(*)              FROM date;

-- ── 3. Date range of transactions ─────────────────────────────

SELECT
    MIN(order_date) AS earliest_order,
    MAX(order_date) AS latest_order,
    DATEDIFF(MAX(order_date), MIN(order_date)) AS date_span_days
FROM transactions;

-- ── 4. Currency breakdown ─────────────────────────────────────

SELECT
    currency,
    COUNT(*)            AS num_transactions,
    SUM(sales_amount)   AS total_sales
FROM transactions
GROUP BY currency;

-- ── 5. Data quality — negative / zero sales ───────────────────

SELECT COUNT(*) AS bad_records
FROM transactions
WHERE sales_amount <= 0;

-- View those records
SELECT *
FROM transactions
WHERE sales_amount <= 0
LIMIT 50;

-- ── 6. Unique products sold per market ────────────────────────

SELECT
    m.market_name,
    COUNT(DISTINCT t.product_code) AS unique_products
FROM transactions t
JOIN markets m ON t.market_code = m.markets_code
GROUP BY m.market_name
ORDER BY unique_products DESC;

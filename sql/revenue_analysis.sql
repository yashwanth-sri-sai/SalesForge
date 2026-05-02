-- ============================================================
-- SalesForge Sales Intelligence Platform
-- File: revenue_analysis.sql
-- Purpose: Deep-dive revenue KPIs and trend analysis
-- ============================================================

-- ── 1. Total revenue by market (all time) ────────────────────

SELECT
    m.market_name,
    m.zone,
    SUM(t.sales_amount)                                             AS total_revenue,
    COUNT(*)                                                        AS total_transactions,
    ROUND(SUM(t.sales_amount) * 100.0 /
          (SELECT SUM(sales_amount) FROM transactions WHERE sales_amount > 0), 2) AS revenue_pct
FROM transactions t
JOIN markets m ON t.market_code = m.markets_code
WHERE t.sales_amount > 0
GROUP BY m.market_name, m.zone
ORDER BY total_revenue DESC;

-- ── 2. Year-over-year revenue ─────────────────────────────────

SELECT
    d.year,
    SUM(t.sales_amount)  AS annual_revenue,
    COUNT(*)             AS num_orders,
    ROUND(AVG(t.sales_amount), 2) AS avg_order_value
FROM transactions t
JOIN date d ON t.order_date = d.date
WHERE t.sales_amount > 0
GROUP BY d.year
ORDER BY d.year;

-- ── 3. Month-over-month revenue in 2020 ──────────────────────

SELECT
    d.month_name,
    d.year,
    SUM(t.sales_amount)   AS monthly_revenue,
    SUM(t.sales_qty)      AS units_sold
FROM transactions t
JOIN date d ON t.order_date = d.date
WHERE d.year = 2020
  AND t.sales_amount > 0
GROUP BY d.month_name, d.year, MONTH(d.date)
ORDER BY MONTH(d.date);

-- ── 4. Revenue by zone ────────────────────────────────────────

SELECT
    m.zone,
    SUM(t.sales_amount) AS zone_revenue,
    COUNT(DISTINCT t.customer_code) AS unique_customers
FROM transactions t
JOIN markets m ON t.market_code = m.markets_code
WHERE t.sales_amount > 0
GROUP BY m.zone
ORDER BY zone_revenue DESC;

-- ── 5. Top 10 customers by revenue ───────────────────────────

SELECT
    c.custmer_name,
    m.market_name,
    SUM(t.sales_amount)  AS total_revenue,
    SUM(t.sales_qty)     AS total_units,
    COUNT(*)             AS total_orders,
    ROUND(AVG(t.sales_amount), 2) AS avg_order_value
FROM transactions t
JOIN customers c ON t.customer_code = c.customer_code
JOIN markets   m ON t.market_code   = m.markets_code
WHERE t.sales_amount > 0
GROUP BY c.custmer_name, m.market_name
ORDER BY total_revenue DESC
LIMIT 10;

-- ── 6. Top 5 products by revenue ─────────────────────────────

SELECT
    t.product_code,
    p.product_type,
    SUM(t.sales_amount)  AS product_revenue,
    SUM(t.sales_qty)     AS units_sold
FROM transactions t
JOIN products p ON t.product_code = p.product_code
WHERE t.sales_amount > 0
GROUP BY t.product_code, p.product_type
ORDER BY product_revenue DESC
LIMIT 5;

-- ── 7. Revenue split: Own Brand vs Distribution ───────────────

SELECT
    p.product_type,
    SUM(t.sales_amount) AS revenue,
    ROUND(SUM(t.sales_amount) * 100.0 /
          (SELECT SUM(sales_amount) FROM transactions WHERE sales_amount > 0), 2) AS pct_of_total
FROM transactions t
JOIN products p ON t.product_code = p.product_code
WHERE t.sales_amount > 0
GROUP BY p.product_type;

-- ── 8. Churned customers (bought in 2019 but not 2020) ───────

SELECT DISTINCT c.custmer_name, c.customer_code
FROM transactions t
JOIN customers c ON t.customer_code = c.customer_code
JOIN date d ON t.order_date = d.date
WHERE d.year = 2019
  AND t.customer_code NOT IN (
      SELECT DISTINCT t2.customer_code
      FROM transactions t2
      JOIN date d2 ON t2.order_date = d2.date
      WHERE d2.year = 2020
  );

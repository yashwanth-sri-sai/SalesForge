-- ============================================================
-- RetailEdge Sales Intelligence Platform
-- File: profit_analysis.sql
-- Purpose: Profit margin KPIs and loss-market identification
-- ============================================================

-- ── 1. Profit margin by market ────────────────────────────────

SELECT
    m.market_name,
    m.zone,
    SUM(t.profit_margin_amount)             AS total_profit,
    SUM(t.sales_amount)                     AS total_revenue,
    ROUND(AVG(t.profit_margin_percentage), 2) AS avg_margin_pct,
    ROUND(SUM(t.profit_margin_amount) * 100.0 / NULLIF(SUM(t.sales_amount), 0), 2)
                                            AS effective_margin_pct
FROM transactions t
JOIN markets m ON t.market_code = m.markets_code
WHERE t.sales_amount > 0
GROUP BY m.market_name, m.zone
ORDER BY effective_margin_pct DESC;

-- ── 2. Loss-making markets (negative profit) ──────────────────

SELECT
    m.market_name,
    m.zone,
    SUM(t.profit_margin_amount) AS net_profit
FROM transactions t
JOIN markets m ON t.market_code = m.markets_code
GROUP BY m.market_name, m.zone
HAVING net_profit < 0
ORDER BY net_profit ASC;

-- ── 3. Customer-level profitability ───────────────────────────

SELECT
    c.custmer_name,
    SUM(t.profit_margin_amount) AS total_profit,
    SUM(t.sales_amount)         AS total_revenue,
    ROUND(AVG(t.profit_margin_percentage), 2) AS avg_margin_pct
FROM transactions t
JOIN customers c ON t.customer_code = c.customer_code
WHERE t.sales_amount > 0
GROUP BY c.custmer_name
ORDER BY total_profit DESC
LIMIT 10;

-- ── 4. Product profitability ──────────────────────────────────

SELECT
    t.product_code,
    p.product_type,
    SUM(t.profit_margin_amount) AS total_profit,
    ROUND(AVG(t.profit_margin_percentage), 2) AS avg_margin_pct
FROM transactions t
JOIN products p ON t.product_code = p.product_code
WHERE t.sales_amount > 0
GROUP BY t.product_code, p.product_type
ORDER BY total_profit DESC
LIMIT 10;

-- ── 5. Yearly profit trend ────────────────────────────────────

SELECT
    d.year,
    SUM(t.profit_margin_amount)               AS annual_profit,
    SUM(t.sales_amount)                       AS annual_revenue,
    ROUND(SUM(t.profit_margin_amount) * 100.0
          / NULLIF(SUM(t.sales_amount), 0), 2) AS profit_margin_pct
FROM transactions t
JOIN date d ON t.order_date = d.date
WHERE t.sales_amount > 0
GROUP BY d.year
ORDER BY d.year;

-- ── 6. Top 5 most profitable months (2020) ────────────────────

SELECT
    d.month_name,
    SUM(t.profit_margin_amount) AS monthly_profit,
    ROUND(AVG(t.profit_margin_percentage), 2) AS avg_margin_pct
FROM transactions t
JOIN date d ON t.order_date = d.date
WHERE d.year = 2020
  AND t.sales_amount > 0
GROUP BY d.month_name, MONTH(d.date)
ORDER BY monthly_profit DESC
LIMIT 5;

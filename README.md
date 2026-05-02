<h1 align="center">RetailEdge 📊 — Sales Performance Intelligence Platform</h1>

<p align="center">
  <img src="https://img.shields.io/badge/SQL-MySQL-blue?style=for-the-badge&logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/Visualization-Tableau-orange?style=for-the-badge&logo=tableau&logoColor=white" />
  <img src="https://img.shields.io/badge/Language-Python-yellow?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" />
</p>

> **RetailEdge** is an end-to-end sales intelligence project built to transform raw transactional data into actionable business insights. Using MySQL for data extraction and transformation, and Tableau for interactive dashboards, this platform empowers sales teams and business leaders to make data-driven decisions with confidence.

---

## 🧩 Project Overview

Modern retail businesses generate enormous volumes of transaction data daily. Without structured analysis, identifying revenue trends, underperforming markets, or high-value customer segments is nearly impossible. **RetailEdge** bridges that gap by:

- Designing a clean **star schema** data model from raw OLTP data
- Running advanced **SQL queries** for KPI extraction
- Building **Tableau dashboards** for revenue and profit insights
- Providing a **Python EDA script** for supplemental statistical analysis

---

## ⚙️ Tech Stack

| Tool | Purpose |
|------|---------|
| **MySQL** | Data storage, ETL, and SQL-based analysis |
| **Tableau Public / Desktop** | Interactive dashboard visualizations |
| **Python (Pandas, Matplotlib)** | Exploratory Data Analysis (EDA) |
| **Excel** | Raw data inspection and quick pivots |

---

## 🗃️ Database Schema

The project uses a **Star Schema** optimized for analytical queries:

- **Fact Table:** `transactions` — stores sales order records
- **Dimension Tables:** `customers`, `products`, `markets`, `date`

```
transactions ──── customers
     │       ──── products
     │       ──── markets
     └───────── date
```

---

## 🚀 Setup Instructions

### Step 1 — Clone & Import Database

```bash
git clone https://github.com/yourusername/retailedge-sales-intelligence.git
cd retailedge-sales-intelligence
```

Import the SQL dump into your MySQL instance:

```bash
mysql -u root -p < Databases/db_dump.sql
```

Or import `Databases/db_dump.xlsx` directly into Tableau.

### Step 2 — Connect Tableau

1. Open Tableau Public (free) or Tableau Desktop
2. Connect to **MySQL** using your credentials, or use the `.xlsx` as a flat-file source
3. Open `RetailEdge - Sales Performance Dashboard.twbx`

### Step 3 — Run Python EDA (Optional)

```bash
pip install pandas matplotlib seaborn openpyxl
python analysis/eda_sales.py
```

---

## 🔍 Business Questions Answered

| # | Question |
|---|----------|
| Q1 | What is the revenue breakdown across different cities? |
| Q2 | How does revenue trend month-over-month and year-over-year? |
| Q3 | Who are the top 10 customers by revenue and sales volume? |
| Q4 | Which products drive the highest revenue? |
| Q5 | What is the net profit and profit margin by market? |
| Q6 | Which markets are operating at a loss? |
| Q7 | What is the sales contribution % of each zone (North/South/Central)? |

---

## 🗄️ Data Analysis — SQL Queries

### Basic Exploration

```sql
-- View all customer records
SELECT * FROM customers;

-- Count total number of customers
SELECT COUNT(*) AS total_customers FROM customers;

-- List all unique markets
SELECT DISTINCT market_name, zone FROM markets;
```

### Sales Filtering

```sql
-- Transactions from Mumbai (market code: Mark002)
SELECT t.*, c.custmer_name, p.product_type
FROM transactions t
JOIN customers c ON t.customer_code = c.customer_code
JOIN products p  ON t.product_code  = p.product_code
WHERE t.market_code = 'Mark002';

-- All transactions in USD (international customers)
SELECT * FROM transactions WHERE currency = 'USD';

-- Transactions with negative or zero sales amount (data quality check)
SELECT * FROM transactions WHERE sales_amount <= 0;
```

### Revenue Analysis

```sql
-- Total revenue by market (all years)
SELECT m.market_name, m.zone,
       SUM(t.sales_amount) AS total_revenue,
       COUNT(t.product_code) AS total_orders
FROM transactions t
JOIN markets m ON t.market_code = m.markets_code
GROUP BY m.market_name, m.zone
ORDER BY total_revenue DESC;

-- Monthly revenue trend for 2020
SELECT d.month_name, d.year,
       SUM(t.sales_amount) AS monthly_revenue
FROM transactions t
JOIN date d ON t.order_date = d.date
WHERE d.year = 2020
  AND t.currency IN ('INR\r', 'USD\r')
GROUP BY d.month_name, d.year
ORDER BY d.date;

-- Year-over-year revenue comparison
SELECT d.year,
       SUM(t.sales_amount) AS total_revenue,
       COUNT(*) AS num_transactions
FROM transactions t
JOIN date d ON t.order_date = d.date
GROUP BY d.year
ORDER BY d.year;
```

### Customer Intelligence

```sql
-- Top 10 customers by total revenue
SELECT c.custmer_name,
       SUM(t.sales_amount)  AS total_revenue,
       SUM(t.sales_qty)     AS total_units_sold,
       COUNT(t.order_date)  AS total_orders
FROM transactions t
JOIN customers c ON t.customer_code = c.customer_code
GROUP BY c.custmer_name
ORDER BY total_revenue DESC
LIMIT 10;

-- Customers who bought in 2019 but NOT in 2020 (churned customers)
SELECT DISTINCT c.custmer_name
FROM transactions t
JOIN customers c ON t.customer_code = c.customer_code
JOIN date d ON t.order_date = d.date
WHERE d.year = 2019
  AND t.customer_code NOT IN (
      SELECT DISTINCT customer_code
      FROM transactions t2
      JOIN date d2 ON t2.order_date = d2.date
      WHERE d2.year = 2020
  );
```

### Product Performance

```sql
-- Top 5 products by revenue
SELECT t.product_code, p.product_type,
       SUM(t.sales_amount) AS product_revenue
FROM transactions t
JOIN products p ON t.product_code = p.product_code
GROUP BY t.product_code, p.product_type
ORDER BY product_revenue DESC
LIMIT 5;

-- Revenue share % per product type
SELECT p.product_type,
       SUM(t.sales_amount) AS revenue,
       ROUND(SUM(t.sales_amount) * 100.0 /
           (SELECT SUM(sales_amount) FROM transactions), 2) AS revenue_pct
FROM transactions t
JOIN products p ON t.product_code = p.product_code
GROUP BY p.product_type
ORDER BY revenue DESC;
```

### Profit Analysis

```sql
-- Profit margin by market
SELECT m.market_name,
       SUM(t.profit_margin_amount)  AS total_profit,
       SUM(t.sales_amount)          AS total_revenue,
       ROUND(AVG(t.profit_margin_percentage), 2) AS avg_margin_pct
FROM transactions t
JOIN markets m ON t.market_code = m.markets_code
GROUP BY m.market_name
ORDER BY avg_margin_pct DESC;

-- Markets with negative profit (loss-making zones)
SELECT m.market_name, SUM(t.profit_margin_amount) AS net_profit
FROM transactions t
JOIN markets m ON t.market_code = m.markets_code
GROUP BY m.market_name
HAVING net_profit < 0;
```

---

## 📊 Dashboard Snapshots

### Revenue Analysis Dashboard
<p align="center"><img width="100%" src="images/Tableau Dashbpard Revenue Analysis.png"/></p>

### Profit Analysis Dashboard
<p align="center"><img width="100%" src="images/Tableau Dashbpard Profit Analysis.png"/></p>

### Star Schema — Data Model
<p align="center"><img width="80%" src="images/Star Schema.png"/></p>

---

## 📁 Project Structure

```
retailedge-sales-intelligence/
│
├── Databases/
│   ├── db_dump.sql          # Full MySQL database dump
│   ├── db_dump.xlsx         # Excel version of the database
│   ├── db_dump_v1.sql       # Version 1 (subset) of the dump
│   └── db_dump_v1.xlsx      # Excel version 1
│
├── analysis/
│   └── eda_sales.py         # Python EDA script
│
├── sql/
│   ├── basic_exploration.sql
│   ├── revenue_analysis.sql
│   └── profit_analysis.sql
│
├── images/
│   ├── Star Schema.png
│   ├── Tableau Dashbpard Revenue Analysis.png
│   └── Tableau Dashbpard Profit Analysis.png
│
├── RetailEdge - Sales Performance Dashboard.twbx
└── README.md
```

---

## 🎯 Key Insights Uncovered

- **Delhi NCR** contributes ~50% of total revenue but operates on thinner margins
- **Bengaluru** market shows the highest loss margins — flagged for cost review
- **Electricalsara Stores** is the single highest-revenue customer
- Revenue dipped sharply in **Q1 2020** — correlated with market disruptions
- **Own Brand** products consistently outperform **Distribution** type in profit margin

---

## 📌 Methodology

```
Raw Data (OLTP)
     │
     ▼
ETL via SQL (Clean, Normalize, Filter)
     │
     ▼
Star Schema (Fact + Dimension Tables)
     │
     ▼
Tableau Dashboards + Python EDA
     │
     ▼
Business Insights & Recommendations
```

---

## 📚 References

| # | Resource | Link |
|---|----------|------|
| 1 | MySQL Documentation | [dev.mysql.com](https://dev.mysql.com/doc/) |
| 2 | Tableau Public | [public.tableau.com](https://public.tableau.com) |
| 3 | Star Schema Design | [Microsoft Docs](https://docs.microsoft.com/en-us/power-bi/guidance/star-schema) |
| 4 | OLAP vs OLTP | [GeeksForGeeks](https://www.geeksforgeeks.org/difference-between-olap-and-oltp-in-dbms/) |

---

## 📬 Contact

Have questions or suggestions? Feel free to open an issue or reach out via GitHub.

---

*Built with 💡 to turn data chaos into business clarity.*

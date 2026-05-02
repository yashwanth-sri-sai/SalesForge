"""
RetailEdge — Sales Performance Intelligence Platform
====================================================
File    : eda_sales.py
Purpose : Exploratory Data Analysis on the sales database using Excel export
Usage   : python analysis/eda_sales.py

Requirements:
    pip install pandas matplotlib seaborn openpyxl
"""

import os
import warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

warnings.filterwarnings("ignore")

# ── Configuration ─────────────────────────────────────────────────────────────
DATA_PATH   = os.path.join(os.path.dirname(__file__), "..", "Databases", "db_dump.xlsx")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "analysis_outputs")
PALETTE     = "coolwarm"
FIG_SIZE    = (14, 6)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
print("📂 Loading data from:", DATA_PATH)
xls = pd.ExcelFile(DATA_PATH)
print(f"   Sheets found: {xls.sheet_names}\n")

sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}

# Try to identify the transactions-like sheet (largest row count)
txn_sheet = max(sheets, key=lambda s: len(sheets[s]))
df = sheets[txn_sheet].copy()

print(f"✅ Using sheet: '{txn_sheet}'  |  Shape: {df.shape}")
print("\n── Sample Records ──")
print(df.head())
print("\n── Data Types ──")
print(df.dtypes)
print("\n── Null Counts ──")
print(df.isnull().sum())


# ── Helper: save figure ───────────────────────────────────────────────────────
def save_fig(name: str):
    path = os.path.join(OUTPUT_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"   💾 Saved → {path}")


# ── 1. Revenue by Market ──────────────────────────────────────────────────────
print("\n📊 Plot 1: Revenue by Market")
if "market_code" in df.columns and "sales_amount" in df.columns:
    mkt_rev = (
        df[df["sales_amount"] > 0]
        .groupby("market_code")["sales_amount"]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    bars = ax.bar(mkt_rev.index, mkt_rev.values, color=sns.color_palette(PALETTE, len(mkt_rev)))
    ax.set_title("Total Revenue by Market Code", fontsize=16, fontweight="bold")
    ax.set_xlabel("Market Code")
    ax.set_ylabel("Revenue (INR)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
    ax.bar_label(bars, fmt="%.0f", fontsize=8, padding=3)
    save_fig("01_revenue_by_market.png")
else:
    print("   ⚠️  Columns 'market_code' or 'sales_amount' not found — skipping.")


# ── 2. Monthly Revenue Trend ──────────────────────────────────────────────────
print("\n📊 Plot 2: Monthly Revenue Trend")
date_cols = [c for c in df.columns if "date" in c.lower() or "order" in c.lower()]
if date_cols and "sales_amount" in df.columns:
    date_col = date_cols[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["year_month"] = df[date_col].dt.to_period("M")

    monthly = (
        df[df["sales_amount"] > 0]
        .groupby("year_month")["sales_amount"]
        .sum()
        .reset_index()
    )
    monthly["year_month_str"] = monthly["year_month"].astype(str)

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.plot(monthly["year_month_str"], monthly["sales_amount"],
            marker="o", linewidth=2, color="#E64545")
    ax.fill_between(range(len(monthly)), monthly["sales_amount"],
                    alpha=0.15, color="#E64545")
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly["year_month_str"], rotation=45, ha="right", fontsize=8)
    ax.set_title("Monthly Revenue Trend", fontsize=16, fontweight="bold")
    ax.set_ylabel("Revenue (INR)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
    save_fig("02_monthly_revenue_trend.png")
else:
    print("   ⚠️  Date/sales columns not found — skipping.")


# ── 3. Revenue Distribution (Histogram) ───────────────────────────────────────
print("\n📊 Plot 3: Sales Amount Distribution")
if "sales_amount" in df.columns:
    clean = df[df["sales_amount"] > 0]["sales_amount"]
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.hist(clean, bins=60, color="#4A90D9", edgecolor="white", alpha=0.85)
    ax.set_title("Distribution of Individual Transaction Amounts", fontsize=16, fontweight="bold")
    ax.set_xlabel("Sales Amount (INR)")
    ax.set_ylabel("Frequency")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    save_fig("03_sales_distribution.png")


# ── 4. Top 10 Customers by Revenue ───────────────────────────────────────────
print("\n📊 Plot 4: Top 10 Customers by Revenue")
if "customer_code" in df.columns and "sales_amount" in df.columns:
    top_cust = (
        df[df["sales_amount"] > 0]
        .groupby("customer_code")["sales_amount"]
        .sum()
        .nlargest(10)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.barh(top_cust["customer_code"][::-1], top_cust["sales_amount"][::-1],
            color=sns.color_palette("Blues_d", 10))
    ax.set_title("Top 10 Customers by Total Revenue", fontsize=16, fontweight="bold")
    ax.set_xlabel("Revenue (INR)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
    save_fig("04_top10_customers.png")


# ── 5. Correlation Heatmap ────────────────────────────────────────────────────
print("\n📊 Plot 5: Numeric Correlation Heatmap")
numeric_cols = df.select_dtypes(include="number").columns.tolist()
if len(numeric_cols) >= 2:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        df[numeric_cols].corr(),
        annot=True, fmt=".2f",
        cmap="coolwarm", linewidths=0.5, ax=ax
    )
    ax.set_title("Correlation Matrix — Numeric Features", fontsize=16, fontweight="bold")
    save_fig("05_correlation_heatmap.png")
else:
    print("   ⚠️  Not enough numeric columns for heatmap — skipping.")


# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n✅ EDA complete! All plots saved to: {os.path.abspath(OUTPUT_DIR)}")
print("\n── Summary Statistics ──")
if "sales_amount" in df.columns:
    clean = df[df["sales_amount"] > 0]["sales_amount"]
    print(f"   Total Revenue       : ₹{clean.sum():,.0f}")
    print(f"   Total Transactions  : {len(clean):,}")
    print(f"   Average Order Value : ₹{clean.mean():,.2f}")
    print(f"   Median Order Value  : ₹{clean.median():,.2f}")
    print(f"   Max Single Order    : ₹{clean.max():,.0f}")

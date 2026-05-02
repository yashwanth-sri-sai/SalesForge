"""
SalesForge — Sales Performance Intelligence Platform
====================================================
File    : eda_sales.py
Purpose : Exploratory Data Analysis on the sales database
Usage   : python analysis/eda_sales.py

Requirements:
    pip install pandas matplotlib seaborn openpyxl
"""

import os
import warnings
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, "Databases", "db_dump.xlsx")
OUT_DIR    = os.path.join(BASE_DIR, "analysis_outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load all sheets ────────────────────────────────────────────────────────────
print("=" * 60)
print("  SalesForge — Sales EDA")
print("=" * 60)
print(f"\n📂 Loading: {DATA_PATH}\n")

xls          = pd.ExcelFile(DATA_PATH)
transactions = xls.parse("transactions")
customers    = xls.parse("customers")
products     = xls.parse("products")
markets      = xls.parse("markets")
date_df      = xls.parse("date")

# ── Merge into one analytical frame ───────────────────────────────────────────
df = (
    transactions
    .merge(customers, on="customer_code", how="left")
    .merge(products,  on="product_code",  how="left")
    .merge(markets,   left_on="market_code", right_on="markets_code", how="left")
    .merge(date_df,   left_on="order_date",  right_on="date",         how="left")
)

# Clean: keep only positive sales
df_clean = df[df["sales_amount"] > 0].copy()
df_clean["order_date"] = pd.to_datetime(df_clean["order_date"], errors="coerce")
df_clean["year_month"] = df_clean["order_date"].dt.to_period("M")

print(f"✅ Transactions loaded  : {len(transactions):,}")
print(f"✅ After cleaning (>0)  : {len(df_clean):,}")
print(f"📅 Date range           : {df_clean['order_date'].min().date()} → {df_clean['order_date'].max().date()}")
print(f"🏪 Markets              : {df_clean['markets_name'].nunique()}")
print(f"👥 Customers            : {df_clean['custmer_name'].nunique()}")
print(f"📦 Products             : {df_clean['product_code'].nunique()}")

# ── Helper ─────────────────────────────────────────────────────────────────────
def save_fig(filename):
    path = os.path.join(OUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"   💾 {path}")


plt.rcParams.update({
    "figure.facecolor": "#0f0f1a",
    "axes.facecolor":   "#1a1a2e",
    "axes.edgecolor":   "#444466",
    "axes.labelcolor":  "#ccccee",
    "xtick.color":      "#aaaacc",
    "ytick.color":      "#aaaacc",
    "text.color":       "#e0e0ff",
    "grid.color":       "#2a2a4a",
    "grid.alpha":       0.5,
})


# ── CHART 1: Revenue by Market ────────────────────────────────────────────────
print("\n📊 Chart 1: Revenue by Market")
mkt_rev = (
    df_clean.groupby("markets_name")["sales_amount"]
    .sum().sort_values(ascending=False)
)
colors = sns.color_palette("coolwarm", len(mkt_rev))

fig, ax = plt.subplots(figsize=(14, 6), facecolor="#0f0f1a")
bars = ax.bar(mkt_rev.index, mkt_rev.values, color=colors, edgecolor="#0f0f1a", linewidth=0.5)
ax.set_title("💰 Total Revenue by Market", fontsize=17, fontweight="bold", pad=14)
ax.set_xlabel("Market", labelpad=8)
ax.set_ylabel("Revenue (INR)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.set_xticklabels(mkt_rev.index, rotation=40, ha="right", fontsize=9)
ax.bar_label(bars, labels=[f"₹{v/1e6:.1f}M" for v in mkt_rev.values],
             fontsize=7.5, padding=3, color="#ccccee")
ax.grid(axis="y")
save_fig("01_revenue_by_market.png")


# ── CHART 2: Monthly Revenue Trend ────────────────────────────────────────────
print("📊 Chart 2: Monthly Revenue Trend")
monthly = (
    df_clean.groupby("year_month")["sales_amount"]
    .sum().reset_index()
)
monthly["ym_str"] = monthly["year_month"].astype(str)

fig, ax = plt.subplots(figsize=(14, 5), facecolor="#0f0f1a")
ax.plot(monthly["ym_str"], monthly["sales_amount"],
        marker="o", linewidth=2.2, color="#e05c5c", markersize=5)
ax.fill_between(range(len(monthly)), monthly["sales_amount"],
                alpha=0.18, color="#e05c5c")
ax.set_xticks(range(len(monthly)))
ax.set_xticklabels(monthly["ym_str"], rotation=45, ha="right", fontsize=8)
ax.set_title("📅 Monthly Revenue Trend", fontsize=17, fontweight="bold", pad=14)
ax.set_ylabel("Revenue (INR)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.grid(axis="y")
save_fig("02_monthly_revenue_trend.png")


# ── CHART 3: Year-over-Year Revenue ───────────────────────────────────────────
print("📊 Chart 3: Year-over-Year Revenue")
yoy = df_clean.groupby("year")["sales_amount"].sum()

fig, ax = plt.subplots(figsize=(8, 5), facecolor="#0f0f1a")
bars = ax.bar(yoy.index.astype(str), yoy.values,
              color=["#4a90d9", "#e05c5c", "#f0a500"], edgecolor="#0f0f1a", width=0.5)
ax.set_title("📈 Year-over-Year Revenue", fontsize=17, fontweight="bold", pad=14)
ax.set_ylabel("Revenue (INR)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.bar_label(bars, labels=[f"₹{v/1e6:.1f}M" for v in yoy.values],
             fontsize=10, padding=4, color="#ccccee")
ax.grid(axis="y")
save_fig("03_yoy_revenue.png")


# ── CHART 4: Top 10 Customers ─────────────────────────────────────────────────
print("📊 Chart 4: Top 10 Customers by Revenue")
top_cust = (
    df_clean.groupby("custmer_name")["sales_amount"]
    .sum().nlargest(10).sort_values()
)

fig, ax = plt.subplots(figsize=(12, 6), facecolor="#0f0f1a")
bars = ax.barh(top_cust.index, top_cust.values,
               color=sns.color_palette("Blues_d", 10), edgecolor="#0f0f1a")
ax.set_title("🏆 Top 10 Customers by Revenue", fontsize=17, fontweight="bold", pad=14)
ax.set_xlabel("Revenue (INR)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.bar_label(bars, labels=[f"₹{v/1e6:.1f}M" for v in top_cust.values],
             padding=4, fontsize=8.5, color="#ccccee")
ax.grid(axis="x")
save_fig("04_top10_customers.png")


# ── CHART 5: Revenue by Product Type ──────────────────────────────────────────
print("📊 Chart 5: Revenue by Product Type")
prod_rev = df_clean.groupby("product_type")["sales_amount"].sum()

fig, ax = plt.subplots(figsize=(7, 7), facecolor="#0f0f1a")
wedges, texts, autotexts = ax.pie(
    prod_rev.values,
    labels=prod_rev.index,
    autopct="%1.1f%%",
    startangle=140,
    colors=["#4a90d9", "#e05c5c"],
    wedgeprops=dict(edgecolor="#0f0f1a", linewidth=2),
    pctdistance=0.75,
)
for t in autotexts:
    t.set_color("#ffffff")
    t.set_fontsize(12)
ax.set_title("📦 Revenue Share by Product Type", fontsize=16, fontweight="bold", pad=20)
save_fig("05_product_type_revenue.png")


# ── CHART 6: Profit Margin by Market ──────────────────────────────────────────
print("📊 Chart 6: Profit Margin by Market")
if "profit_margin" in df_clean.columns:
    margin_col = "profit_margin"
elif "profit" in df_clean.columns:
    margin_col = "profit"
else:
    margin_col = None

if margin_col:
    mkt_margin = (
        df_clean.groupby("markets_name")[margin_col]
        .mean()
        .sort_values(ascending=False)
    )
    colors_m = ["#2ecc71" if v >= 0 else "#e74c3c" for v in mkt_margin.values]

    fig, ax = plt.subplots(figsize=(14, 6), facecolor="#0f0f1a")
    bars = ax.bar(mkt_margin.index, mkt_margin.values, color=colors_m, edgecolor="#0f0f1a")
    ax.axhline(0, color="#888", linewidth=0.8, linestyle="--")
    ax.set_title("📉 Avg Profit Margin % by Market", fontsize=17, fontweight="bold", pad=14)
    ax.set_ylabel("Avg Profit Margin")
    ax.set_xticklabels(mkt_margin.index, rotation=40, ha="right", fontsize=9)
    ax.bar_label(bars, labels=[f"{v:.2f}" for v in mkt_margin.values],
                 fontsize=7.5, padding=3, color="#ccccee")
    ax.grid(axis="y")
    save_fig("06_profit_margin_by_market.png")


# ── CHART 7: Revenue by Zone ───────────────────────────────────────────────────
print("📊 Chart 7: Revenue by Zone")
zone_rev = df_clean.groupby("zone")["sales_amount"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 5), facecolor="#0f0f1a")
bars = ax.bar(zone_rev.index, zone_rev.values,
              color=["#9b59b6", "#3498db", "#e67e22"], edgecolor="#0f0f1a", width=0.4)
ax.set_title("🗺️  Revenue by Geographic Zone", fontsize=17, fontweight="bold", pad=14)
ax.set_ylabel("Revenue (INR)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.bar_label(bars, labels=[f"₹{v/1e6:.1f}M" for v in zone_rev.values],
             fontsize=10, padding=4, color="#ccccee")
ax.grid(axis="y")
save_fig("07_revenue_by_zone.png")


# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  📊 Summary Statistics")
print("=" * 60)
print(f"  Total Revenue         : ₹{df_clean['sales_amount'].sum():>15,.0f}")
print(f"  Total Transactions    : {len(df_clean):>15,}")
print(f"  Avg Order Value       : ₹{df_clean['sales_amount'].mean():>15,.2f}")
print(f"  Median Order Value    : ₹{df_clean['sales_amount'].median():>15,.2f}")
print(f"  Highest Single Order  : ₹{df_clean['sales_amount'].max():>15,.0f}")
print(f"  Top Market            :   {mkt_rev.idxmax()}")
print(f"  Top Customer          :   {df_clean.groupby('custmer_name')['sales_amount'].sum().idxmax()}")
print("=" * 60)
print(f"\n✅ All 7 charts saved to: {OUT_DIR}\n")

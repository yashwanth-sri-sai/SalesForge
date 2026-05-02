"""
SalesForge — Sales Performance Intelligence Platform
Interactive Streamlit Dashboard
Run: streamlit run dashboard.py
"""

import os
import warnings
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

warnings.filterwarnings("ignore")

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SalesForge — Sales Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Dark gradient background */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0f0f2e 50%, #0a1628 100%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d26 0%, #111130 100%);
        border-right: 1px solid #1e1e4a;
    }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a1a3e 0%, #16213e 100%);
        border: 1px solid #2a2a6a;
        border-radius: 16px;
        padding: 22px 20px;
        text-align: center;
        box-shadow: 0 4px 24px rgba(80, 80, 255, 0.1);
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-3px); }
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #8888cc;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #e0e0ff;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 11px;
        color: #5555aa;
        margin-top: 6px;
    }
    .kpi-icon { font-size: 22px; margin-bottom: 6px; }

    /* Section headers */
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #c0c0ff;
        border-left: 4px solid #5555ff;
        padding-left: 12px;
        margin: 28px 0 16px 0;
    }

    /* Hero banner */
    .hero {
        background: linear-gradient(135deg, #1a1a4e 0%, #0e2048 50%, #1a3060 100%);
        border: 1px solid #2a2a7a;
        border-radius: 20px;
        padding: 32px 36px;
        margin-bottom: 28px;
        box-shadow: 0 8px 40px rgba(40, 40, 200, 0.2);
    }
    .hero h1 {
        font-size: 36px;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 8px 0;
        background: linear-gradient(90deg, #7799ff, #aa77ff, #ff7799);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p { color: #9999cc; font-size: 15px; margin: 0; }

    /* Insight badge */
    .insight-badge {
        display: inline-block;
        background: rgba(80, 80, 255, 0.15);
        border: 1px solid rgba(80, 80, 255, 0.35);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 12px;
        color: #9999ff;
        margin: 4px 3px;
    }

    /* Data table tweaks */
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

    /* Hide default Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    xls  = pd.ExcelFile(os.path.join(base, "Databases", "db_dump.xlsx"))

    txn  = xls.parse("transactions")
    cust = xls.parse("customers")
    prod = xls.parse("products")
    mkt  = xls.parse("markets")
    dt   = xls.parse("date")

    df = (
        txn
        .merge(cust, on="customer_code", how="left")
        .merge(prod, on="product_code",  how="left")
        .merge(mkt,  left_on="market_code", right_on="markets_code", how="left")
        .merge(dt,   left_on="order_date",  right_on="date",         how="left")
    )
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["year"]       = df["order_date"].dt.year.astype("Int64")
    return df[df["sales_amount"] > 0].copy()

df = load_data()

COLORS = {
    "primary":   "#5566ff",
    "accent":    "#aa66ff",
    "danger":    "#ff5566",
    "success":   "#33cc88",
    "warning":   "#ffaa33",
    "bg":        "#0f0f2e",
    "card":      "#1a1a3e",
    "text":      "#e0e0ff",
    "muted":     "#8888cc",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(20,20,50,0.6)",
    font=dict(family="Inter", color=COLORS["text"]),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#1e1e4a", linecolor="#2a2a6a"),
    yaxis=dict(gridcolor="#1e1e4a", linecolor="#2a2a6a"),
)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 12px 0 20px 0;'>
        <div style='font-size:40px;'>📊</div>
        <div style='font-size:20px; font-weight:800; color:#c0c0ff;'>SalesForge</div>
        <div style='font-size:11px; color:#6666aa; letter-spacing:2px;'>SALES INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='color:#8888cc; font-size:12px; font-weight:600; letter-spacing:1px;'>FILTERS</div>", unsafe_allow_html=True)

    years = sorted(df["year"].dropna().unique().tolist())
    sel_years = st.multiselect("📅 Year", years, default=years)

    zones = sorted(df["zone"].dropna().unique().tolist())
    sel_zones = st.multiselect("🗺️ Zone", zones, default=zones)

    markets_list = sorted(df["markets_name"].dropna().unique().tolist())
    sel_markets  = st.multiselect("🏪 Market", markets_list, default=markets_list)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px; color:#5555aa; text-align:center; line-height:1.8;'>
        Data range<br>
        <span style='color:#8888cc;'>Oct 2017 — Jun 2020</span><br><br>
        Stack: MySQL · Tableau · Python<br>
        <span style='color:#5566ff;'>SalesForge v1.0</span>
    </div>
    """, unsafe_allow_html=True)

# Apply filters
mask = (
    df["year"].isin(sel_years) &
    df["zone"].isin(sel_zones) &
    df["markets_name"].isin(sel_markets)
)
fdf = df[mask].copy()


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>SalesForge · Sales Performance Intelligence</h1>
    <p>End-to-end sales data analysis — from raw SQL transactions to actionable business insights</p>
    <br>
    <span class="insight-badge">📍 Multi-Market</span>
    <span class="insight-badge">📅 2017–2020</span>
    <span class="insight-badge">🧾 Transactional Data</span>
    <span class="insight-badge">💡 Profit Analysis</span>
    <span class="insight-badge">🏆 Customer Insights</span>
</div>
""", unsafe_allow_html=True)


# ── KPI Cards ──────────────────────────────────────────────────────────────────
total_rev   = fdf["sales_amount"].sum()
total_txn   = len(fdf)
avg_order   = fdf["sales_amount"].mean()
top_market  = fdf.groupby("markets_name")["sales_amount"].sum().idxmax() if len(fdf) else "—"
top_cust    = fdf.groupby("custmer_name")["sales_amount"].sum().idxmax() if len(fdf) else "—"
total_units = fdf["sales_qty"].sum() if "sales_qty" in fdf.columns else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    (c1, "💰", "Total Revenue",    f"₹{total_rev/1e6:.2f}M",    "All filtered markets"),
    (c2, "🧾", "Transactions",     f"{total_txn:,}",             "Valid orders"),
    (c3, "📦", "Units Sold",       f"{int(total_units):,}",      "Aggregate qty"),
    (c4, "📈", "Avg Order Value",  f"₹{avg_order:,.0f}",         "Per transaction"),
    (c5, "🏪", "Top Market",       top_market,                   "By total revenue"),
    (c6, "🏆", "Top Customer",     top_cust[:16]+"…" if len(top_cust)>16 else top_cust, "By total revenue"),
]
for col, icon, label, val, sub in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Row 1: Revenue by Market + Monthly Trend ───────────────────────────────────
st.markdown('<div class="section-header">📊 Revenue Analysis</div>', unsafe_allow_html=True)
col_left, col_right = st.columns([1.1, 1])

with col_left:
    mkt_rev = (
        fdf.groupby("markets_name")["sales_amount"]
        .sum().sort_values(ascending=False).reset_index()
    )
    mkt_rev.columns = ["Market", "Revenue"]
    fig = px.bar(
        mkt_rev, x="Market", y="Revenue",
        title="Revenue by Market",
        color="Revenue",
        color_continuous_scale=["#1a1a6e", "#5566ff", "#aa88ff"],
        text=mkt_rev["Revenue"].apply(lambda v: f"₹{v/1e6:.2f}M"),
    )
    fig.update_traces(textposition="outside", textfont_size=11, marker_line_width=0)
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                      title_font_size=15, title_x=0)
    fig.update_yaxes(tickprefix="₹", ticksuffix="")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    monthly = (
        fdf.groupby("year_month")["sales_amount"]
        .sum().reset_index().sort_values("year_month")
    )
    monthly.columns = ["Month", "Revenue"]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Revenue"],
        mode="lines+markers",
        line=dict(color=COLORS["accent"], width=2.5),
        marker=dict(size=6, color=COLORS["accent"]),
        fill="tozeroy",
        fillcolor="rgba(170,102,255,0.12)",
        name="Revenue",
    ))
    fig2.update_layout(**PLOTLY_LAYOUT,
                       title=dict(text="Monthly Revenue Trend", font_size=15, x=0))
    fig2.update_yaxes(tickprefix="₹")
    fig2.update_xaxes(tickangle=45, nticks=12)
    st.plotly_chart(fig2, use_container_width=True)


# ── Row 2: YoY + Zone donut ────────────────────────────────────────────────────
col_a, col_b, col_c = st.columns([1, 1, 0.9])

with col_a:
    yoy = fdf.groupby("year")["sales_amount"].sum().reset_index()
    yoy.columns = ["Year", "Revenue"]
    yoy["Year"] = yoy["Year"].astype(str)
    fig3 = px.bar(
        yoy, x="Year", y="Revenue",
        title="Year-over-Year Revenue",
        color="Year",
        color_discrete_sequence=["#5566ff", "#aa66ff", "#ff6699", "#33ccaa"],
        text=yoy["Revenue"].apply(lambda v: f"₹{v/1e6:.1f}M"),
    )
    fig3.update_traces(textposition="outside", textfont_size=12, marker_line_width=0)
    fig3.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                       title_font_size=15, title_x=0, bargap=0.45)
    fig3.update_yaxes(tickprefix="₹")
    st.plotly_chart(fig3, use_container_width=True)

with col_b:
    zone_rev = fdf.groupby("zone")["sales_amount"].sum().reset_index()
    zone_rev.columns = ["Zone", "Revenue"]
    fig4 = px.pie(
        zone_rev, names="Zone", values="Revenue",
        title="Revenue by Zone",
        color_discrete_sequence=["#5566ff", "#aa66ff", "#ff6699"],
        hole=0.55,
    )
    fig4.update_traces(textposition="outside", textinfo="label+percent",
                       pull=[0.04]*len(zone_rev))
    fig4.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=COLORS["text"]),
        margin=dict(l=20, r=20, t=40, b=20),
        title_font_size=15, title_x=0,
        legend=dict(font_color=COLORS["text"]),
        showlegend=False,
    )
    st.plotly_chart(fig4, use_container_width=True)

with col_c:
    prod_rev = fdf.groupby("product_type")["sales_amount"].sum().reset_index()
    prod_rev.columns = ["Type", "Revenue"]
    fig5 = px.pie(
        prod_rev, names="Type", values="Revenue",
        title="Own Brand vs Distribution",
        color_discrete_sequence=["#5566ff", "#ff6699"],
        hole=0.55,
    )
    fig5.update_traces(textposition="outside", textinfo="label+percent",
                       pull=[0.04]*len(prod_rev))
    fig5.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=COLORS["text"]),
        margin=dict(l=20, r=20, t=40, b=20),
        title_font_size=15, title_x=0,
        showlegend=False,
    )
    st.plotly_chart(fig5, use_container_width=True)


# ── Row 3: Top Customers + Profit Margin ──────────────────────────────────────
st.markdown('<div class="section-header">🏆 Customer & Profit Intelligence</div>', unsafe_allow_html=True)
col_p, col_q = st.columns([1, 1])

with col_p:
    top_n = st.slider("Top N Customers", 5, 20, 10, key="topn")
    top_cust_df = (
        fdf.groupby("custmer_name")["sales_amount"]
        .sum().nlargest(top_n).sort_values(ascending=True).reset_index()
    )
    top_cust_df.columns = ["Customer", "Revenue"]
    fig6 = px.bar(
        top_cust_df, x="Revenue", y="Customer",
        orientation="h",
        title=f"Top {top_n} Customers by Revenue",
        color="Revenue",
        color_continuous_scale=["#1a1a6e", "#5566ff", "#aa88ff"],
        text=top_cust_df["Revenue"].apply(lambda v: f"₹{v/1e6:.2f}M"),
    )
    fig6.update_traces(textposition="outside", textfont_size=10, marker_line_width=0)
    fig6.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                       title_font_size=15, title_x=0)
    fig6.update_xaxes(tickprefix="₹")
    st.plotly_chart(fig6, use_container_width=True)

with col_q:
    margin_col = "profit_margin" if "profit_margin" in fdf.columns else (
        "profit" if "profit" in fdf.columns else None
    )
    if margin_col:
        mkt_margin = (
            fdf.groupby("markets_name")[margin_col]
            .mean().sort_values(ascending=False).reset_index()
        )
        mkt_margin.columns = ["Market", "AvgMargin"]
        mkt_margin["Color"] = mkt_margin["AvgMargin"].apply(
            lambda v: COLORS["success"] if v >= 0 else COLORS["danger"]
        )
        fig7 = go.Figure(go.Bar(
            x=mkt_margin["Market"],
            y=mkt_margin["AvgMargin"],
            marker_color=mkt_margin["Color"],
            text=[f"{v:.2f}" for v in mkt_margin["AvgMargin"]],
            textposition="outside",
        ))
        fig7.add_hline(y=0, line_dash="dash", line_color="#888888", line_width=1)
        fig7.update_layout(**PLOTLY_LAYOUT,
                           title=dict(text="Avg Profit Margin by Market", font_size=15, x=0))
        fig7.update_yaxes(title_text="Avg Profit Margin")
        fig7.update_xaxes(tickangle=30)
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.info("Profit margin column not found in this dataset slice.")


# ── Row 4: Monthly Heatmap ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">🗓️ Sales Heatmap</div>', unsafe_allow_html=True)

fdf["month_num"] = fdf["order_date"].dt.month
fdf["month_name_s"] = fdf["order_date"].dt.strftime("%b")
heatmap_data = (
    fdf.groupby(["year", "month_name_s", "month_num"])["sales_amount"]
    .sum().reset_index()
    .sort_values(["year", "month_num"])
)

if not heatmap_data.empty:
    pivot = heatmap_data.pivot_table(
        index="year", columns="month_name_s", values="sales_amount", aggfunc="sum"
    )
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot = pivot.reindex(columns=[m for m in month_order if m in pivot.columns])

    fig8 = px.imshow(
        pivot,
        color_continuous_scale=["#0a0a2e", "#2233aa", "#5566ff", "#aaccff"],
        title="Monthly Revenue Heatmap (Year × Month)",
        text_auto=".2s",
        aspect="auto",
    )
    fig8.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=COLORS["text"]),
        margin=dict(l=20, r=20, t=40, b=20),
        title_font_size=15, title_x=0,
        coloraxis_colorbar=dict(title="Revenue", tickprefix="₹"),
    )
    fig8.update_xaxes(side="bottom")
    st.plotly_chart(fig8, use_container_width=True)


# ── Row 5: Raw Data Explorer ───────────────────────────────────────────────────
st.markdown('<div class="section-header">🔍 Data Explorer</div>', unsafe_allow_html=True)

with st.expander("📋 View Filtered Transactions", expanded=False):
    display_cols = [c for c in [
        "order_date", "custmer_name", "markets_name", "zone",
        "product_code", "product_type", "sales_qty", "sales_amount",
        "currency", "profit_margin"
    ] if c in fdf.columns]
    st.dataframe(
        fdf[display_cols].sort_values("order_date", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=320,
    )

with st.expander("📌 Market Summary Table", expanded=False):
    summary = (
        fdf.groupby(["markets_name", "zone"])
        .agg(
            Total_Revenue=("sales_amount", "sum"),
            Transactions=("sales_amount", "count"),
            Avg_Order=("sales_amount", "mean"),
            Avg_Margin=(margin_col, "mean") if margin_col else ("sales_amount", "count"),
        )
        .sort_values("Total_Revenue", ascending=False)
        .reset_index()
    )
    summary["Total_Revenue"] = summary["Total_Revenue"].map("₹{:,.0f}".format)
    summary["Avg_Order"]     = summary["Avg_Order"].map("₹{:,.0f}".format)
    st.dataframe(summary, use_container_width=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; margin-top:40px; padding:20px 0;
            border-top:1px solid #1e1e4a; color:#444488; font-size:12px;'>
    SalesForge · Sales Performance Intelligence Platform &nbsp;·&nbsp;
    Built with Python · Streamlit · Plotly &nbsp;·&nbsp;
    Data: MySQL Database (Oct 2017 – Jun 2020)
</div>
""", unsafe_allow_html=True)

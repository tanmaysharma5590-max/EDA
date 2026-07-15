import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS (base theme)
# =====================================================

st.markdown("""
<style>
.stApp{
background:linear-gradient(135deg,#EEF5FF,#DCEBFF,#C5DBFF);
}
[data-testid="stSidebar"]{
background:linear-gradient(180deg,#0F172A,#1E3A8A);
}
[data-testid="stSidebar"] *{
color:white;
}
h1{
color:#0F172A;
font-weight:bold;
}
h2,h3{
color:#1E40AF;
}
[data-testid="stDataFrame"]{
background:white;
padding:10px;
border-radius:12px;
}
.stPlotlyChart{
background:white;
padding:15px;
border-radius:15px;
box-shadow:0px 6px 15px rgba(0,0,0,.12);
}
.stButton>button{
background:#2563EB;
color:white;
border:none;
border-radius:10px;
font-weight:bold;
padding:10px;
}
.stDownloadButton>button{
background:#16A34A;
color:white;
border:none;
border-radius:10px;
font-weight:bold;
padding:10px;
}
.stTabs [data-baseweb="tab-list"]{
gap:8px;
}
.stTabs [data-baseweb="tab"]{
background:white;
border-radius:10px 10px 0 0;
padding:10px 18px;
font-weight:600;
}
footer{visibility:hidden;}
header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HELPER: THEMED PAGE HEADER + KPI CARDS
# =====================================================

def page_header(title, color):
    st.markdown(
        f"""<div style="background:{color};padding:16px 24px;border-radius:14px;
        margin-bottom:18px;box-shadow:0px 6px 16px rgba(0,0,0,.2);">
        <h2 style="color:white;margin:0;">{title}</h2></div>""",
        unsafe_allow_html=True
    )

def kpi_card(label, value, color):
    return f"""<div style="background:{color};color:white;padding:22px 10px;
    border-radius:14px;text-align:center;box-shadow:0px 6px 16px rgba(0,0,0,.18);
    min-height:90px;">
    <div style="font-size:13px;opacity:.9;font-weight:600;letter-spacing:.5px;">{label}</div>
    <div style="font-size:26px;font-weight:800;margin-top:6px;">{value}</div>
    </div>"""

def render_kpis(cards):
    cols = st.columns(len(cards))
    for c, (label, value, color) in zip(cols, cards):
        with c:
            st.markdown(kpi_card(label, value, color), unsafe_allow_html=True)

# US state name -> abbreviation (for choropleth map)
US_STATE_ABBR = {
    'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
    'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
    'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA',
    'Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD',
    'Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO',
    'Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ',
    'New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH',
    'Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
    'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT',
    'Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY',
    'District of Columbia':'DC'
}

def has_cols(dframe, cols):
    return all(c in dframe.columns for c in cols)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    if "Ship Date" in df.columns:
        df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")
    return df

# =====================================================
# TITLE
# =====================================================

st.title("📊 Sales Analytics Dashboard")
st.markdown("### Interactive Business Intelligence Dashboard")
st.write("---")

# =====================================================
# SIDEBAR — UPLOAD + GLOBAL FILTERS
# =====================================================

st.sidebar.title("📂 Upload Dataset")

uploaded_file = st.sidebar.file_uploader("Choose CSV File", type=["csv"])

if uploaded_file is None:
    st.info("👈 Upload synthetic_sales_data.csv se shuru karein")
    st.stop()

df = load_data(uploaded_file)

st.sidebar.header("Filters")

def multiselect_if_exists(col_name, label, icon=""):
    if col_name in df.columns:
        return st.sidebar.multiselect(
            f"{icon} {label}", df[col_name].dropna().unique(),
            default=df[col_name].dropna().unique()
        )
    return None

region_sel   = multiselect_if_exists("Region", "Region", "🌍")
category_sel = multiselect_if_exists("Category", "Category", "📦")
segment_sel  = multiselect_if_exists("Customer Segment", "Customer Segment", "👥")
payment_sel  = multiselect_if_exists("Payment Mode", "Payment Mode", "💳")

filtered_df = df.copy()
if region_sel   is not None: filtered_df = filtered_df[filtered_df["Region"].isin(region_sel)]
if category_sel is not None: filtered_df = filtered_df[filtered_df["Category"].isin(category_sel)]
if segment_sel  is not None: filtered_df = filtered_df[filtered_df["Customer Segment"].isin(segment_sel)]
if payment_sel  is not None: filtered_df = filtered_df[filtered_df["Payment Mode"].isin(payment_sel)]

# =====================================================
# TABS — 3 THEMED PAGES + DEEP DIVE
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📈  Superstore Performance",
    "📦  Inventory & Supplier",
    "👥  Customer & Delivery",
    "🧠  Deep Dive & Data"
])

# =====================================================
# TAB 1 — SUPERSTORE PERFORMANCE DASHBOARD (navy + orange)
# =====================================================

with tab1:
    page_header("🧡 Superstore Performance Dashboard", "linear-gradient(90deg,#0F172A,#1E3A8A)")

    # local region quick-filter buttons (mimics image)
    if "Region" in filtered_df.columns:
        regions_avail = ["All"] + sorted(filtered_df["Region"].dropna().unique().tolist())
        page1_region = st.radio("Region", regions_avail, horizontal=True, key="p1_region")
        p1_df = filtered_df if page1_region == "All" else filtered_df[filtered_df["Region"] == page1_region]
    else:
        p1_df = filtered_df

    total_sales   = p1_df["Sales Amount"].sum() if "Sales Amount" in p1_df.columns else 0
    total_profit  = p1_df["Profit"].sum() if "Profit" in p1_df.columns else 0
    total_orders  = p1_df["Order ID"].nunique() if "Order ID" in p1_df.columns else 0
    avg_discount  = p1_df["Discount (%)"].mean() if "Discount (%)" in p1_df.columns else 0

    render_kpis([
        ("💰 TOTAL SALES", f"${total_sales:,.0f}", "#F97316"),
        ("📈 TOTAL PROFIT", f"${total_profit:,.0f}", "#1D4ED8"),
        ("🧾 ORDERS", f"{total_orders:,}", "#0F172A"),
        ("🏷 AVG DISCOUNT", f"{avg_discount:.1f}%", "#F59E0B"),
    ])

    st.write("")
    c1, c2 = st.columns([1.3, 1])

    with c1:
        if has_cols(p1_df, ["Product Name", "Sales Amount"]):
            top_p = (p1_df.groupby("Product Name")["Sales Amount"].sum()
                     .sort_values(ascending=False).head(10).reset_index())
            fig = px.bar(top_p, x="Product Name", y="Sales Amount",
                         color="Sales Amount", color_continuous_scale="Blues",
                         text_auto=".2s", title="Sum of Sales Amount by Product Name")
            fig.update_layout(height=420, xaxis_tickangle=-35)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if has_cols(p1_df, ["Category", "Sales Amount"]):
            cat = p1_df.groupby("Category")["Sales Amount"].sum().reset_index()
            fig = px.bar(cat, x="Category", y="Sales Amount", color="Category",
                         text_auto=".2s", title="Sales by Category")
            fig.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    c3, c4, c5 = st.columns(3)

    with c3:
        if has_cols(p1_df, ["State", "Sales Amount"]):
            st_sales = p1_df.groupby("State")["Sales Amount"].sum().reset_index()
            st_sales["abbr"] = st_sales["State"].map(US_STATE_ABBR)
            mapped = st_sales.dropna(subset=["abbr"])
            if not mapped.empty:
                fig = px.choropleth(mapped, locations="abbr", locationmode="USA-states",
                                     color="Sales Amount", scope="usa",
                                     color_continuous_scale="Blues", title="Sales by State")
                fig.update_layout(height=380)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = px.bar(st_sales.sort_values("Sales Amount", ascending=False).head(10),
                             x="State", y="Sales Amount", title="Sales by State (Top 10)")
                fig.update_layout(height=380)
                st.plotly_chart(fig, use_container_width=True)

    with c4:
        if has_cols(p1_df, ["Region", "Sales Amount"]):
            reg = p1_df.groupby("Region")["Sales Amount"].sum().reset_index()
            fig = px.pie(reg, names="Region", values="Sales Amount", hole=0.55,
                         title="Sales by Region")
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

    with c5:
        if has_cols(p1_df, ["Payment Mode", "Sales Amount"]):
            pay = p1_df.groupby("Payment Mode")["Sales Amount"].sum().reset_index()
            fig = px.pie(pay, names="Payment Mode", values="Sales Amount", hole=0.55,
                         title="Sales by Payment Mode")
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

    if has_cols(p1_df, ["Order Date", "Sales Amount"]):
        tmp = p1_df.copy()
        tmp["Month"] = tmp["Order Date"].dt.strftime("%Y-%m")
        monthly = tmp.groupby("Month")["Sales Amount"].sum().reset_index()
        fig = px.line(monthly, x="Month", y="Sales Amount", markers=True,
                      title="Sum of Sales Amount by Month")
        fig.update_traces(line_width=4, line_color="#F97316")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TAB 2 — INVENTORY & SUPPLIER DASHBOARD (maroon/red)
# =====================================================

with tab2:
    page_header("📦 Inventory & Supplier Dashboard", "linear-gradient(90deg,#3B0A0A,#7C1D1D)")

    if "Region" in filtered_df.columns:
        regions_avail2 = ["All"] + sorted(filtered_df["Region"].dropna().unique().tolist())
        page2_region = st.radio("Region", regions_avail2, horizontal=True, key="p2_region")
        p2_df = filtered_df if page2_region == "All" else filtered_df[filtered_df["Region"] == page2_region]
    else:
        p2_df = filtered_df

    stock_left_total = p2_df["Stock Left"].sum() if "Stock Left" in p2_df.columns else 0
    low_stock_items  = (p2_df["Stock Left"] < 50).sum() if "Stock Left" in p2_df.columns else 0
    avg_reorder_qty  = (p2_df["Reorder Quantity"].mean()
                        if "Reorder Quantity" in p2_df.columns
                        else (p2_df["Quantity"].mean() if "Quantity" in p2_df.columns else 0))

    render_kpis([
        ("📦 STOCK LEFT", f"{stock_left_total:,.0f}", "#7C1D1D"),
        ("⚠️ LOW STOCK ITEMS", f"{low_stock_items:,}", "#B91C1C"),
        ("🔁 AVG REORDER QTY", f"{avg_reorder_qty:.2f}", "#DC2626"),
    ])

    st.write("")
    c1, c2 = st.columns([1, 1.3])

    with c1:
        if has_cols(p2_df, ["Category", "Stock Left"]):
            stock_cat = p2_df.groupby("Category")["Stock Left"].sum().reset_index()
            fig = px.bar(stock_cat, x="Stock Left", y="Category", orientation="h",
                         color="Stock Left", color_continuous_scale="Reds",
                         title="Stock Left by Category")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("`Category` / `Stock Left` columns dataset mein nahi mile.")

    with c2:
        st.subheader("🧾 Supplier / Product Table")
        table_cols = [c for c in ["Supplier Name", "Category", "Product Name", "Unit Price"] if c in p2_df.columns]
        if table_cols:
            st.dataframe(p2_df[table_cols].drop_duplicates().head(50), use_container_width=True, height=420)
        else:
            fallback_cols = [c for c in ["Product Name", "Category", "Sales Amount"] if c in p2_df.columns]
            if fallback_cols:
                st.info("`Supplier Name` column nahi mili — Product-level table dikha rahe hain.")
                st.dataframe(p2_df[fallback_cols].drop_duplicates().head(50), use_container_width=True, height=380)

    c3, c4 = st.columns(2)

    with c3:
        if "Auto Reorder" in p2_df.columns:
            reorder = p2_df.groupby("Auto Reorder").size().reset_index(name="Orders")
            fig = px.pie(reorder, names="Auto Reorder", values="Orders", hole=0.5,
                         title="Auto Reorder", color_discrete_sequence=["#F97316", "#7C1D1D"])
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("`Auto Reorder` column dataset mein nahi mili.")

    with c4:
        if has_cols(p2_df, ["Order Date"]) and ("Reorder Quantity" in p2_df.columns or "Quantity" in p2_df.columns):
            qty_col = "Reorder Quantity" if "Reorder Quantity" in p2_df.columns else "Quantity"
            tmp = p2_df.copy()
            tmp["Month"] = tmp["Order Date"].dt.strftime("%Y-%m")
            monthly_qty = tmp.groupby("Month")[qty_col].sum().reset_index()
            fig = px.line(monthly_qty, x="Month", y=qty_col, markers=True,
                          title="Reorder Quantity by Month")
            fig.update_traces(line_width=4, line_color="#B91C1C")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TAB 3 — CUSTOMER & DELIVERY INSIGHTS (purple/pink)
# =====================================================

with tab3:
    page_header("💜 Customer & Delivery Insights", "linear-gradient(90deg,#4A1942,#7C2D6E)")

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        opts = ["All"] + sorted(filtered_df["Region"].dropna().unique().tolist()) if "Region" in filtered_df.columns else ["All"]
        p3_region = st.selectbox("Region", opts, key="p3_region")
    with fc2:
        opts = ["All"] + sorted(filtered_df["Payment Mode"].dropna().unique().tolist()) if "Payment Mode" in filtered_df.columns else ["All"]
        p3_payment = st.selectbox("Payment Mode", opts, key="p3_payment")
    with fc3:
        opts = ["All"] + sorted(filtered_df["Category"].dropna().unique().tolist()) if "Category" in filtered_df.columns else ["All"]
        p3_category = st.selectbox("Category", opts, key="p3_category")

    p3_df = filtered_df.copy()
    if p3_region != "All" and "Region" in p3_df.columns:
        p3_df = p3_df[p3_df["Region"] == p3_region]
    if p3_payment != "All" and "Payment Mode" in p3_df.columns:
        p3_df = p3_df[p3_df["Payment Mode"] == p3_payment]
    if p3_category != "All" and "Category" in p3_df.columns:
        p3_df = p3_df[p3_df["Category"] == p3_category]

    total_customers = p3_df["Customer ID"].nunique() if "Customer ID" in p3_df.columns else 0
    top_payment = (p3_df["Payment Mode"].mode()[0] if "Payment Mode" in p3_df.columns and not p3_df.empty else "N/A")
    avg_items = (p3_df["Quantity"].mean() if "Quantity" in p3_df.columns else
                 (p3_df["Sales Amount"].mean() if "Sales Amount" in p3_df.columns else 0))

    render_kpis([
        ("👥 TOTAL CUSTOMERS", f"{total_customers:,}", "#7C2D6E"),
        ("💳 TOP PAYMENT MODE", f"{top_payment}", "#9D174D"),
        ("📦 AVG QTY / ORDER", f"{avg_items:.2f}", "#BE185D"),
    ])

    st.write("")
    c1, c2 = st.columns(2)

    with c1:
        if has_cols(p3_df, ["Region", "Sales Amount"]):
            reg_sales = p3_df.groupby("Region")["Sales Amount"].sum().reset_index()
            fig = px.bar(reg_sales, x="Region", y="Sales Amount", color="Region",
                         text_auto=".2s", title="Sales Amount by Region",
                         color_discrete_sequence=px.colors.sequential.Magenta)
            fig.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if has_cols(p3_df, ["Region", "Profit"]):
            reg_profit = p3_df.groupby("Region")["Profit"].sum().reset_index()
            fig = px.bar(reg_profit, x="Profit", y="Region", orientation="h",
                         color="Region", text_auto=".2s", title="Profit by Region",
                         color_discrete_sequence=px.colors.sequential.Purp)
            fig.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        if has_cols(p3_df, ["Customer Segment", "Profit"]):
            seg_profit = p3_df.groupby("Customer Segment")["Profit"].sum().reset_index()
            fig = px.pie(seg_profit, names="Customer Segment", values="Profit", hole=0.55,
                         title="Profit by Customer Segment",
                         color_discrete_sequence=px.colors.sequential.RdPu)
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        if has_cols(p3_df, ["State", "Sales Amount"]):
            st_sales2 = p3_df.groupby("State")["Sales Amount"].sum().reset_index()
            st_sales2["abbr"] = st_sales2["State"].map(US_STATE_ABBR)
            mapped2 = st_sales2.dropna(subset=["abbr"])
            if not mapped2.empty:
                fig = px.choropleth(mapped2, locations="abbr", locationmode="USA-states",
                                     color="Sales Amount", scope="usa",
                                     color_continuous_scale="Magenta", title="State and Sales Amount")
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)

    if "Delivery Status" in p3_df.columns:
        st.write("---")
        st.subheader("🚚 Delivery Status")
        delivery = p3_df.groupby("Delivery Status").size().reset_index(name="Count")
        fig = px.bar(delivery, x="Delivery Status", y="Count", color="Delivery Status",
                     text_auto=True, color_discrete_sequence=px.colors.sequential.Magenta)
        fig.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TAB 4 — DEEP DIVE & DATA (advanced analysis, preserved)
# =====================================================

with tab4:
    page_header("🧠 Deep Dive & Data Explorer", "linear-gradient(90deg,#1E293B,#334155)")

    left, right = st.columns([3, 1])
    with left:
        st.subheader("Dataset Preview")
        st.dataframe(filtered_df, use_container_width=True, height=350)
    with right:
        st.subheader("Dataset Shape")
        st.metric("Rows", filtered_df.shape[0])
        st.metric("Columns", filtered_df.shape[1])
        st.subheader("Missing Values")
        st.dataframe(filtered_df.isnull().sum(), use_container_width=True)

    st.write("---")

    if "Sales Amount" in filtered_df.columns and "Profit" in filtered_df.columns:
        st.subheader("Business Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success(f"Highest Sale : ${filtered_df['Sales Amount'].max():,.0f}")
            st.info(f"Lowest Sale : ${filtered_df['Sales Amount'].min():,.0f}")
        with col2:
            st.success(f"Highest Profit : ${filtered_df['Profit'].max():,.0f}")
            st.info(f"Lowest Profit : ${filtered_df['Profit'].min():,.0f}")
        with col3:
            st.success(f"Average Profit : ${filtered_df['Profit'].mean():,.0f}")
            if "Discount (%)" in filtered_df.columns:
                st.info(f"Average Discount : {filtered_df['Discount (%)'].mean():.1f}%")

    st.write("---")

    numeric_df = filtered_df.select_dtypes(include="number")
    if numeric_df.shape[1] >= 2:
        st.subheader("🔥 Correlation Heatmap")
        corr = numeric_df.corr(numeric_only=True)
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                         aspect="auto", title="Correlation Matrix")
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        st.write("---")

    if has_cols(filtered_df, ["Sales Amount", "Profit", "Category"]):
        st.subheader("📈 Sales vs Profit")
        size_col = "Quantity" if "Quantity" in filtered_df.columns else None
        hover_col = "Customer Name" if "Customer Name" in filtered_df.columns else None
        fig = px.scatter(filtered_df, x="Sales Amount", y="Profit", color="Category",
                          size=size_col, hover_name=hover_col)
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.write("---")

    if has_cols(filtered_df, ["Category", "Discount (%)"]):
        st.subheader("🏷 Discount Analysis")
        fig = px.box(filtered_df, x="Category", y="Discount (%)", color="Category")
        fig.update_layout(height=450, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.write("---")

    if "Customer Name" in filtered_df.columns:
        st.subheader("🔍 Search Customer")
        search = st.text_input("Enter Customer Name")
        if search:
            result = filtered_df[filtered_df["Customer Name"].str.contains(search, case=False, na=False)]
            st.dataframe(result, use_container_width=True)
        st.write("---")

    st.subheader("📊 Summary Statistics")
    st.dataframe(filtered_df.describe(), use_container_width=True)
    st.write("---")

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Filtered Dataset", data=csv,
                        file_name="Filtered_Sales_Data.csv", mime="text/csv")

# =====================================================
# FOOTER
# =====================================================

st.write("---")
st.markdown(
"""
<style>
.footer{
background:white;
padding:20px;
border-radius:15px;
text-align:center;
box-shadow:0px 4px 15px rgba(0,0,0,0.1);
margin-top:20px;
}
</style>
<div class="footer">
<h3>📊 Sales Analytics Dashboard</h3>
<p>Developed using <b>Python • Streamlit • Plotly • Pandas</b></p>
<p>Made with ❤️ by <b>Tanmay Sharma</b></p>
</div>
""",
unsafe_allow_html=True
)

# =====================================================
# END
# =====================================================
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
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

/* Background */
.stApp{
background:linear-gradient(135deg,#EEF5FF,#DCEBFF,#C5DBFF);
}

/* Sidebar */
[data-testid="stSidebar"]{
background:linear-gradient(180deg,#0F172A,#1E3A8A);
}

[data-testid="stSidebar"] *{
color:white;
}

/* Title */
h1{
color:#0F172A;
font-weight:bold;
}

h2,h3{
color:#1E40AF;
}

/* Metric Cards */
[data-testid="metric-container"]{
background:white;
padding:20px;
border-radius:15px;
box-shadow:0px 8px 20px rgba(0,0,0,.15);
border-left:6px solid #2563EB;
}

/* Dataframe */
[data-testid="stDataFrame"]{
background:white;
padding:10px;
border-radius:12px;
}

/* Plotly Charts */
.stPlotlyChart{
background:white;
padding:15px;
border-radius:15px;
box-shadow:0px 6px 15px rgba(0,0,0,.12);
}

/* Buttons */
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

footer{
visibility:hidden;
}

header{
visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================

st.title("📊 Sales Analytics Dashboard")

st.markdown("### Interactive Business Intelligence Dashboard")

st.write("---")

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data(file):

    df = pd.read_csv(file)

    df["Order Date"] = pd.to_datetime(df["Order Date"])

    df["Ship Date"] = pd.to_datetime(df["Ship Date"])

    return df

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("📂 Upload Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Choose CSV File",
    type=["csv"]
)

if uploaded_file is None:

    st.info("👈 Upload synthetic_sales_data.csv")

    st.stop()

df = load_data(uploaded_file)

# =====================================================
# FILTERS
# =====================================================

st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Region",
    df["Region"].unique(),
    default=df["Region"].unique()
)

category = st.sidebar.multiselect(
    "Category",
    df["Category"].unique(),
    default=df["Category"].unique()
)

segment = st.sidebar.multiselect(
    "Customer Segment",
    df["Customer Segment"].unique(),
    default=df["Customer Segment"].unique()
)

payment = st.sidebar.multiselect(
    "Payment Mode",
    df["Payment Mode"].unique(),
    default=df["Payment Mode"].unique()
)

filtered_df = df[
    (df["Region"].isin(region))
    &
    (df["Category"].isin(category))
    &
    (df["Customer Segment"].isin(segment))
    &
    (df["Payment Mode"].isin(payment))
]

# =====================================================
# KPI CARDS
# =====================================================

sales = filtered_df["Sales Amount"].sum()

profit = filtered_df["Profit"].sum()

orders = filtered_df["Order ID"].nunique()

customers = filtered_df["Customer ID"].nunique()

avg_sale = filtered_df["Sales Amount"].mean()

c1,c2,c3,c4,c5 = st.columns(5)

c1.metric(
    "💰 Total Sales",
    f"${sales:,.0f}"
)

c2.metric(
    "📈 Total Profit",
    f"${profit:,.0f}"
)

c3.metric(
    "🧾 Orders",
    orders
)

c4.metric(
    "👥 Customers",
    customers
)

c5.metric(
    "🛒 Avg Order",
    f"${avg_sale:,.0f}"
)

st.write("---")

# =====================================================
# DATASET OVERVIEW
# =====================================================

left,right = st.columns([3,1])

with left:

    st.subheader("Dataset Preview")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )

with right:

    st.subheader("Dataset Shape")

    st.metric("Rows", filtered_df.shape[0])

    st.metric("Columns", filtered_df.shape[1])

    st.subheader("Missing Values")

    st.dataframe(
        filtered_df.isnull().sum(),
        use_container_width=True
    )

st.write("---")

# =====================================================
# QUICK SUMMARY
# =====================================================

st.subheader("Business Summary")

col1,col2,col3 = st.columns(3)

with col1:

    st.success(
        f"Highest Sale : ${filtered_df['Sales Amount'].max():,.0f}"
    )

    st.info(
        f"Lowest Sale : ${filtered_df['Sales Amount'].min():,.0f}"
    )

with col2:

    st.success(
        f"Highest Profit : ${filtered_df['Profit'].max():,.0f}"
    )

    st.info(
        f"Lowest Profit : ${filtered_df['Profit'].min():,.0f}"
    )

with col3:

    st.success(
        f"Average Profit : ${filtered_df['Profit'].mean():,.0f}"
    )

    st.info(
        f"Average Discount : {filtered_df['Discount (%)'].mean():.1f}%"
    )

st.write("---")

# =====================================================
# SALES BY CATEGORY
# =====================================================

st.subheader("📦 Sales by Category")

category_sales = (
    filtered_df.groupby("Category")["Sales Amount"]
    .sum()
    .reset_index()
)

fig = px.bar(
    category_sales,
    x="Category",
    y="Sales Amount",
    color="Category",
    text_auto=".2s"
)

fig.update_layout(height=500)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# TOP PRODUCTS
# =====================================================

st.subheader("🏆 Top 10 Products")

top_products = (
    filtered_df.groupby("Product Name")["Sales Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig = px.bar(
    x=top_products.values,
    y=top_products.index,
    orientation="h",
    text_auto=".2s"
)

fig.update_layout(height=500)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

st.success("✅ Part 1 Completed")
# =====================================================
# MONTHLY SALES TREND
# =====================================================

st.subheader("📈 Monthly Sales Trend")

filtered_df["Month"] = filtered_df["Order Date"].dt.strftime("%Y-%m")

monthly_sales = (
    filtered_df.groupby("Month")["Sales Amount"]
    .sum()
    .reset_index()
)

fig = px.line(
    monthly_sales,
    x="Month",
    y="Sales Amount",
    markers=True,
    title="Monthly Sales Trend"
)

fig.update_traces(line_width=4)

fig.update_layout(
    height=500,
    xaxis_title="Month",
    yaxis_title="Sales"
)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# PROFIT BY REGION
# =====================================================

st.subheader("🌍 Profit by Region")

region_profit = (
    filtered_df.groupby("Region")["Profit"]
    .sum()
    .reset_index()
)

fig = px.bar(
    region_profit,
    x="Region",
    y="Profit",
    color="Region",
    text_auto=".2s"
)

fig.update_layout(height=500)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# SALES BY REGION (DONUT)
# =====================================================

st.subheader("🥧 Sales Distribution by Region")

region_sales = (
    filtered_df.groupby("Region")["Sales Amount"]
    .sum()
    .reset_index()
)

fig = px.pie(
    region_sales,
    names="Region",
    values="Sales Amount",
    hole=0.55
)

fig.update_layout(height=500)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# TOP 10 CUSTOMERS
# =====================================================

st.subheader("👥 Top 10 Customers")

top_customer = (
    filtered_df.groupby("Customer Name")["Sales Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig = px.bar(
    x=top_customer.values,
    y=top_customer.index,
    orientation="h",
    text_auto=".2s",
    color=top_customer.values,
    color_continuous_scale="Blues"
)

fig.update_layout(
    height=550,
    xaxis_title="Sales"
)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# TOP STATES
# =====================================================

st.subheader("🏙️ Top 10 States by Sales")

state_sales = (
    filtered_df.groupby("State")["Sales Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig = px.bar(
    x=state_sales.index,
    y=state_sales.values,
    text_auto=".2s",
    color=state_sales.values,
    color_continuous_scale="Viridis"
)

fig.update_layout(
    height=500,
    xaxis_title="State",
    yaxis_title="Sales"
)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# PAYMENT MODE
# =====================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("💳 Payment Mode")

    payment_data = (
        filtered_df.groupby("Payment Mode")
        .size()
        .reset_index(name="Count")
    )

    fig = px.pie(
        payment_data,
        names="Payment Mode",
        values="Count",
        hole=0.45
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    st.subheader("🚚 Delivery Status")

    delivery = (
        filtered_df.groupby("Delivery Status")
        .size()
        .reset_index(name="Count")
    )

    fig = px.bar(
        delivery,
        x="Delivery Status",
        y="Count",
        color="Delivery Status",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# CUSTOMER SEGMENT
# =====================================================

st.subheader("👨‍💼 Customer Segment Analysis")

segment_sales = (
    filtered_df.groupby("Customer Segment")["Sales Amount"]
    .sum()
    .reset_index()
)

fig = px.bar(
    segment_sales,
    x="Customer Segment",
    y="Sales Amount",
    color="Customer Segment",
    text_auto=".2s"
)

fig.update_layout(height=450)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# STOCK ANALYSIS
# =====================================================

st.subheader("📦 Stock Left Distribution")

fig = px.histogram(
    filtered_df,
    x="Stock Left",
    nbins=25,
    color_discrete_sequence=["royalblue"]
)

fig.update_layout(height=450)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# AUTO REORDER
# =====================================================

st.subheader("📋 Auto Reorder")

reorder = (
    filtered_df.groupby("Auto Reorder")
    .size()
    .reset_index(name="Orders")
)

fig = px.pie(
    reorder,
    names="Auto Reorder",
    values="Orders",
    hole=0.50
)

fig.update_layout(height=450)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

st.success("✅ Part 2 Completed Successfully")
# =====================================================
# CORRELATION HEATMAP
# =====================================================

st.subheader("🔥 Correlation Heatmap")

numeric_df = filtered_df.select_dtypes(include="number")

corr = numeric_df.corr(numeric_only=True)

fig = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    aspect="auto",
    title="Correlation Matrix"
)

fig.update_layout(height=650)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# SALES VS PROFIT
# =====================================================

st.subheader("📈 Sales vs Profit")

fig = px.scatter(
    filtered_df,
    x="Sales Amount",
    y="Profit",
    color="Category",
    size="Quantity",
    hover_name="Customer Name"
)

fig.update_layout(height=550)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# DISCOUNT ANALYSIS
# =====================================================

st.subheader("🏷 Discount Analysis")

fig = px.box(
    filtered_df,
    x="Category",
    y="Discount (%)",
    color="Category"
)

fig.update_layout(height=500)

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# =====================================================
# SEARCH CUSTOMER
# =====================================================

st.subheader("🔍 Search Customer")

search = st.text_input("Enter Customer Name")

if search:

    result = filtered_df[
        filtered_df["Customer Name"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

    st.dataframe(
        result,
        use_container_width=True
    )

st.write("---")

# =====================================================
# SUMMARY STATISTICS
# =====================================================

st.subheader("📊 Summary Statistics")

st.dataframe(
    filtered_df.describe(),
    use_container_width=True
)

st.write("---")

# =====================================================
# DOWNLOAD BUTTON
# =====================================================

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Dataset",
    data=csv,
    file_name="Filtered_Sales_Data.csv",
    mime="text/csv"
)

st.write("---")

# =====================================================
# COMPLETE DATASET
# =====================================================

with st.expander("📄 View Complete Dataset"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )

st.write("---")

# =====================================================
# FOOTER
# =====================================================

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
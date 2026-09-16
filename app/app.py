import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="FORESIGHT - Demand & Inventory Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("FORESIGHT")
st.subheader("Demand & Inventory Intelligence")

st.write("Dashboard starting...")

st.success("Streamlit app is working!")


from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Risk scored data load
risk_file = BASE_DIR / "data" / "processed" / "risk_scored_data.csv"

risk_df = pd.read_csv(risk_file)

st.write("Risk Scored Data Shape:", risk_df.shape)
st.write("Risk Scored Data Columns:")
st.write(risk_df.columns.tolist())

st.dataframe(risk_df.head(10))


# SKU Master data load
sku_file = BASE_DIR / "data" / "raw" / "sku_master.csv"

sku_master = pd.read_csv(sku_file)

# Keep SKU and Category information
sku_category = sku_master[["sku_id", "category"]].drop_duplicates("sku_id")

# Add category to risk data
risk_df = risk_df.merge(
    sku_category,
    on="sku_id",
    how="left",
    validate="many_to_one"
)

st.write("Category added successfully!")
st.write("Updated Risk Data Shape:", risk_df.shape)

st.dataframe(
    risk_df[["sku_id", "category"]].head(10)
)


# -----------------------------
# Dashboard Filters
# -----------------------------

st.subheader("Filters")

categories = ["All"] + sorted(
    risk_df["category"].dropna().unique().tolist()
)

selected_category = st.selectbox(
    "Select Category",
    categories
)

# Apply category filter
if selected_category != "All":
    filtered_df = risk_df[
        risk_df["category"] == selected_category
    ].copy()
else:
    filtered_df = risk_df.copy()

st.write("Filtered Data Shape:", filtered_df.shape)

st.dataframe(filtered_df.head(10))


# SKU Filter
skus = ["All"] + sorted(
    filtered_df["sku_id"].dropna().unique().tolist()
)

selected_sku = st.selectbox(
    "Select SKU",
    skus
)

# Apply SKU filter
if selected_sku != "All":
    filtered_df = filtered_df[
        filtered_df["sku_id"] == selected_sku
    ].copy()

st.write("Final Filtered Data Shape:", filtered_df.shape)

st.dataframe(filtered_df.head(10))


# -----------------------------
# Actual vs Forecast
# -----------------------------

st.subheader("Actual vs Forecast")

# Aggregate demand by week
forecast_df = (
    filtered_df
    .groupby("week_number")[["actual_demand", "forecast_demand"]]
    .sum()
    .reset_index()
    .sort_values("week_number")
)

st.line_chart(
    forecast_df.set_index("week_number")[
        ["actual_demand", "forecast_demand"]
    ]
)



# -----------------------------
# Risk Summary
# -----------------------------

st.subheader("Risk Overview")

stockout_count = (filtered_df["stockout_risk"] == True).sum()
overstock_count = (filtered_df["overstock_risk"] == True).sum()

healthy_count = len(filtered_df) - stockout_count - overstock_count

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🔴 Stockout", stockout_count)

with col2:
    st.metric("🟠 Overstock", overstock_count)

with col3:
    st.metric("🟢 Healthy", healthy_count)



st.subheader("Priority Actions")

reorder_df = filtered_df[filtered_df["action"] == "Reorder Now"]

st.write("### 🔴 Reorder Now")

if len(reorder_df) > 0:
    st.dataframe(
        reorder_df[
            ["sku_id", "category", "stockout_units_at_risk", "sales_at_risk_rupees"]
        ].head(10)
    )
else:
    st.success("No SKU requires immediate reorder.")


# Markdown / Overstock actions
# Use the overstock risk flag so the dashboard still shows the
# required markdown list even when the source action label is
# something like "Markdown Clear".
markdown_df = filtered_df[
    filtered_df["overstock_risk"] == True
].copy()

st.write("### 🟠 Markdown")

if len(markdown_df) > 0:
    st.dataframe(
        markdown_df[
            ["sku_id", "category", "overstock_units_at_risk", "locked_capital_rupees"]
        ].sort_values(
            "overstock_units_at_risk",
            ascending=False
        ).head(10)
    )
else:
    st.success("No SKU requires markdown.")


# Watch list
# Watch = SKUs that are currently healthy and therefore need
# monitoring rather than immediate reorder/markdown action.
watch_df = filtered_df[
    (filtered_df["stockout_risk"] == False)
    & (filtered_df["overstock_risk"] == False)
].copy()

st.write("### 🟢 Watch SKU")

if len(watch_df) > 0:
    watch_columns = [
        "sku_id",
        "category",
        "unit_price",
        "cost_price"
    ]

    st.dataframe(
        watch_df[watch_columns].head(10)
    )
else:
    st.info("No SKU currently requires monitoring.")


# Action summary
st.write("### Action Summary")
st.dataframe(
    filtered_df["action"]
    .value_counts()
    .rename_axis("action")
    .reset_index(name="count")
)





























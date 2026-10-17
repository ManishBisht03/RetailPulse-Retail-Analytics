
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="RetailPulse Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("RetailPulse – Retail Sales & Customer Analytics")
st.write(
    "Explore retail sales trends using the analysed "
    "Online Retail II dataset."
)

file_path = Path("retailpulse_monthly_summary.csv")

if file_path.exists():
    df = pd.read_csv(file_path)

    st.success("Monthly sales dataset connected successfully!")

    st.subheader("Monthly Sales Summary")

    st.dataframe(df, use_container_width=True)

    if "Total_Sales" in df.columns and "Month" in df.columns:
        df["Month"] = df["Month"].astype(str)
        df = df.sort_values("Month")

        st.subheader("Monthly Recorded Sales Trend")
        chart_data = df.set_index("Month")[["Total_Sales"]]
        st.line_chart(chart_data)
        st.subheader("Monthly Sales Comparison")
st.bar_chart(chart_data)

        col1, col2 = st.columns(2)
        col1.metric(
            "Months Analysed",
            f"{df['Month'].nunique():,}"
        )
        col2.metric(
            "Total Recorded Sales",
            f"{df['Total_Sales'].sum():,.2f}"
        )
    else:
        st.warning(
            "Expected columns Month and Total_Sales were not found. "
            "Check the column names in the uploaded CSV."
        )

else:
    st.error(
        "Monthly summary file not found. "
        "Check that retailpulse_monthly_summary.csv "
        "is uploaded to the repository root."
    )

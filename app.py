import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="RetailPulse Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("RetailPulse – Retail Sales & Customer Analytics")
st.write(
    "Explore retail sales trends and estimated future sales "
    "using the analysed Online Retail II dataset."
)

# --------------------------------------------------
# Monthly Sales Data
# --------------------------------------------------
file_path = Path("retailpulse_monthly_summary.csv")

if file_path.exists():
    df = pd.read_csv(file_path)

    if "Month" in df.columns and "Total_Sales" in df.columns:
        df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
        df["Total_Sales"] = pd.to_numeric(
            df["Total_Sales"], errors="coerce"
        )
        df = df.dropna(subset=["Month", "Total_Sales"])

        # Normalize dates to month start and aggregate duplicate months
        df["Month"] = df["Month"].dt.to_period("M").dt.to_timestamp()
        df = df.groupby("Month", as_index=False)["Total_Sales"].sum()
        df = df.sort_values("Month").reset_index(drop=True)

        st.success("Monthly sales dataset connected successfully!")

        st.subheader("Monthly Sales Summary")
        display_df = df.copy()
        display_df["Month"] = display_df["Month"].dt.strftime("%Y-%m")
        st.dataframe(display_df, use_container_width=True)

        # --------------------------------------------------
        # Month Filter
        # --------------------------------------------------
        month_options = df["Month"].dt.strftime("%Y-%m").tolist()
        selected_months = st.multiselect(
            "Filter by month",
            options=month_options,
            default=month_options
        )

        filtered_df = df[
            df["Month"].dt.strftime("%Y-%m").isin(selected_months)
        ].copy()

        if not filtered_df.empty:
            # --------------------------------------------------
            # Historical Sales Trend
            # --------------------------------------------------
            st.subheader("Monthly Recorded Sales Trend")
            historical_data = filtered_df.set_index("Month")[["Total_Sales"]]
            historical_data.columns = ["Historical Sales"]
            st.line_chart(historical_data)

            # --------------------------------------------------
            # Monthly Sales Comparison
            # --------------------------------------------------
            st.subheader("Monthly Sales Comparison")
            comparison_data = filtered_df.copy()
            comparison_data["Month"] = comparison_data["Month"].dt.strftime("%Y-%m")
            st.bar_chart(
                comparison_data.set_index("Month")[["Total_Sales"]]
            )

            # --------------------------------------------------
            # Demand Forecasting
            # --------------------------------------------------
            st.subheader("Demand Forecasting")
            st.write(
                "Explore recorded monthly sales, the estimated future sales, "
                "and historical forecast evaluation."
            )

            forecast_months = st.slider(
                "Months to forecast",
                min_value=1,
                max_value=12,
                value=6
            )

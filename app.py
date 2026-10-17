import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="RetailPulse Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 RetailPulse – Retail Sales & Customer Analytics")
st.write(
    "Explore retail sales, product performance, and customer "
    "purchasing behaviour using the Online Retail II dataset."
)

file_path = Path("retailpulse_analysis_ready.csv")

if file_path.exists():
    df = pd.read_csv(file_path)

    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Transaction Rows", f"{len(df):,}")

    if "Invoice" in df.columns:
        col2.metric("Unique Invoices", f"{df['Invoice'].nunique():,}")

    if "Country" in df.columns:
        col3.metric("Countries", f"{df['Country'].nunique():,}")

    if "Sales" in df.columns:
        st.subheader("Recorded Sales")
        sales_by_country = (
            df.groupby("Country", dropna=False)["Sales"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        st.bar_chart(sales_by_country)

    st.subheader("Explore the Data")
    st.dataframe(df.head(100), use_container_width=True)

else:
    st.info(
        "The dataset has not been added to this GitHub repository yet. "
        "Upload retailpulse_analysis_ready.csv to enable the data visuals."
    )

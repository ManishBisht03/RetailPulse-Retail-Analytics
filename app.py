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
    "An interactive overview of retail transactions, "
    "product performance, and customer purchasing behaviour."
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

    if "Sales" in df.columns and "Country" in df.columns:
        st.subheader("Recorded Sales by Country")
        sales = (
            df.groupby("Country")["Sales"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        st.bar_chart(sales)

    st.subheader("Dataset Preview")
    st.dataframe(df.head(100), use_container_width=True)

else:
    st.info(
        "The source dataset is not connected to this web app yet."
    )

    st.subheader("Project Highlights")

    col1, col2, col3 = st.columns(3)
    col1.metric("Transaction Rows Analysed", "1.03M")
    col2.metric("Unique Invoices", "53.63K")
    col3.metric("Countries", "43")

    st.subheader("Project Scope")
    st.markdown("""
    - Retail sales and transaction analysis
    - Product performance analysis
    - Customer purchasing behaviour and segmentation
    - Country-level sales comparisons
    - Interactive Power BI reporting

    **Note:** The figures above summarize the completed analysis.
    The original dataset is not currently connected to this web app.
    """)

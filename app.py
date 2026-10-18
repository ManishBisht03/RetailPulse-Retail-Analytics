
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
    selected_months = st.multiselect(
    "Filter by month",
    options=sorted(df["Month"].astype(str).unique()),
    default=sorted(df["Month"].astype(str).unique())
    )
    df = df[df["Month"].astype(str).isin(selected_months)]

    if "Total_Sales" in df.columns and "Month" in df.columns:
        df["Month"] = df["Month"].astype(str)
        df = df.sort_values("Month")

        st.subheader("Monthly Recorded Sales Trend")
        chart_data = df.set_index("Month")[["Total_Sales"]]
        st.line_chart(chart_data)
        st.subheader("Monthly Sales Comparison")
        
        # Demand Forecasting
        st.subheader("Demand Forecasting")

        st.write(
            "Estimate future monthly recorded sales using "
            "a linear trend from historical monthly data."
        )

        forecast_months = st.slider(
            "Months to forecast",
            min_value=1,
            max_value=12,
            value=6
        )

        forecast_df = df[["Month", "Total_Sales"]].copy()
        forecast_df["Month"] = pd.to_datetime(
            forecast_df["Month"], errors="coerce"
        )
        forecast_df["Total_Sales"] = pd.to_numeric(
            forecast_df["Total_Sales"], errors="coerce"
        )
        forecast_df = forecast_df.dropna()
        forecast_df = forecast_df.sort_values("Month")

        # Forecast only when at least two historical months exist
        if len(forecast_df) >= 2:
            forecast_df = forecast_df.groupby(
                "Month", as_index=False
            )["Total_Sales"].sum()

            forecast_df["Month_Number"] = range(len(forecast_df))

            slope, intercept = __import__("numpy").polyfit(
                forecast_df["Month_Number"],
                forecast_df["Total_Sales"],
                1
            )

            future_numbers = range(
                len(forecast_df),
                len(forecast_df) + forecast_months
            )

            future_dates = pd.date_range(
                start=forecast_df["Month"].max() + pd.offsets.MonthBegin(1),
                periods=forecast_months,
                freq="MS"
            )

            future_sales = [
                max(0, slope * number + intercept)
                for number in future_numbers
            ]

            historical_chart = forecast_df[
                ["Month", "Total_Sales"]
            ].copy()
            historical_chart["Type"] = "Historical"

            future_chart = pd.DataFrame({
                "Month": future_dates,
                "Total_Sales": future_sales,
                "Type": "Forecast"
            })

            combined_chart = pd.concat(
                [historical_chart, future_chart],
                ignore_index=True
            )

            combined_chart = combined_chart.rename(
                columns={
                    "Month": "Month",
                    "Total_Sales": "Recorded Sales"
                }
            )

            st.line_chart(
                combined_chart,
                x="Month",
                y="Recorded Sales",
                color="Type"
            )

            st.caption(
                "Forecasts are estimates based on a linear trend, "
                "not guaranteed future sales. Filtered historical "
                "data may change the forecast."
            )

            st.subheader("Forecast Values")
            st.dataframe(
                future_chart[["Month", "Total_Sales"]].rename(
                    columns={
                        "Month": "Forecast Month",
                        "Total_Sales": "Estimated Sales"
                    }
                ).style.format({"Estimated Sales": "{:,.2f}"}),
                use_container_width=True
            )
        else:
            st.info(
                "At least two valid historical months are needed "
                "to generate a forecast."
            )

        st.bar_chart(chart_data)
        country_file = Path("retailpulse_country_summary.csv")
        if country_file.exists():
            country_df = pd.read_csv(country_file)
            st.subheader("Recorded Sales by Country")
            st.dataframe(country_df, use_container_width=True)
            if "Country" in country_df.columns and "Total_Sales" in country_df.columns:
                country_df = country_df.sort_values("Total_Sales", ascending=False).head(10)
                st.bar_chart(country_df.set_index("Country")[["Total_Sales"]])
            product_file = Path("retailpulse_product_summary.csv")
            if product_file.exists():
                product_df = pd.read_csv(product_file)
                st.subheader("Top 10 Products by Recorded Sales")
                st.dataframe(product_df.head(10), use_container_width=True)
                if "Description" in product_df.columns and "Total_Sales" in product_df.columns:
                    top_products = product_df.sort_values(
                        "Total_Sales", ascending=False
                    ).head(10)
                    product_chart = top_products.set_index("Description")[["Total_Sales"]]
                    st.bar_chart(product_chart)
                customer_file = Path("retailpulse_customer_summary.csv")
                if customer_file.exists():
                    customer_df = pd.read_csv(customer_file)
                    customer_df.columns = customer_df.columns.str.strip().str.lower()
                    st.subheader("Customer Analysis")
                    selected_customer = st.selectbox("Customer ID",
                    ["All Customers"] + customer_df["customer id"].astype(str).tolist())
                    st.dataframe(customer_df.head(10), use_container_width=True)
                    if selected_customer != "All Customers":
                        customer_df = customer_df[
                        customer_df["customer id"].astype(str) == selected_customer
                        ]
                    st.metric("Customers Displayed",
                    customer_df["customer id"].nunique()
                    )
                    st.metric("Total Recorded Sales",
                    f"{customer_df['total_sales'].sum():,.2f}"
                    )
                    st.metric("Total Quantity",
                    f"{customer_df['total_quantity'].sum():,.0f}"
                    )
                    customer_metric = st.selectbox(
                    "Choose Customer Metric",
                    ["total_sales", "total_quantity"]
                    )
                    if "customer id" in customer_df.columns and "total_sales" in customer_df.columns:
                        top_customers = customer_df.sort_values(
                        customer_metric, ascending=False
                        ).head(10)
                        customer_chart = top_customers.set_index("customer id")[[customer_metric]]
                        st.subheader("Top 10 Customers by Recorded Sales")
                        st.bar_chart(customer_chart)

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

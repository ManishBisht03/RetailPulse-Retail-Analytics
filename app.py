
import streamlit as st
import pandas as pd
import numpy as np
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
    "Explore retail sales trends and estimated future "
    "sales using the analysed Online Retail II dataset."
)

# --------------------------------------------------
# Monthly Sales Data
# --------------------------------------------------
file_path = Path("retailpulse_monthly_summary.csv")

if file_path.exists():
    df = pd.read_csv(file_path)

    st.success("Monthly sales dataset connected successfully!")

    if "Month" in df.columns and "Total_Sales" in df.columns:

        df["Month"] = pd.to_datetime(
            df["Month"], errors="coerce"
        )
        df["Total_Sales"] = pd.to_numeric(
            df["Total_Sales"], errors="coerce"
        )
        df = df.dropna(subset=["Month", "Total_Sales"])

        # Aggregate duplicate months if present
        df = df.groupby(
            "Month", as_index=False
        )["Total_Sales"].sum()

        df = df.sort_values("Month")

        st.subheader("Monthly Sales Summary")

        display_df = df.copy()
        display_df["Month"] = display_df["Month"].dt.strftime(
            "%Y-%m"
        )
        st.dataframe(display_df, use_container_width=True)

        # --------------------------------------------------
        # Month Filter
        # --------------------------------------------------
        month_options = df["Month"].dt.strftime(
            "%Y-%m"
        ).tolist()

        selected_months = st.multiselect(
            "Filter by month",
            options=month_options,
            default=month_options
        )

        filtered_df = df[
            df["Month"].dt.strftime("%Y-%m").isin(
                selected_months
            )
        ].copy()

        if not filtered_df.empty:

            # --------------------------------------------------
            # Historical Sales Trend
            # --------------------------------------------------
            st.subheader("Monthly Recorded Sales Trend")

            historical_data = filtered_df.set_index(
                "Month"
            )[["Total_Sales"]]

            historical_data.columns = ["Historical Sales"]

            st.line_chart(historical_data)

            # --------------------------------------------------
            # Monthly Sales Comparison
            # --------------------------------------------------
            st.subheader("Monthly Sales Comparison")

            comparison_data = filtered_df.copy()
            comparison_data["Month"] = (
                comparison_data["Month"].dt.strftime("%Y-%m")
            )

            st.bar_chart(
                comparison_data.set_index("Month")[
                    ["Total_Sales"]
                ]
            )

            # --------------------------------------------------
            # Demand Forecasting
            # --------------------------------------------------
            st.subheader("Demand Forecasting")

            st.write(
                "Compare historical monthly recorded sales "
                "with estimated future sales."
            )

            forecast_months = st.slider(
                "Months to forecast",
                min_value=1,
                max_value=12,
                value=6
            )

            # Forecast uses the complete monthly history,
            # not only the months selected for display.
            forecast_df = df[
                ["Month", "Total_Sales"]
            ].copy().sort_values("Month")

            if len(forecast_df) >= 2:

                # Create a numeric time index
                forecast_df["Month_Number"] = np.arange(
                    len(forecast_df)
                )

                # Fit a simple linear trend
                slope, intercept = np.polyfit(
                    forecast_df["Month_Number"],
                    forecast_df["Total_Sales"],
                    1
                )
                

                future_numbers = np.arange(
                    len(forecast_df),
                    len(forecast_df) + forecast_months
                )

                # Start with the month after the last recorded month
                future_dates = pd.date_range(
                    start=forecast_df["Month"].max()
                    + pd.offsets.MonthBegin(1),
                    periods=forecast_months,
                    freq="MS"
                )

                future_sales = np.maximum(
                    0,
                    slope * future_numbers + intercept
                )
                # Historical Forecast Accuracy using MAE
                st.subheader("Historical Forecast Accuracy")

                if len(forecast_df) >= 5:
                    test_size = min(
                        3,
                        max(1, len(forecast_df) // 5)
                    )

                    train_df = forecast_df.iloc[:-test_size].copy()
                    test_df = forecast_df.iloc[-test_size:].copy()

                    train_slope, train_intercept = np.polyfit(
                        train_df["Month_Number"],
                        train_df["Total_Sales"],
                        1
                    )

                    test_predictions = np.maximum(
                        0,
                        train_slope * test_df["Month_Number"].to_numpy()
                        + train_intercept
                    )

                    mae = np.mean(
                        np.abs(
                            test_df["Total_Sales"].to_numpy()
                            - test_predictions
                        )
                    )

                    st.metric(
                        "Historical Test MAE",
                        f"{mae:,.2f}"
                    )

                    st.caption(
                        f"MAE evaluated on the most recent {test_size} "
                        "historical month(s) held out from model fitting. "
                        "Lower MAE indicates closer predictions."
                    )
                else:
                    st.info(
                        "At least 5 historical months are needed "
                        "to evaluate forecast accuracy."
                    )

                # Historical line: values only for historical months
                historical_chart = forecast_df[
                    ["Month", "Total_Sales"]
                ].rename(
                    columns={
                        "Total_Sales": "Historical Sales"
                    }
                )

                historical_chart["Forecast Sales"] = np.nan

                # Forecast line: values only for future months
                future_chart = pd.DataFrame({
                    "Month": future_dates,
                    "Historical Sales": np.nan,
                    "Forecast Sales": future_sales
                })

                # Combine the two series
                combined_chart = pd.concat(
                    [historical_chart, future_chart],
                    ignore_index=True
                )

                combined_chart["Month"] = pd.to_datetime(
                    combined_chart["Month"]
                )

                combined_chart = combined_chart.sort_values(
                    "Month"
                ).set_index("Month")

                # Display two separate lines
                st.line_chart(
                    combined_chart[
                        ["Historical Sales", "Forecast Sales"]
                    ]
                )

                st.caption(
                    "Historical Sales represents recorded data. "
                    "Forecast Sales is a simple linear-trend estimate, "
                    "not a guaranteed result or a trained AI model."
                )

                # --------------------------------------------------
                # Forecast Values Table
                # --------------------------------------------------
                st.subheader("Forecast Values")

                forecast_table = pd.DataFrame({
                    "Forecast Month": future_dates.strftime(
                        "%Y-%m"
                    ),
                    "Estimated Sales": future_sales
                })

                st.dataframe(
                    forecast_table.style.format({
                        "Estimated Sales": "{:,.2f}"
                    }),
                    use_container_width=True
                )

            else:
                st.info(
                    "At least two months of historical sales "
                    "are required to generate a forecast."
                )

        else:
            st.warning(
                "No months are selected. Select one or more months "
                "to display the sales charts."
            )

        # --------------------------------------------------
        # Summary Metrics
        # --------------------------------------------------
        col1, col2 = st.columns(2)

        col1.metric(
            "Months Analysed",
            f"{len(filtered_df):,}"
        )

        col2.metric(
            "Total Recorded Sales",
            f"{filtered_df['Total_Sales'].sum():,.2f}"
        )

    else:
        st.warning(
            "Expected columns Month and Total_Sales were not found. "
            "Please check the monthly summary CSV."
        )

else:
    st.error(
        "Monthly summary file not found. Ensure "
        "retailpulse_monthly_summary.csv is uploaded "
        "to the repository root."
    )

# --------------------------------------------------
# Country Analytics
# --------------------------------------------------
country_file = Path("retailpulse_country_summary.csv")

if country_file.exists():
    country_df = pd.read_csv(country_file)

    st.subheader("Recorded Sales by Country")
    st.dataframe(country_df, use_container_width=True)

    if (
        "Country" in country_df.columns
        and "Total_Sales" in country_df.columns
    ):
        country_df["Total_Sales"] = pd.to_numeric(
            country_df["Total_Sales"], errors="coerce"
        )

        top_countries = country_df.sort_values(
            "Total_Sales", ascending=False
        ).head(10)

        st.subheader("Top 10 Countries by Recorded Sales")
        st.bar_chart(
            top_countries.set_index("Country")[["Total_Sales"]]
        )

# --------------------------------------------------
# Product Analytics
# --------------------------------------------------
product_file = Path("retailpulse_product_summary.csv")

if product_file.exists():
    product_df = pd.read_csv(product_file)

    st.subheader("Top 10 Products by Recorded Sales")

    if (
        "Description" in product_df.columns
        and "Total_Sales" in product_df.columns
    ):
        product_df["Total_Sales"] = pd.to_numeric(
            product_df["Total_Sales"], errors="coerce"
        )

        top_products = product_df.sort_values(
            "Total_Sales", ascending=False
        ).head(10)

        st.dataframe(top_products, use_container_width=True)

        product_chart = top_products.set_index(
            "Description"
        )[["Total_Sales"]]

        st.bar_chart(product_chart)
    else:
        st.dataframe(product_df.head(10), use_container_width=True)

# --------------------------------------------------
# Customer Analytics
# --------------------------------------------------
customer_file = Path("retailpulse_customer_summary.csv")

if customer_file.exists():
    customer_df = pd.read_csv(customer_file)

    customer_df.columns = (
        customer_df.columns.str.strip().str.lower()
    )

    required_columns = {
        "customer id", "total_sales", "total_quantity"
    }

    if required_columns.issubset(customer_df.columns):

        customer_df["total_sales"] = pd.to_numeric(
            customer_df["total_sales"], errors="coerce"
        ).fillna(0)

        customer_df["total_quantity"] = pd.to_numeric(
            customer_df["total_quantity"], errors="coerce"
        ).fillna(0)

        st.subheader("Customer Analysis")

        customer_ids = (
            customer_df["customer id"]
            .dropna()
            .astype(str)
            .sort_values()
            .unique()
            .tolist()
        )

        selected_customer = st.selectbox(
            "Select Customer ID",
            ["All Customers"] + customer_ids
        )

        if selected_customer == "All Customers":
            displayed_customers = customer_df.copy()
        else:
            displayed_customers = customer_df[
                customer_df["customer id"].astype(str)
                == selected_customer
            ].copy()

        st.dataframe(
            displayed_customers.head(10),
            use_container_width=True
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Customers Displayed",
            f"{displayed_customers['customer id'].nunique():,}"
        )

        col2.metric(
            "Total Recorded Sales",
            f"{displayed_customers['total_sales'].sum():,.2f}"
        )

        col3.metric(
            "Total Quantity",
            f"{displayed_customers['total_quantity'].sum():,.0f}"
        )

        customer_metric = st.selectbox(
            "Choose Customer Metric",
            ["total_sales", "total_quantity"],
            format_func=lambda value: {
                "total_sales": "Recorded Sales",
                "total_quantity": "Total Quantity"
            }[value]
        )

        top_customers = displayed_customers.sort_values(
            customer_metric, ascending=False
        ).head(10)

        if not top_customers.empty:
            st.subheader("Top Customers")

            customer_chart = top_customers.set_index(
                "customer id"
            )[[customer_metric]]

            st.bar_chart(customer_chart)

    else:
        st.warning(
            "The customer summary CSV is missing one or more "
            "required columns: customer id, total_sales, total_quantity."
        )

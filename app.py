
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="RetailPulse Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("RetailPulse – Retail Sales & Customer Analytics")
st.caption(
    "Retail sales analysis, demand forecasting, "
    "product performance, country insights and customer analytics."
)

# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------
def load_csv(filename):
    """Load a CSV file safely from the app directory."""
    file_path = Path(filename)

    if not file_path.exists():
        return None

    try:
        return pd.read_csv(file_path)
    except Exception as error:
        st.error(f"Could not read {filename}: {error}")
        return None


def find_column(df, possible_names):
    """Find a column without depending on capitalization."""
    if df is None:
        return None

    column_lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:
        if name.lower() in column_lookup:
            return column_lookup[name.lower()]

    return None


def format_sales(value):
    """Format a sales value for display."""
    if pd.isna(value):
        return "N/A"

    return f"{value:,.2f}"


def prepare_monthly_data(df):
    """Prepare monthly sales data for analysis."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["Month", "Total_Sales"])

    month_col = find_column(
        df, ["Month", "InvoiceDate", "Date", "YearMonth"]
    )
    sales_col = find_column(
        df, ["Total_Sales", "Sales", "Monthly_Sales", "Revenue"]
    )

    if month_col is None or sales_col is None:
        st.error(
            "Monthly CSV must contain a month/date column and a "
            "sales column such as Month and Total_Sales."
        )
        return pd.DataFrame(columns=["Month", "Total_Sales"])

    result = df[[month_col, sales_col]].copy()
    result.columns = ["Month", "Total_Sales"]

    result["Month"] = pd.to_datetime(
        result["Month"], errors="coerce"
    )
    result["Total_Sales"] = pd.to_numeric(
        result["Total_Sales"], errors="coerce"
    )

    result = result.dropna(subset=["Month", "Total_Sales"])

    # Standardize dates to month start.
    result["Month"] = (
        result["Month"].dt.to_period("M").dt.to_timestamp()
    )

    # Combine multiple records belonging to the same month.
    result = (
        result.groupby("Month", as_index=False)["Total_Sales"]
        .sum()
        .sort_values("Month")
        .reset_index(drop=True)
    )

    return result


def make_forecast(history, periods):
    """
    Create a simple linear-trend forecast using historical monthly sales.
    This is a baseline forecast, not a machine-learning model.
    """
    values = history["Total_Sales"].astype(float).to_numpy()

    x = np.arange(len(values), dtype=float)

    if len(values) >= 2:
        slope, intercept = np.polyfit(x, values, 1)
        future_x = np.arange(
            len(values), len(values) + periods, dtype=float
        )
        predictions = slope * future_x + intercept
    elif len(values) == 1:
        predictions = np.repeat(values[0], periods)
    else:
        predictions = np.array([])

    future_dates = pd.date_range(
        start=history["Month"].max() + pd.offsets.MonthBegin(1),
        periods=periods,
        freq="MS"
    )

    # Sales cannot be negative in this baseline forecast.
    predictions = np.maximum(predictions, 0)

    return pd.DataFrame({
        "Month": future_dates,
        "Forecast_Sales": predictions
    })


def evaluate_forecast(history):
    """
    Evaluate a one-step-ahead linear-trend baseline on the last
    available observations. At least 4 months are required.
    """
    values = history["Total_Sales"].astype(float).to_numpy()

    if len(values) < 4:
        return None

    # Keep the final 20% for evaluation, with at least one month.
    test_size = max(1, int(np.ceil(len(values) * 0.2)))
    train_size = len(values) - test_size

    if train_size < 2:
        return None

    train_values = values[:train_size]
    actual_values = values[train_size:]

    x_train = np.arange(len(train_values), dtype=float)
    slope, intercept = np.polyfit(x_train, train_values, 1)

    x_test = np.arange(
        len(train_values), len(values), dtype=float
    )
    predicted_values = np.maximum(
        slope * x_test + intercept, 0
    )

    errors = actual_values - predicted_values
    mae = float(np.mean(np.abs(errors)))

    nonzero = actual_values != 0
    if np.any(nonzero):
        mape = float(
            np.mean(
                np.abs(
                    errors[nonzero] / actual_values[nonzero]
                )
            ) * 100
        )
    else:
        mape = None

    comparison = pd.DataFrame({
        "Month": history["Month"].iloc[train_size:].to_numpy(),
        "Actual_Sales": actual_values,
        "Predicted_Sales": predicted_values
    })

    return mae, mape, comparison


# --------------------------------------------------
# 3. LOAD PROJECT DATA
# --------------------------------------------------
monthly_raw = load_csv("retailpulse_monthly_summary.csv")
country_df = load_csv("retailpulse_country_summary.csv")
product_df = load_csv("retailpulse_product_summary.csv")
customer_df = load_csv("retailpulse_customer_summary.csv")

monthly_df = prepare_monthly_data(monthly_raw)

# --------------------------------------------------
# 4. EXECUTIVE SUMMARY
# --------------------------------------------------
st.header("Executive Summary")

if not monthly_df.empty:
    total_monthly_sales = monthly_df["Total_Sales"].sum()
    average_monthly_sales = monthly_df["Total_Sales"].mean()
    highest_month_row = monthly_df.loc[
        monthly_df["Total_Sales"].idxmax()
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Net Recorded Sales",
        f"{total_monthly_sales:,.2f}"
    )
    col2.metric(
        "Average Monthly Sales",
        f"{average_monthly_sales:,.2f}"
    )
    col3.metric(
        "Months Analysed",
        f"{len(monthly_df):,}"
    )
    col4.metric(
        "Highest Sales Month",
        highest_month_row["Month"].strftime("%b %Y")
    )

    st.caption(
        "Sales figures reflect the supplied summary CSV. "
        "Net recorded sales can include negative values from returns "
        "or adjustments."
    )
else:
    st.warning(
        "Monthly sales data is unavailable. Check that "
        "retailpulse_monthly_summary.csv exists and contains "
        "Month and Total_Sales columns."
    )

st.divider()

# --------------------------------------------------
# 5. MONTHLY SALES TREND AND FORECAST
# --------------------------------------------------
st.header("Monthly Sales Trend & Demand Forecasting")

if not monthly_df.empty:
    min_date = monthly_df["Month"].min().date()
    max_date = monthly_df["Month"].max().date()

    date_col1, date_col2 = st.columns(2)

    with date_col1:
        start_date = st.date_input(
            "Start month",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key="start_month"
        )

    with date_col2:
        end_date = st.date_input(
            "End month",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="end_month"
        )

    filtered_monthly = monthly_df[
        (monthly_df["Month"].dt.date >= start_date)
        & (monthly_df["Month"].dt.date <= end_date)
    ].copy()

    if start_date > end_date:
        st.error("The start month must be before the end month.")
        filtered_monthly = pd.DataFrame(
            columns=["Month", "Total_Sales"]
        )

    if filtered_monthly.empty:
        st.info("No monthly sales data exists in this date range.")
    else:
        forecast_months = st.slider(
            "Months to forecast",
            min_value=1,
            max_value=12,
            value=6,
            key="forecast_months"
        )

        forecast_df = make_forecast(
            filtered_monthly, forecast_months
        )

        # Historical sales chart.
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=filtered_monthly["Month"],
            y=filtered_monthly["Total_Sales"],
            mode="lines+markers",
            name="Historical Sales",
            line=dict(width=3, color="#2563eb"),
            marker=dict(size=6),
            hovertemplate=(
                "Month: %{x|%b %Y}<br>"
                "Sales: %{y:,.2f}<extra></extra>"
            )
        ))

        # Historical trend line.
        if len(filtered_monthly) >= 2:
            trend_x = np.arange(len(filtered_monthly), dtype=float)
            trend_slope, trend_intercept = np.polyfit(
                trend_x,
                filtered_monthly["Total_Sales"].to_numpy(),
                1
            )
            trend_values = (
                trend_slope * trend_x + trend_intercept
            )

            fig.add_trace(go.Scatter(
                x=filtered_monthly["Month"],
                y=trend_values,
                mode="lines",
                name="Historical Trend",
                line=dict(
                    width=2,
                    dash="dot",
                    color="#16a34a"
                ),
                hovertemplate=(
                    "Month: %{x|%b %Y}<br>"
                    "Trend: %{y:,.2f}<extra></extra>"
                )
            ))

        # Forecast line starts at the last historical point.
        forecast_x = pd.concat([
            filtered_monthly[["Month"]].tail(1),
            forecast_df[["Month"]]
        ], ignore_index=True)

        forecast_y = pd.concat([
            filtered_monthly["Total_Sales"].tail(1),
            forecast_df["Forecast_Sales"]
        ], ignore_index=True)

        fig.add_trace(go.Scatter(
            x=forecast_x["Month"],
            y=forecast_y,
            mode="lines+markers",
            name="Forecast Sales",
            line=dict(
                width=3,
                dash="dash",
                color="#f97316"
            ),
            marker=dict(size=7),
            hovertemplate=(
                "Month: %{x|%b %Y}<br>"
                "Forecast: %{y:,.2f}<extra></extra>"
            )
        ))

        fig.add_vline(
            x=filtered_monthly["Month"].max().timestamp() * 1000,
            line_dash="dash",
            line_color="gray",
            annotation_text="Forecast starts"
        )

        fig.update_layout(
            title="Historical Monthly Sales and Demand Forecast",
            xaxis_title="Month",
            yaxis_title="Sales",
            hovermode="x unified",
            legend_title="Series",
            template="plotly_white",
            height=520,
            margin=dict(l=20, r=20, t=70, b=20)
        )

        fig.update_xaxes(
            rangeslider_visible=True,
            tickformat="%b %Y"
        )
        fig.update_yaxes(tickformat=",.0f")

        st.plotly_chart(
            fig, use_container_width=True,
            key="sales_forecast_chart"
        )

        st.caption(
            "Forecast method: linear trend fitted to the selected "
            "historical months. This is an exploratory baseline, "
            "not a guarantee of future sales."
        )

        # Forecast KPI cards.
        forecast_total = forecast_df["Forecast_Sales"].sum()
        forecast_average = forecast_df["Forecast_Sales"].mean()

        fcol1, fcol2, fcol3 = st.columns(3)

        fcol1.metric(
            "Forecast Period",
            f"{forecast_months} months"
        )
        fcol2.metric(
            "Total Forecast Sales",
            f"{forecast_total:,.2f}"
        )
        fcol3.metric(
            "Average Forecast per Month",
            f"{forecast_average:,.2f}"
        )

        st.subheader("Forecast Values")

        display_forecast = forecast_df.copy()
        display_forecast["Month"] = (
            display_forecast["Month"].dt.strftime("%B %Y")
        )
        display_forecast["Forecast_Sales"] = (
            display_forecast["Forecast_Sales"].round(2)
        )
        display_forecast.columns = [
            "Forecast Month", "Forecast Sales"
        ]

        st.dataframe(
            display_forecast,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Forecast CSV",
            data=forecast_df.to_csv(index=False).encode("utf-8"),
            file_name="retailpulse_forecast.csv",
            mime="text/csv"
        )

        # --------------------------------------------------
        # 6. HISTORICAL FORECAST ACCURACY
        # --------------------------------------------------
        st.subheader("Historical Forecast Accuracy Evaluation")

        evaluation = evaluate_forecast(filtered_monthly)

        if evaluation is None:
            st.info(
                "At least 4 months of historical data are required "
                "to calculate the baseline forecast accuracy. "
                "Select a wider date range if possible."
            )
        else:
            mae, mape, comparison_df = evaluation

            accuracy_col1, accuracy_col2 = st.columns(2)

            accuracy_col1.metric(
                "Mean Absolute Error (MAE)",
                f"{mae:,.2f}"
            )

            if mape is not None:
                accuracy_col2.metric(
                    "Mean Absolute Percentage Error (MAPE)",
                    f"{mape:.2f}%"
                )
            else:
                accuracy_col2.metric(
                    "Mean Absolute Percentage Error (MAPE)",
                    "N/A"
                )

            st.caption(
                "MAE is the average absolute difference between actual "
                "and predicted sales, in sales units. Lower MAE means "
                "smaller errors on this evaluation period. MAPE is not "
                "calculated for months whose actual sales are zero."
            )

            accuracy_fig = go.Figure()

            accuracy_fig.add_trace(go.Scatter(
                x=comparison_df["Month"],
                y=comparison_df["Actual_Sales"],
                mode="lines+markers",
                name="Actual Sales",
                line=dict(width=3, color="#2563eb")
            ))

            accuracy_fig.add_trace(go.Scatter(
                x=comparison_df["Month"],
                y=comparison_df["Predicted_Sales"],
                mode="lines+markers",
                name="Predicted Sales",
                line=dict(
                    width=3,
                    dash="dash",
                    color="#f97316"
                )
            ))

            accuracy_fig.update_layout(
                title="Actual vs Predicted Sales (Holdout Period)",
                xaxis_title="Month",
                yaxis_title="Sales",
                hovermode="x unified",
                template="plotly_white",
                height=420
            )

            accuracy_fig.update_xaxes(tickformat="%b %Y")
            accuracy_fig.update_yaxes(tickformat=",.0f")

            st.plotly_chart(
                accuracy_fig,
                use_container_width=True,
                key="actual_vs_predicted_chart"
            )

            comparison_display = comparison_df.copy()
            comparison_display["Month"] = (
                comparison_display["Month"].dt.strftime("%B %Y")
            )
            comparison_display["Absolute Error"] = (
                comparison_display["Actual_Sales"]
                - comparison_display["Predicted_Sales"]
            ).abs()

            st.dataframe(
                comparison_display.round(2),
                use_container_width=True,
                hide_index=True
            )

else:
    st.info(
        "The forecasting section will appear after valid monthly "
        "sales data is loaded."
    )

st.divider()

# --------------------------------------------------
# 7. COUNTRY ANALYTICS
# --------------------------------------------------
st.header("Country Analytics")

if country_df is None:
    st.warning(
        "Country analytics data file is missing: "
        "retailpulse_country_summary.csv"
    )
elif country_df.empty:
    st.info("The country analytics file is empty.")
else:
    country_col = find_column(
        country_df, ["Country", "country"]
    )
    country_sales_col = find_column(
        country_df, ["Total_Sales", "Sales", "Revenue"]
    )

    if country_col is None or country_sales_col is None:
        st.error(
            "Country summary needs Country and Total_Sales columns."
        )
    else:
        country_plot = country_df[
            [country_col, country_sales_col]
        ].copy()
        country_plot.columns = ["Country", "Total_Sales"]

        country_plot["Total_Sales"] = pd.to_numeric(
            country_plot["Total_Sales"], errors="coerce"
        )
        country_plot = country_plot.dropna(
            subset=["Country", "Total_Sales"]
        )

        country_plot = (
            country_plot.groupby("Country", as_index=False)
            ["Total_Sales"].sum()
            .sort_values("Total_Sales", ascending=False)
        )

        if country_plot.empty:
            st.info("No valid country sales records were found.")
        else:
            ccol1, ccol2 = st.columns(2)

            ccol1.metric(
                "Countries Analysed",
                f"{country_plot['Country'].nunique():,}"
            )
            ccol2.metric(
                "Top Country",
                str(country_plot.iloc[0]["Country"])
            )

            country_top_n = st.slider(
                "Number of countries to display",
                min_value=5,
                max_value=min(20, len(country_plot)),
                value=min(10, len(country_plot)),
                key="country_top_n"
            )

            top_countries = country_plot.head(country_top_n)

            country_fig = go.Figure(go.Bar(
                x=top_countries["Total_Sales"],
                y=top_countries["Country"],
                orientation="h",
                marker_color="#2563eb",
                hovertemplate=(
                    "Country: %{y}<br>"
                    "Sales: %{x:,.2f}<extra></extra>"
                )
            ))

            country_fig.update_layout(
                title=f"Top {country_top_n} Countries by Recorded Sales",
                xaxis_title="Sales",
                yaxis_title="Country",
                yaxis=dict(autorange="reversed"),
                template="plotly_white",
                height=max(400, country_top_n * 32)
            )

            st.plotly_chart(
                country_fig,
                use_container_width=True,
                key="country_sales_chart"
            )

            st.subheader("Country Sales Details")
            st.dataframe(
                country_plot.round(2),
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Download Country Summary",
                data=country_plot.to_csv(index=False).encode("utf-8"),
                file_name="retailpulse_country_analysis.csv",
                mime="text/csv"
            )

st.divider()

# --------------------------------------------------
# 8. PRODUCT ANALYTICS
# --------------------------------------------------
st.header("Product Analytics")

if product_df is None:
    st.warning(
        "Product analytics data file is missing: "
        "retailpulse_product_summary.csv"
    )
elif product_df.empty:
    st.info("The product analytics file is empty.")
else:
    product_name_col = find_column(
        product_df, ["Description", "Product", "Product_Name", "Item"]
    )
    product_sales_col = find_column(
        product_df, ["Total_Sales", "Sales", "Revenue"]
    )

    if product_name_col is None or product_sales_col is None:
        st.error(
            "Product summary needs a product name column such as "
            "Description and a sales column such as Total_Sales."
        )
    else:
        product_plot = product_df[
            [product_name_col, product_sales_col]
        ].copy()
        product_plot.columns = ["Product", "Total_Sales"]

        product_plot["Total_Sales"] = pd.to_numeric(
            product_plot["Total_Sales"], errors="coerce"
        )
        product_plot = product_plot.dropna(
            subset=["Product", "Total_Sales"]
        )

        product_plot["Product"] = (
            product_plot["Product"].astype(str)
        )

        product_plot = (
            product_plot.groupby("Product", as_index=False)
            ["Total_Sales"].sum()
            .sort_values("Total_Sales", ascending=False)
        )

        if product_plot.empty:
            st.info("No valid product sales records were found.")
        else:
            pcol1, pcol2 = st.columns(2)

            pcol1.metric(
                "Products Analysed",
                f"{product_plot['Product'].nunique():,}"
            )
            pcol2.metric(
                "Top Product Sales",
                format_sales(product_plot.iloc[0]["Total_Sales"])
            )

            product_top_n = st.slider(
                "Number of products to display",
                min_value=5,
                max_value=min(20, len(product_plot)),
                value=min(10, len(product_plot)),
                key="product_top_n"
            )

            top_products = product_plot.head(product_top_n)

            product_fig = go.Figure(go.Bar(
                x=top_products["Total_Sales"],
                y=top_products["Product"],
                orientation="h",
                marker_color="#7c3aed",
                hovertemplate=(
                    "Product: %{y}<br>"
                    "Sales: %{x:,.2f}<extra></extra>"
                )
            ))

            product_fig.update_layout(
                title=f"Top {product_top_n} Products by Recorded Sales",
                xaxis_title="Sales",
                yaxis_title="Product",
                yaxis=dict(autorange="reversed"),
                template="plotly_white",
                height=max(420, product_top_n * 38)
            )

            st.plotly_chart(
                product_fig,
                use_container_width=True,
                key="product_sales_chart"
            )

            st.subheader("Product Sales Details")
            st.dataframe(
                product_plot.round(2),
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Download Product Summary",
                data=product_plot.to_csv(index=False).encode("utf-8"),
                file_name="retailpulse_product_analysis.csv",
                mime="text/csv"
            )

st.divider()

# --------------------------------------------------
# 9. CUSTOMER ANALYTICS
# --------------------------------------------------
st.header("Customer Analytics")

if customer_df is None:
    st.warning(
        "Customer analytics data file is missing: "
        "retailpulse_customer_summary.csv"
    )
elif customer_df.empty:
    st.info("The customer analytics file is empty.")
else:
    customer_id_col = find_column(
        customer_df, ["Customer ID", "Customer_ID", "CustomerID"]
    )
    customer_sales_col = find_column(
        customer_df, ["Total_Sales", "total_sales", "Sales", "Revenue"]
    )
    customer_quantity_col = find_column(
        customer_df,
        ["Total_Quantity", "total_quantity", "Quantity", "TotalQuantity"]
    )

    if customer_id_col is None or customer_sales_col is None:
        st.error(
            "Customer summary needs a customer ID column and a sales "
            "column, for example Customer ID and total_sales."
        )
    else:
        customer_plot = customer_df.copy()

        customer_plot[customer_sales_col] = pd.to_numeric(
            customer_plot[customer_sales_col], errors="coerce"
        )

        if customer_quantity_col is not None:
            customer_plot[customer_quantity_col] = pd.to_numeric(
                customer_plot[customer_quantity_col],
                errors="coerce"
            )

        customer_plot = customer_plot.dropna(
            subset=[customer_id_col, customer_sales_col]
        )

        customer_plot = (
            customer_plot.sort_values(
                customer_sales_col, ascending=False
            )
            .drop_duplicates(subset=[customer_id_col])
        )

        if customer_plot.empty:
            st.info("No valid customer records were found.")
        else:
            customer_total_sales = customer_plot[
                customer_sales_col
            ].sum()
            average_customer_sales = customer_plot[
                customer_sales_col
            ].mean()

            cust_col1, cust_col2, cust_col3 = st.columns(3)

            cust_col1.metric(
                "Identified Customers",
                f"{customer_plot[customer_id_col].nunique():,}"
            )
            cust_col2.metric(
                "Average Sales per Customer",
                format_sales(average_customer_sales)
            )
            cust_col3.metric(
                "Total Customer Sales",
                format_sales(customer_total_sales)
            )

            st.subheader("Top Customers")

            customer_top_n = st.slider(
                "Number of customers to display",
                min_value=5,
                max_value=min(20, len(customer_plot)),
                value=min(10, len(customer_plot)),
                key="customer_top_n"
            )

            top_customers = customer_plot.head(customer_top_n)

            customer_fig = go.Figure(go.Bar(
                x=top_customers[customer_id_col].astype(str),
                y=top_customers[customer_sales_col],
                marker_color="#0891b2",
                hovertemplate=(
                    "Customer ID: %{x}<br>"
                    "Sales: %{y:,.2f}<extra></extra>"
                )
            ))

            customer_fig.update_layout(
                title=f"Top {customer_top_n} Customers by Sales",
                xaxis_title="Customer ID",
                yaxis_title="Recorded Sales",
                template="plotly_white",
                height=430
            )

            st.plotly_chart(
                customer_fig,
                use_container_width=True,
                key="customer_sales_chart"
            )

            # Customer selector.
            customer_ids = customer_plot[
                customer_id_col
            ].astype(str).tolist()

            selected_customer = st.selectbox(
                "Select a customer to inspect",
                options=customer_ids,
                key="selected_customer"
                )

            selected_row = customer_plot[
                customer_plot[customer_id_col].astype(str)
                == selected_customer
            ].iloc[0]

            st.subheader("Selected Customer Details")

            detail_col1, detail_col2 = st.columns(2)

            detail_col1.metric(
                "Customer ID",
                selected_customer
            )
            detail_col2.metric(
                "Recorded Sales",
                format_sales(selected_row[customer_sales_col])
            )

            if customer_quantity_col is not None:
                quantity_value = selected_row[
                    customer_quantity_col
                ]

                st.metric(
                    "Recorded Quantity",
                    (
                        f"{quantity_value:,.0f}"
                        if pd.notna(quantity_value)
                        else "N/A"
                    )
                )

            st.subheader("Customer Summary Table")
            st.dataframe(
                customer_plot.head(100).round(2),
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Download Customer Summary",
                data=customer_plot.to_csv(index=False).encode("utf-8"),
                file_name="retailpulse_customer_analysis.csv",
                mime="text/csv"
            )

st.divider()

# --------------------------------------------------
# 10. PROJECT NOTES
# --------------------------------------------------
with st.expander("About this dashboard and its data"):
    st.write(
        """
        **RetailPulse** is a retail sales and customer analytics project
        using the Online Retail II dataset.

        - Monthly sales are used for historical trend analysis.
        - The forecast is a simple linear-trend baseline.
        - MAE and MAPE evaluate the baseline against a held-out period.
        - Country and product summaries support sales comparisons.
        - Customer summaries support customer-level sales analysis.

        Forecasts and historical error measures are exploratory and
        should not be interpreted as guaranteed future results.
        """
    )

st.caption("RetailPulse | Retail Sales & Customer Analytics")

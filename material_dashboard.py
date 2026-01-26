import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuration ---
st.set_page_config(
    page_title="Global Construction Materials Dashboard", page_icon="🏗️", layout="wide"
)

# --- Constants ---
DATA_FILE = "data/material_prices.csv"

# ISO-3 Code Mapping
COUNTRY_MAPPING = {
    "Bolivia": "BOL",
    "Santa Cruz": "BOL",  # Asumiendo Santa Cruz como parte de Bolivia data
    "Brasil": "BRA",
    "Brazil": "BRA",
    "Argentina": "ARG",
    "Chile": "CHL",
    "Peru": "PER",
    "China": "CHN",
    "USA": "USA",
    "United States": "USA",
    "Paraguay": "PRY",
    "Russia": "RUS",
    "Rusia": "RUS",  # Added Spanish variant
    "India": "IND",
    "Europe": "EUR",  # No es un país ISO, pero se puede manejar o ignorar
    "Global": "GLO",  # Código custom para Global
}

# Approximate Exchange Rates to USD (Jan 2026 Reference)
EXCHANGE_RATES = {
    "USD": 1.0,
    "BOB": 0.14,  # 1 BOB = ~0.14 USD (approx 6.96)
    "CNY": 0.14,  # 1 CNY = ~0.14 USD
    "BRL": 0.17,  # 1 BRL = ~0.17 USD
    "ARS": 0.0008,  # Highly volatile
    "RUB": 0.011,
    "INR": 0.012,
    "EUR": 1.08,
}


# --- Helper Functions ---
@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        st.error(
            f"Data file not found at {DATA_FILE}. Please run raw scraping script first."
        )
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)

    # Ensure price is numeric
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df.dropna(subset=["price"])

    # Add Country ID (ISO-3)
    if "country" in df.columns:
        df["country_id"] = df["country"].map(COUNTRY_MAPPING).fillna("UNK")

    return df


def convert_to_usd(row):
    rate = EXCHANGE_RATES.get(
        row["currency"], 1.0
    )  # Default to 1.0 if not found (assume USD or error)
    if row["currency"] not in EXCHANGE_RATES and row["currency"] != "USD":
        # Fallback for unknown currencies, assuming they might already be USD-ish or alert user
        pass
    return row["price"] * rate


# --- Main App ---
def main():
    st.title("🏗️ Construction Material Prices Tracker")
    st.markdown("### Global Overview & Analysis")

    # 1. Load Data
    df = load_data()
    if df.empty:
        return

    # Add USD Normalized Price
    df["price_usd"] = df.apply(convert_to_usd, axis=1)

    # 2. Sidebar Filters
    st.sidebar.header("Filters")

    # Material Filter
    available_materials = df["material"].unique()
    selected_material = st.sidebar.selectbox(
        "Select Material", available_materials, index=0
    )

    # Filter Data
    df_filtered = df[df["material"] == selected_material].copy()

    # Country Filter (New)
    available_countries = sorted(df_filtered["country"].unique())
    # Default to all if possible, or let user select
    selected_countries = st.sidebar.multiselect(
        "Select Country", available_countries, default=available_countries
    )

    if selected_countries:
        df_filtered = df_filtered[df_filtered["country"].isin(selected_countries)]

    if df_filtered.empty:
        st.warning("No data available for the selected filters.")
        return

    # 3. KPIs
    avg_price = df_filtered["price_usd"].mean()
    min_price_row = df_filtered.loc[df_filtered["price_usd"].idxmin()]
    max_price_row = df_filtered.loc[df_filtered["price_usd"].idxmax()]

    # Unit (Assuming mostly consistent unit for same material, take mode or first)
    unit = df_filtered["unit"].iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Price (Global)", f"${avg_price:,.2f} USD")
    col2.metric(
        "Cheapest Market",
        f"{min_price_row['country']} ({min_price_row['country_id']})",
        f"${min_price_row['price_usd']:,.2f} USD / {unit}",
    )
    col3.metric(
        "Most Expensive Market",
        f"{max_price_row['country']} ({max_price_row['country_id']})",
        f"${max_price_row['price_usd']:,.2f} USD / {unit}",
    )

    st.markdown("---")

    # 4. Visualizations

    # Map
    st.subheader(f"Global Price Distribution: {selected_material}")

    # Use ISO-3 codes for better mapping
    fig_map = px.choropleth(
        df_filtered,
        locations="country_id",
        locationmode="ISO-3",
        color="price_usd",
        hover_name="country",
        hover_data={
            "country_id": True,
            "price": ":,.2f",  # Original Price
            "currency": True,
            "price_usd": ":,.2f",  # USD Price
            "unit": True,
        },
        labels={"price_usd": "Price (USD)"},
        color_continuous_scale=px.colors.sequential.Blues,  # Changed to Blue scale
        title=f"Price Intensity (USD) - {selected_material}",
        projection="natural earth",  # Changed projection type
    )
    fig_map.update_geos(showcountries=True, countrycolor="Black", showcoastlines=True)
    st.plotly_chart(fig_map, use_container_width=True)

    # Bar Chart Comparison
    col_chart, col_table = st.columns([2, 1])

    with col_chart:
        st.subheader("Price Comparison by Country (USD)")
        fig_bar = px.bar(
            df_filtered.sort_values("price_usd"),
            x="country",
            y="price_usd",
            color="country",
            text="country_id",  # Show ID on bars
            title=f"Price per Unit ({unit}) in USD",
            hover_data=["country_id", "price_usd"],
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_table:
        st.subheader("Detailed Data")
        # Format for display
        display_df = df_filtered[
            [
                "country",
                "country_id",
                "price",
                "currency",
                "price_usd",
                "unit",
                "source",
            ]
        ].copy()
        display_df["price_usd"] = display_df["price_usd"].map("${:,.2f}".format)

        st.dataframe(
            display_df,
            hide_index=True,
        )

    # 5. Raw Data Section
    with st.expander("View All Raw Data"):
        st.dataframe(df)


if __name__ == "__main__":
    import sys
    from streamlit.web import cli as stcli

    if st.runtime.exists():
        main()
    else:
        # Auto-relaunch with streamlit
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())

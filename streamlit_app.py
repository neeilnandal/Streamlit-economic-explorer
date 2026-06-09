import math
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
import streamlit as st


# -----------------------------------------------------------------------------
# Page setup

st.set_page_config(
    page_title="GDP Dashboard",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 GDP Dashboard")
st.caption(
    "Explore country-level GDP, GDP per capita, region trends, rankings, "
    "and inflation-adjusted comparisons using World Bank-style economic data."
)


# -----------------------------------------------------------------------------
# Constants

LOCAL_DATA_PATH = Path(__file__).parent / "data" / "gdp_data.csv"

WORLD_BANK_API_BASE = "https://api.worldbank.org/v2"

INDICATORS: Dict[str, str] = {
    "GDP current US$": "NY.GDP.MKTP.CD",
    "GDP per capita current US$": "NY.GDP.PCAP.CD",
    "GDP constant 2015 US$": "NY.GDP.MKTP.KD",
}

DEFAULT_COUNTRIES = ["DEU", "FRA", "GBR", "BRA", "MEX", "JPN"]
DEFAULT_START_YEAR = 1960
DEFAULT_END_YEAR = 2024


# -----------------------------------------------------------------------------
# Helper functions

def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    """Safely divide two values and return None if division is not possible."""
    if numerator is None or denominator is None:
        return None

    if pd.isna(numerator) or pd.isna(denominator):
        return None

    if denominator == 0:
        return None

    return numerator / denominator


def format_billions(value: Optional[float]) -> str:
    """Format large GDP values into billions."""
    if value is None or pd.isna(value):
        return "n/a"

    return f"${value / 1_000_000_000:,.0f}B"


def format_currency(value: Optional[float]) -> str:
    """Format per-capita values."""
    if value is None or pd.isna(value):
        return "n/a"

    return f"${value:,.0f}"


def format_percentage(value: Optional[float]) -> str:
    """Format percentage values."""
    if value is None or pd.isna(value):
        return "n/a"

    return f"{value:,.1f}%"


def get_api_json(url: str, params: Optional[dict] = None):
    """Fetch JSON from World Bank API with basic error handling."""
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.warning(f"World Bank API request failed: {exc}")
        return None


@st.cache_data(show_spinner=False)
def get_country_metadata() -> pd.DataFrame:
    """
    Fetch country metadata from the World Bank API.

    Returns country code, country name, region, and income level.
    Aggregates and non-country entries are filtered out where possible.
    """
    url = f"{WORLD_BANK_API_BASE}/country"
    params = {
        "format": "json",
        "per_page": 400,
    }

    payload = get_api_json(url, params=params)

    if not payload or len(payload) < 2:
        return pd.DataFrame(
            columns=[
                "Country Code",
                "Country Name",
                "Region",
                "Income Level",
            ]
        )

    records = []

    for item in payload[1]:
        country_code = item.get("id")
        country_name = item.get("name")
        region = item.get("region", {}).get("value")
        income_level = item.get("incomeLevel", {}).get("value")

        if not country_code or not country_name:
            continue

        # Filter out aggregates where World Bank marks region as "Aggregates"
        if region == "Aggregates":
            continue

        records.append(
            {
                "Country Code": country_code,
                "Country Name": country_name,
                "Region": region,
                "Income Level": income_level,
            }
        )

    return pd.DataFrame(records)


@st.cache_data(show_spinner=False)
def fetch_world_bank_indicator(indicator_code: str, start_year: int, end_year: int) -> pd.DataFrame:
    """
    Fetch country-level indicator data from the World Bank API.

    The API returns paginated JSON. This function fetches all returned pages.
    """
    all_rows: List[dict] = []
    page = 1
    total_pages = 1

    while page <= total_pages:
        url = f"{WORLD_BANK_API_BASE}/country/all/indicator/{indicator_code}"
        params = {
            "format": "json",
            "per_page": 20000,
            "page": page,
            "date": f"{start_year}:{end_year}",
        }

        payload = get_api_json(url, params=params)

        if not payload or len(payload) < 2:
            break

        metadata = payload[0]
        rows = payload[1]

        total_pages = metadata.get("pages", 1)

        for row in rows:
            country = row.get("country", {})
            all_rows.append(
                {
                    "Country Code": row.get("countryiso3code"),
                    "Country Name": country.get("value"),
                    "Year": int(row.get("date")) if row.get("date") else None,
                    "Value": row.get("value"),
                }
            )

        page += 1

    result = pd.DataFrame(all_rows)

    if result.empty:
        return pd.DataFrame(columns=["Country Code", "Country Name", "Year", "Value"])

    result = result.dropna(subset=["Country Code", "Year"])
    result["Year"] = result["Year"].astype(int)
    result["Value"] = pd.to_numeric(result["Value"], errors="coerce")

    return result


@st.cache_data(show_spinner=False)
def load_local_gdp_data() -> pd.DataFrame:
    """
    Load local GDP data if the CSV exists.

    Expected format:
    Country Code | 1960 | 1961 | ... | 2022
    Optional:
    Country Name
    """
    if not LOCAL_DATA_PATH.exists():
        return pd.DataFrame()

    raw_gdp_df = pd.read_csv(LOCAL_DATA_PATH)

    year_columns = [col for col in raw_gdp_df.columns if col.isdigit()]

    if "Country Code" not in raw_gdp_df.columns or not year_columns:
        return pd.DataFrame()

    id_columns = ["Country Code"]

    if "Country Name" in raw_gdp_df.columns:
        id_columns.append("Country Name")

    gdp_df = raw_gdp_df.melt(
        id_vars=id_columns,
        value_vars=year_columns,
        var_name="Year",
        value_name="GDP current US$",
    )

    gdp_df["Year"] = pd.to_numeric(gdp_df["Year"], errors="coerce")
    gdp_df["GDP current US$"] = pd.to_numeric(gdp_df["GDP current US$"], errors="coerce")
    gdp_df = gdp_df.dropna(subset=["Country Code", "Year"])
    gdp_df["Year"] = gdp_df["Year"].astype(int)

    return gdp_df


@st.cache_data(show_spinner=True)
def build_dataset(data_source: str, start_year: int, end_year: int) -> pd.DataFrame:
    """
    Build the dashboard dataset.

    Supports:
    - World Bank API mode
    - Local CSV fallback mode
    """
    country_meta = get_country_metadata()

    if data_source == "World Bank API":
        gdp_current = fetch_world_bank_indicator(
            INDICATORS["GDP current US$"],
            start_year,
            end_year,
        ).rename(columns={"Value": "GDP current US$"})

        gdp_per_capita = fetch_world_bank_indicator(
            INDICATORS["GDP per capita current US$"],
            start_year,
            end_year,
        ).rename(columns={"Value": "GDP per capita current US$"})

        gdp_constant = fetch_world_bank_indicator(
            INDICATORS["GDP constant 2015 US$"],
            start_year,
            end_year,
        ).rename(columns={"Value": "GDP constant 2015 US$"})

        if gdp_current.empty:
            return pd.DataFrame()

        df = gdp_current.merge(
            gdp_per_capita[["Country Code", "Year", "GDP per capita current US$"]],
            on=["Country Code", "Year"],
            how="left",
        ).merge(
            gdp_constant[["Country Code", "Year", "GDP constant 2015 US$"]],
            on=["Country Code", "Year"],
            how="left",
        )

    else:
        df = load_local_gdp_data()

        if df.empty:
            return pd.DataFrame()

        # Local CSV only guarantees GDP current US$.
        df["GDP per capita current US$"] = pd.NA
        df["GDP constant 2015 US$"] = pd.NA

    if not country_meta.empty:
        df = df.merge(
            country_meta,
            on="Country Code",
            how="left",
            suffixes=("", "_metadata"),
        )

        if "Country Name_metadata" in df.columns:
            df["Country Name"] = df["Country Name"].fillna(df["Country Name_metadata"])
            df = df.drop(columns=["Country Name_metadata"])

    df["Country Label"] = df.apply(
        lambda row: (
            f"{row['Country Name']} ({row['Country Code']})"
            if pd.notna(row.get("Country Name"))
            else row["Country Code"]
        ),
        axis=1,
    )

    return df


def get_latest_available_year(df: pd.DataFrame, value_column: str) -> Optional[int]:
    """Return the latest year with at least one non-null value."""
    valid = df.dropna(subset=[value_column])

    if valid.empty:
        return None

    return int(valid["Year"].max())


# -----------------------------------------------------------------------------
# Sidebar controls

st.sidebar.header("Dashboard Controls")

data_source = st.sidebar.radio(
    "Data source",
    options=["World Bank API", "Local CSV"],
    index=0,
    help="Use the World Bank API for richer features. Local CSV mode only supports GDP current US$ unless extra columns are added.",
)

year_range = st.sidebar.slider(
    "Select year range",
    min_value=1960,
    max_value=2024,
    value=(DEFAULT_START_YEAR, DEFAULT_END_YEAR),
)

from_year, to_year = year_range

with st.spinner("Loading economic data..."):
    gdp_df = build_dataset(data_source, from_year, to_year)

if gdp_df.empty:
    st.error(
        "No GDP data could be loaded. If using Local CSV mode, confirm that "
        "`data/gdp_data.csv` exists and contains a `Country Code` column plus year columns."
    )
    st.stop()


# -----------------------------------------------------------------------------
# Filters

available_regions = sorted(
    [region for region in gdp_df["Region"].dropna().unique()]
) if "Region" in gdp_df.columns else []

region_filter = st.sidebar.multiselect(
    "Region filter",
    options=available_regions,
    default=available_regions,
)

region_filtered_df = gdp_df.copy()

if region_filter and "Region" in region_filtered_df.columns:
    region_filtered_df = region_filtered_df[region_filtered_df["Region"].isin(region_filter)]

country_options = (
    region_filtered_df[["Country Code", "Country Label"]]
    .drop_duplicates()
    .sort_values("Country Label")
)

label_to_code = dict(zip(country_options["Country Label"], country_options["Country Code"]))
code_to_label = dict(zip(country_options["Country Code"], country_options["Country Label"]))

default_labels = [
    code_to_label[code]
    for code in DEFAULT_COUNTRIES
    if code in code_to_label
]

selected_country_labels = st.sidebar.multiselect(
    "Select countries",
    options=country_options["Country Label"].tolist(),
    default=default_labels,
)

selected_country_codes = [label_to_code[label] for label in selected_country_labels]

metric_choice = st.sidebar.selectbox(
    "Primary metric",
    options=[
        "GDP current US$",
        "GDP per capita current US$",
        "GDP constant 2015 US$",
    ],
    index=0,
)

top_n = st.sidebar.slider(
    "Top-N ranking size",
    min_value=5,
    max_value=25,
    value=10,
    step=5,
)

filtered_df = region_filtered_df[
    (region_filtered_df["Country Code"].isin(selected_country_codes))
    & (region_filtered_df["Year"] >= from_year)
    & (region_filtered_df["Year"] <= to_year)
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()


# -----------------------------------------------------------------------------
# Main KPI cards

latest_year = get_latest_available_year(gdp_df, metric_choice)

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.metric("Selected countries", len(selected_country_codes))

with kpi_col2:
    st.metric("Selected regions", len(region_filter) if region_filter else 0)

with kpi_col3:
    st.metric("Year range", f"{from_year}–{to_year}")

with kpi_col4:
    st.metric("Latest available year", latest_year if latest_year else "n/a")


# -----------------------------------------------------------------------------
# GDP over time

st.header("GDP over time", divider="gray")

st.line_chart(
    filtered_df,
    x="Year",
    y=metric_choice,
    color="Country Label",
)

with st.expander("View filtered dataset"):
    st.dataframe(filtered_df, use_container_width=True)

    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download filtered CSV",
        data=csv_bytes,
        file_name="filtered_gdp_data.csv",
        mime="text/csv",
    )


# -----------------------------------------------------------------------------
# Country metric cards

st.header(f"Country snapshot in {to_year}", divider="gray")

snapshot_df = filtered_df[filtered_df["Year"] == to_year].copy()

if snapshot_df.empty:
    st.info(f"No country snapshot data available for {to_year}.")
else:
    cols = st.columns(3)

    for i, country_code in enumerate(selected_country_codes):
        country_data = filtered_df[filtered_df["Country Code"] == country_code]
        country_label = code_to_label.get(country_code, country_code)

        start_row = country_data[country_data["Year"] == from_year]
        end_row = country_data[country_data["Year"] == to_year]

        if start_row.empty or end_row.empty:
            continue

        start_value = start_row[metric_choice].iloc[0]
        end_value = end_row[metric_choice].iloc[0]

        growth_multiple = safe_divide(end_value, start_value)

        if growth_multiple is None:
            growth_label = "n/a"
            delta_color = "off"
        else:
            percentage_growth = (growth_multiple - 1) * 100
            growth_label = f"{percentage_growth:,.1f}%"
            delta_color = "normal"

        if metric_choice == "GDP per capita current US$":
            metric_value = format_currency(end_value)
        else:
            metric_value = format_billions(end_value)

        with cols[i % 3]:
            st.metric(
                label=country_label,
                value=metric_value,
                delta=growth_label,
                delta_color=delta_color,
                help=f"Percentage growth from {from_year} to {to_year}.",
            )


# -----------------------------------------------------------------------------
# GDP per capita comparison

st.header("GDP per capita comparison", divider="gray")

per_capita_df = filtered_df.dropna(subset=["GDP per capita current US$"])

if per_capita_df.empty:
    st.info("GDP per capita data is not available for the selected source or filters.")
else:
    st.line_chart(
        per_capita_df,
        x="Year",
        y="GDP per capita current US$",
        color="Country Label",
    )


# -----------------------------------------------------------------------------
# Inflation-adjusted comparison

st.header("Inflation-adjusted GDP comparison", divider="gray")

constant_gdp_df = filtered_df.dropna(subset=["GDP constant 2015 US$"])

if constant_gdp_df.empty:
    st.info("Inflation-adjusted GDP data is not available for the selected source or filters.")
else:
    st.line_chart(
        constant_gdp_df,
        x="Year",
        y="GDP constant 2015 US$",
        color="Country Label",
    )

    st.caption(
        "This chart uses constant 2015 US$ GDP where available, which helps compare output "
        "over time after adjusting for price-level changes."
    )


# -----------------------------------------------------------------------------
# Region-level comparison

st.header("Region-level comparison", divider="gray")

if "Region" not in gdp_df.columns or gdp_df["Region"].dropna().empty:
    st.info("Region metadata is not available.")
else:
    region_metric_df = (
        region_filtered_df
        .dropna(subset=[metric_choice])
        .groupby(["Region", "Year"], as_index=False)[metric_choice]
        .sum()
    )

    region_metric_df = region_metric_df[
        (region_metric_df["Year"] >= from_year)
        & (region_metric_df["Year"] <= to_year)
    ]

    if region_metric_df.empty:
        st.info("No region-level data available for the selected filters.")
    else:
        st.line_chart(
            region_metric_df,
            x="Year",
            y=metric_choice,
            color="Region",
        )


# -----------------------------------------------------------------------------
# Top-N GDP rankings

st.header(f"Top {top_n} country rankings in {to_year}", divider="gray")

ranking_df = (
    region_filtered_df[
        (region_filtered_df["Year"] == to_year)
        & region_filtered_df[metric_choice].notna()
    ]
    .sort_values(metric_choice, ascending=False)
    .head(top_n)
    .copy()
)

if ranking_df.empty:
    st.info(f"No ranking data available for {to_year}.")
else:
    ranking_display_df = ranking_df[
        [
            "Country Name",
            "Country Code",
            "Region",
            "GDP current US$",
            "GDP per capita current US$",
            "GDP constant 2015 US$",
        ]
    ].copy()

    ranking_display_df.insert(0, "Rank", range(1, len(ranking_display_df) + 1))

    st.dataframe(
        ranking_display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        ranking_df,
        x="Country Label",
        y=metric_choice,
    )


# -----------------------------------------------------------------------------
# Percentage growth table

st.header(f"Percentage growth from {from_year} to {to_year}", divider="gray")

growth_rows = []

for country_code in selected_country_codes:
    country_data = filtered_df[filtered_df["Country Code"] == country_code]
    country_label = code_to_label.get(country_code, country_code)

    start_row = country_data[country_data["Year"] == from_year]
    end_row = country_data[country_data["Year"] == to_year]

    if start_row.empty or end_row.empty:
        continue

    start_value = start_row[metric_choice].iloc[0]
    end_value = end_row[metric_choice].iloc[0]

    growth_multiple = safe_divide(end_value, start_value)

    if growth_multiple is None:
        percentage_growth = None
    else:
        percentage_growth = (growth_multiple - 1) * 100

    growth_rows.append(
        {
            "Country": country_label,
            "Start Year": from_year,
            "End Year": to_year,
            "Start Value": start_value,
            "End Value": end_value,
            "Percentage Growth": percentage_growth,
        }
    )

growth_df = pd.DataFrame(growth_rows)

if growth_df.empty:
    st.info("Growth table is not available for the selected filters.")
else:
    st.dataframe(
        growth_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Start Value": st.column_config.NumberColumn(format="$%.0f"),
            "End Value": st.column_config.NumberColumn(format="$%.0f"),
            "Percentage Growth": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )



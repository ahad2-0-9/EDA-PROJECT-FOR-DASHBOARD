"""
Filters module for the Food Price Dashboard
Handles all data filtering operations
"""

import pandas as pd
import streamlit as st
from datetime import datetime


def apply_filters(df):
    """
    Apply all filters to the dataframe and return filtered data.
    Uses Streamlit session state to maintain filter values.
    """
    filtered_df = df.copy()

    # Price Type Filter
    if st.session_state.get("selected_price_type") and st.session_state["selected_price_type"] != "All":
        filtered_df = filtered_df[filtered_df["pricetype"] == st.session_state["selected_price_type"]]

    # Date Range Filter
    if st.session_state.get("date_range"):
        start_date, end_date = st.session_state["date_range"]
        # Convert to datetime if needed
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        filtered_df = filtered_df[
            (filtered_df["date"] >= start_date) & (filtered_df["date"] <= end_date)
        ]

    # Country Filter
    if st.session_state.get("selected_countries") and "All" not in st.session_state["selected_countries"]:
        filtered_df = filtered_df[filtered_df["countryiso3"].isin(st.session_state["selected_countries"])]

    # Category Filter
    if st.session_state.get("selected_categories") and "All" not in st.session_state["selected_categories"]:
        filtered_df = filtered_df[filtered_df["category"].isin(st.session_state["selected_categories"])]

    # Commodity Filter
    if st.session_state.get("selected_commodities") and "All" not in st.session_state["selected_commodities"]:
        filtered_df = filtered_df[filtered_df["commodity"].isin(st.session_state["selected_commodities"])]

    # Price Range Filter
    if st.session_state.get("price_range"):
        min_price, max_price = st.session_state["price_range"]
        filtered_df = filtered_df[(filtered_df["price"] >= min_price) & (filtered_df["price"] <= max_price)]

    # Market Search Filter
    if st.session_state.get("market_search") and st.session_state["market_search"].strip():
        search_term = st.session_state["market_search"].strip().lower()
        filtered_df = filtered_df[
            filtered_df["market"].str.lower().str.contains(search_term, na=False)
        ]

    return filtered_df


def reset_filters():
    """Reset all filters to default values"""
    st.session_state["date_range"] = None
    st.session_state["selected_countries"] = ["All"]
    st.session_state["selected_categories"] = ["All"]
    st.session_state["selected_commodities"] = ["All"]
    st.session_state["price_range"] = None
    st.session_state["market_search"] = ""


def initialize_session_state(df):
    """Initialize session state variables if not already initialized"""
    if "price_type" not in st.session_state:
        st.session_state["selected_price_type"] = "All"

    if "date_range" not in st.session_state:
        min_date = pd.to_datetime(df["date"]).min()
        max_date = pd.to_datetime(df["date"]).max()
        st.session_state["date_range"] = (min_date, max_date)

    if "selected_countries" not in st.session_state:
        st.session_state["selected_countries"] = ["All"]

    if "selected_categories" not in st.session_state:
        st.session_state["selected_categories"] = ["All"]

    if "selected_commodities" not in st.session_state:
        st.session_state["selected_commodities"] = ["All"]

    if "price_range" not in st.session_state:
        min_price = df["price"].min()
        max_price = df["price"].max()
        st.session_state["price_range"] = (min_price, max_price)

    if "market_search" not in st.session_state:
        st.session_state["market_search"] = ""


def render_filters(df):
    """
    Render all filter controls in the sidebar.
    Returns the filtered dataframe.
    """
    st.sidebar.header("Filters")

    # Initialize session state
    initialize_session_state(df)

    # Price Type Filter (NEW)
    st.sidebar.subheader("Price Type")
    price_types = ["All", "Retail", "Wholesale"]
    selected_price_type = st.sidebar.selectbox(
        "Select price type:",
        price_types,
        index=0,
        key="price_type_select",
    )
    st.session_state["selected_price_type"] = selected_price_type

    # Date Range Filter
    st.sidebar.subheader("Date Range")
    min_date = pd.to_datetime(df["date"]).min()
    max_date = pd.to_datetime(df["date"]).max()
    date_range = st.sidebar.date_input(
        "Select date range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_input",
    )
    if len(date_range) == 2:
        st.session_state["date_range"] = date_range

    # Country Filter
    st.sidebar.subheader("Country")
    countries = ["All"] + sorted(df["countryiso3"].unique().tolist())
    selected_countries = st.sidebar.multiselect(
        "Select countries:",
        countries,
        default=["All"],
        key="country_select",
    )
    st.session_state["selected_countries"] = selected_countries if selected_countries else ["All"]

    # Category Filter
    st.sidebar.subheader("Category")
    categories = ["All"] + sorted(df["category"].unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "Select categories:",
        categories,
        default=["All"],
        key="category_select",
    )
    st.session_state["selected_categories"] = selected_categories if selected_categories else ["All"]

    # Commodity Filter
    st.sidebar.subheader("Commodity")
    commodities = ["All"] + sorted(df["commodity"].unique().tolist())
    selected_commodities = st.sidebar.multiselect(
        "Select commodities:",
        commodities,
        default=["All"],
        key="commodity_select",
    )
    st.session_state["selected_commodities"] = selected_commodities if selected_commodities else ["All"]

    # Price Range Filter
    st.sidebar.subheader("Price Range (USD)")
    min_price = df["price"].min()
    max_price = df["price"].max()
    price_range = st.sidebar.slider(
        "Select price range:",
        min_value=float(min_price),
        max_value=float(max_price),
        value=(float(min_price), float(max_price)),
        key="price_slider",
    )
    st.session_state["price_range"] = price_range

    # Market Search Filter
    st.sidebar.subheader("Search Market")
    market_search = st.sidebar.text_input(
        "Search by market name:",
        value="",
        key="market_search_input",
    )
    st.session_state["market_search"] = market_search

    # Reset Filters Button
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Reset Filters", use_container_width=True):
            reset_filters()
            st.rerun()

    with col2:
        if st.button("Info", use_container_width=True):
            st.sidebar.info(
                "Tips:\n"
                "- Use 'All' to select all items\n"
                "- Filters are applied in real-time\n"
                "- Charts update automatically"
            )

    # Apply filters and return
    return apply_filters(df)

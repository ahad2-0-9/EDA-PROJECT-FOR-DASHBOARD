"""
Food Price Dashboard - Interactive Streamlit Application
Analyzes global food prices data with multiple visualizations and filters
"""

import streamlit as st
import pandas as pd
import numpy as np
from filters import render_filters
from charts import (
    pie_chart_distribution,
    histogram_price_distribution,
    line_chart_trends,
    bar_chart_comparison,
    scatter_plot_relationship,
    box_plot_spread,
    heatmap_correlation,
    area_chart_cumulative,
    count_plot_frequency,
    violin_plot_distribution,
    bonus_pair_plot,
    bonus_bubble_chart,
    bonus_retail_vs_wholesale,
    world_map_prices,
    market_map,
    get_kpi_metrics,
)


# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WFP Global Food Price Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Top banner */
    .main-header {
        font-size: 2.4em;
        font-weight: 800;
        background: linear-gradient(90deg, #1f77b4 0%, #2ecc71 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.05em;
        color: #666;
        text-align: center;
        margin-bottom: 24px;
    }
    /* Section headings */
    .section-header {
        font-size: 1.25em;
        font-weight: 700;
        color: #1f77b4;
        margin-top: 18px;
        margin-bottom: 12px;
        border-left: 4px solid #1f77b4;
        padding-left: 10px;
    }
    /* Insight boxes */
    .insight-box {
        background: #f0f6ff;
        border-left: 4px solid #1f77b4;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 8px;
        font-size: 0.95em;
        color: #333;
    }
    /* Reduce sidebar padding */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    """Load and minimally clean the WFP dataset."""
    df = pd.read_csv("data/wfp_food_prices_global_2026.csv")
    df["date"] = pd.to_datetime(df["date"])
    # Resolve country ISO-3 → full names (cached once)
    try:
        import pycountry
        iso_to_name = {
            c.alpha_3: c.name for c in pycountry.countries
        }
        df["country_name"] = df["countryiso3"].map(iso_to_name).fillna(df["countryiso3"])
    except Exception:
        df["country_name"] = df["countryiso3"]
    return df


def _generate_insights(df):
    """Return a list of plain-text insight strings about the filtered data."""
    if len(df) == 0:
        return ["No data available for the selected filters."]

    insights = []

    # Most expensive commodity
    top_comm = df.groupby("commodity")["usdprice"].mean().idxmax()
    top_comm_price = df.groupby("commodity")["usdprice"].mean().max()
    insights.append(
        f"💰 **Most expensive commodity:** {top_comm} (avg ${top_comm_price:.2f} / unit)"
    )

    # Cheapest commodity
    cheap_comm = df.groupby("commodity")["usdprice"].mean().idxmin()
    cheap_comm_price = df.groupby("commodity")["usdprice"].mean().min()
    insights.append(
        f"🏷️ **Most affordable commodity:** {cheap_comm} (avg ${cheap_comm_price:.2f} / unit)"
    )

    # Country with highest avg price
    top_country = df.groupby("country_name")["usdprice"].mean().idxmax()
    top_country_price = df.groupby("country_name")["usdprice"].mean().max()
    insights.append(
        f"🌍 **Highest average prices:** {top_country} (avg ${top_country_price:.2f})"
    )

    # Dominant category
    top_cat = df["category"].value_counts().idxmax()
    top_cat_pct = df["category"].value_counts(normalize=True).max() * 100
    insights.append(
        f"📦 **Most represented category:** {top_cat.title()} ({top_cat_pct:.1f}% of records)"
    )

    # Retail vs wholesale spread
    retail = df[df["pricetype"] == "Retail"]["usdprice"].mean()
    wholesale = df[df["pricetype"] == "Wholesale"]["usdprice"].mean()
    if not np.isnan(retail) and not np.isnan(wholesale) and wholesale > 0:
        markup = (retail - wholesale) / wholesale * 100
        insights.append(
            f"🏪 **Retail vs Wholesale:** Retail prices are on average "
            f"{'higher' if markup >= 0 else 'lower'} by {abs(markup):.1f}%"
        )

    return insights


# ── Main app ──────────────────────────────────────────────────────────────────
def main():
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="main-header">🌾 WFP Global Food Price Dashboard</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Interactive analysis of food prices worldwide · '
        'World Food Programme (WFP) data</div>',
        unsafe_allow_html=True,
    )

    # ── Load & filter data ────────────────────────────────────────────────────
    df_original = load_data()
    df_filtered = render_filters(df_original)

    # Guard – show a friendly message when filters return nothing
    if len(df_filtered) == 0:
        st.warning(
            "⚠️ No records match the current filters. "
            "Please adjust your selections in the sidebar."
        )
        return

    # ── KPI row ───────────────────────────────────────────────────────────────
    metrics = get_kpi_metrics(df_filtered)
    st.markdown(
        '<div class="section-header">Key Performance Indicators</div>',
        unsafe_allow_html=True,
    )
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Records", f"{metrics['total_records']:,}", border=True)
    k2.metric("Avg Price (USD)", f"${metrics['avg_usd_price']:.2f}", border=True)
    k3.metric("Countries", f"{metrics['unique_countries']}", border=True)
    k4.metric("Commodities", f"{metrics['unique_commodities']}", border=True)
    k5.metric("Markets", f"{metrics['unique_markets']}", border=True)

    # ── Quick Insights ────────────────────────────────────────────────────────
    with st.expander("💡 Quick Insights", expanded=True):
        for insight in _generate_insights(df_filtered):
            st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)

    # ── Data download ─────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("**📥 Download Filtered Data**")
        csv = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="wfp_filtered_data.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🗺️ Maps",
        "📊 Overview",
        "📈 Price Trends",
        "📉 Distribution",
        "🔬 Advanced",
        "🛒 Retail vs Wholesale",
    ])

    # ── Tab 1 – Maps ──────────────────────────────────────────────────────────
    with tab1:
        st.markdown(
            '<div class="section-header">Geographic Analysis</div>',
            unsafe_allow_html=True,
        )
        st.subheader("Average Food Price by Country")
        st.plotly_chart(world_map_prices(df_filtered), use_container_width=True)

        st.subheader("Market Locations & Prices")
        st.plotly_chart(market_map(df_filtered), use_container_width=True)

    # ── Tab 2 – Overview ──────────────────────────────────────────────────────
    with tab2:
        st.markdown(
            '<div class="section-header">Overview Charts</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Food Category Distribution")
            st.plotly_chart(
                pie_chart_distribution(df_filtered, "category"),
                use_container_width=True,
            )
        with c2:
            st.subheader("Top 15 Commodities by Frequency")
            st.plotly_chart(
                count_plot_frequency(df_filtered, "commodity", top_n=15),
                use_container_width=True,
            )

    # ── Tab 3 – Price Trends ──────────────────────────────────────────────────
    with tab3:
        st.markdown(
            '<div class="section-header">Price Analysis</div>',
            unsafe_allow_html=True,
        )
        st.subheader("Price Trends Over Time")
        st.plotly_chart(
            line_chart_trends(df_filtered, x="date", y="usdprice", hue="commodity"),
            use_container_width=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Average Price by Country (Top 20)")
            st.plotly_chart(
                bar_chart_comparison(
                    df_filtered, x="countryiso3", y="usdprice", aggregation="mean"
                ),
                use_container_width=True,
            )
        with c2:
            st.subheader("Price Distribution (USD)")
            st.plotly_chart(
                histogram_price_distribution(df_filtered, column="usdprice", bins=50),
                use_container_width=True,
            )

    # ── Tab 4 – Distribution ──────────────────────────────────────────────────
    with tab4:
        st.markdown(
            '<div class="section-header">Distribution & Relationship Analysis</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Local Price vs USD Price")
            st.plotly_chart(
                scatter_plot_relationship(df_filtered),
                use_container_width=True,
            )
        with c2:
            st.subheader("Price Spread by Category")
            st.plotly_chart(
                box_plot_spread(df_filtered, y="usdprice", x="category"),
                use_container_width=True,
            )

        st.subheader("Price Distribution by Commodity (Top 10)")
        top_10 = df_filtered["commodity"].value_counts().head(10).index
        st.plotly_chart(
            box_plot_spread(
                df_filtered[df_filtered["commodity"].isin(top_10)],
                y="usdprice",
                x="commodity",
            ),
            use_container_width=True,
        )

    # ── Tab 5 – Advanced ──────────────────────────────────────────────────────
    with tab5:
        st.markdown(
            '<div class="section-header">Advanced Analytics</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Cumulative Price Trends")
            st.plotly_chart(area_chart_cumulative(df_filtered), use_container_width=True)
        with c2:
            st.subheader("Price Distribution – Violin")
            top_5_cats = df_filtered["category"].value_counts().head(5).index
            st.plotly_chart(
                violin_plot_distribution(
                    df_filtered[df_filtered["category"].isin(top_5_cats)],
                    y="usdprice",
                    x="category",
                ),
                use_container_width=True,
            )

        st.subheader("Correlation Matrix")
        st.plotly_chart(heatmap_correlation(df_filtered), use_container_width=True)

        st.markdown("---")
        st.markdown(
            '<div class="section-header">Bonus Visualizations</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader("Bubble Chart – Commodity Prices by Category")
            st.plotly_chart(bonus_bubble_chart(df_filtered), use_container_width=True)
        with c2:
            st.info(
                "**How to read:**\n\n"
                "- Bubble **size** = number of records\n"
                "- **Colour** = commodity\n"
                "- **X-axis** = food category\n"
                "- **Y-axis** = average price (USD)\n\n"
                "Hover over any bubble for details."
            )

    # ── Tab 6 – Retail vs Wholesale ───────────────────────────────────────────
    with tab6:
        st.markdown(
            '<div class="section-header">Retail vs Wholesale Analysis</div>',
            unsafe_allow_html=True,
        )
        retail_data = df_filtered[df_filtered["pricetype"] == "Retail"]
        wholesale_data = df_filtered[df_filtered["pricetype"] == "Wholesale"]

        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Retail Records",
            f"{len(retail_data):,}",
            f"{len(retail_data)/len(df_filtered)*100:.1f}% of total",
            border=True,
        )
        c2.metric(
            "Wholesale Records",
            f"{len(wholesale_data):,}",
            f"{len(wholesale_data)/len(df_filtered)*100:.1f}% of total",
            border=True,
        )
        if len(retail_data) > 0 and len(wholesale_data) > 0:
            diff = retail_data["usdprice"].mean() - wholesale_data["usdprice"].mean()
            c3.metric(
                "Price Difference (Retail − Wholesale)",
                f"${diff:.2f}",
                "Retail higher" if diff >= 0 else "Wholesale higher",
                border=True,
            )

        st.markdown("---")
        st.plotly_chart(bonus_retail_vs_wholesale(df_filtered), use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Retail Price Statistics")
            if len(retail_data) > 0:
                st.dataframe(
                    retail_data["usdprice"]
                    .describe()
                    .rename("USD Price")
                    .to_frame()
                    .style.format("${:.2f}"),
                    use_container_width=True,
                )
            else:
                st.info("No retail data for selected filters.")
        with c2:
            st.subheader("Wholesale Price Statistics")
            if len(wholesale_data) > 0:
                st.dataframe(
                    wholesale_data["usdprice"]
                    .describe()
                    .rename("USD Price")
                    .to_frame()
                    .style.format("${:.2f}"),
                    use_container_width=True,
                )
            else:
                st.info("No wholesale data for selected filters.")

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center;color:#999;font-size:0.85em;'>"
        f"WFP Global Food Price Dashboard · "
        f"Showing <strong>{len(df_filtered):,}</strong> of "
        f"<strong>{len(df_original):,}</strong> records · "
        f"Data up to {df_original['date'].max().strftime('%B %Y')}"
        f"</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

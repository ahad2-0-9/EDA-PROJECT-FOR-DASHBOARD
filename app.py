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
    get_kpi_metrics
)


# Page configuration
st.set_page_config(
    page_title="Global Food Price Dashboard",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2em;
        color: #555;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px;
    }
    .metric-value {
        font-size: 1.8em;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    .section-header {
        font-size: 1.5em;
        font-weight: bold;
        color: #1f77b4;
        margin-top: 20px;
        margin-bottom: 15px;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load the dataset"""
    df = pd.read_csv("data/wfp_food_prices_global_2026.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


# Main app
def main():
    # Header
    st.markdown('<div class="main-header">Global Food Price Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Comprehensive Analysis of Food Prices Worldwide</div>', unsafe_allow_html=True)
    
    # Load data
    df_original = load_data()
    
    # Apply filters
    df_filtered = render_filters(df_original)
    
    # Get KPI metrics
    metrics = get_kpi_metrics(df_filtered)
    
    # Display KPI Cards
    st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Records",
            f"{metrics['total_records']:,}",
            f"{len(df_filtered):,} filtered",
            border=True
        )
    
    with col2:
        st.metric(
            "Avg Price (USD)",
            f"${metrics['avg_usd_price']:.2f}",
            f"Min: ${metrics['min_price']:.2f}",
            border=True
        )
    
    with col3:
        st.metric(
            "Unique Commodities",
            f"{metrics['unique_commodities']}",
            f"Categories: {metrics['unique_countries']}",
            border=True
        )
    
    with col4:
        st.metric(
            "Markets Covered",
            f"{metrics['unique_markets']}",
            f"Max: ${metrics['max_price']:.2f}",
            border=True
        )
    
    # Create tabs for different chart groups
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Overview", "Price Analysis", "Distribution", "Advanced", "Retail vs Wholesale"]
    )
    
    # Tab 1: Overview Charts
    with tab1:
        st.markdown('<div class="section-header">Overview Charts</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Food Category Distribution")
            fig_pie = pie_chart_distribution(df_filtered, "category")
            st.pyplot(fig_pie)
        
        with col2:
            st.subheader("Top 15 Commodities by Frequency")
            fig_count = count_plot_frequency(df_filtered, "commodity", top_n=15)
            st.pyplot(fig_count)
    
    # Tab 2: Price Analysis
    with tab2:
        st.markdown('<div class="section-header">Price Analysis</div>', unsafe_allow_html=True)
        
        # Price trends
        st.subheader("Price Trends Over Time")
        fig_line = line_chart_trends(df_filtered, x="date", y="usdprice", hue="commodity")
        st.pyplot(fig_line)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Average Price by Country")
            fig_bar = bar_chart_comparison(df_filtered, x="countryiso3", y="usdprice", aggregation="mean")
            st.pyplot(fig_bar)
        
        with col2:
            st.subheader("Price Distribution (Histogram)")
            fig_hist = histogram_price_distribution(df_filtered, column="usdprice", bins=50)
            st.pyplot(fig_hist)
    
    # Tab 3: Distribution Analysis
    with tab3:
        st.markdown('<div class="section-header">Distribution & Relationship Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Price vs USD Price Relationship")
            try:
                fig_scatter = scatter_plot_relationship(df_filtered)
                st.pyplot(fig_scatter)
            except Exception as e:
                st.warning("Unable to display scatter plot. Please try different filters.")
        
        with col2:
            st.subheader("Price Spread by Category")
            fig_box = box_plot_spread(df_filtered, y="usdprice", x="category")
            st.pyplot(fig_box)
        
        # Box plot by commodity
        st.subheader("Price Distribution by Commodity (Top 10)")
        top_commodities = df_filtered["commodity"].value_counts().head(10).index
        df_top_comm = df_filtered[df_filtered["commodity"].isin(top_commodities)]
        fig_box_comm = box_plot_spread(df_top_comm, y="usdprice", x="commodity")
        st.pyplot(fig_box_comm)
    
    # Tab 4: Advanced Analytics
    with tab4:
        st.markdown('<div class="section-header">Advanced Analytics</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Cumulative Price Trends")
            fig_area = area_chart_cumulative(df_filtered)
            st.pyplot(fig_area)
        
        with col2:
            st.subheader("Price Distribution Violin Plot")
            top_5_categories = df_filtered["category"].value_counts().head(5).index
            df_top_cat = df_filtered[df_filtered["category"].isin(top_5_categories)]
            fig_violin = violin_plot_distribution(df_top_cat, y="usdprice", x="category")
            st.pyplot(fig_violin)
        
        # Correlation heatmap
        st.subheader("Correlation Matrix Heatmap")
        fig_heatmap = heatmap_correlation(df_filtered)
        st.pyplot(fig_heatmap)
        
        # Bonus charts
        st.markdown("---")
        st.markdown('<div class="section-header">Bonus Visualizations</div>', unsafe_allow_html=True)
        
        bonus_col1, bonus_col2 = st.columns(2)
        
        with bonus_col1:
            st.subheader("Bubble Chart Analysis")
            try:
                fig_bubble = bonus_bubble_chart(df_filtered)
                st.pyplot(fig_bubble)
            except Exception as e:
                st.warning("Unable to display bubble chart with current filters")
                st.info("Try selecting more data or different commodities")
        
        with bonus_col2:
            st.info(
                "Bubble Chart Info:\n"
                "- Bubble size represents number of records\n"
                "- Color represents commodity type\n"
                "- X-axis shows food category\n"
                "- Y-axis shows average price"
            )
    
    # Tab 5: Retail vs Wholesale Comparison
    with tab5:
        st.markdown('<div class="section-header">Retail vs Wholesale Analysis</div>', unsafe_allow_html=True)
        
        try:
            # Summary stats
            col1, col2, col3 = st.columns(3)
            
            retail_data = df_filtered[df_filtered["pricetype"] == "Retail"]
            wholesale_data = df_filtered[df_filtered["pricetype"] == "Wholesale"]
            
            with col1:
                st.metric(
                    "Retail Records",
                    f"{len(retail_data):,}",
                    f"{len(retail_data)/len(df_filtered)*100:.1f}%" if len(df_filtered) > 0 else "0%",
                    border=True
                )
            
            with col2:
                st.metric(
                    "Wholesale Records",
                    f"{len(wholesale_data):,}",
                    f"{len(wholesale_data)/len(df_filtered)*100:.1f}%" if len(df_filtered) > 0 else "0%",
                    border=True
                )
            
            with col3:
                if len(retail_data) > 0 and len(wholesale_data) > 0:
                    price_diff = retail_data["usdprice"].mean() - wholesale_data["usdprice"].mean()
                    st.metric(
                        "Avg Price Difference (USD)",
                        f"${price_diff:.2f}",
                        f"Retail higher",
                        border=True
                    )
            
            st.markdown("---")
            
            # Retail vs Wholesale comparison
            st.subheader("Price Comparison by Commodity")
            fig_comparison = bonus_retail_vs_wholesale(df_filtered)
            st.pyplot(fig_comparison)
            
            # Retail statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Retail Price Statistics")
                if len(retail_data) > 0:
                    retail_stats = {
                        "Average Price (USD)": f"${retail_data['usdprice'].mean():.2f}",
                        "Min Price": f"${retail_data['usdprice'].min():.2f}",
                        "Max Price": f"${retail_data['usdprice'].max():.2f}",
                        "Std Dev": f"${retail_data['usdprice'].std():.2f}",
                    }
                    for key, value in retail_stats.items():
                        st.write(f"- {key}: {value}")
                else:
                    st.info("No retail data available for selected filters")
            
            with col2:
                st.subheader("Wholesale Price Statistics")
                if len(wholesale_data) > 0:
                    wholesale_stats = {
                        "Average Price (USD)": f"${wholesale_data['usdprice'].mean():.2f}",
                        "Min Price": f"${wholesale_data['usdprice'].min():.2f}",
                        "Max Price": f"${wholesale_data['usdprice'].max():.2f}",
                        "Std Dev": f"${wholesale_data['usdprice'].std():.2f}",
                    }
                    for key, value in wholesale_stats.items():
                        st.write(f"- {key}: {value}")
                else:
                    st.info("No wholesale data available for selected filters")
        except Exception as e:
            st.error(f"Error displaying retail/wholesale analysis: {str(e)}")
            st.info("Try adjusting filters to show more data")
    
    # Footer with data info
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9em;'>
        <p>Dashboard powered by Streamlit | WFP Global Food Price Data</p>
        <p>Showing {0:,} records out of {1:,} total | Last updated: {2}</p>
    </div>
    """.format(len(df_filtered), len(df_original), pd.to_datetime(df_original["date"]).max().strftime("%Y-%m-%d")),
    unsafe_allow_html=True)


if __name__ == "__main__":
    main()

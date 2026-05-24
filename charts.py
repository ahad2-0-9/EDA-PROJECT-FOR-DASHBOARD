"""
Charts module for the Food Price Dashboard
Contains all visualization functions using interactive Plotly charts
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Consistent colour sequence used across all charts
COLORS = px.colors.qualitative.Set2

# Shared layout defaults for a clean, consistent look
_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", size=13),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=40, t=60, b=40),
    legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#ddd", borderwidth=1),
)


def _empty_fig(message="No data available for selected filters"):
    fig = go.Figure()
    fig.add_annotation(
        text=message, x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False, font=dict(size=15, color="#888"),
    )
    fig.update_layout(**_LAYOUT, height=400)
    return fig


# ---------------------------------------------------------------------------
# 1. Pie chart – category / column distribution
# ---------------------------------------------------------------------------
def pie_chart_distribution(df, column="category"):
    """Interactive pie chart showing proportional distribution."""
    if len(df) == 0:
        return _empty_fig()
    distribution = df[column].value_counts().reset_index()
    distribution.columns = [column, "count"]
    fig = px.pie(
        distribution,
        names=column,
        values="count",
        color_discrete_sequence=COLORS,
        hole=0.35,
        title=f"Distribution of {column.replace('_', ' ').title()}",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", pull=0.02)
    fig.update_layout(**_LAYOUT, height=420)
    return fig


# ---------------------------------------------------------------------------
# 2. Histogram – price distribution
# ---------------------------------------------------------------------------
def histogram_price_distribution(df, column="usdprice", bins=50):
    """Interactive histogram for price distribution."""
    if len(df) == 0:
        return _empty_fig()
    fig = px.histogram(
        df,
        x=column,
        nbins=bins,
        color_discrete_sequence=["#3498db"],
        title="Price Distribution (USD)",
        labels={column: "USD Price", "count": "Frequency"},
        opacity=0.80,
    )
    fig.update_traces(marker_line_color="white", marker_line_width=0.5)
    fig.update_layout(**_LAYOUT, height=420,
                      xaxis_title="Price (USD)", yaxis_title="Frequency",
                      bargap=0.05)
    return fig


# ---------------------------------------------------------------------------
# 3. Line chart – price trends over time
# ---------------------------------------------------------------------------
def line_chart_trends(df, x="date", y="usdprice", hue="commodity", max_commodities=8):
    """Interactive multi-line chart of price trends."""
    if len(df) == 0:
        return _empty_fig()

    df_plot = df.copy()
    df_plot[x] = pd.to_datetime(df_plot[x])

    top_items = df_plot[hue].value_counts().head(max_commodities).index
    df_plot = df_plot[df_plot[hue].isin(top_items)]

    if len(df_plot) == 0:
        return _empty_fig()

    df_agg = df_plot.groupby([x, hue])[y].mean().reset_index()

    fig = px.line(
        df_agg,
        x=x,
        y=y,
        color=hue,
        color_discrete_sequence=COLORS,
        markers=True,
        title="Average Price Trends Over Time",
        labels={x: "Date", y: "Avg Price (USD)", hue: "Commodity"},
    )
    fig.update_traces(line_width=2.5, marker_size=5)
    fig.update_layout(**_LAYOUT, height=450,
                      xaxis_title="Date", yaxis_title="Average Price (USD)",
                      hovermode="x unified")
    return fig


# ---------------------------------------------------------------------------
# 4. Bar chart – comparison across categories
# ---------------------------------------------------------------------------
def bar_chart_comparison(df, x="countryiso3", y="usdprice", aggregation="mean"):
    """Interactive horizontal bar chart."""
    if len(df) == 0:
        return _empty_fig()

    if aggregation == "mean":
        data = df.groupby(x)[y].mean().sort_values(ascending=False).head(20).reset_index()
        y_label = "Average Price (USD)"
    elif aggregation == "sum":
        data = df.groupby(x)[y].sum().sort_values(ascending=False).head(20).reset_index()
        y_label = "Total Price (USD)"
    else:
        data = df.groupby(x).size().sort_values(ascending=False).head(20).reset_index()
        data.columns = [x, y]
        y_label = "Count"

    data.columns = [x, y]

    fig = px.bar(
        data.sort_values(y),
        x=y,
        y=x,
        orientation="h",
        color=y,
        color_continuous_scale="Blues",
        title=f"{y_label} by {x.replace('_', ' ').title()} (Top 20)",
        labels={x: x.replace("_", " ").title(), y: y_label},
        text=data.sort_values(y)[y].apply(lambda v: f"${v:.2f}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    fig.update_layout(**_LAYOUT, height=max(400, len(data) * 28),
                      xaxis_title=y_label, yaxis_title="")
    return fig


# ---------------------------------------------------------------------------
# 5. Scatter plot – local price vs USD price
# ---------------------------------------------------------------------------
def scatter_plot_relationship(df, x="price", y="usdprice"):
    """Interactive scatter plot coloured by category."""
    if len(df) == 0:
        return _empty_fig()

    sample = df.sample(min(3000, len(df)), random_state=42) if len(df) > 3000 else df

    fig = px.scatter(
        sample,
        x=x,
        y=y,
        color="category",
        color_discrete_sequence=COLORS,
        opacity=0.6,
        title="Local Price vs USD Price by Category",
        labels={x: "Local Price", y: "USD Price", "category": "Category"},
        hover_data=["commodity", "countryiso3", "market"],
        trendline="ols",
        trendline_scope="overall",
    )
    fig.update_layout(**_LAYOUT, height=450)
    return fig


# ---------------------------------------------------------------------------
# 6. Box plot – price spread
# ---------------------------------------------------------------------------
def box_plot_spread(df, y="usdprice", x="category"):
    """Interactive box plot with outlier hover."""
    if len(df) == 0:
        return _empty_fig()

    fig = px.box(
        df,
        x=x,
        y=y,
        color=x,
        color_discrete_sequence=COLORS,
        notched=False,
        points="outliers",
        title=f"Price Spread by {x.replace('_', ' ').title()}",
        labels={x: x.replace("_", " ").title(), y: "Price (USD)"},
    )
    fig.update_layout(**_LAYOUT, height=450,
                      xaxis_tickangle=-30, showlegend=False)
    return fig


# ---------------------------------------------------------------------------
# 7. Heatmap – correlation matrix
# ---------------------------------------------------------------------------
def heatmap_correlation(df):
    """Interactive correlation heatmap."""
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numerical_cols) < 2:
        return _empty_fig("Not enough numerical columns for a correlation heatmap.")

    corr = df[numerical_cols].corr().round(2)

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation Matrix Heatmap",
        aspect="auto",
    )
    fig.update_layout(**_LAYOUT, height=460)
    return fig


# ---------------------------------------------------------------------------
# 8. Area chart – cumulative price trends
# ---------------------------------------------------------------------------
def area_chart_cumulative(df, date_col="date", value_col="usdprice"):
    """Interactive stacked area chart of top-5 commodities over time."""
    if len(df) == 0:
        return _empty_fig()

    df_plot = df.copy()
    df_plot[date_col] = pd.to_datetime(df_plot[date_col])

    top_5 = df_plot["commodity"].value_counts().head(5).index
    df_plot = df_plot[df_plot["commodity"].isin(top_5)]

    df_agg = df_plot.groupby([date_col, "commodity"])[value_col].mean().reset_index()

    fig = px.area(
        df_agg,
        x=date_col,
        y=value_col,
        color="commodity",
        color_discrete_sequence=COLORS,
        title="Cumulative Price Trends – Top 5 Commodities",
        labels={date_col: "Date", value_col: "Avg Price (USD)", "commodity": "Commodity"},
    )
    fig.update_layout(**_LAYOUT, height=450,
                      xaxis_title="Date", yaxis_title="Average Price (USD)",
                      hovermode="x unified")
    return fig


# ---------------------------------------------------------------------------
# 9. Count / frequency bar chart
# ---------------------------------------------------------------------------
def count_plot_frequency(df, column="commodity", top_n=15):
    """Interactive horizontal bar chart for category counts."""
    if len(df) == 0:
        return _empty_fig()

    data = df[column].value_counts().head(top_n).reset_index()
    data.columns = [column, "count"]

    fig = px.bar(
        data.sort_values("count"),
        x="count",
        y=column,
        orientation="h",
        color="count",
        color_continuous_scale="Blues",
        title=f"Top {top_n} {column.replace('_', ' ').title()} by Frequency",
        labels={column: column.replace("_", " ").title(), "count": "Records"},
        text="count",
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    fig.update_layout(**_LAYOUT, height=max(350, top_n * 30),
                      xaxis_title="Number of Records", yaxis_title="")
    return fig


# ---------------------------------------------------------------------------
# 10. Violin plot – distribution by category
# ---------------------------------------------------------------------------
def violin_plot_distribution(df, y="usdprice", x="category"):
    """Interactive violin plot."""
    if len(df) == 0:
        return _empty_fig()

    fig = px.violin(
        df,
        x=x,
        y=y,
        color=x,
        color_discrete_sequence=COLORS,
        box=True,
        points="outliers",
        title=f"Price Distribution by {x.replace('_', ' ').title()}",
        labels={x: x.replace("_", " ").title(), y: "Price (USD)"},
    )
    fig.update_layout(**_LAYOUT, height=450,
                      xaxis_tickangle=-30, showlegend=False)
    return fig


# ---------------------------------------------------------------------------
# 11. Bonus – bubble chart
# ---------------------------------------------------------------------------
def bonus_bubble_chart(df):
    """Interactive bubble chart: category × avg price, sized by record count."""
    if len(df) == 0:
        return _empty_fig()

    df_agg = df.groupby(["commodity", "category"]).agg(
        avg_price=("usdprice", "mean"),
        count=("usdprice", "count"),
    ).reset_index()

    top_commodities = df_agg.groupby("commodity")["count"].sum().nlargest(12).index
    df_agg = df_agg[df_agg["commodity"].isin(top_commodities)]

    fig = px.scatter(
        df_agg,
        x="category",
        y="avg_price",
        size="count",
        color="commodity",
        color_discrete_sequence=COLORS,
        hover_name="commodity",
        hover_data={"count": True, "avg_price": ":.2f"},
        title="Bubble Chart – Top Commodity Prices by Category\n(Size = Number of Records)",
        labels={"category": "Category", "avg_price": "Avg Price (USD)", "count": "Records"},
        size_max=60,
    )
    fig.update_layout(**_LAYOUT, height=500,
                      xaxis_tickangle=-25,
                      legend_title="Commodity")
    return fig


# ---------------------------------------------------------------------------
# 12. Bonus – pair plot
# ---------------------------------------------------------------------------
def bonus_pair_plot(df, columns=None, max_size=5):
    """Interactive scatter matrix (pair plot)."""
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns[:max_size].tolist()

    sample = df.sample(min(2000, len(df)), random_state=42) if len(df) > 2000 else df

    fig = px.scatter_matrix(
        sample,
        dimensions=columns,
        color="category" if "category" in df.columns else None,
        color_discrete_sequence=COLORS,
        title="Pair Plot – Relationships Between Numeric Variables",
        labels={col: col.replace("_", " ").title() for col in columns},
    )
    fig.update_traces(diagonal_visible=False, marker_size=3, opacity=0.5)
    fig.update_layout(**_LAYOUT, height=700)
    return fig


# ---------------------------------------------------------------------------
# 13. Bonus – retail vs wholesale comparison
# ---------------------------------------------------------------------------
def bonus_retail_vs_wholesale(df):
    """Interactive grouped bar chart comparing Retail vs Wholesale."""
    if "Retail" not in df["pricetype"].values and "Wholesale" not in df["pricetype"].values:
        return _empty_fig("No Retail or Wholesale data for selected filters.")

    df_agg = (
        df.groupby(["commodity", "pricetype"])["usdprice"]
        .mean()
        .reset_index()
    )

    # Keep top 15 commodities by avg retail price (or overall if retail missing)
    top_comm = (
        df_agg.groupby("commodity")["usdprice"]
        .mean()
        .nlargest(15)
        .index
    )
    df_agg = df_agg[df_agg["commodity"].isin(top_comm)]

    fig = px.bar(
        df_agg,
        x="commodity",
        y="usdprice",
        color="pricetype",
        barmode="group",
        color_discrete_map={"Retail": "#3498db", "Wholesale": "#e74c3c"},
        title="Retail vs Wholesale Average Price Comparison (Top 15 Commodities)",
        labels={"commodity": "Commodity", "usdprice": "Avg Price (USD)", "pricetype": "Price Type"},
        text_auto=".2f",
    )
    fig.update_traces(textposition="outside", textfont_size=10)
    fig.update_layout(**_LAYOUT, height=480,
                      xaxis_tickangle=-35,
                      legend_title="Price Type",
                      uniformtext_minsize=8, uniformtext_mode="hide")
    return fig


# ---------------------------------------------------------------------------
# 14. World map – choropleth
# ---------------------------------------------------------------------------
def world_map_prices(df):
    """Choropleth world map showing average USD price per country."""
    if len(df) == 0:
        return _empty_fig("No data available for map.")

    df_country = (
        df.groupby("countryiso3")
        .agg(avg_price=("usdprice", "mean"), records=("usdprice", "count"))
        .reset_index()
    )

    # Resolve full country names using pycountry (graceful fallback)
    try:
        import pycountry
        def _name(iso3):
            c = pycountry.countries.get(alpha_3=iso3)
            return c.name if c else iso3
        df_country["country_name"] = df_country["countryiso3"].apply(_name)
    except Exception:
        df_country["country_name"] = df_country["countryiso3"]

    fig = px.choropleth(
        df_country,
        locations="countryiso3",
        color="avg_price",
        hover_name="country_name",
        hover_data={"avg_price": ":.2f", "records": True, "countryiso3": False},
        color_continuous_scale="YlOrRd",
        title="Average Food Price (USD) by Country",
        labels={"avg_price": "Avg Price (USD)", "records": "Records"},
        projection="natural earth",
    )
    fig.update_layout(
        **_LAYOUT,
        height=520,
        coloraxis_colorbar=dict(title="Avg Price (USD)"),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="lightgrey",
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# 15. Market map – scatter on map
# ---------------------------------------------------------------------------
def market_map(df):
    """Scatter map showing individual market locations coloured by category."""
    if len(df) == 0 or "latitude" not in df.columns:
        return _empty_fig("No geographic data available.")

    df_markets = (
        df.dropna(subset=["latitude", "longitude"])
        .groupby(["market", "countryiso3", "category", "latitude", "longitude"])
        .agg(avg_price=("usdprice", "mean"), records=("usdprice", "count"))
        .reset_index()
    )

    fig = px.scatter_geo(
        df_markets,
        lat="latitude",
        lon="longitude",
        color="category",
        color_discrete_sequence=COLORS,
        hover_name="market",
        hover_data={"avg_price": ":.2f", "records": True,
                    "countryiso3": True, "latitude": False, "longitude": False},
        size="records",
        size_max=18,
        projection="natural earth",
        title="Market Locations & Average Prices",
        labels={"category": "Category", "avg_price": "Avg Price (USD)"},
    )
    fig.update_layout(
        **_LAYOUT,
        height=520,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="lightgrey",
            bgcolor="rgba(0,0,0,0)",
        ),
        legend_title="Food Category",
    )
    return fig


# ---------------------------------------------------------------------------
# KPI helper
# ---------------------------------------------------------------------------
def get_kpi_metrics(df):
    """Calculate KPI metrics for display."""
    if len(df) == 0:
        return {k: 0 for k in [
            "total_records", "avg_price", "min_price", "max_price",
            "avg_usd_price", "unique_commodities", "unique_countries", "unique_markets",
        ]}
    return {
        "total_records": len(df),
        "avg_price": df["price"].mean(),
        "min_price": df["usdprice"].min(),
        "max_price": df["usdprice"].max(),
        "avg_usd_price": df["usdprice"].mean(),
        "unique_commodities": df["commodity"].nunique(),
        "unique_countries": df["countryiso3"].nunique(),
        "unique_markets": df["market"].nunique(),
    }

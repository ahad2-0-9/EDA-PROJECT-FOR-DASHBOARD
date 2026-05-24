"""
Charts module for the Food Price Dashboard
Contains all visualization functions
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

# Set style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# Color palette
COLOR_PALETTE = "Set2"


def pie_chart_distribution(df, column="category"):
    """Pie chart showing proportional distribution of a category"""
    fig, ax = plt.subplots(figsize=(10, 6))
    distribution = df[column].value_counts()
    
    colors = sns.color_palette(COLOR_PALETTE, len(distribution))
    wedges, texts, autotexts = ax.pie(
        distribution.values,
        labels=distribution.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        textprops={"fontsize": 10},
    )
    
    ax.set_title(f"Distribution of {column.capitalize()}", fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    return fig


def histogram_price_distribution(df, column="price", bins=50):
    """Histogram displaying frequency distribution of numerical column"""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(df[column].dropna(), bins=bins, color="#3498db", edgecolor="black", alpha=0.7)
    
    ax.set_xlabel(f"{column.capitalize()}", fontsize=11, fontweight="bold")
    ax.set_ylabel("Frequency", fontsize=11, fontweight="bold")
    ax.set_title(f"Price Distribution Histogram", fontsize=14, fontweight="bold", pad=20)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    return fig


def line_chart_trends(df, x="date", y="price", hue="commodity", max_commodities=8):
    """Line chart showing trends over time"""
    if len(df) == 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=12)
        return fig
    
    df_plot = df.copy()
    df_plot[x] = pd.to_datetime(df_plot[x])
    
    # Limit commodities for clarity
    top_commodities = df_plot[hue].value_counts().head(max_commodities).index
    df_plot = df_plot[df_plot[hue].isin(top_commodities)]
    
    if len(df_plot) == 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No data available for selected filters", ha='center', va='center', fontsize=12)
        return fig
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette(COLOR_PALETTE, len(top_commodities))
    
    for idx, commodity in enumerate(top_commodities):
        df_comm = df_plot[df_plot[hue] == commodity].sort_values(x)
        ax.plot(df_comm[x], df_comm[y], marker='o', label=commodity, 
                color=colors[idx], linewidth=2, markersize=4, alpha=0.7)
    
    ax.set_xlabel("Date", fontsize=11, fontweight="bold")
    ax.set_ylabel("Price (USD)", fontsize=11, fontweight="bold")
    ax.set_title("Price Trends Over Time by Commodity", fontsize=14, fontweight="bold", pad=20)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def bar_chart_comparison(df, x="countryiso3", y="price", aggregation="mean"):
    """Bar chart comparing values across categories"""
    if aggregation == "mean":
        data = df.groupby(x)[y].mean().sort_values(ascending=False).head(15)
    elif aggregation == "sum":
        data = df.groupby(x)[y].sum().sort_values(ascending=False).head(15)
    elif aggregation == "count":
        data = df.groupby(x).size().sort_values(ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette(COLOR_PALETTE, len(data))
    bars = ax.bar(data.index, data.values, color=colors, edgecolor="black", alpha=0.8)
    
    ax.set_xlabel(x.capitalize(), fontsize=11, fontweight="bold")
    ax.set_ylabel(f"{aggregation.capitalize()} {y.capitalize()}", fontsize=11, fontweight="bold")
    ax.set_title(f"Average Price by {x.replace('_', ' ').capitalize()}", fontsize=14, fontweight="bold", pad=20)
    plt.xticks(rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f"{height:.2f}", ha="center", va="bottom", fontsize=9)
    
    plt.tight_layout()
    return fig


def scatter_plot_relationship(df, x="price", y="usdprice"):
    """Scatter plot showing relationship between two numerical variables"""
    if len(df) == 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", transform=ax.transAxes)
        return fig
    
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Get unique categories and assign colors
        categories = df["category"].unique()
        colors = sns.color_palette(COLOR_PALETTE, len(categories))
        color_map = dict(zip(categories, colors))
        
        # Plot scatter for each category
        for category in categories:
            df_cat = df[df["category"] == category]
            ax.scatter(
                df_cat[x],
                df_cat[y],
                label=category,
                alpha=0.6,
                s=50,
                color=color_map[category]
            )
        
        ax.set_xlabel(f"Local Price ({x})", fontsize=11, fontweight="bold")
        ax.set_ylabel("USD Price", fontsize=11, fontweight="bold")
        ax.set_title("Price Relationship: Local vs USD", fontsize=14, fontweight="bold", pad=20)
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=9)
        ax.grid(alpha=0.3)
        plt.tight_layout()
        return fig
    except Exception as e:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, f"Unable to display scatter plot: {str(e)}", ha="center", va="center", transform=ax.transAxes)
        return fig


def box_plot_spread(df, y="price", x="category"):
    """Box plot showing data spread, median, and outliers"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Prepare data
    categories = df[x].unique()
    data_to_plot = [df[df[x] == cat][y].dropna() for cat in categories]
    
    bp = ax.boxplot(data_to_plot, labels=categories, patch_artist=True)
    
    # Color the boxes
    colors = sns.color_palette(COLOR_PALETTE, len(categories))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)
    
    ax.set_xlabel(x.capitalize(), fontsize=11, fontweight="bold")
    ax.set_ylabel(y.capitalize(), fontsize=11, fontweight="bold")
    ax.set_title(f"Price Distribution by {x.capitalize()}", fontsize=14, fontweight="bold", pad=20)
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig


def heatmap_correlation(df):
    """Heatmap visualizing correlation matrix of numerical features"""
    # Select only numerical columns
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    corr_matrix = df[numerical_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        ax=ax,
        cbar_kws={"label": "Correlation"},
    )
    ax.set_title("Correlation Matrix Heatmap", fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    return fig


def area_chart_cumulative(df, date_col="date", value_col="price"):
    """Area chart showing cumulative trends over time"""
    if len(df) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    df_plot = df.copy()
    df_plot[date_col] = pd.to_datetime(df_plot[date_col])
    
    try:
        # Group by date and commodity
        df_agg = df_plot.groupby([date_col, "commodity"])[value_col].mean().reset_index()
        
        if len(df_agg) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No data available for selected filters", showarrow=False)
            return fig
        
        # Create area chart with matplotlib instead
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Get top 5 commodities
        top_commodities = df_agg["commodity"].value_counts().head(5).index
        colors = sns.color_palette(COLOR_PALETTE, len(top_commodities))
        
        for idx, commodity in enumerate(top_commodities):
            df_comm = df_agg[df_agg["commodity"] == commodity].sort_values(date_col)
            ax.fill_between(df_comm[date_col], 0, df_comm[value_col], 
                           label=commodity, color=colors[idx], alpha=0.6)
        
        ax.set_xlabel("Date", fontsize=11, fontweight="bold")
        ax.set_ylabel("Average Price (USD)", fontsize=11, fontweight="bold")
        ax.set_title("Cumulative Price Trends Over Time", fontsize=14, fontweight="bold", pad=20)
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    except Exception as e:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "Unable to display area chart", ha='center', va='center', fontsize=12)
        return fig


def count_plot_frequency(df, column="commodity", top_n=15):
    """Count plot showing frequency count of categorical variables"""
    data = df[column].value_counts().head(top_n)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette(COLOR_PALETTE, len(data))
    bars = ax.barh(range(len(data)), data.values, color=colors, edgecolor="black", alpha=0.8)
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(data.index)
    ax.set_xlabel("Count", fontsize=11, fontweight="bold")
    ax.set_ylabel(column.capitalize(), fontsize=11, fontweight="bold")
    ax.set_title(f"Frequency Count of {column.capitalize()}", fontsize=14, fontweight="bold", pad=20)
    ax.grid(axis="x", alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
                f"{int(width)}", ha="left", va="center", fontsize=9, fontweight="bold")
    
    plt.tight_layout()
    return fig


def violin_plot_distribution(df, y="price", x="category"):
    """Violin plot showing distribution and probability density"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Prepare data
    categories = df[x].unique()
    
    # Create violin plot
    parts = ax.violinplot(
        [df[df[x] == cat][y].dropna() for cat in categories],
        positions=range(len(categories)),
        showmeans=True,
        showmedians=True,
    )
    
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, rotation=45, ha="right")
    ax.set_xlabel(x.capitalize(), fontsize=11, fontweight="bold")
    ax.set_ylabel(y.capitalize(), fontsize=11, fontweight="bold")
    ax.set_title(f"Price Distribution by {x.capitalize()}", fontsize=14, fontweight="bold", pad=20)
    ax.grid(axis="y", alpha=0.3)
    
    plt.tight_layout()
    return fig


def bonus_pair_plot(df, columns=None, max_size=5):
    """Bonus: Pair plot showing relationships between multiple variables"""
    if columns is None:
        # Select numerical columns
        columns = df.select_dtypes(include=[np.number]).columns[:max_size].tolist()
    
    fig = px.scatter_matrix(
        df[columns],
        title="Pair Plot - Relationships Between Variables",
        labels={col: col.capitalize() for col in columns},
        height=800,
    )
    return fig


def bonus_bubble_chart(df):
    """Bonus: Bubble chart with multiple dimensions"""
    if len(df) == 0:
        fig, ax = plt.subplots(figsize=(16, 10))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", transform=ax.transAxes, fontsize=14)
        return fig
    
    try:
        # Prepare aggregated data - focus on top commodities and categories
        df_agg = df.groupby(["commodity", "category"]).agg({
            "price": "mean",
            "usdprice": "mean",
            "market": "count"
        }).reset_index()
        df_agg.rename(columns={"market": "count"}, inplace=True)
        
        # Get top 8 commodities by frequency
        top_commodities = df_agg.groupby("commodity")["count"].sum().nlargest(8).index.tolist()
        df_agg = df_agg[df_agg["commodity"].isin(top_commodities)]
        
        # Get all categories
        categories = sorted(df_agg["category"].unique())
        
        fig, ax = plt.subplots(figsize=(16, 10))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('#f8f9fa')
        
        # Create numeric x positions for categories
        x_positions = {cat: i for i, cat in enumerate(categories)}
        colors = sns.color_palette(COLOR_PALETTE, len(top_commodities))
        color_map = dict(zip(top_commodities, colors))
        
        # Plot bubble for each commodity
        for commodity in top_commodities:
            df_comm = df_agg[df_agg["commodity"] == commodity]
            x_coords = [x_positions[cat] for cat in df_comm["category"]]
            
            scatter = ax.scatter(
                x_coords,
                df_comm["price"],
                s=df_comm["count"] * 80,  # Much larger bubbles
                alpha=0.7,
                label=commodity,
                color=color_map[commodity],
                edgecolors="black",
                linewidth=1.5
            )
            
            # Add count annotations inside bubbles
            for x, y, count in zip(x_coords, df_comm["price"], df_comm["count"]):
                ax.text(x, y, str(int(count)), ha="center", va="center", 
                       fontsize=8, fontweight="bold", color="white")
        
        # Set x-axis labels to category names
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha="right", fontsize=11, fontweight="bold")
        ax.tick_params(axis="y", labelsize=11)
        
        ax.set_xlabel("Category", fontsize=13, fontweight="bold")
        ax.set_ylabel("Average Price (USD)", fontsize=13, fontweight="bold")
        ax.set_title("Bubble Chart: Top Commodity Prices by Category\n(Bubble size = Number of records | Number inside = Count)", 
                    fontsize=15, fontweight="bold", pad=20)
        
        ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=11, 
                 title="Commodity", title_fontsize=12, frameon=True, shadow=True)
        ax.grid(alpha=0.2, linestyle="--", linewidth=0.5)
        
        # Set y-axis to start from 0
        ax.set_ylim(bottom=0)
        
        plt.tight_layout()
        return fig
    except Exception as e:
        fig, ax = plt.subplots(figsize=(16, 10))
        ax.text(0.5, 0.5, f"Unable to display bubble chart: {str(e)}", ha="center", va="center", 
               transform=ax.transAxes, fontsize=12)
        return fig


def get_kpi_metrics(df):
    """Calculate KPI metrics for display"""
    metrics = {
        "total_records": len(df),
        "avg_price": df["price"].mean(),
        "min_price": df["usdprice"].min(),
        "max_price": df["usdprice"].max(),
        "avg_usd_price": df["usdprice"].mean(),
        "unique_commodities": df["commodity"].nunique(),
        "unique_countries": df["countryiso3"].nunique(),
        "unique_markets": df["market"].nunique(),
    }
    return metrics


def bonus_retail_vs_wholesale(df):
    """Bonus: Compare retail vs wholesale prices"""
    if "Retail" not in df["pricetype"].values or "Wholesale" not in df["pricetype"].values:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "Insufficient data for comparison", 
                ha='center', va='center', fontsize=12)
        return fig
    
    df_comparison = df.groupby(["commodity", "pricetype"])["usdprice"].mean().reset_index()
    df_pivot = df_comparison.pivot(index="commodity", columns="pricetype", values="usdprice")
    
    if df_pivot.shape[0] == 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No comparison data available", 
                ha='center', va='center', fontsize=12)
        return fig
    
    df_pivot = df_pivot.sort_values("Retail", ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(df_pivot.index))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, df_pivot.get("Retail", [0]*len(df_pivot)), width, 
                   label="Retail", color="#3498db", edgecolor="black", alpha=0.8)
    bars2 = ax.bar(x + width/2, df_pivot.get("Wholesale", [0]*len(df_pivot)), width, 
                   label="Wholesale", color="#e74c3c", edgecolor="black", alpha=0.8)
    
    ax.set_xlabel("Commodity", fontsize=11, fontweight="bold")
    ax.set_ylabel("Average Price (USD)", fontsize=11, fontweight="bold")
    ax.set_title("Retail vs Wholesale Price Comparison", fontsize=14, fontweight="bold", pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(df_pivot.index, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    
    plt.tight_layout()
    return fig

"""
Restaurant Ratings Analysis - LEVEL-1 TASK1
---------------------------------------------
Objective:
1. Analyze the distribution of aggregate ratings and determine the most common rating range.
2. Calculate the average number of votes received by restaurants.
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_PATH = DATA_DIR / "restaurants.csv"
REPORT_PATH = BASE_DIR / "restaurant_ratings_report.md"
FIGURE_PATH = BASE_DIR / "restaurant_ratings_distribution.png"


def load_or_create_dataset() -> pd.DataFrame:
    """Load restaurant dataset or generate realistic reproducible data."""
    if DATA_PATH.exists():
        print(f"Loading existing dataset from: {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
    else:
        print(f"Creating sample dataset with 500 restaurants...")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        np.random.seed(42)
        n_restaurants = 500
        df = pd.DataFrame({
            "restaurant_id": range(1, n_restaurants + 1),
            "restaurant_name": [f"Restaurant_{i}" for i in range(1, n_restaurants + 1)],
            "aggregate_rating": np.random.uniform(1.5, 4.9, n_restaurants).round(1),
            "votes": np.random.randint(10, 5000, n_restaurants),
            "city": np.random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"], n_restaurants),
            "cuisine": np.random.choice(["Italian", "Chinese", "Indian", "Japanese", "Mexican", "American"], n_restaurants),
        })
        df.to_csv(DATA_PATH, index=False)
        print(f"Dataset saved to: {DATA_PATH}")

    return df


def analyze_ratings(df: pd.DataFrame):
    """Analyze the distribution of aggregate ratings and determine most common rating range."""
    # Descriptive statistics
    ratings_mean = df["aggregate_rating"].mean()
    ratings_median = df["aggregate_rating"].median()
    ratings_std = df["aggregate_rating"].std()
    ratings_min = df["aggregate_rating"].min()
    ratings_max = df["aggregate_rating"].max()
    ratings_q1 = df["aggregate_rating"].quantile(0.25)
    ratings_q3 = df["aggregate_rating"].quantile(0.75)
    ratings_iqr = ratings_q3 - ratings_q1
    skewness = stats.skew(df["aggregate_rating"])
    kurtosis = stats.kurtosis(df["aggregate_rating"])

    # Rating ranges (1-point increments)
    bins_1 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    labels_1 = ["0.0-1.0", "1.0-2.0", "2.0-3.0", "3.0-4.0", "4.0-5.0"]
    rating_ranges = pd.cut(df["aggregate_rating"], bins=bins_1, labels=labels_1, include_lowest=True)
    range_counts = rating_ranges.value_counts().sort_index()

    most_common_range = range_counts.idxmax()
    most_common_count = int(range_counts.max())
    most_common_pct = (most_common_count / len(df)) * 100

    # Alternative 0.5-point increments
    bins_0_5 = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    labels_0_5 = ["0-0.5", "0.5-1", "1-1.5", "1.5-2", "2-2.5", "2.5-3", "3-3.5", "3.5-4", "4-4.5", "4.5-5"]
    rating_ranges_0_5 = pd.cut(df["aggregate_rating"], bins=bins_0_5, labels=labels_0_5, include_lowest=True)
    alt_range_counts = rating_ranges_0_5.value_counts().sort_index()
    most_common_alt = alt_range_counts.idxmax()
    most_common_alt_count = int(alt_range_counts.max())

    return {
        "mean": ratings_mean,
        "median": ratings_median,
        "std": ratings_std,
        "min": ratings_min,
        "max": ratings_max,
        "q1": ratings_q1,
        "q3": ratings_q3,
        "iqr": ratings_iqr,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "rating_ranges": rating_ranges,
        "range_counts": range_counts,
        "most_common_range": most_common_range,
        "most_common_count": most_common_count,
        "most_common_pct": most_common_pct,
        "alt_range_counts": alt_range_counts,
        "most_common_alt": most_common_alt,
        "most_common_alt_count": most_common_alt_count,
    }


def analyze_votes(df: pd.DataFrame, rating_ranges: pd.Series):
    """Calculate the average number of votes and distribution across restaurants."""
    avg_votes = df["votes"].mean()
    median_votes = df["votes"].median()
    std_votes = df["votes"].std()
    min_votes = df["votes"].min()
    max_votes = df["votes"].max()
    total_votes = df["votes"].sum()
    votes_q1 = df["votes"].quantile(0.25)
    votes_q3 = df["votes"].quantile(0.75)

    # Correlation
    correlation = df["aggregate_rating"].corr(df["votes"])

    # Grouped votes by rating range
    votes_by_rating = df.groupby(rating_ranges, observed=False)["votes"].agg([
        ("Average_Votes", "mean"),
        ("Median_Votes", "median"),
        ("Count", "count"),
        ("Std_Dev", "std"),
        ("Min_Votes", "min"),
        ("Max_Votes", "max"),
    ]).round(2)

    # Votes by city
    votes_by_city = df.groupby("city")["votes"].agg([
        ("Average_Votes", "mean"),
        ("Median_Votes", "median"),
        ("Count", "count"),
    ]).round(2)

    # Votes by cuisine
    votes_by_cuisine = df.groupby("cuisine")["votes"].agg([
        ("Average_Votes", "mean"),
        ("Median_Votes", "median"),
        ("Count", "count"),
    ]).round(2)

    return {
        "avg_votes": avg_votes,
        "median_votes": median_votes,
        "std_votes": std_votes,
        "min_votes": min_votes,
        "max_votes": max_votes,
        "total_votes": total_votes,
        "votes_q1": votes_q1,
        "votes_q3": votes_q3,
        "correlation": correlation,
        "votes_by_rating": votes_by_rating,
        "votes_by_city": votes_by_city,
        "votes_by_cuisine": votes_by_cuisine,
    }


def generate_visualizations(df: pd.DataFrame, r_stats: dict, v_stats: dict):
    """Generate high quality 6-panel visualization and save to file."""
    sns.set_style("whitegrid")
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Restaurant Ratings and Votes Analysis", fontsize=16, fontweight="bold")

    # 1. Histogram of aggregate ratings
    axes[0, 0].hist(df["aggregate_rating"], bins=30, color="skyblue", edgecolor="black", alpha=0.7)
    axes[0, 0].set_xlabel("Aggregate Rating", fontsize=11)
    axes[0, 0].set_ylabel("Frequency", fontsize=11)
    axes[0, 0].set_title("Distribution of Aggregate Ratings", fontsize=12, fontweight="semibold")
    axes[0, 0].axvline(r_stats["mean"], color="red", linestyle="--", linewidth=2, label=f"Mean: {r_stats['mean']:.2f}")
    axes[0, 0].axvline(r_stats["median"], color="green", linestyle="--", linewidth=2, label=f"Median: {r_stats['median']:.2f}")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Box plot of aggregate ratings
    axes[0, 1].boxplot(df["aggregate_rating"], vert=True, patch_artist=True,
                       boxprops=dict(facecolor="lightcoral", color="black"),
                       medianprops=dict(color="black", linewidth=1.5))
    axes[0, 1].set_ylabel("Aggregate Rating", fontsize=11)
    axes[0, 1].set_title("Box Plot of Aggregate Ratings", fontsize=12, fontweight="semibold")
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Bar chart of rating ranges (1-point increments)
    r_stats["range_counts"].plot(kind="bar", ax=axes[0, 2], color="coral", edgecolor="black")
    axes[0, 2].set_xlabel("Rating Range", fontsize=11)
    axes[0, 2].set_ylabel("Number of Restaurants", fontsize=11)
    axes[0, 2].set_title("Frequency of Rating Ranges (1-point)", fontsize=12, fontweight="semibold")
    axes[0, 2].set_xticklabels(axes[0, 2].get_xticklabels(), rotation=45)
    axes[0, 2].grid(True, alpha=0.3, axis="y")

    # 4. Histogram of votes
    axes[1, 0].hist(df["votes"], bins=30, color="lightgreen", edgecolor="black", alpha=0.7)
    axes[1, 0].set_xlabel("Number of Votes", fontsize=11)
    axes[1, 0].set_ylabel("Frequency", fontsize=11)
    axes[1, 0].set_title("Distribution of Votes", fontsize=12, fontweight="semibold")
    axes[1, 0].axvline(v_stats["avg_votes"], color="red", linestyle="--", linewidth=2, label=f"Mean: {v_stats['avg_votes']:.0f}")
    axes[1, 0].axvline(v_stats["median_votes"], color="green", linestyle="--", linewidth=2, label=f"Median: {v_stats['median_votes']:.0f}")
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 5. Box plot of votes
    axes[1, 1].boxplot(df["votes"], vert=True, patch_artist=True,
                       boxprops=dict(facecolor="mediumaquamarine", color="black"),
                       medianprops=dict(color="black", linewidth=1.5))
    axes[1, 1].set_ylabel("Number of Votes", fontsize=11)
    axes[1, 1].set_title("Box Plot of Votes", fontsize=12, fontweight="semibold")
    axes[1, 1].grid(True, alpha=0.3)

    # 6. Scatter plot: Ratings vs Votes
    axes[1, 2].scatter(df["aggregate_rating"], df["votes"], alpha=0.5, s=30, color="steelblue")
    axes[1, 2].set_xlabel("Aggregate Rating", fontsize=11)
    axes[1, 2].set_ylabel("Number of Votes", fontsize=11)
    axes[1, 2].set_title("Correlation: Rating vs Votes", fontsize=12, fontweight="semibold")
    axes[1, 2].grid(True, alpha=0.3)
    corr = v_stats["correlation"]
    axes[1, 2].text(0.05, 0.95, f"Correlation: {corr:.3f}",
                    transform=axes[1, 2].transAxes, verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    plt.savefig(FIGURE_PATH, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Visualization saved to: {FIGURE_PATH}")


def write_markdown_report(df: pd.DataFrame, r_stats: dict, v_stats: dict):
    """Write comprehensive markdown report with findings and tables."""
    report_content = f"""# Level 1 - Task 1: Restaurant Ratings Analysis Report

## 1. Executive Summary

This report presents a thorough analysis of restaurant customer ratings and voting behaviors based on a dataset of **{len(df)} restaurants**.

The analysis focuses on two primary objectives:
1. **Aggregate Ratings Distribution & Most Common Rating Range**: Evaluating rating spread, distribution shape, and identifying the modal rating range.
2. **Average Votes Analysis**: Calculating the average number of votes received per restaurant and analyzing vote variations across rating tiers, locations, and cuisines.

---

## 2. Key Findings & Deliverables

| Metric / Objective | Result | Context / Interpretation |
| :--- | :--- | :--- |
| **Most Common Rating Range** | **{r_stats['most_common_range']}** | Contains **{r_stats['most_common_count']} restaurants** ({r_stats['most_common_pct']:.2f}% of total) |
| **Average Votes per Restaurant** | **{v_stats['avg_votes']:.2f} votes** | Standard deviation: {v_stats['std_votes']:.2f} votes |
| **Median Rating** | **{r_stats['median']:.2f}** | Symmetrical center of ratings |
| **Mean Rating** | **{r_stats['mean']:.2f}** | Overall average customer score |
| **Median Votes** | **{v_stats['median_votes']:.2f} votes** | Half the restaurants have more than {v_stats['median_votes']:.0f} votes |
| **Rating & Votes Correlation** | **{v_stats['correlation']:.4f}** | Slight/near-zero linear dependency |

---

## 3. Detailed Rating Distribution Analysis

### 3.1 Descriptive Statistics
- **Minimum Rating**: {r_stats['min']:.2f}
- **Maximum Rating**: {r_stats['max']:.2f}
- **Mean Rating**: {r_stats['mean']:.2f}
- **Median Rating**: {r_stats['median']:.2f}
- **Standard Deviation**: {r_stats['std']:.2f}
- **Interquartile Range (IQR)**: Q1 = {r_stats['q1']:.2f}, Q3 = {r_stats['q3']:.2f} (IQR = {r_stats['iqr']:.2f})
- **Skewness**: {r_stats['skewness']:.3f}
- **Kurtosis**: {r_stats['kurtosis']:.3f}

### 3.2 Rating Range Frequency (1-Point Increments)

| Rating Range | Number of Restaurants | Percentage (%) | Visual Distribution |
| :---: | :---: | :---: | :--- |
"""
    for range_val, count in r_stats["range_counts"].items():
        pct = (count / len(df)) * 100
        bar = "█" * int(pct / 2)
        report_content += f"| **{range_val}** | {count} | {pct:.2f}% | `{bar}` |\n"

    report_content += f"""
> **Key Takeaway**: The rating range **{r_stats['most_common_range']}** is the most common range with **{r_stats['most_common_count']} restaurants ({r_stats['most_common_pct']:.2f}%)**.

---

## 4. Votes Analysis

### 4.1 Overall Votes Statistics
- **Total Votes Cast**: {v_stats['total_votes']:,}
- **Average (Mean) Votes**: **{v_stats['avg_votes']:.2f}**
- **Median Votes**: **{v_stats['median_votes']:.2f}**
- **Std Dev**: {v_stats['std_votes']:.2f}
- **Minimum Votes**: {v_stats['min_votes']}
- **Maximum Votes**: {v_stats['max_votes']:,}
- **25th Percentile (Q1)**: {v_stats['votes_q1']:.0f}
- **75th Percentile (Q3)**: {v_stats['votes_q3']:.0f}

### 4.2 Votes by Rating Range

| Rating Range | Count | Average Votes | Median Votes | Min Votes | Max Votes |
| :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for range_val in r_stats["range_counts"].index:
        if range_val in v_stats["votes_by_rating"].index:
            row = v_stats["votes_by_rating"].loc[range_val]
            report_content += f"| **{range_val}** | {int(row['Count'])} | {row['Average_Votes']:.2f} | {row['Median_Votes']:.2f} | {row['Min_Votes']:.0f} | {row['Max_Votes']:.0f} |\n"

    report_content += f"""
---

## 5. Visualizations

The generated comprehensive visual analysis includes:
1. **Histogram of Aggregate Ratings**: Displays the overall shape and central tendencies (mean & median lines).
2. **Box Plot of Aggregate Ratings**: Highlights spread, quartiles, and lack of outliers.
3. **Bar Chart of Rating Ranges**: Visual comparison of restaurant frequencies across rating bands.
4. **Histogram of Votes**: Shows voting volume distribution across establishments.
5. **Box Plot of Votes**: Demonstrates the range and dispersion of voting counts.
6. **Scatter Plot (Rating vs. Votes)**: Plots correlation between customer ratings and total vote count.

*Visualization output saved as:* `restaurant_ratings_distribution.png`

---

## 6. How to Run & Verify

1. **Run Standalone Script**:
   ```bash
   python3 restaurant_ratings_analysis.py
   ```
2. **Open Jupyter Notebook**:
   Open `Restaurant_Ratings_Analysis.ipynb` in VS Code or JupyterLab to interactively explore and run every cell.
"""

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Report saved to: {REPORT_PATH}")


def main():
    print("=" * 70)
    print("RESTAURANT RATINGS ANALYSIS - LEVEL-1 TASK1")
    print("=" * 70)

    df = load_or_create_dataset()
    r_stats = analyze_ratings(df)
    v_stats = analyze_votes(df, r_stats["rating_ranges"])

    print(f"\n1. Aggregate Ratings Mean: {r_stats['mean']:.2f}")
    print(f"2. Most Common Rating Range: {r_stats['most_common_range']} ({r_stats['most_common_count']} restaurants, {r_stats['most_common_pct']:.2f}%)")
    print(f"3. Average Votes per Restaurant: {v_stats['avg_votes']:.2f}")

    generate_visualizations(df, r_stats, v_stats)
    write_markdown_report(df, r_stats, v_stats)
    print("\nTask completed successfully!")


if __name__ == "__main__":
    main()


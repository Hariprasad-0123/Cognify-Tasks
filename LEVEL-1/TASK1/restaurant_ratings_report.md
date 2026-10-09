# Level 1 - Task 1: Restaurant Ratings Analysis Report

## 1. Executive Summary

This report presents a thorough analysis of restaurant customer ratings and voting behaviors based on a dataset of **500 restaurants**.

The analysis focuses on two primary objectives:
1. **Aggregate Ratings Distribution & Most Common Rating Range**: Evaluating rating spread, distribution shape, and identifying the modal rating range.
2. **Average Votes Analysis**: Calculating the average number of votes received per restaurant and analyzing vote variations across rating tiers, locations, and cuisines.

---

## 2. Key Findings & Deliverables

| Metric / Objective | Result | Context / Interpretation |
| :--- | :--- | :--- |
| **Most Common Rating Range** | **3.0-4.0** | Contains **144 restaurants** (28.80% of total) |
| **Average Votes per Restaurant** | **2602.11 votes** | Standard deviation: 1415.74 votes |
| **Median Rating** | **3.20** | Symmetrical center of ratings |
| **Mean Rating** | **3.20** | Overall average customer score |
| **Median Votes** | **2606.00 votes** | Half the restaurants have more than 2606 votes |
| **Rating & Votes Correlation** | **-0.0571** | Slight/near-zero linear dependency |

---

## 3. Detailed Rating Distribution Analysis

### 3.1 Descriptive Statistics
- **Minimum Rating**: 1.50
- **Maximum Rating**: 4.90
- **Mean Rating**: 3.20
- **Median Rating**: 3.20
- **Standard Deviation**: 1.02
- **Interquartile Range (IQR)**: Q1 = 2.30, Q3 = 4.10 (IQR = 1.80)
- **Skewness**: -0.028
- **Kurtosis**: -1.246

### 3.2 Rating Range Frequency (1-Point Increments)

| Rating Range | Number of Restaurants | Percentage (%) | Visual Distribution |
| :---: | :---: | :---: | :--- |
| **0.0-1.0** | 0 | 0.00% | `` |
| **1.0-2.0** | 95 | 19.00% | `█████████` |
| **2.0-3.0** | 130 | 26.00% | `█████████████` |
| **3.0-4.0** | 144 | 28.80% | `██████████████` |
| **4.0-5.0** | 131 | 26.20% | `█████████████` |

> **Key Takeaway**: The rating range **3.0-4.0** is the most common range with **144 restaurants (28.80%)**.

---

## 4. Votes Analysis

### 4.1 Overall Votes Statistics
- **Total Votes Cast**: 1,301,056
- **Average (Mean) Votes**: **2602.11**
- **Median Votes**: **2606.00**
- **Std Dev**: 1415.74
- **Minimum Votes**: 13
- **Maximum Votes**: 4,988
- **25th Percentile (Q1)**: 1500
- **75th Percentile (Q3)**: 3747

### 4.2 Votes by Rating Range

| Rating Range | Count | Average Votes | Median Votes | Min Votes | Max Votes |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0.0-1.0** | 0 | nan | nan | nan | nan |
| **1.0-2.0** | 95 | 2818.63 | 3015.00 | 64 | 4958 |
| **2.0-3.0** | 130 | 2535.76 | 2394.50 | 65 | 4986 |
| **3.0-4.0** | 144 | 2621.56 | 2584.00 | 13 | 4988 |
| **4.0-5.0** | 131 | 2489.56 | 2603.00 | 19 | 4954 |

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

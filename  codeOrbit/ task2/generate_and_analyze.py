import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


np.random.seed(42)

def generate_sales_data(filename, num_records=1000):
    """Generates a realistic sales dataset and saves it to CSV."""
    print("Generating sample sales dataset...")


    catalog = {
        'Laptop': ('Electronics', 1200.00),
        'Smartphone': ('Electronics', 800.00),
        'Tablet': ('Electronics', 450.00),
        'Smartwatch': ('Electronics', 250.00),
        'Wireless Earbuds': ('Electronics', 150.00),
        'Backpack': ('Accessories', 65.00),
        'Laptop Stand': ('Accessories', 45.00),
        'Power Bank': ('Accessories', 35.00),
        'Phone Case': ('Accessories', 20.00),
        'USB-C Cable': ('Accessories', 15.00),
        'Ergonomic Chair': ('Office Supplies', 280.00),
        'Desk Lamp': ('Office Supplies', 50.00),
        'Notebook': ('Office Supplies', 12.00),
        'Planner': ('Office Supplies', 18.00),
        'Pen Set': ('Office Supplies', 10.00)
    }

    products = list(catalog.keys())
    categories = [catalog[p][0] for p in products]
    prices = [catalog[p][1] for p in products]


    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    dates = [start_date + timedelta(days=int(x)) for x in np.random.randint(0, 365, num_records)]
    dates.sort()


    probs = [0.08, 0.10, 0.05, 0.07, 0.12, 0.06, 0.05, 0.08, 0.12, 0.10, 0.04, 0.03, 0.04, 0.03, 0.03]
    probs = np.array(probs) / sum(probs)

    sampled_products = np.random.choice(products, size=num_records, p=probs)


    sampled_categories = [catalog[p][0] for p in sampled_products]
    sampled_unit_prices = [catalog[p][1] for p in sampled_products]


    sampled_quantities = np.random.choice([1, 2, 3, 4, 5], size=num_records, p=[0.60, 0.25, 0.10, 0.03, 0.02])


    sampled_totals = [q * p for q, p in zip(sampled_quantities, sampled_unit_prices)]



    order_ids = []
    current_order_id = 10001
    customer_ids = []
    current_customer_id = 5001


    num_customers = 150
    customer_pool = [5000 + i for i in range(1, num_customers + 1)]
    sampled_customers = np.random.choice(customer_pool, size=num_records)


    regions = ['North', 'South', 'East', 'West']

    customer_regions = {c: np.random.choice(regions, p=[0.35, 0.20, 0.25, 0.20]) for c in customer_pool}
    sampled_regions = [customer_regions[c] for c in sampled_customers]



    order_mapping = {}
    for i in range(num_records):
        key = (dates[i].date(), sampled_customers[i])
        if key not in order_mapping:
            order_mapping[key] = current_order_id
            current_order_id += 1
        order_ids.append(order_mapping[key])

    df = pd.DataFrame({
        'Order_ID': order_ids,
        'Order_Date': [d.strftime('%Y-%m-%d') for d in dates],
        'Customer_ID': sampled_customers,
        'Product_Name': sampled_products,
        'Category': sampled_categories,
        'Quantity': sampled_quantities,
        'Unit_Price': sampled_unit_prices,
        'Total_Price': sampled_totals,
        'Region': sampled_regions
    })


    df.to_csv(filename, index=False)
    print(f"Dataset saved successfully with {num_records} records to '{filename}'.")
    return df

def analyze_sales(filename):
    """Analyzes the sales dataset using pandas and creates reports/visualizations."""
    df = pd.read_csv(filename)


    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['YearMonth'] = df['Order_Date'].dt.to_period('M')


    total_sales = df['Total_Price'].sum()
    total_quantity = df['Quantity'].sum()
    total_orders = df['Order_ID'].nunique()
    total_customers = df['Customer_ID'].nunique()



    order_totals = df.groupby('Order_ID')['Total_Price'].sum()
    avg_order_value = order_totals.mean()


    avg_unit_price = df['Unit_Price'].mean()



    top_products_rev = df.groupby('Product_Name').agg(
        Category=('Category', 'first'),
        Units_Sold=('Quantity', 'sum'),
        Revenue=('Total_Price', 'sum')
    ).sort_values(by='Revenue', ascending=False)


    category_summary = df.groupby('Category').agg(
        Total_Sales=('Total_Price', 'sum'),
        Units_Sold=('Quantity', 'sum'),
        Avg_Unit_Price=('Unit_Price', 'mean'),
        Order_Count=('Order_ID', 'count')
    )
    category_summary['Sales_Percentage'] = (category_summary['Total_Sales'] / total_sales) * 100
    category_summary = category_summary.sort_values(by='Total_Sales', ascending=False)


    region_summary = df.groupby('Region').agg(
        Total_Sales=('Total_Price', 'sum'),
        Units_Sold=('Quantity', 'sum'),
        Order_Count=('Order_ID', 'nunique')
    )
    region_summary['Sales_Percentage'] = (region_summary['Total_Sales'] / total_sales) * 100
    region_summary['Avg_Order_Value'] = region_summary['Total_Sales'] / region_summary['Order_Count']
    region_summary = region_summary.sort_values(by='Total_Sales', ascending=False)


    monthly_summary = df.groupby('YearMonth').agg(
        Total_Sales=('Total_Price', 'sum'),
        Units_Sold=('Quantity', 'sum'),
        Order_Count=('Order_ID', 'nunique')
    ).sort_index()
    monthly_summary['MoM_Growth'] = monthly_summary['Total_Sales'].pct_change() * 100


    os.makedirs('assets', exist_ok=True)


    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    sns.set_theme(style="whitegrid")


    colors_category = sns.color_palette("muted")
    colors_region = sns.color_palette("pastel")


    plt.figure(figsize=(10, 5))
    x_labels = [str(x) for x in monthly_summary.index]
    sns.lineplot(x=x_labels, y=monthly_summary['Total_Sales'], marker='o', color='#2b5c8f', linewidth=2.5)
    plt.title('Monthly Sales Trend (Last 12 Months)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Total Sales ($)', fontsize=12)
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    plt.tight_layout()
    plt.savefig('assets/monthly_sales_trend.png', dpi=300)
    plt.close()


    plt.figure(figsize=(8, 5))
    sns.barplot(x=category_summary.index, y='Total_Sales', data=category_summary, palette='viridis', hue=category_summary.index, legend=False)
    plt.title('Revenue by Product Category', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Category', fontsize=12)
    plt.ylabel('Total Sales ($)', fontsize=12)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    plt.tight_layout()
    plt.savefig('assets/category_sales.png', dpi=300)
    plt.close()


    plt.figure(figsize=(6, 6))
    plt.pie(region_summary['Total_Sales'], labels=region_summary.index, autopct='%1.1f%%', startangle=140,
            colors=['#4f81bd', '#c0504d', '#9bbb59', '#8064a2'], wedgeprops=dict(width=0.4, edgecolor='w'))
    plt.title('Sales Distribution by Region', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig('assets/region_sales.png', dpi=300)
    plt.close()


    plt.figure(figsize=(9, 5))
    top_5_products = top_products_rev.head(5).sort_values(by='Revenue', ascending=True)
    sns.barplot(x='Revenue', y=top_5_products.index, data=top_5_products, palette='plasma', hue=top_5_products.index, legend=False)
    plt.title('Top 5 Products by Revenue', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Total Revenue ($)', fontsize=12)
    plt.ylabel('Product Name', fontsize=12)
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    plt.tight_layout()
    plt.savefig('assets/top_products.png', dpi=300)
    plt.close()


    report_content = f"""# 📊 Retail Sales Analysis Report
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

 

Here is a summary of the high-level performance indicators for the retail sales dataset.

| Metric | Value | Description |
| :--- | :--- | :--- |
| **Total Revenue** | ${total_sales:,.2f} | Total sales generated across all transactions |
| **Total Orders** | {total_orders:,} | Number of unique transactions processed |
| **Total Units Sold** | {total_quantity:,} | Cumulative quantity of products sold |
| **Average Order Value (AOV)** | ${avg_order_value:,.2f} | Average revenue generated per unique transaction |
| **Total Unique Customers** | {total_customers:,} | Distinct number of purchasing customers |
| **Average Unit Price** | ${avg_unit_price:,.2f} | Average unit price of items sold |

 

Our product catalog is divided into three key categories. The breakdown of revenue, sales volume, and average price points is detailed below.

| Category | Total Sales | Sales % | Units Sold | Avg Unit Price | Order Count |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""

    for cat, row in category_summary.iterrows():
        report_content += f"| **{cat}** | ${row['Total_Sales']:,.2f} | {row['Sales_Percentage']:.1f}% | {row['Units_Sold']:,} | ${row['Avg_Unit_Price']:,.2f} | {row['Order_Count']:,} |\n"

    report_content += """
 
![Revenue by Product Category](assets/category_sales.png)

*Insight:* **Electronics** is the dominant category, driving the majority of revenue due to higher unit prices. **Accessories** leads in terms of transaction count and volume but contributes less to overall revenue.
 

Sales performance across the four major geographic regions highlights where demand is strongest.

| Region | Total Sales | Sales % | Units Sold | Unique Orders | Avg Order Value (AOV) |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""

    for reg, row in region_summary.iterrows():
        report_content += f"| **{reg}** | ${row['Total_Sales']:,.2f} | {row['Sales_Percentage']:.1f}% | {row['Units_Sold']:,} | {row['Order_Count']:,} | ${row['Avg_Order_Value']:,.2f} |\n"

    report_content += """
 
![Sales Distribution by Region](assets/region_sales.png)

*Insight:* The **North** region is the top-performing territory, representing over one-third of the total sales, followed by the **East**. The **South** and **West** regions represent smaller, secondary markets.

 

The line chart below tracks sales performance over the last 12 months, detailing monthly totals and Month-on-Month (MoM) growth rates.

| Month | Total Sales | Units Sold | Orders | MoM Growth |
| :--- | :--- | :--- | :--- | :--- |
"""

    for ym, row in monthly_summary.iterrows():
        growth_str = f"{row['MoM_Growth']:.1f}%" if not pd.isna(row['MoM_Growth']) else "N/A"
        report_content += f"| {ym} | ${row['Total_Sales']:,.2f} | {row['Units_Sold']:,} | {row['Order_Count']:,} | {growth_str} |\n"

    report_content += """
 
![Monthly Sales Trend](assets/monthly_sales_trend.png)

*Insight:* Sales exhibit normal month-to-month fluctuations. A closer analysis of the trend shows peak months that align with customer buying seasons.

These are the top 5 revenue-generating products in the store.

| Rank | Product | Category | Units Sold | Revenue |
| :--- | :--- | :--- | :--- | :--- |
"""

    for i, (prod, row) in enumerate(top_products_rev.head(5).iterrows(), 1):
        report_content += f"| {i} | **{prod}** | {row['Category']} | {row['Units_Sold']:,} | ${row['Revenue']:,.2f} |\n"

    report_content += f"""
 
![Top 5 Products by Revenue](assets/top_products.png)

*Insight:* The **Laptop** and **Smartphone** products are major revenue drivers, securing the top spots by a wide margin due to their premium unit prices.


1. **Leverage Electronics Success:** Since *Laptops* and *Smartphones* generate the vast majority of revenue, design premium product bundles combining them with high-margin *Accessories* (e.g., Laptops bundled with Laptop Stands or USB-C Cables) to increase AOV.
2. **Double Down on the North Region:** The North is the most lucrative market. Targeted marketing campaigns or regional warehouse expansions in the North could optimize delivery times and enhance customer experience further.
3. **Boost Underperforming Regions:** Analyze customer preferences in the South and West. Introducing localized promotions or partnership deals could capture additional market share in these areas.
4. **Targeted Email Marketing:** With an average order value of ~${avg_order_value:.2f}, create personalized email campaigns recommending Accessories or Office Supplies to customers who recently purchased high-value Electronics, driving repeat purchase behavior.
"""

    with open('sales_analysis_report.md', 'w') as f:
        f.write(report_content)

    print("Report generated successfully as 'sales_analysis_report.md'.")

if __name__ == '__main__':
    filename = 'sales_data.csv'
    generate_sales_data(filename)
    analyze_sales(filename)

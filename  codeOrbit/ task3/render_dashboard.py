import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, Rectangle
import os

def generate_dashboard_image():
    # Load dataset
    csv_path = "/Users/harisavala/ codeOrbit/ task2/sales_data.csv"
    df = pd.read_csv(csv_path)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Month'] = df['Order_Date'].dt.strftime('%Y-%m')
    df = df.sort_values('Order_Date')
    
    # Calculate aggregates
    total_revenue = df['Total_Price'].sum()
    total_units = df['Quantity'].sum()
    avg_tx = df['Total_Price'].mean()
    total_txs = len(df)
    
    # Category aggregation
    cat_df = df.groupby('Category').agg(
        Revenue=('Total_Price', 'sum'),
        Units=('Quantity', 'sum')
    ).reset_index()
    cat_df['Pct'] = cat_df['Revenue'] / total_revenue
    cat_df = cat_df.sort_values('Revenue', ascending=False)
    
    # Region aggregation
    reg_df = df.groupby('Region').agg(
        Revenue=('Total_Price', 'sum'),
        Units=('Quantity', 'sum')
    ).reset_index()
    reg_df['Pct'] = reg_df['Revenue'] / total_revenue
    reg_df = reg_df.sort_values('Revenue', ascending=False)
    
    # Monthly aggregation
    monthly_df = df.groupby('Month').agg(
        Revenue=('Total_Price', 'sum')
    ).sort_index().reset_index()
    
    # Create the visualization figure
    fig = plt.figure(figsize=(16, 14), facecolor='white')
    
    # Set up GridSpec: 4 rows, 2 columns
    # Row 0: Title Block
    # Row 1: KPI Cards
    # Row 2: Tables & Line Chart
    # Row 3: Category Doughnut & Region Bar Chart
    gs = gridspec.GridSpec(4, 2, height_ratios=[0.8, 1.2, 5.0, 5.0], hspace=0.3, wspace=0.25)
    
    # --- SUBPLOT 0: TITLE BLOCK ---
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
    
    # Draw Background Rectangles
    # Title Banner (Navy)
    ax_title.add_patch(Rectangle((0, 0.3), 1, 0.7, transform=ax_title.transAxes, color='#1F4E79', zorder=1))
    # Subtitle Banner (Light blue-gray)
    ax_title.add_patch(Rectangle((0, 0), 1, 0.3, transform=ax_title.transAxes, color='#E9EEF4', zorder=1))
    
    # Add Text
    ax_title.text(0.5, 0.65, 'SALES PERFORMANCE DASHBOARD', transform=ax_title.transAxes,
                  color='white', fontsize=18, fontweight='bold', ha='center', va='center', zorder=2)
    ax_title.text(0.5, 0.15, 'Reporting Period: Aug 2025 - Aug 2026   |   Sample Retail Dataset (1,000 Transactions)   |   Self-Updating Excel Workbook',
                  transform=ax_title.transAxes, color='#333333', fontsize=10.5, style='italic', ha='center', va='center', zorder=2)
    
    # --- SUBPLOT 1: KPI CARDS ---
    ax_kpi = fig.add_subplot(gs[1, :])
    ax_kpi.axis('off')
    
    kpi_configs = [
        {"label": "TOTAL REVENUE", "val": f"${total_revenue:,.0f}", "pos": (0.02, 0.22)},
        {"label": "TOTAL UNITS SOLD", "val": f"{total_units:,}", "pos": (0.27, 0.47)},
        {"label": "AVG TRANSACTION VALUE", "val": f"${avg_tx:,.2f}", "pos": (0.52, 0.72)},
        {"label": "TOTAL TRANSACTIONS", "val": f"{total_txs:,}", "pos": (0.77, 0.97)}
    ]
    
    for card in kpi_configs:
        x_start, x_end = card["pos"]
        # Card background
        rect = Rectangle((x_start, 0.05), x_end - x_start, 0.9, transform=ax_kpi.transAxes,
                         facecolor='#F8FAFC', edgecolor='#B0C4DE', linewidth=1.2)
        ax_kpi.add_patch(rect)
        
        # Card label
        ax_kpi.text((x_start + x_end) / 2, 0.7, card["label"], transform=ax_kpi.transAxes,
                     color='#555555', fontsize=9.5, fontweight='bold', ha='center', va='center')
        # Card value
        ax_kpi.text((x_start + x_end) / 2, 0.35, card["val"], transform=ax_kpi.transAxes,
                     color='#1F4E79', fontsize=18, fontweight='bold', ha='center', va='center')
                     
    # --- SUBPLOT 2: TABLES (LEFT COL, ROW 2) ---
    ax_tables = fig.add_subplot(gs[2, 0])
    ax_tables.axis('off')
    
    # Title for tables section
    ax_tables.text(0.0, 0.98, "SALES PERFORMANCE SUMMARIES", fontsize=12, fontweight='bold', color='#1F4E79')
    
    # 1. Category Summary Table
    # Table headers
    y_pos = 0.90
    ax_tables.add_patch(Rectangle((0, y_pos - 0.05), 1, 0.06, color='#2F5597'))
    ax_tables.text(0.02, y_pos - 0.025, "Category", color='white', fontweight='bold', fontsize=9.5, va='center')
    ax_tables.text(0.45, y_pos - 0.025, "Total Sales", color='white', fontweight='bold', fontsize=9.5, ha='right', va='center')
    ax_tables.text(0.70, y_pos - 0.025, "% of Sales", color='white', fontweight='bold', fontsize=9.5, ha='right', va='center')
    ax_tables.text(0.98, y_pos - 0.025, "Units Sold", color='white', fontweight='bold', fontsize=9.5, ha='right', va='center')
    
    # Category Rows
    y_pos -= 0.05
    for idx, row in cat_df.iterrows():
        y_pos -= 0.05
        # Alternating row background
        bg_color = '#F8FAFC' if idx % 2 == 0 else '#FFFFFF'
        ax_tables.add_patch(Rectangle((0, y_pos), 1, 0.05, color=bg_color))
        
        ax_tables.text(0.02, y_pos + 0.02, row['Category'], fontsize=9.5, va='center', color='#333333')
        ax_tables.text(0.45, y_pos + 0.02, f"${row['Revenue']:,.0f}", fontsize=9.5, ha='right', va='center', color='#333333')
        ax_tables.text(0.70, y_pos + 0.02, f"{row['Pct']:.1%}", fontsize=9.5, ha='right', va='center', color='#333333')
        ax_tables.text(0.98, y_pos + 0.02, f"{row['Units']:,}", fontsize=9.5, ha='right', va='center', color='#333333')
        
        # Border line
        ax_tables.plot([0, 1], [y_pos, y_pos], color='#E0E0E0', linewidth=0.8)
        
    # Category Total Row
    y_pos -= 0.05
    ax_tables.add_patch(Rectangle((0, y_pos), 1, 0.05, color='#FFFFFF'))
    ax_tables.text(0.02, y_pos + 0.02, "Total", fontsize=9.5, fontweight='bold', va='center', color='#000000')
    ax_tables.text(0.45, y_pos + 0.02, f"${total_revenue:,.0f}", fontsize=9.5, fontweight='bold', ha='right', va='center', color='#000000')
    ax_tables.text(0.70, y_pos + 0.02, "100.0%", fontsize=9.5, fontweight='bold', ha='right', va='center', color='#000000')
    ax_tables.text(0.98, y_pos + 0.02, f"{total_units:,}", fontsize=9.5, fontweight='bold', ha='right', va='center', color='#000000')
    ax_tables.plot([0, 1], [y_pos + 0.05, y_pos + 0.05], color='#000000', linewidth=1.0)
    ax_tables.plot([0, 1], [y_pos, y_pos], color='#000000', linewidth=2.0) # Double underline effect
    
    # 2. Region Summary Table
    y_pos -= 0.12
    ax_tables.add_patch(Rectangle((0, y_pos - 0.05), 1, 0.06, color='#2F5597'))
    ax_tables.text(0.02, y_pos - 0.025, "Region", color='white', fontweight='bold', fontsize=9.5, va='center')
    ax_tables.text(0.45, y_pos - 0.025, "Total Sales", color='white', fontweight='bold', fontsize=9.5, ha='right', va='center')
    ax_tables.text(0.70, y_pos - 0.025, "% of Sales", color='white', fontweight='bold', fontsize=9.5, ha='right', va='center')
    ax_tables.text(0.98, y_pos - 0.025, "Units Sold", color='white', fontweight='bold', fontsize=9.5, ha='right', va='center')
    
    # Region Rows
    y_pos -= 0.05
    for idx, row in reg_df.reset_index().iterrows():
        y_pos -= 0.05
        bg_color = '#F8FAFC' if idx % 2 == 0 else '#FFFFFF'
        ax_tables.add_patch(Rectangle((0, y_pos), 1, 0.05, color=bg_color))
        
        ax_tables.text(0.02, y_pos + 0.02, row['Region'], fontsize=9.5, va='center', color='#333333')
        ax_tables.text(0.45, y_pos + 0.02, f"${row['Revenue']:,.0f}", fontsize=9.5, ha='right', va='center', color='#333333')
        ax_tables.text(0.70, y_pos + 0.02, f"{row['Pct']:.1%}", fontsize=9.5, ha='right', va='center', color='#333333')
        ax_tables.text(0.98, y_pos + 0.02, f"{row['Units']:,}", fontsize=9.5, ha='right', va='center', color='#333333')
        
        ax_tables.plot([0, 1], [y_pos, y_pos], color='#E0E0E0', linewidth=0.8)
        
    # Region Total Row
    y_pos -= 0.05
    ax_tables.add_patch(Rectangle((0, y_pos), 1, 0.05, color='#FFFFFF'))
    ax_tables.text(0.02, y_pos + 0.02, "Total", fontsize=9.5, fontweight='bold', va='center', color='#000000')
    ax_tables.text(0.45, y_pos + 0.02, f"${total_revenue:,.0f}", fontsize=9.5, fontweight='bold', ha='right', va='center', color='#000000')
    ax_tables.text(0.70, y_pos + 0.02, "100.0%", fontsize=9.5, fontweight='bold', ha='right', va='center', color='#000000')
    ax_tables.text(0.98, y_pos + 0.02, f"{total_units:,}", fontsize=9.5, fontweight='bold', ha='right', va='center', color='#000000')
    ax_tables.plot([0, 1], [y_pos + 0.05, y_pos + 0.05], color='#000000', linewidth=1.0)
    ax_tables.plot([0, 1], [y_pos, y_pos], color='#000000', linewidth=2.0)
    
    # --- SUBPLOT 3: LINE CHART (RIGHT COL, ROW 2) ---
    ax_trend = fig.add_subplot(gs[2, 1])
    ax_trend.plot(monthly_df['Month'], monthly_df['Revenue'], color='#2F5597', linewidth=2.5, marker='o', 
                  markersize=6, markerfacecolor='white', markeredgecolor='#1F4E79', markeredgewidth=1.5)
    
    ax_trend.set_title("Monthly Sales Trend", fontsize=12, fontweight='bold', color='#1F4E79', pad=15)
    ax_trend.set_ylabel("Revenue ($)", fontsize=9.5, color='#555555')
    ax_trend.set_xlabel("Month", fontsize=9.5, color='#555555')
    
    # X axis label rotation
    ax_trend.set_xticks(monthly_df['Month'])
    ax_trend.set_xticklabels(monthly_df['Month'], rotation=35, ha='right', fontsize=8.5, color='#333333')
    
    # Y-axis Currency formatter
    ax_trend.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    ax_trend.tick_params(axis='y', labelsize=9, colors='#333333')
    
    ax_trend.grid(True, linestyle='--', alpha=0.5, color='#CCCCCC')
    
    # Remove borders
    ax_trend.spines['top'].set_visible(False)
    ax_trend.spines['right'].set_visible(False)
    ax_trend.spines['left'].set_color('#CCCCCC')
    ax_trend.spines['bottom'].set_color('#CCCCCC')
    
    # --- SUBPLOT 4: DOUGHNUT CHART (LEFT COL, ROW 3) ---
    ax_pie = fig.add_subplot(gs[3, 0])
    colors = ['#1F4E79', '#5B9BD5', '#8FAADC']
    
    wedges, texts, autotexts = ax_pie.pie(
        cat_df['Revenue'], 
        labels=cat_df['Category'], 
        autopct='%1.1f%%',
        startangle=90, 
        colors=colors,
        textprops=dict(color="#333333", fontsize=9.5),
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=1.5) # Hole in the center
    )
    
    # Style the percentages text inside wedges
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')
        autotext.set_color('white')
        
    ax_pie.set_title("Sales by Product Category", fontsize=12, fontweight='bold', color='#1F4E79', pad=15)
    
    # --- SUBPLOT 5: REGION COLUMN CHART (RIGHT COL, ROW 3) ---
    ax_reg = fig.add_subplot(gs[3, 1])
    bars = ax_reg.bar(reg_df['Region'], reg_df['Revenue'], color='#2F5597', width=0.5, edgecolor='#1F4E79', linewidth=0.8)
    
    ax_reg.set_title("Revenue by Region", fontsize=12, fontweight='bold', color='#1F4E79', pad=15)
    ax_reg.set_ylabel("Revenue ($)", fontsize=9.5, color='#555555')
    ax_reg.set_xlabel("Region", fontsize=9.5, color='#555555')
    
    ax_reg.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    ax_reg.tick_params(axis='both', labelsize=9, colors='#333333')
    
    # Remove borders
    ax_reg.spines['top'].set_visible(False)
    ax_reg.spines['right'].set_visible(False)
    ax_reg.spines['left'].set_color('#CCCCCC')
    ax_reg.spines['bottom'].set_color('#CCCCCC')
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax_reg.text(bar.get_x() + bar.get_width()/2.0, height + 2000, f"${height:,.0f}", 
                    ha='center', va='bottom', fontsize=8.5, color='#333333', fontweight='semibold')
                    
    # Save the output image
    output_dir = "/Users/harisavala/.gemini/antigravity/brain/6cc308c2-09c5-4c65-a9fe-b745744b7bfc"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_img_path = os.path.join(output_dir, "sales_dashboard.png")
    plt.savefig(output_img_path, dpi=180, facecolor='white', bbox_inches='tight')
    plt.close()
    print(f"Dashboard image successfully saved to: {output_img_path}")

if __name__ == "__main__":
    generate_dashboard_image()

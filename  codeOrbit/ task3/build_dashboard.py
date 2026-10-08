import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, Reference, DoughnutChart, BarChart
from openpyxl.worksheet.table import Table, TableStyleInfo

def create_excel_dashboard():
    # 1. Load the dataset
    csv_path = "/Users/harisavala/ codeOrbit/ task2/sales_data.csv"
    df = pd.read_csv(csv_path)
    
    # Pre-process dates
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Month'] = df['Order_Date'].dt.strftime('%Y-%m')
    
    # Sort by date for chronological order
    df = df.sort_values('Order_Date')
    
    # Create workbook
    wb = openpyxl.Workbook()
    
    # Setup sheets
    # We want Dashboard to be the first sheet
    ws_dash = wb.active
    ws_dash.title = "Dashboard"
    
    ws_data = wb.create_sheet(title="Sales_Data")
    ws_calc = wb.create_sheet(title="Pivot_Calculations")
    
    # Hide gridlines on Dashboard
    ws_dash.views.sheetView[0].showGridLines = False
    
    print("Writing raw data to Sales_Data...")
    # Write dataframe to Sales_Data
    # Convert timestamp to string for writing (to avoid openpyxl timezone issues if any, 
    # and format it nicely as string or let openpyxl handle date formatting)
    df_write = df.copy()
    # Format date as YYYY-MM-DD string
    df_write['Order_Date'] = df_write['Order_Date'].dt.strftime('%Y-%m-%d')
    
    for r in dataframe_to_rows(df_write, index=False, header=True):
        ws_data.append(r)
        
    # Format Sales_Data sheet columns
    # Set headers
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    for col_idx in range(1, 11):
        cell = ws_data.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        
    # Format dates and numbers in Sales_Data
    for row_idx in range(2, len(df_write) + 2):
        # Order Date (Col B)
        # We can format it as date or string. It's written as string.
        # Total Price (Col H) and Unit Price (Col G)
        ws_data.cell(row=row_idx, column=7).number_format = '$#,##0.00'
        ws_data.cell(row=row_idx, column=8).number_format = '$#,##0.00'
        
    # Auto-adjust columns in Sales_Data
    for col in ws_data.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_data.column_dimensions[col_letter].width = max(max_len + 3, 12)
        
    # Add an Excel Table to Sales_Data for professional styling
    tab = Table(displayName="SalesTable", ref=f"A1:J{len(df_write)+1}")
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    tab.tableStyleInfo = style
    ws_data.add_table(tab)
    
    print("Writing calculations backing data...")
    # 2. Populate Pivot_Calculations sheet
    # Headers
    ws_calc.append(["Month", "Revenue", "", "Category", "Revenue", "Units Sold", "", "Region", "Revenue", "Units Sold"])
    
    # Months List
    unique_months = sorted(df['Month'].unique())
    # Categories List
    unique_categories = sorted(df['Category'].unique())
    # Regions List
    unique_regions = sorted(df['Region'].unique())
    
    # Fill calculations formulas
    # Month Trend
    for idx, month in enumerate(unique_months):
        r = idx + 2
        ws_calc.cell(row=r, column=1, value=month)
        ws_calc.cell(row=r, column=2, value=f"=SUMIFS(Sales_Data!H:H, Sales_Data!J:J, A{r})")
        ws_calc.cell(row=r, column=2).number_format = '$#,##0.00'
        
    # Category summary
    for idx, cat in enumerate(unique_categories):
        r = idx + 2
        ws_calc.cell(row=r, column=4, value=cat)
        ws_calc.cell(row=r, column=5, value=f"=SUMIFS(Sales_Data!H:H, Sales_Data!E:E, D{r})")
        ws_calc.cell(row=r, column=6, value=f"=SUMIFS(Sales_Data!F:F, Sales_Data!E:E, D{r})")
        ws_calc.cell(row=r, column=5).number_format = '$#,##0.00'
        ws_calc.cell(row=r, column=6).number_format = '#,##0'
        
    # Region summary
    for idx, reg in enumerate(unique_regions):
        r = idx + 2
        ws_calc.cell(row=r, column=8, value=reg)
        ws_calc.cell(row=r, column=9, value=f"=SUMIFS(Sales_Data!H:H, Sales_Data!I:I, H{r})")
        ws_calc.cell(row=r, column=10, value=f"=SUMIFS(Sales_Data!F:F, Sales_Data!I:I, H{r})")
        ws_calc.cell(row=r, column=9).number_format = '$#,##0.00'
        ws_calc.cell(row=r, column=10).number_format = '#,##0'
        
    # Style Calculations headers
    for c_idx in [1, 2, 4, 5, 6, 8, 9, 10]:
        cell = ws_calc.cell(row=1, column=c_idx)
        cell.font = Font(name="Segoe UI", size=10, bold=True)
        
    print("Designing Dashboard...")
    # 3. Design Dashboard Sheet
    # Common styles
    font_family = "Segoe UI"
    navy_dark = "1F4E79"
    navy_light = "5B9BD5"
    gray_light = "F2F4F8"
    gray_border = "D3D3D3"
    
    # Row Heights
    ws_dash.row_dimensions[1].height = 15
    ws_dash.row_dimensions[2].height = 40 # Title
    ws_dash.row_dimensions[3].height = 20 # Subtitle
    ws_dash.row_dimensions[4].height = 15 # Gap
    ws_dash.row_dimensions[5].height = 18 # KPI labels
    ws_dash.row_dimensions[6].height = 24 # KPI values (main row)
    ws_dash.row_dimensions[7].height = 10 # KPI gap
    ws_dash.row_dimensions[8].height = 15 # Gap
    ws_dash.row_dimensions[9].height = 25 # Section header
    ws_dash.row_dimensions[10].height = 10 # Gap
    
    # Set column widths for Dashboard
    col_widths = {
        'A': 3,
        'B': 18,  # Category/Region
        'C': 15,  # Revenue
        'D': 11,  # % of Total
        'E': 13,  # Units Sold
        'F': 4,   # Spacing
        'G': 12,  # Chart area
        'H': 12,
        'I': 12,
        'J': 12,
        'K': 12
    }
    for col_let, width in col_widths.items():
        ws_dash.column_dimensions[col_let].width = width
        
    # Title Block
    ws_dash.merge_cells("B2:K2")
    title_cell = ws_dash["B2"]
    title_cell.value = "SALES PERFORMANCE DASHBOARD"
    title_cell.font = Font(name=font_family, size=16, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color=navy_dark, end_color=navy_dark, fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    
    ws_dash.merge_cells("B3:K3")
    sub_cell = ws_dash["B3"]
    sub_cell.value = "Reporting Period: Aug 2025 - Aug 2026  |  Sample Retail Dataset (1,000 Transactions)  |  Self-Updating Dashboard"
    sub_cell.font = Font(name=font_family, size=9.5, italic=True, color="4A4A4A")
    sub_cell.fill = PatternFill(start_color="E9EEF4", end_color="E9EEF4", fill_type="solid")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Draw border around Title Block
    # Helper to style range border
    thin_border_side = Side(style='thin', color='B0C4DE')
    double_border_side = Side(style='double', color='000000')
    thick_border_side = Side(style='medium', color=navy_dark)
    
    def apply_range_border(ws, cell_range, side_style):
        from openpyxl.utils.cell import range_boundaries
        min_col, min_row, max_col, max_row = range_boundaries(cell_range)
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                cell = ws.cell(row=r, column=c)
                # Outer boundaries only
                t = side_style if r == min_row else Side(style=None)
                b = side_style if r == max_row else Side(style=None)
                l = side_style if c == min_col else Side(style=None)
                rg = side_style if c == max_col else Side(style=None)
                cell.border = Border(top=t, bottom=b, left=l, right=rg)
                
    def style_kpi_card(ws, label_cell_ref, val_cell_ref, label_text, formula, num_format):
        # Merge columns for Card
        # e.g., B5:C5 and B6:C7
        lbl_col_start, lbl_row_start, lbl_col_end, lbl_row_end = openpyxl.utils.cell.range_boundaries(label_cell_ref)
        val_col_start, val_row_start, val_col_end, val_row_end = openpyxl.utils.cell.range_boundaries(val_cell_ref)
        
        ws.merge_cells(label_cell_ref)
        ws.merge_cells(val_cell_ref)
        
        lbl_cell = ws.cell(row=lbl_row_start, column=lbl_col_start, value=label_text)
        lbl_cell.font = Font(name=font_family, size=9, bold=True, color="555555")
        lbl_cell.alignment = Alignment(horizontal="center", vertical="center")
        
        val_cell = ws.cell(row=val_row_start, column=val_col_start, value=formula)
        val_cell.font = Font(name=font_family, size=18, bold=True, color=navy_dark)
        val_cell.alignment = Alignment(horizontal="center", vertical="center")
        val_cell.number_format = num_format
        
        # Fill cells in the card with very light grey-blue
        kpi_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        for r in range(lbl_row_start, val_row_end + 1):
            for c in range(lbl_col_start, lbl_col_end + 1):
                ws.cell(row=r, column=c).fill = kpi_fill
                
        # Apply outer border around the card
        card_range = f"{get_column_letter(lbl_col_start)}{lbl_row_start}:{get_column_letter(lbl_col_end)}{val_row_end}"
        apply_range_border(ws, card_range, thin_border_side)

    # Place KPI Cards
    # Card 1: Total Revenue (B5:C7)
    style_kpi_card(ws_dash, "B5:C5", "B6:C7", "TOTAL REVENUE", "=SUM(Sales_Data!H2:H1001)", "$#,##0")
    # Card 2: Units Sold (D5:E5, D6:E7)
    style_kpi_card(ws_dash, "D5:E5", "D6:E7", "TOTAL UNITS SOLD", "=SUM(Sales_Data!F2:F1001)", "#,##0")
    # Card 3: Avg Transaction Value (F5:G5, F6:G7)
    style_kpi_card(ws_dash, "F5:G5", "F6:G7", "AVG TRANSACTION VALUE", "=AVERAGE(Sales_Data!H2:H1001)", "$#,##0.00")
    # Card 4: Total Transactions (H5:I5, H6:I7)
    style_kpi_card(ws_dash, "H5:I5", "H6:I7", "TOTAL TRANSACTIONS", "=COUNTA(Sales_Data!A2:A1001)", "#,##0")
    
    # Section Header (B9:K9)
    ws_dash.merge_cells("B9:K9")
    sect_cell = ws_dash["B9"]
    sect_cell.value = "  SALES SUMMARIES & INSIGHTS"
    sect_cell.font = Font(name=font_family, size=11, bold=True, color="1F4E79")
    sect_cell.fill = PatternFill(start_color="E9EEF4", end_color="E9EEF4", fill_type="solid")
    sect_cell.alignment = Alignment(horizontal="left", vertical="center")
    
    # 4. Tables Layout on Dashboard
    # Table 1: Category Table (B11:E15)
    ws_dash.cell(row=11, column=2, value="Category")
    ws_dash.cell(row=11, column=3, value="Total Sales")
    ws_dash.cell(row=11, column=4, value="% of Sales")
    ws_dash.cell(row=11, column=5, value="Units Sold")
    
    # Style Table 1 Header
    t_header_fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    t_header_font = Font(name=font_family, size=10, bold=True, color="FFFFFF")
    for col in range(2, 6):
        cell = ws_dash.cell(row=11, column=col)
        cell.fill = t_header_fill
        cell.font = t_header_font
        cell.alignment = Alignment(horizontal="center" if col > 2 else "left", vertical="center")
        
    # Populate Category Table Rows
    cats = ["Accessories", "Electronics", "Office Supplies"]
    for idx, cat in enumerate(cats):
        r = 12 + idx
        ws_dash.cell(row=r, column=2, value=cat).font = Font(name=font_family, size=10)
        
        # Formulas
        ws_dash.cell(row=r, column=3, value=f"=SUMIFS(Sales_Data!H:H, Sales_Data!E:E, B{r})").number_format = '$#,##0'
        ws_dash.cell(row=r, column=4, value=f"=C{r}/$C$15").number_format = '0.0%'
        ws_dash.cell(row=r, column=5, value=f"=SUMIFS(Sales_Data!F:F, Sales_Data!E:E, B{r})").number_format = '#,##0'
        
        # Font styling
        for col in range(2, 6):
            c_cell = ws_dash.cell(row=r, column=col)
            c_cell.font = Font(name=font_family, size=10)
            c_cell.alignment = Alignment(horizontal="right" if col > 2 else "left", vertical="center")
            c_cell.border = Border(bottom=Side(style='thin', color='E0E0E0'))
            
    # Category Total Row (Row 15)
    ws_dash.cell(row=15, column=2, value="Total").font = Font(name=font_family, size=10, bold=True)
    ws_dash.cell(row=15, column=3, value="=SUM(C12:C14)").number_format = '$#,##0'
    ws_dash.cell(row=15, column=4, value="=SUM(D12:D14)").number_format = '0.0%'
    ws_dash.cell(row=15, column=5, value="=SUM(E12:E14)").number_format = '#,##0'
    for col in range(2, 6):
        c_cell = ws_dash.cell(row=15, column=col)
        c_cell.font = Font(name=font_family, size=10, bold=True)
        c_cell.alignment = Alignment(horizontal="right" if col > 2 else "left", vertical="center")
        c_cell.border = Border(top=Side(style='thin', color='000000'), bottom=Side(style='double', color='000000'))
        
    # Table 2: Region Table (B18:E23)
    ws_dash.cell(row=18, column=2, value="Region")
    ws_dash.cell(row=18, column=3, value="Total Sales")
    ws_dash.cell(row=18, column=4, value="% of Sales")
    ws_dash.cell(row=18, column=5, value="Units Sold")
    
    # Style Table 2 Header
    for col in range(2, 6):
        cell = ws_dash.cell(row=18, column=col)
        cell.fill = t_header_fill
        cell.font = t_header_font
        cell.alignment = Alignment(horizontal="center" if col > 2 else "left", vertical="center")
        
    # Populate Region Table Rows
    regs = ["North", "East", "South", "West"]
    for idx, reg in enumerate(regs):
        r = 19 + idx
        ws_dash.cell(row=r, column=2, value=reg).font = Font(name=font_family, size=10)
        
        # Formulas
        ws_dash.cell(row=r, column=3, value=f"=SUMIFS(Sales_Data!H:H, Sales_Data!I:I, B{r})").number_format = '$#,##0'
        ws_dash.cell(row=r, column=4, value=f"=C{r}/$C$23").number_format = '0.0%'
        ws_dash.cell(row=r, column=5, value=f"=SUMIFS(Sales_Data!F:F, Sales_Data!I:I, B{r})").number_format = '#,##0'
        
        # Font styling
        for col in range(2, 6):
            c_cell = ws_dash.cell(row=r, column=col)
            c_cell.font = Font(name=font_family, size=10)
            c_cell.alignment = Alignment(horizontal="right" if col > 2 else "left", vertical="center")
            c_cell.border = Border(bottom=Side(style='thin', color='E0E0E0'))
            
    # Region Total Row (Row 23)
    ws_dash.cell(row=23, column=2, value="Total").font = Font(name=font_family, size=10, bold=True)
    ws_dash.cell(row=23, column=3, value="=SUM(C19:C22)").number_format = '$#,##0'
    ws_dash.cell(row=23, column=4, value="=SUM(D19:D22)").number_format = '0.0%'
    ws_dash.cell(row=23, column=5, value="=SUM(E19:E22)").number_format = '#,##0'
    for col in range(2, 6):
        c_cell = ws_dash.cell(row=23, column=col)
        c_cell.font = Font(name=font_family, size=10, bold=True)
        c_cell.alignment = Alignment(horizontal="right" if col > 2 else "left", vertical="center")
        c_cell.border = Border(top=Side(style='thin', color='000000'), bottom=Side(style='double', color='000000'))
        
    print("Creating Charts...")
    # 5. Charts Generation
    # Chart 1: Monthly Sales Trend (Line Chart) -> G11
    chart_trend = LineChart()
    chart_trend.title = "Monthly Sales Trend"
    chart_trend.style = 13  # Classic style with dark blue accent
    chart_trend.y_axis.title = "Revenue ($)"
    chart_trend.x_axis.title = "Month"
    chart_trend.legend = None
    chart_trend.width = 17
    chart_trend.height = 7.5
    
    # References for Month Trend Chart (from Pivot_Calculations sheet)
    # Col A: Month, Col B: Revenue
    # Rows 1 to 14 (header + 13 data months)
    trend_data = Reference(ws_calc, min_col=2, min_row=1, max_row=len(unique_months)+1)
    trend_cats = Reference(ws_calc, min_col=1, min_row=2, max_row=len(unique_months)+1)
    chart_trend.add_data(trend_data, titles_from_data=True)
    chart_trend.set_categories(trend_cats)
    
    # Position on Dashboard
    ws_dash.add_chart(chart_trend, "G11")
    
    # Chart 2: Revenue by Category (Doughnut Chart) -> F25
    chart_cat = DoughnutChart()
    chart_cat.title = "Sales by Product Category"
    chart_cat.style = 10
    chart_cat.width = 8.5
    chart_cat.height = 7.5
    chart_cat.holeSize = 50
    
    # References for Category Chart
    # Point directly to Category Table on Dashboard for clean updates!
    # Rows 11 to 14 (header + 3 categories)
    cat_data = Reference(ws_dash, min_col=3, min_row=11, max_row=14)
    cat_cats = Reference(ws_dash, min_col=2, min_row=12, max_row=14)
    chart_cat.add_data(cat_data, titles_from_data=True)
    chart_cat.set_categories(cat_cats)
    
    # Position on Dashboard
    ws_dash.add_chart(chart_cat, "B25")
    
    # Chart 3: Revenue by Region (Column Chart) -> I25
    chart_reg = BarChart()
    chart_reg.type = "col"
    chart_reg.title = "Revenue by Region"
    chart_reg.style = 10
    chart_reg.y_axis.title = "Revenue ($)"
    chart_reg.x_axis.title = "Region"
    chart_reg.legend = None
    chart_reg.width = 11.5
    chart_reg.height = 7.5
    
    # References for Region Chart
    # Point directly to Region Table on Dashboard
    # Rows 18 to 22 (header + 4 regions)
    reg_data = Reference(ws_dash, min_col=3, min_row=18, max_row=22)
    reg_cats = Reference(ws_dash, min_col=2, min_row=19, max_row=22)
    chart_reg.add_data(reg_data, titles_from_data=True)
    chart_reg.set_categories(reg_cats)
    
    # Position on Dashboard
    ws_dash.add_chart(chart_reg, "G25")
    
    # Save Workbook
    output_path = "/Users/harisavala/ codeOrbit/ task3/sales_dashboard.xlsx"
    wb.save(output_path)
    print(f"Excel dashboard successfully saved to: {output_path}")

if __name__ == "__main__":
    create_excel_dashboard()

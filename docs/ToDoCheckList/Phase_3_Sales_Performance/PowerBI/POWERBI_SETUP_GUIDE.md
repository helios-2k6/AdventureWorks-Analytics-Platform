# Power BI Sales Performance Dashboard - Setup Guide

**Phase 3 Task: Connect Power BI to PostgreSQL Gold Layer & Build Dashboard**

**Status**: Ready to Execute  
**Dependencies**: Gold layer tables (completed)  
**Deliverables**: 
- `sales_performance_dashboard.pbix` (Power BI file)
- `phase3_dashboard_validation.md` (validation report)

---

## 📋 Table of Contents
1. [Prerequisites & Connections](#prerequisites--connections)
2. [Step 1: Connect Power BI to PostgreSQL](#step-1-connect-power-bi-to-postgresql)
3. [Step 2: Import Gold Layer Tables](#step-2-import-gold-layer-tables)
4. [Step 3: Create Data Model & Relationships](#step-3-create-data-model--relationships)
5. [Step 4: Build Dashboard Visualizations](#step-4-build-dashboard-visualizations)
6. [Step 5: Validate KPI Metrics](#step-5-validate-kpi-metrics)
7. [Step 6: Publish & Save](#step-6-publish--save)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites & Connections

### Required Software
- **Power BI Desktop** (latest version) - [Download Here](https://powerbi.microsoft.com/en-us/desktop/)
- PostgreSQL Driver for Power BI (usually installed with Power BI)
- Access to PostgreSQL database: `adventureworks_warehouse`

### Database Connection Details
```
Host:     localhost
Port:     5432
Database: adventureworks_warehouse
Schema:   gold
Username: (your PostgreSQL username)
Password: (your PostgreSQL password)
```

### Gold Layer Tables
| Table | Rows | Type | Purpose |
|-------|------|------|---------|
| `gold.dim_date` | 1,127 | Dimension | Date/calendar attributes |
| `gold.dim_customer` | 19,820 | Dimension | Customer profiles |
| `gold.dim_product` | 504 | Dimension | Product catalog |
| `gold.dim_territory` | 10 | Dimension | Sales territories |
| `gold.dim_salesperson` | 17 | Dimension | Sales representatives |
| `gold.fact_sales` | 121,317 | Fact | Sales transactions (line-item grain) |

---

## Step 1: Connect Power BI to PostgreSQL

### 1.1 Open Power BI Desktop
```
1. Launch Power BI Desktop
2. Select "Get Data" → Click "More..."
   OR: File → New → Get Data → Database → PostgreSQL Database
```

### 1.2 Enter Connection Details
In the **PostgreSQL Database** dialog:
```
Server:     localhost:5432
Database:   adventureworks_warehouse
Data Connectivity Mode: Import (recommended)
              OR: DirectQuery (for live data, slower dashboards)
```

**Recommendation**: Use **Import** mode for better performance.

### 1.3 Enter Credentials
```
Username: (your PostgreSQL user)
Password: (your PostgreSQL password)
☑ Save my password (optional)
```

Click **Connect**

### 1.4 Verify Connection
You should see the Navigator panel showing:
```
adventureworks_warehouse
├── Schemas
│   ├── bronze/
│   ├── gold/
│   │   ├── dim_date
│   │   ├── dim_customer
│   │   ├── dim_product
│   │   ├── dim_territory
│   │   ├── dim_salesperson
│   │   └── fact_sales
│   └── silver/
```

---

## Step 2: Import Gold Layer Tables

### 2.1 Select Tables to Import
In the Navigator panel:

**Check these boxes:**
```
☑ gold.dim_date
☑ gold.dim_customer
☑ gold.dim_product
☑ gold.dim_territory
☑ gold.dim_salesperson
☑ gold.fact_sales
```

### 2.2 Load Data
Click **Load** to import the selected tables.

**Expected Load Time**:
- Total rows: ~142K (dimensions + fact)
- ~5-30 seconds depending on machine

### 2.3 Verify Data Import
After loading, you should see in **Fields panel** (right side):
```
📊 Data
├── dim_date (1,127 rows)
├── dim_customer (19,820 rows)
├── dim_product (504 rows)
├── dim_territory (10 rows)
├── dim_salesperson (17 rows)
└── fact_sales (121,317 rows)
```

---

## Step 3: Create Data Model & Relationships

### 3.1 Open Model View
```
Home → Model View
  OR: Right-side panel icon showing tables
```

### 3.2 Create Relationships

**Relationship 1: Fact → Date**
```
FROM:  fact_sales.sales_date_key
TO:    dim_date.date_key
Type:  Many-to-One (1:*) ✓
```

**Relationship 2: Fact → Customer**
```
FROM:  fact_sales.customer_id
TO:    dim_customer.customer_id
Type:  Many-to-One (1:*) ✓
```

**Relationship 3: Fact → Product**
```
FROM:  fact_sales.product_id
TO:    dim_product.product_id
Type:  Many-to-One (1:*) ✓
```

**Relationship 4: Fact → Territory**
```
FROM:  fact_sales.territory_id
TO:    dim_territory.territory_id
Type:  Many-to-One (1:*) ✓
```

**Relationship 5: Fact → Salesperson**
```
FROM:  fact_sales.salesperson_id
TO:    dim_salesperson.salesperson_id
Type:  Many-to-One (1:*) ✓
```

### 3.3 Verify Relationships
After creating all 5 relationships, the model should show:
```
┌─────────────────────────────────┐
│                                 │
│    dim_date    dim_customer      │
│      ↑             ↑             │
│      │             │             │
│    dim_territory---fact_sales    │
│      ↑             ↑             │
│      │             │             │
│  dim_salesperson  dim_product    │
│                                 │
└─────────────────────────────────┘
```

---

## Step 4: Build Dashboard Visualizations

### 4.1 Create New Report Page
```
Home → New Page
  OR: Right-click "Page" tab → Duplicate Page
```

### 4.2 Dashboard Layout (Suggested)
Create 1 main page with these visualizations:

#### **ROW 1: Key Performance Indicators (Cards)**

**Card 1: Total Revenue**
```
Visual Type: Card
Field:       fact_sales.sales_amount (Sum)
Format:      $#,##0.00
Position:    Top-Left
Size:        1/3 width
```

**Card 2: Total Orders**
```
Visual Type: Card
Field:       fact_sales.sales_order_id (Distinct Count)
Format:      #,##0
Position:    Top-Center
Size:        1/3 width
```

**Card 3: Average Order Value (AOV)**
```
Visual Type: Card
Field:       fact_sales.sales_amount / fact_sales.sales_order_id (Distinct)
Format:      $#,##0.00
Position:    Top-Right
Size:        1/3 width
```

---

#### **ROW 2: Trend Charts**

**Chart 1: Revenue by Month**
```
Visual Type: Line Chart
X-Axis:      dim_date.month_name (or date hierarchy)
Y-Axis:      fact_sales.sales_amount (Sum)
Position:    Left (1/2 width)
```

**Chart 2: Orders by Territory**
```
Visual Type: Bar Chart (Horizontal)
X-Axis:      fact_sales.order_count (Count)
Y-Axis:      dim_territory.territory_name
Position:    Right (1/2 width)
```

---

#### **ROW 3: Breakdown Charts**

**Chart 3: Top 10 Products by Revenue**
```
Visual Type: Bar Chart (Vertical)
X-Axis:      dim_product.product_name
Y-Axis:      fact_sales.sales_amount (Sum)
Filters:     Top 10 by sales
Position:    Left (1/2 width)
```

**Chart 4: Revenue by Salesperson**
```
Visual Type: Bar Chart
X-Axis:      dim_salesperson.salesperson_name
Y-Axis:      fact_sales.sales_amount (Sum)
Position:    Right (1/2 width)
```

---

#### **ROW 4: Detailed Table**

**Table: Top 20 Customers by Order Count**
```
Visual Type: Table
Columns:
  - dim_customer.customer_name
  - COUNT(fact_sales.sales_order_id) as Orders
  - SUM(fact_sales.sales_amount) as Revenue
  - AVG(fact_sales.sales_amount) as Avg Order Value
Sort:        Orders Descending
Position:    Full width
```

---

### 4.3 Add Slicers (Filters)

**Slicer 1: Date Range**
```
Visual Type: Date Slicer
Field:       dim_date.date
Type:        Between dates
Position:    Top-Left corner
```

**Slicer 2: Territory**
```
Visual Type: Dropdown Slicer
Field:       dim_territory.territory_name
Type:        Multi-select
Position:    Top-Center
```

**Slicer 3: Product Category**
```
Visual Type: Dropdown Slicer
Field:       dim_product.category (if available)
Type:        Multi-select
Position:    Top-Right
```

---

## Step 5: Validate KPI Metrics

### 5.1 Compare Power BI Numbers with Gold Layer

After building the dashboard, verify these KPIs match the SQL baseline:

| KPI | Expected (Gold Layer) | Power BI Value | Match? |
|-----|----------------------|----------------|--------|
| Total Revenue | $109,846,100.22 | ? | ☐ |
| Total Orders | 31,465 | ? | ☐ |
| Total Line Items | 121,317 | ? | ☐ |
| Units Sold | 1,246,115 | ? | ☐ |
| Average Order Value | $3,490.14 | ? | ☐ |
| Avg Line Item Price | $88.01 | ? | ☐ |
| Avg Discount % | 0.03% | ? | ☐ |
| Unique Customers | 19,820 | ? | ☐ |
| Unique Salespeople | 17 | ? | ☐ |

**Acceptance Criteria**: All metrics within **±0.1%** of Gold layer baseline.

### 5.2 SQL Query for Manual Validation

Run this query to get the baseline KPIs:

```sql
-- Gold Layer KPI Validation
SELECT
  COUNT(DISTINCT sales_order_id) as total_orders,
  COUNT(*) as total_line_items,
  SUM(sales_amount) as total_revenue,
  SUM(order_quantity) as units_sold,
  ROUND(SUM(sales_amount) / COUNT(DISTINCT sales_order_id), 2) as avg_order_value,
  ROUND(SUM(sales_amount) / COUNT(*), 2) as avg_line_item_price,
  ROUND(AVG(unit_price_discount) * 100, 2) as avg_discount_pct,
  COUNT(DISTINCT customer_id) as unique_customers,
  COUNT(DISTINCT salesperson_id) as unique_salespeople
FROM gold.fact_sales;
```

Expected Output:
```
total_orders: 31465
total_line_items: 121317
total_revenue: 109846100.22
units_sold: 1246115
avg_order_value: 3490.14
avg_line_item_price: 88.01
avg_discount_pct: 0.03
unique_customers: 19820
unique_salespeople: 17
```

---

## Step 6: Publish & Save

### 6.1 Save Report
```
File → Save
Location: docs/reports/
Filename: sales_performance_dashboard.pbix
```

### 6.2 (Optional) Publish to Power BI Service
```
Home → Publish
Workspace: (select your workspace)
Destination: Your Power BI Service workspace
```

### 6.3 Git Commit
```powershell
cd "a:\Workspace\DataEngineer\AdventureWorks Analytics Platform"
git add docs/reports/sales_performance_dashboard.pbix
git commit -m "Phase 3: Add Power BI dashboard"
git push origin feature/phase3-sales-performance
```

---

## Troubleshooting

### ❌ Problem: PostgreSQL Connection Failed
**Solutions:**
1. Verify PostgreSQL is running: `docker ps | findstr postgres`
2. Check credentials in `.env` file
3. Test connection: `psql -h localhost -U postgres -d adventureworks_warehouse`
4. Check Windows Firewall allows port 5432

### ❌ Problem: Tables Not Showing in Navigator
**Solutions:**
1. Ensure schema is set to `gold` in connection
2. Refresh: Navigator → Refresh
3. Check user has SELECT permissions on gold schema
4. Try different data connectivity mode (Import vs DirectQuery)

### ❌ Problem: Relationships Not Auto-Creating
**Solutions:**
1. Check column names match exactly (case-sensitive in some systems)
2. Verify data types are compatible (int → int)
3. Create relationships manually in Model View
4. Check foreign key constraints in PostgreSQL

### ❌ Problem: Dashboard Metrics Don't Match SQL
**Solutions:**
1. Check for filters applied (slicers)
2. Verify relationships are correctly configured
3. Check for NULL values in key columns
4. Run manual validation query (see Step 5.2)
5. Check aggregation functions (Sum vs Average)

### ❌ Problem: Slow Performance
**Solutions:**
1. Use **Import** mode instead of DirectQuery
2. Close other applications to free memory
3. Reduce date range in slicers
4. Check fact table row count (should be 121,317)

---

## Checklist: Before Committing

- [ ] All 6 Gold tables imported successfully
- [ ] All 5 relationships created and verified
- [ ] Dashboard has 8+ visualizations
- [ ] All KPI metrics match Gold layer (±0.1%)
- [ ] Slicers functional (Date, Territory, Product)
- [ ] File saved as `sales_performance_dashboard.pbix`
- [ ] File saved in `docs/reports/` folder
- [ ] No error messages in Power BI
- [ ] Manual validation query run and confirmed

---

## Next Steps

1. **Complete Dashboard Building** → Use steps 4.1-4.3 above
2. **Validate KPI Metrics** → Compare with SQL (Step 5)
3. **Save & Commit** → Follow Step 6
4. **Merge to Dev** → After code review
5. **Update CheckList.md** → Mark tasks as Done

---

## Reference Files

- **Gold Layer SQL**: `scripts/warehouse/postgres/gold/sales_gold_load.py`
- **KPI Validation**: `scripts/warehouse/postgres/gold/validate_sales_kpis.py`
- **Documentation**: `docs/ToDoCheckList/Phase_3_Sales_Performance/`
- **Repository**: https://github.com/helios-2k6/AdventureWorks-Analytics-Platform

---

**Questions or Issues?** Check Phase 3 documentation or run:
```powershell
cd scripts/warehouse/postgres/gold
python validate_sales_kpis.py  # Get expected KPI baseline
```

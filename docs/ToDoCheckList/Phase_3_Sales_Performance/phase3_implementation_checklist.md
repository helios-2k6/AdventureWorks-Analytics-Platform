# Phase 3 — Implementation Checklist

> Detailed task tracker for Phase 3 Sales Performance implementation

---

## Phase 3.1 — Bronze Extraction (Sales source tables)

### 3.1.1 Bronze Script Setup

- [x] Create `scripts/ingestion/bronze/sales_bronze_load.py`
  - Import required libraries: pyodbc, psycopg2, sqlalchemy, logging
  - Create function: `get_sqlserver_connection()`
  - Create function: `get_postgres_connection()`
  - Create function: `extract_table(table_name, query)` — read from SQL Server
  - Create function: `add_lineage_metadata(df, source_table, load_date)` — add 4 cols
  - Create function: `load_to_bronze(df, bronze_table_name)` — write to PostgreSQL

- [x] Implement error handling and logging
  - Log extract start/end times
  - Log row counts before/after
  - Log any extraction errors
---

## Phase 3.2 — Silver Transformation (Clean & standardize)

### 3.2.1 Silver Script Setup

- [x] Create `scripts/transformation/silver/sales_silver_clean.py`
  - Import libraries: sqlalchemy, pandas, psycopg2, logging
  - Create warehouse connection and Silver loading flow
  - Create table-specific cleaning functions and validation-ready outputs

- [x] Implement error handling and logging
  - Preserve source and target row counts in run results
  - Fail fast when the warehouse connection or source table is unavailable

### 3.2.2 Clean sales_order_header

- [ ] SQL: Create `silver.sales_order_header_clean` from `bronze.sales_order_header`
  - SELECT with transformations:
    - `CAST(OrderDate AS DATE)`
    - `CAST(DueDate AS DATE)`
    - `CAST(ShipDate AS DATE)`
    - `CAST(SubTotal AS NUMERIC(10, 2))`
    - `CAST(TaxAmt AS NUMERIC(10, 2))`
    - `CAST(Freight AS NUMERIC(10, 2))`
    - `CAST(TotalDue AS NUMERIC(10, 2))`
    - Standardize and deduplicate on `SalesOrderID`
  - Validate no duplicate `SalesOrderID`
  - Validate no critical NULLs on `OrderDate`, `CustomerID`, `SalesPersonID`

### 3.2.3 Clean sales_order_detail

- [ ] SQL: Create `silver.sales_order_detail_clean` from `bronze.sales_order_detail`
  - Standardize numeric fields and compute line totals
  - Join to header to retain order date and status information
  - Validate duplicates on `SalesOrderDetailID`

### 3.2.4 Clean customer

- [ ] SQL: Create `silver.customer_clean` from `bronze.customer`
  - Standardize names and account references
  - Validate no duplicate `CustomerID`

### 3.2.5 Clean sales_territory, sales_person, and product

- [ ] Create Silver versions for territory, salesperson, and product
  - Validate counts and key constraints
  - Use the Bronze tables as source data

---

## Phase 3.2 — Silver Transformation (Clean & standardize)

### 3.2.1 Silver Script Setup

- [ ] Create `scripts/transformation/silver/sales_silver_clean.py`
  - Import libraries: sqlalchemy, pandas, psycopg2, logging
  - Create function: `connect_warehouse()` → PostgreSQL
  - Create function: `clean_table(table_name, business_rules)` → SQL transforms
  - Create function: `load_silver_table(sql_query, target_table)` → write to silver schema
  - Create function: `validate_silver(table_name, row_count_before, row_count_after)` → QA

### 3.2.2 Clean sales_order_header

- [ ] SQL: Create `silver.sales_order_header_clean` from `bronze.sales_order_header`
  - SELECT with transformations:
    - `CAST(OrderDate AS DATE)` — ISO format
    - `CAST(DueDate AS DATE)` — ISO format
    - `CAST(ShipDate AS DATE)` — ISO format
    - `CAST(SubTotal AS NUMERIC(10, 2))` — standardize precision
    - `CAST(TaxAmt AS NUMERIC(10, 2))`
    - `CAST(Freight AS NUMERIC(10, 2))`
    - `CAST(TotalDue AS NUMERIC(10, 2))`
    - `TRIM(SalesOrderNumber) AS SalesOrderNumber` — remove spaces
    - `Status AS order_status` — rename for clarity
  - WHERE: exclude test/cancelled orders (business rule TBD)
  - DISTINCT ON: SalesOrderID (keep latest if duplicates exist)
  - Add computed columns:
    - `DATEDIFF(day, OrderDate, ShipDate) AS days_to_ship`
    - `CASE WHEN Status = 'Shipped' THEN 1 ELSE 0 END AS is_shipped`

- [ ] Validate:
  - Row count: silver should be ≤ bronze (same after dedup)
  - No duplicates on SalesOrderID
  - No NULLs on OrderDate, CustomerID, SalesPersonID (critical)
  - Document validation results

### 3.2.3 Clean sales_order_detail

- [ ] SQL: Create `silver.sales_order_detail_clean` from `bronze.sales_order_detail`
  - SELECT with transformations:
    - All numeric fields cast to NUMERIC(10, 2) or (12, 4)
    - `TRIM(ProductName)` if exists
    - `OrderQty AS order_qty`, `UnitPrice AS unit_price` — standardize naming
    - Add computed columns:
      - `OrderQty * UnitPrice AS line_total_calc` (verify against LineTotal)
      - `LineTotal - DiscountAmount AS net_sales`
      - `CASE WHEN DiscountAmount > 0 THEN DiscountAmount / LineTotal ELSE 0 END AS discount_pct`
  - WHERE: exclude rows where OrderQty = 0 or UnitPrice = 0
  - JOIN: `silver.sales_order_header_clean` on SalesOrderID to inherit OrderDate, Status
  - DISTINCT ON: SalesOrderDetailID

- [ ] Validate:
  - Row count: should be ~121K (or less if business rules filter)
  - No duplicates on SalesOrderDetailID
  - Verify line_total_calc ≈ LineTotal (within rounding error)
  - Verify net_sales > 0 for all rows (or 0 if fully discounted)
  - Document validation results

### 3.2.4 Clean customer

- [ ] SQL: Create `silver.customer_clean` from `bronze.customer`
  - SELECT with transformations:
    - `CustomerID` — PK
    - `TRIM(UPPER(SUBSTRING(CustomerName, 1, 1))) + LOWER(SUBSTRING(CustomerName, 2)) AS customer_name` — proper case
    - `CustomerType` — business / individual (standardize if needed)
    - `SalesPersonID` — FK to salesperson
    - `TerritoryID` — FK to territory (may be NULL for some customers)
    - `AccountNumber` — account reference
    - Leave postal code, country, phone as-is
  - WHERE: exclude deleted/inactive customers (if column exists)
  - DISTINCT ON: CustomerID

- [ ] Validate:
  - Row count: should be ~20K
  - No duplicates on CustomerID
  - No NULLs on customer_name (critical)
  - Document validation results

### 3.2.5 Clean sales_territory

- [ ] SQL: Create `silver.sales_territory_clean` from `bronze.sales_territory`
  - SELECT with transformations:
    - `TerritoryID` — PK
    - `TRIM(Name) AS territory_name` — remove spaces
    - `Country` — standardized country name
    - `Region` — state/province
    - Group — business group (e.g., "North America", "Europe")
  - DISTINCT ON: TerritoryID

- [ ] Validate:
  - Row count: should be ~10
  - No duplicates on TerritoryID
  - No NULLs on territory_name
  - Document validation results

### 3.2.6 Clean sales_person

- [ ] SQL: Create `silver.sales_person_clean` from `bronze.sales_person`
  - SELECT with transformations:
    - `SalesPersonID` — PK
    - `BusinessEntityID` — reference to person entity (for joining to full name)
    - `TerritoryID` — FK to territory
    - LEFT JOIN to `bronze.person` on BusinessEntityID to get full name
    - `CONCAT(FirstName, ' ', LastName) AS salesperson_name`
    - `EmailAddress`, `Phone` — contact info
    - `CommissionPct` — commission percentage
  - DISTINCT ON: SalesPersonID

- [ ] Validate:
  - Row count: should be ~17
  - No duplicates on SalesPersonID
  - No NULLs on salesperson_name, TerritoryID
  - Document validation results

### 3.2.7 Clean product

- [ ] SQL: Create `silver.product_clean` from `bronze.product`
  - SELECT with transformations:
    - `ProductID` — PK
    - `TRIM(Name) AS product_name` — standardize
    - `ProductNumber` — SKU
    - `Category AS product_category` (need to categorize from hierarchy)
    - `SubCategory AS product_subcategory`
    - `ListPrice` — standard price
    - `Color` — product color (may be NULL)
    - `Size` — product size (may be NULL)
    - `StandardCost` — cost
  - WHERE: include both active and discontinued products (business rule: flag if discontinued)
  - DISTINCT ON: ProductID

- [ ] Validate:
  - Row count: should be ~504
  - No duplicates on ProductID
  - No NULLs on product_name, ListPrice
  - Document validation results

### 3.2.8 Silver Validation Summary

- [x] Run aggregate quality checks:
  ```sql
  SELECT 'sales_order_header' AS table_name, COUNT(*) AS row_count, COUNT(DISTINCT SalesOrderID) AS unique_keys
  UNION ALL
  SELECT 'sales_order_detail', COUNT(*), COUNT(DISTINCT SalesOrderDetailID)
  UNION ALL
  SELECT 'customer', COUNT(*), COUNT(DISTINCT CustomerID)
  UNION ALL
  SELECT 'sales_territory', COUNT(*), COUNT(DISTINCT TerritoryID)
  UNION ALL
  SELECT 'sales_person', COUNT(*), COUNT(DISTINCT SalesPersonID)
  UNION ALL
  SELECT 'product', COUNT(*), COUNT(DISTINCT ProductID)
  FROM silver.*;
  ```

- [x] Document results in `docs/ToDoCheckList/Phase_3_Sales_Performance/phase3_silver_validation.md`
  - Result: PASS; all six row counts match Bronze, keys are unique, required NULL counts are zero, and all defined joins have zero orphan rows.

### 3.2.9 Silver Commit

- [ ] Commit code and validation results
  - Message: "Phase 3.2: Silver cleaning and standardization for sales domain"
  - Include: scripts/transformation/silver/sales_silver_clean.py
  - Include: phase3_silver_validation.md

---

## Phase 3.3 — Gold Star Schema (Fact & dimensions)

### 3.3.1 Create Gold Dimensions

- [x] Create `gold.dim_date` (calendar dimension)
  - Grain: 1 row per day
  - Date range: 2004-01-01 to 2025-12-31 (or based on sales data range)
  - Columns: date_id, date, year, quarter, month, month_name, week, day_of_week, day_name, is_holiday, is_weekend
  - PK: date_id
  - Index on: date

- [x] Create `gold.dim_customer` from `silver.customer_clean`
  - Grain: 1 row per unique customer
  - Columns: customer_id (PK), customer_name, customer_type, territory_id (FK), country, postal_code, account_number
  - Index on: customer_name, territory_id

- [x] Create `gold.dim_product` from `silver.product_clean`
  - Grain: 1 row per unique product
  - Columns: product_id (PK), product_name, product_category, product_subcategory, list_price, color, size, standard_cost
  - Index on: product_name, product_category, product_subcategory

- [x] Create `gold.dim_territory` from `silver.sales_territory_clean`
  - Grain: 1 row per unique territory
  - Columns: territory_id (PK), territory_name, country, region, group_name
  - Index on: territory_name

- [x] Create `gold.dim_salesperson` from `silver.sales_person_clean`
  - Grain: 1 row per unique salesperson
  - Columns: salesperson_id (PK), salesperson_name, email_address, phone, territory_id (FK)
  - FK constraint: territory_id → gold.dim_territory(territory_id)
  - Index on: salesperson_name, territory_id

### 3.3.2 Create Gold Fact Table

- [x] Create `gold.fact_sales` from `silver.sales_order_detail_clean` + `silver.sales_order_header_clean`
  - Grain: 1 row = 1 sales order line item
  - PK: sales_order_detail_id (surrogate, or use source SalesOrderDetailID)
  - FKs: order_date_id → dim_date, customer_id → dim_customer, product_id → dim_product, territory_id → dim_territory, salesperson_id → dim_salesperson
  - Dimensions:
    - sales_order_id
    - order_date_id
    - customer_id
    - product_id
    - territory_id
    - salesperson_id
  - Measures:
    - order_qty
    - unit_price
    - line_total
    - discount_amount
    - net_sales
    - discount_pct (calculated)
    - effective_price (calculated)
  - Source SQL:
    ```sql
    SELECT
        sod.SalesOrderDetailID AS sales_order_detail_id,
        sod.SalesOrderID AS sales_order_id,
        DATE_PART('year', soh.OrderDate)::INT * 10000 + 
        DATE_PART('month', soh.OrderDate)::INT * 100 + 
        DATE_PART('day', soh.OrderDate)::INT AS order_date_id, -- YYYYMMDD format
        soh.CustomerID AS customer_id,
        sod.ProductID AS product_id,
        soh.TerritoryID AS territory_id,
        soh.SalesPersonID AS salesperson_id,
        sod.order_qty,
        sod.unit_price,
        sod.line_total_calc AS line_total,
        sod.DiscountAmount AS discount_amount,
        sod.net_sales,
        sod.discount_pct
    FROM silver.sales_order_detail_clean sod
    JOIN silver.sales_order_header_clean soh
      ON sod.SalesOrderID = soh.SalesOrderID
    ORDER BY soh.OrderDate, sod.SalesOrderDetailID;
    ```

- [x] Add FK constraints:
  - `ALTER TABLE gold.fact_sales ADD FOREIGN KEY (order_date_id) REFERENCES gold.dim_date(date_id)`
  - `ALTER TABLE gold.fact_sales ADD FOREIGN KEY (customer_id) REFERENCES gold.dim_customer(customer_id)`
  - `ALTER TABLE gold.fact_sales ADD FOREIGN KEY (product_id) REFERENCES gold.dim_product(product_id)`
  - `ALTER TABLE gold.fact_sales ADD FOREIGN KEY (territory_id) REFERENCES gold.dim_territory(territory_id)`
  - `ALTER TABLE gold.fact_sales ADD FOREIGN KEY (salesperson_id) REFERENCES gold.dim_salesperson(salesperson_id)`

- [ ] Add indexes for query performance:
  - `CREATE INDEX idx_fact_sales_order_date ON gold.fact_sales(order_date_id)`
  - `CREATE INDEX idx_fact_sales_customer ON gold.fact_sales(customer_id)`
  - `CREATE INDEX idx_fact_sales_product ON gold.fact_sales(product_id)`
  - `CREATE INDEX idx_fact_sales_territory ON gold.fact_sales(territory_id)`
  - `CREATE INDEX idx_fact_sales_salesperson ON gold.fact_sales(salesperson_id)`

### 3.3.3 Gold Validation

- [ ] Grain validation: count rows in fact_sales
  - Should equal row count in `silver.sales_order_detail_clean` (100%)
  - Run: `SELECT COUNT(*) FROM gold.fact_sales` → expect ~121K

- [ ] FK referential integrity checks
  - Run: `SELECT COUNT(*) FROM gold.fact_sales WHERE customer_id NOT IN (SELECT customer_id FROM gold.dim_customer)`
  - Should return 0 (no orphaned FKs)
  - Repeat for all dimensions

- [ ] Dimension row counts
  - `gold.dim_date`: ~8000 rows (2004-2024)
  - `gold.dim_customer`: ~20K rows
  - `gold.dim_product`: ~504 rows
  - `gold.dim_territory`: ~10 rows
  - `gold.dim_salesperson`: ~17 rows

- [ ] Fact table measure validation
  - Min/max net_sales should be reasonable
  - Sum of net_sales should match total revenue
  - No negative quantities or prices (unless business rule)

- [x] Document validation results in `phase3_gold_validation.md`

### 3.3.4 Gold Schema Commit

- [ ] Commit DDL and validation scripts
  - Message: "Phase 3.3: Gold star schema for sales domain"
  - Include: scripts/warehouse/postgres/schema/04_create_sales_gold_schema.sql
  - Include: phase3_gold_validation.md
  - Include: sample queries for dimension/fact validation

---

## Phase 3.4 — Validation & BI Dashboard

### 3.4.1 KPI Calculation & Validation

- [x] Calculate expected KPIs manually from Silver baseline data
  - Total revenue (sum net_sales)
  - Total orders (count distinct order_id)
  - Average order value
  - Revenue by territory
  - Top 10 products by revenue
  - Discount rate
  - Customer count

- [x] Run KPI queries against Gold schema
  ```sql
  -- Total Revenue
  SELECT SUM(net_sales) AS total_revenue FROM gold.fact_sales;
  
  -- Total Orders
  SELECT COUNT(DISTINCT sales_order_id) AS total_orders FROM gold.fact_sales;
  
  -- Average Order Value
  SELECT SUM(net_sales) / COUNT(DISTINCT sales_order_id) AS avg_order_value FROM gold.fact_sales;
  
  -- Revenue by Territory
  SELECT t.territory_name, SUM(f.net_sales) AS revenue
  FROM gold.fact_sales f
  JOIN gold.dim_territory t ON f.territory_id = t.territory_id
  GROUP BY t.territory_id, t.territory_name
  ORDER BY revenue DESC;
  
  -- Top 10 Products
  SELECT p.product_name, SUM(f.net_sales) AS revenue, SUM(f.order_qty) AS qty
  FROM gold.fact_sales f
  JOIN gold.dim_product p ON f.product_id = p.product_id
  GROUP BY p.product_id, p.product_name
  ORDER BY revenue DESC
  LIMIT 10;
  ```

- [x] Compare Gold KPIs to expected values (within ±2% tolerance)
  - Document comparison in `phase3_kpi_validation.md`
  - Flag any discrepancies > 2%

- [x] Create summary report
  - Include: all KPI calculations
  - Include: comparison to expected values
  - Include: any variance explanations
  - Result: PASS; all nine KPIs have 0% variance against the independent Silver baseline.

### 3.4.2 Power BI Connection & Dashboard

- [ ] Connect Power BI to PostgreSQL Gold layer
  - Create connection to postgresql://localhost/warehouse
  - Select tables: fact_sales, dim_customer, dim_product, dim_date, dim_territory, dim_salesperson
  - Import data or set up live connection

- [ ] Create Sales Performance dashboard with visualizations:
  - **Card**: Total Revenue
  - **Card**: Total Orders
  - **Card**: Average Order Value
  - **Clustered Column Chart**: Revenue by Month (line chart with order count overlay)
  - **Map or Table**: Revenue by Territory
  - **Bar Chart**: Top 10 Products by Revenue
  - **Clustered Column Chart**: Revenue by Salesperson
  - **Table**: Top Customers by Revenue
  - **Gauge**: Discount Rate (%) — expect 5-10%

- [ ] Validate dashboard metrics match KPI calculations from 3.4.1
  - Compare Power BI numbers to SQL results
  - Flag any discrepancies

- [ ] Save Power BI file
  - Location: `docs/reports/sales_performance_dashboard.pbix`
  - Include: data model diagram

### 3.4.3 Unit & Integration Tests

- [ ] Create `tests/test_sales_gold.py`
  - Test grain of fact_sales table
    - Assert: COUNT(*) = COUNT(DISTINCT sales_order_detail_id)
    - Assert: COUNT(*) = row count in silver.sales_order_detail_clean
  - Test FK referential integrity
    - Assert: no orphaned customer_id
    - Assert: no orphaned product_id
    - Assert: no orphaned territory_id
  - Test measure logic
    - Assert: line_total > 0 for all rows
    - Assert: net_sales > 0 for all rows (or 0 if discounted to 0)
    - Assert: discount_pct between 0 and 1

- [ ] Create `tests/test_sales_kpi.py`
  - Test KPI calculations
    - Assert: total_revenue > 0
    - Assert: total_orders == COUNT(DISTINCT sales_order_id)
    - Assert: avg_order_value = total_revenue / total_orders
    - Assert: revenue_by_territory.sum() == total_revenue

- [ ] Run all tests
  ```
  pytest tests/test_sales_*.py -v
  ```

- [ ] Document test results

### 3.4.4 Code Review & Merge

- [ ] Peer review of Phase 3 code
  - Review scripts/ folder for quality
  - Review tests/ folder for coverage
  - Review docs/ folder for clarity
  - Review git commits for messages and history

- [ ] Address any review comments

- [ ] Create pull request from feature/phase3-sales-performance to dev
  - Title: "Phase 3: Sales Performance domain implementation"
  - Description: link to phase3_analysis.md and checklist
  - Include: screenshots of Power BI dashboard

- [ ] Merge to dev after approval
  ```
  git switch dev
  git merge --no-ff feature/phase3-sales-performance -m "Merge Phase 3: Sales Performance into dev"
  git push origin dev
  ```

- [ ] Delete feature branch
  ```
  git branch -d feature/phase3-sales-performance
  git push origin --delete feature/phase3-sales-performance
  ```

---

## Phase 3 Summary

### Deliverables Checklist
- [x] Phase 3 Analysis document (phase3_analysis.md)
- [ ] Phase 3 Implementation Checklist (this file)
- [ ] Bronze extraction code and validation
- [ ] Silver transformation code and validation
- [ ] Gold schema (DDL and data loads)
- [ ] KPI validation report
- [ ] Power BI dashboard
- [ ] Unit tests (min 80% coverage)
- [ ] Code review completed
- [ ] Feature branch merged to dev

### Definition of Done
✅ All items in the checklist above are completed and reviewed before Phase 3 is considered DONE.

### Next Phase
After Phase 3 is complete and merged to dev:
- Phase 4 — Domain 2: Customer Analysis (follows same pattern)
- Phase 5 — Domain 3: Production / Inventory
- Phase 6 — Domain 4: Purchasing / Supplier
- Phase 7 — Orchestration & Automation
- Phase 8 — Testing, CI/CD & Documentation

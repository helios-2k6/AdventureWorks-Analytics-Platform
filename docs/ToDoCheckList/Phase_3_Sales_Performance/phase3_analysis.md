# Phase 3 — Domain 1: Sales Performance — Analysis & Plan

> Draft analysis for Phase 3 Sales Performance domain implementation

## 1. Phase 3 Objectives

**Primary Goal**: Implement the first complete end-to-end pipeline for the **Sales domain** using the medallion architecture (Bronze → Silver → Gold) approved in Phase 2.

**Deliverables**:
1. Raw data extraction and Bronze ingestion for 6 source tables
2. Cleaned and standardized Silver layer with business rules
3. Gold fact_sales table with 5 dimension tables
4. Power BI dashboard with key sales KPIs
5. Unit and integration tests for pipeline correctness

**Success Criteria**:
- All 6 source tables are loaded to Bronze with metadata lineage
- Silver layer has clean, deduplicated data with proper joins
- Gold fact_sales grain is exactly "1 row = 1 sales order line item"
- KPI calculations are validated against business requirements
- Feature branch is merged to dev after review

---

## 2. Data Flow Overview

```
SQL Server AdventureWorks (OLTP)
    ├── Sales.SalesOrderHeader
    ├── Sales.SalesOrderDetail
    ├── Sales.Customer
    ├── Sales.SalesTerritory
    ├── Sales.SalesPerson
    └── Production.Product
            |
            | Extract (Phase 3.1)
            v
    PostgreSQL - bronze
    ├── bronze.sales_order_header
    ├── bronze.sales_order_detail
    ├── bronze.customer
    ├── bronze.sales_territory
    ├── bronze.sales_person
    └── bronze.product
            |
            | Clean + Standardize (Phase 3.2)
            v
    PostgreSQL - silver
    ├── silver.sales_order_header_clean
    ├── silver.sales_order_detail_clean
    ├── silver.customer_clean
    ├── silver.sales_territory_clean
    ├── silver.sales_person_clean
    └── silver.product_clean
            |
            | Build Star Schema (Phase 3.3)
            v
    PostgreSQL - gold
    ├── gold.fact_sales
    ├── gold.dim_customer
    ├── gold.dim_product
    ├── gold.dim_date
    ├── gold.dim_territory
    └── gold.dim_salesperson
            |
            | Connect to BI (Phase 3.4)
            v
    Power BI Dashboard
```

---

## 3. Source Tables & Schema Mapping

### 3.1 Source Tables to Extract (6 tables)

| Source Table | Row Count* | Schema | Purpose | Key Column |
|---|---|---|---|---|
| `Sales.SalesOrderHeader` | ~31K | Header | Order-level facts | `SalesOrderID` |
| `Sales.SalesOrderDetail` | ~121K | Detail | Line-item facts | `SalesOrderDetailID` |
| `Sales.Customer` | ~20K | Dimension | Customer info | `CustomerID` |
| `Sales.SalesTerritory` | ~10 | Dimension | Territory info | `TerritoryID` |
| `Sales.SalesPerson` | ~17 | Dimension | Salesperson info | `SalesPersonID` |
| `Production.Product` | ~504 | Dimension | Product info | `ProductID` |

*Row counts from Phase 1 profiling results*

### 3.2 Source-to-Target Bronze Mapping

| Source | Bronze Table | Lineage Columns | Note |
|---|---|---|---|
| `Sales.SalesOrderHeader` | `bronze.sales_order_header` | _source_system, _source_table, _load_date, _record_hash | Raw copy with metadata |
| `Sales.SalesOrderDetail` | `bronze.sales_order_detail` | _source_system, _source_table, _load_date, _record_hash | Raw copy with metadata |
| `Sales.Customer` | `bronze.customer` | _source_system, _source_table, _load_date, _record_hash | Raw copy with metadata |
| `Sales.SalesTerritory` | `bronze.sales_territory` | _source_system, _source_table, _load_date, _record_hash | Raw copy with metadata |
| `Sales.SalesPerson` | `bronze.sales_person` | _source_system, _source_table, _load_date, _record_hash | Raw copy with metadata |
| `Production.Product` | `bronze.product` | _source_system, _source_table, _load_date, _record_hash | Raw copy with metadata |

---

## 4. Layer Design & Responsibilities

### 4.1 Bronze Layer Tasks

**Responsibility**: Raw ingest with lineage, no transformation

**Input**: Extract from SQL Server source tables

**Output**: 6 bronze tables with metadata

**Transformations**:
- NONE — copy data as-is
- Add 4 lineage columns: `_source_system`, `_source_table`, `_load_date`, `_record_hash`
- Set proper data types to match source

**Quality Checks**:
- Row count validation: extract count == bronze count
- Column count validation: source columns == bronze columns + 4 lineage cols
- Data type consistency
- NULL handling (preserve source NULLs)

**Considerations**:
- Decide: full refresh or incremental? (Phase 3 = full refresh for MVP)
- Add primary keys on source IDs
- Consider indexing on SalesOrderID, CustomerID for performance

---

### 4.2 Silver Layer Tasks

**Responsibility**: Clean, standardize, deduplicate, join for analytics

**Input**: Bronze tables

**Output**: 6 silver tables (clean and joined)

**Transformations per table**:

#### `silver.sales_order_header_clean`
- Remove or flag cancelled orders (if needed by business)
- Convert dates to ISO format (YYYY-MM-DD)
- Standardize numeric precision (amount fields to 2 decimals)
- Remove duplicates on (SalesOrderID) — keep latest if found
- Add computed columns: `is_returned`, `days_to_ship`

#### `silver.sales_order_detail_clean`
- Remove rows where `OrderQty` = 0 or `UnitPrice` = 0
- Calculate `LineTotal = OrderQty * UnitPrice`
- Calculate `NetSales = LineTotal - DiscountAmount`
- Remove duplicates on (SalesOrderDetailID)
- Join to `silver.sales_order_header_clean` to inherit order-level fields (OrderDate, Status, OnlineOrderFlag)

#### `silver.customer_clean`
- Standardize name fields (trim, uppercase first letter)
- Remove or flag duplicate customers on (CustomerID)
- Join to `bronze.person` to get PersonID and full name if CustomerType = 'I' (individual)
- Add standardized `customer_name` field

#### `silver.sales_territory_clean`
- Trim territory names
- Standardize country/region names
- Remove duplicates on (TerritoryID)

#### `silver.sales_person_clean`
- Join to `bronze.person` to get full name and contact info
- Standardize name fields
- Remove duplicates on (SalesPersonID)
- Add `sales_person_name` field

#### `silver.product_clean`
- Standardize product names (trim, remove extra spaces)
- Standardize category and subcategory
- Remove discontinued products (if business rule) OR flag them
- Remove duplicates on (ProductID)
- Join to source product hierarchies if needed

**Quality Checks**:
- Row count comparison: silver ≥ bronze (should be ≈ due to dedup)
- NULL summary: identify critical NULLs that should have been filled
- Duplicate check: count distinct on key fields
- Join validation: verify no rows were lost during joins

---

### 4.3 Gold Layer Tasks

**Responsibility**: Build fact and dimension tables for analytics

**Input**: Silver tables

**Output**: 1 fact table + 5 dimension tables

#### `gold.fact_sales`

**Grain**: 1 row = 1 sales order line item (transaction-level)

**Key Fields**:
- `sales_order_detail_id` (PK, surrogate if needed)
- `sales_order_id` (FK to order)
- `order_date_id` (FK to dim_date)
- `customer_id` (FK to dim_customer)
- `product_id` (FK to dim_product)
- `territory_id` (FK to dim_territory)
- `salesperson_id` (FK to dim_salesperson)

**Measures**:
- `order_qty` (quantity ordered)
- `unit_price` (list price)
- `line_total` (qty * price)
- `discount_amount` (discount)
- `net_sales` (line_total - discount)

**Calculated Fields**:
- `discount_pct` = discount_amount / line_total
- `effective_price` = unit_price * (1 - discount_pct)

**Source**: Join `silver.sales_order_detail_clean` + `silver.sales_order_header_clean`

#### Dimension Tables

**`gold.dim_date`**
- Grain: 1 row = 1 calendar day
- Fields: `date_id`, `date`, `year`, `quarter`, `month`, `week`, `day_of_week`, `is_holiday`, `is_weekend`
- Source: Generate from date range (2004-01-01 to future date) OR extract from silver sales_order_header_clean
- Indexes: PK on `date_id`, index on `date`

**`gold.dim_customer`**
- Grain: 1 row = 1 unique customer
- Fields: `customer_id`, `customer_name`, `customer_type` (individual/store), `country`, `postal_code`, `account_number`
- Source: `silver.customer_clean`
- Indexes: PK on `customer_id`, index on `customer_name`

**`gold.dim_product`**
- Grain: 1 row = 1 unique product
- Fields: `product_id`, `product_name`, `product_category`, `product_subcategory`, `list_price`, `color`, `size`
- Source: `silver.product_clean`
- Indexes: PK on `product_id`, index on `product_name`, `product_category`

**`gold.dim_territory`**
- Grain: 1 row = 1 unique territory
- Fields: `territory_id`, `territory_name`, `country`, `region`, `group`
- Source: `silver.sales_territory_clean`
- Indexes: PK on `territory_id`, index on `territory_name`

**`gold.dim_salesperson`**
- Grain: 1 row = 1 unique salesperson
- Fields: `salesperson_id`, `salesperson_name`, `email_address`, `phone`, `territory_id` (FK to dim_territory)
- Source: `silver.sales_person_clean` + join to `silver.sales_territory_clean`
- Indexes: PK on `salesperson_id`, FK index on `territory_id`

---

## 5. KPI Logic (for validation in Phase 3.4)

**Sales KPIs to validate after Gold load**:

| KPI | Formula | Grain | Example |
|---|---|---|---|
| **Total Revenue** | SUM(net_sales) | Overall | $12.4M |
| **Total Orders** | COUNT(DISTINCT sales_order_id) | Overall | 31K |
| **Total Line Items** | COUNT(*) in fact_sales | Overall | 121K |
| **Average Order Value** | SUM(net_sales) / COUNT(DISTINCT sales_order_id) | Overall | $400 |
| **Avg Item Price** | SUM(unit_price * order_qty) / SUM(order_qty) | Product | $50 |
| **Revenue by Month** | SUM(net_sales) GROUP BY MONTH(order_date) | Time | Jan: $1.2M, Feb: $950K, … |
| **Revenue by Territory** | SUM(net_sales) GROUP BY territory_name | Territory | NA: $5.2M, EU: $3.1M, … |
| **Top 10 Products** | SUM(net_sales) GROUP BY product_name ORDER BY SUM DESC LIMIT 10 | Product | Road-250 Red 52: $2.1M, … |
| **Discount Rate** | SUM(discount_amount) / SUM(line_total) | Overall | 5.2% |
| **Customer Count** | COUNT(DISTINCT customer_id) | Overall | 20K |

---

## 6. Implementation Strategy

### 6.1 Phased Approach (Sub-phases within Phase 3)

1. **Phase 3.1 — Bronze Extraction** (2-3 days)
   - Create extraction scripts for 6 source tables
   - Implement incremental/full refresh logic
   - Validate row counts and data types
   - Commit to feature branch

2. **Phase 3.2 — Silver Transformation** (3-4 days)
   - Create cleaning and standardization SQL
   - Implement deduplication logic
   - Add join logic for related tables
   - Validate data quality metrics
   - Commit to feature branch

3. **Phase 3.3 — Gold Star Schema** (2-3 days)
   - Build fact_sales with proper grain
   - Build 5 dimension tables
   - Create indexes and FKs
   - Validate fact table grain and row counts
   - Commit to feature branch

4. **Phase 3.4 — Validation & BI** (2-3 days)
   - Connect Power BI to Gold layer
   - Build sales dashboard with KPIs
   - Validate KPI numbers against expectations
   - Write unit tests for transform logic
   - Merge feature branch to dev

### 6.2 Code Organization

```
scripts/
├── source/
│   └── sqlserver/
│       └── extraction/
│           └── sales_extract.py
├── ingestion/
│   └── bronze/
│       └── sales_bronze_load.py
├── transformation/
│   ├── silver/
│   │   └── sales_silver_clean.py
│   └── gold/
│       └── sales_gold_build.py
└── warehouse/
    └── postgres/
        ├── schema/
        │   └── 04_create_sales_gold_schema.sql
        └── validation/
            └── sales_validation.sql

tests/
├── test_sales_bronze.py
├── test_sales_silver.py
└── test_sales_gold.py

docs/
└── ToDoCheckList/
    └── Phase_3_Sales_Performance/
        ├── phase3_analysis.md (THIS FILE)
        ├── phase3_implementation_checklist.md
        └── phase3_kpi_validation.md
```

---

## 7. Risk Mitigation

| Risk | Mitigation |
|---|---|
| Data quality issues in Silver layer | Implement row-level validation in Silver; log skipped rows |
| Grain mismatch in fact_sales | Test with sample data; compare line-item count to source detail table |
| Missing FKs in Gold dimensions | Add FK constraints at build time; test for referential integrity |
| Performance bottlenecks in joins | Index on foreign keys; profile query performance on 121K rows |
| Discrepancies in KPI calculations | Pre-calculate expected KPIs manually from source; compare to Gold results |

---

## 8. Definition of Done for Phase 3

- [ ] All 6 Bronze tables are loaded with metadata lineage
- [ ] Row counts match between source and Bronze (100%)
- [ ] All Silver tables are cleaned, deduplicated, and joined
- [ ] Deduplication logic is validated (no unexpected row loss)
- [ ] Gold fact_sales is built at transaction-level grain (121K rows)
- [ ] All 5 Gold dimensions are built and indexed
- [ ] Referential integrity is validated (no broken FKs)
- [ ] All KPIs are calculated and validated against expectations
- [ ] Power BI Desktop is installed and PostgreSQL connection configured
- [ ] Power BI dashboard is connected and displays correct metrics
- [ ] Unit tests pass for all transform steps
- [ ] Code is peer-reviewed
- [ ] Feature branch is merged to dev

---

## 9. Prerequisites & Dependencies

### Required Tools
- ✅ Python 3.8+ with pyodbc, psycopg2, pandas, sqlalchemy
- ✅ SQL Server AdventureWorks2012 database (Phase 0)
- ✅ PostgreSQL Docker container running (Phase 0)
- ⚠️ **Power BI Desktop** — Required for Phase 3.4 (BI dashboard)
  - If not installed, download from [Microsoft Power BI](https://powerbi.microsoft.com/en-us/desktop/)
  - Need PostgreSQL ODBC driver for connection

### Data Prerequisites
- Phase 1: Source tables profiled and documented
- Phase 2: Architecture and DDL scripts finalized
- Bronze schemas created in PostgreSQL

---

## 10. Next Steps (Immediate)

1. **Verify Power BI Desktop is installed** (required for 3.4)
2. **Create Phase 3 implementation checklist** with task breakdown and owners
3. **Start Phase 3.1 — Bronze Extraction** with sales_extract.py script
4. **Set up PostgreSQL Gold schema** (DDL already exists from Phase 2)
5. **Establish KPI validation spreadsheet** for manual pre-calculation
6. **Begin writing tests** alongside implementation

---

## Appendix: Reference Links

- [Phase 2 Architecture Spec](../Phase_2_Architecture_Spec_Finalization/phase2_architecture_spec.md)
- [Phase 2 Star Schema](../Phase_2_Architecture_Spec_Finalization/phase2_star_schema.md)
- [Project Checklist](../CheckList.md)
- [Phase 1 Data Dictionary](../Phase_1_Data_Discovery_Profiling/Explain_To_Do.md)
- [Phase 3 Implementation Checklist](phase3_implementation_checklist.md)

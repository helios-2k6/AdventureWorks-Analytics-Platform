# Phase 2 — Architecture & Spec Finalization

> Final review-ready version for architecture sign-off before implementation begins.

## 1. Objective of Phase 2

Phase 2 is not the first domain ETL implementation. This is the stage where the overall architecture is designed to ensure that:

- data flows correctly from the OLTP source into the warehouse
- Bronze / Silver / Gold schemas remain consistent
- fact tables and dimension tables are defined with the correct grain
- business KPIs can be built on the right model
- the architecture does not need to be redesigned multiple times once pipeline implementation begins

In short:

Phase 2 = “building the architecture foundation before implementing the pipeline and dashboards”.

---

## 2. Proposed overall architecture

### 2.1 Data flow

```text
SQL Server AdventureWorks2012 (OLTP)
          |
          | Extract
          v
PostgreSQL - bronze
          |
          | Clean + standardize + dedupe + business rules
          v
PostgreSQL - silver
          |
          | Build star schema / KPI-ready tables
          v
PostgreSQL - gold
          |
          | Power BI / reporting
          v
Dashboards
```

### 2.2 Responsibilities by layer

#### Bronze layer
- Keeps the raw data from the source unchanged
- Avoids heavy business-rule transformations
- Adds lineage metadata:
  - `_source_system`
  - `_source_table`
  - `_load_date`
  - `_record_hash` (if needed)
- Goal: preserve raw data in a traceable and recoverable form

#### Silver layer
- Cleans and standardizes data
- Handles nulls, duplicates, data types, column naming, and mapping rules
- Can join multiple tables to prepare data for analytics
- Goal: data is ready for fact and dimension construction

#### Gold layer
- Creates fact tables and dimension tables
- Serves dashboards and KPI logic
- Optimizes reporting queries for BI use
- Goal: fast, accurate, and business-ready analytics at the correct grain

---

## 3. Proposed naming convention

### 3.1 Schemas

```text
bronze.<table_name>

silver.<table_name>

gold.fact_<subject>
gold.dim_<entity>
```

Examples:

- `bronze.sales_order_header`
- `silver.sales_order_header_clean`
- `gold.fact_sales`
- `gold.dim_customer`
- `gold.dim_product`
- `gold.dim_date`

### 3.2 Table naming and data types

- Fact table: `fact_<domain>`
- Dimension table: `dim_<entity>`
- Aggregate summary: `agg_<metric>` or `summary_<name>`

---

## 4. Source-to-target mapping

### 4.1 Sales domain

| Source table | Bronze | Silver | Gold |
|---|---|---|---|
| `Sales.SalesOrderHeader` | `bronze.sales_order_header` | `silver.sales_order_header_clean` | `fact_sales` |
| `Sales.SalesOrderDetail` | `bronze.sales_order_detail` | `silver.sales_order_detail_clean` | `fact_sales` |
| `Sales.Customer` | `bronze.customer` | `silver.customer_clean` | `dim_customer` |
| `Sales.SalesTerritory` | `bronze.sales_territory` | `silver.sales_territory_clean` | `dim_territory` |
| `Sales.SalesPerson` | `bronze.sales_person` | `silver.sales_person_clean` | `dim_salesperson` |
| `Production.Product` | `bronze.product` | `silver.product_clean` | `dim_product` |
| `Person.Person` | `bronze.person` | `silver.person_clean` | `dim_customer` / `dim_salesperson` |

### 4.2 Customer domain

| Source table | Bronze | Silver | Gold |
|---|---|---|---|
| `Sales.Customer` | `bronze.customer` | `silver.customer_clean` | `dim_customer` |
| `Sales.SalesOrderHeader` | `bronze.sales_order_header` | `silver.sales_order_header_clean` | `fact_customer_orders` |
| `Sales.SalesOrderDetail` | `bronze.sales_order_detail` | `silver.sales_order_detail_clean` | `fact_customer_orders` |
| `Person.Person` | `bronze.person` | `silver.person_clean` | `dim_customer` |

### 4.3 Production / Inventory domain

| Source table | Bronze | Silver | Gold |
|---|---|---|---|
| `Production.Product` | `bronze.product` | `silver.product_clean` | `dim_product` |
| `Production.WorkOrder` | `bronze.work_order` | `silver.work_order_clean` | `fact_production` |
| `Production.TransactionHistory` | `bronze.transaction_history` | `silver.transaction_history_clean` | `fact_inventory` |
| `Production.ProductInventory` | `bronze.product_inventory` | `silver.product_inventory_clean` | `fact_inventory` |
| `Production.Location` | `bronze.location` | `silver.location_clean` | `dim_location` |

### 4.4 Purchasing / Supplier domain

| Source table | Bronze | Silver | Gold |
|---|---|---|---|
| `Purchasing.PurchaseOrderHeader` | `bronze.purchase_order_header` | `silver.purchase_order_header_clean` | `fact_purchasing` |
| `Purchasing.PurchaseOrderDetail` | `bronze.purchase_order_detail` | `silver.purchase_order_detail_clean` | `fact_purchasing` |
| `Purchasing.Vendor` | `bronze.vendor` | `silver.vendor_clean` | `dim_vendor` |
| `Production.Product` | `bronze.product` | `silver.product_clean` | `dim_product` |

---

## 5. Gold schema proposal

### 5.1 Sales star schema

#### Fact table
- `gold.fact_sales`

Proposed key fields:
- `sales_order_id`
- `order_date_id`
- `customer_id`
- `product_id`
- `territory_id`
- `salesperson_id`
- `order_qty`
- `unit_price`
- `line_total`
- `discount_amount`
- `net_sales`

#### Dimension tables
- `gold.dim_customer`
- `gold.dim_product`
- `gold.dim_date`
- `gold.dim_territory`
- `gold.dim_salesperson`

#### Grain
- 1 row = 1 sales order line item (transaction-level grain)

#### KPI examples
- total revenue
- total orders
- AOV (average order value)
- sales by month
- sales by territory
- product performance

---

### 5.2 Customer star schema

#### Fact table
- `gold.fact_customer_orders`

Key fields:
- `customer_id`
- `order_id`
- `order_date_id`
- `product_id`
- `sales_amount`
- `order_qty`
- `is_returned`

#### Dimension tables
- `gold.dim_customer`
- `gold.dim_date`
- `gold.dim_product`

#### Derived metrics
- RFM score
- customer lifetime value
- new vs returning customer
- retention rate

---

### 5.3 Production / Inventory star schema

#### Fact tables
- `gold.fact_production`
- `gold.fact_inventory`

Key fields:
- `product_id`
- `location_id`
- `date_id`
- `work_order_id`
- `quantity_on_hand`
- `transaction_qty`
- `unit_cost`
- `scrap_qty`
- `completion_date`

#### Dimension tables
- `gold.dim_product`
- `gold.dim_location`
- `gold.dim_date`

#### KPI examples
- stockout risk
- inventory turnover
- production completion rate
- on-time completion rate
- scrap rate

---

### 5.4 Purchasing / Supplier star schema

#### Fact table
- `gold.fact_purchasing`

Key fields:
- `vendor_id`
- `product_id`
- `po_id`
- `date_id`
- `quantity`
- `unit_cost`
- `total_cost`
- `received_qty`
- `lead_time_days`

#### Dimension tables
- `gold.dim_vendor`
- `gold.dim_product`
- `gold.dim_date`

#### KPI examples
- total purchase cost
- on-time delivery rate
- average lead time
- vendor performance

---

## 6. ERD / schema concept

### 6.1 High-level model

```text
Source OLTP (AdventureWorks)
   |
   +--> bronze.*
   |       raw tables
   |
   +--> silver.*
   |       cleaned and standardized tables
   |
   +--> gold.fact_sales
   |       + gold.dim_customer
   |       + gold.dim_product
   |       + gold.dim_date
   |       + gold.dim_territory
   |       + gold.dim_salesperson
   |
   +--> gold.fact_customer_orders
   |       + gold.dim_customer
   |       + gold.dim_date
   |
   +--> gold.fact_inventory
   |       + gold.dim_product
   |       + gold.dim_location
   |
   +--> gold.fact_purchasing
           + gold.dim_vendor
           + gold.dim_product
           + gold.dim_date
```

### 6.2 Grain rules

- `Fact_sales`: 1 row per order line
- `Fact_customer_orders`: 1 row per order/customer interaction
- `Fact_inventory`: 1 row per product / location / date or transaction
- `Fact_purchasing`: 1 row per purchase order line

The grain must be explicitly documented before writing DDL to avoid incorrect metrics.

---

## 7. DDL and implementation approach

### 7.1 DDL scripts

Phase 2 should create DDL files such as:

```text
scripts/schema/
  01_create_bronze_schemas.sql
  02_create_silver_schemas.sql
  03_create_gold_schemas.sql
  04_create_fact_sales.sql
  05_create_dim_customer.sql
  06_create_dim_product.sql
  07_create_dim_date.sql
  08_create_fact_inventory.sql
  09_create_fact_purchasing.sql
```

### 7.2 DDL design standards

- schema names must be consistent
- PK / FK relationships must be clear
- `surrogate keys` are preferred for dimensions over natural keys
- `dim_date` should include complete calendar fields
- `fact_*` tables should store measures and FKs to dimensions
- `null` values should be handled in Silver before data reaches Gold

---

## 8. Business rules to confirm before coding

Before ETL implementation, the business or reviewer should agree on the following:

1. Is `Fact_sales` grain line-level or order-level?
2. Should `Customer` dimensions include additional information from `Person.Person`?
3. How should `dim_date` be generated: from source date fields or a separate calendar table?
4. Is a `dim_location` table needed for inventory?
5. Which KPIs are mandatory in the Gold layer?
6. How should `null`, `duplicate`, and `invalid date` cases be handled by default?

Without these decisions, the model can be wrong from the start.

---

## 9. Proposed exit criteria for Phase 2

Phase 2 is considered complete only when all of the following conditions are met:

- [ ] Warehouse architecture has been approved
- [ ] Bronze / Silver / Gold schemas are clearly defined
- [ ] Fact and dimension tables are mapped for all 4 domains
- [ ] Grain for each fact table is explicitly documented
- [ ] Naming convention is consistent across warehouse schemas and tables
- [ ] ERD or star schema diagrams are stored in the Phase 2 folder
- [ ] DDL scripts for warehouse objects are ready to run in PostgreSQL
- [ ] Architecture is approved before Phase 3 begins

---

## 10. Final conclusion

This Phase 2 architecture proposes a clear and practical data model:

- Source OLTP AdventureWorks2012
- Bronze keeps raw data
- Silver cleans and standardizes data
- Gold builds fact and dimension tables for BI
- Each domain has its own star schema, but all follow the same architecture framework

This is the architecture baseline to start Phase 3 implementation without repeatedly redesigning the model.

> This document has been marked as final review-ready. If grain, KPI, or naming convention changes in the future, it should be updated before real code implementation begins.

---

## 11. Final sign-off checklist

- [x] Warehouse architecture reviewed
- [x] Bronze / Silver / Gold responsibilities confirmed
- [x] Gold schema proposals defined for all four domains
- [x] Grain decisions documented
- [x] Naming convention aligned
- [x] DDL scripts drafted for PostgreSQL
- [x] Phase 2 ready for Phase 3 implementation

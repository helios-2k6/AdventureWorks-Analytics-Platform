# Business Spec — AdventureWorks2012 Analytics Platform

## 1. Project Overview

**Project name:** AdventureWorks Analytics Platform (AWAP)

**Problem statement:** AdventureWorks is a bicycle manufacturing and distribution company. Leadership needs a centralized analytics platform (Data Warehouse) to support decision-making across 4 business areas: Sales, Customer, Production/Inventory, and Purchasing/Supplier.

**Data source:** SQL Server — `AdventureWorks2012` database (OLTP, already available).

**Target:** A Data Warehouse on Postgres following the Medallion architecture (Bronze → Silver → Gold), feeding reports in Power BI. All code is version-controlled on Git, with automated orchestration and test coverage.

**Tooling:** VS Code + AI (Copilot/Claude), Python (pandas/PySpark), SQL Server, Postgres, Power BI, Git, Airflow/Prefect (orchestration), pytest, Docker, GitHub Actions (CI/CD).

**Domain delivery order:**
1. Sales Performance
2. Customer Analysis
3. Production / Inventory
4. Purchasing / Supplier

---

## 2. Technical Architecture

```
┌─────────────────┐
│  SQL Server      │  AdventureWorks2012 (source OLTP)
│  (Source)        │
└────────┬─────────┘
         │ Extract (Python: pyodbc/sqlalchemy)
         ▼
┌─────────────────┐
│  BRONZE          │  Raw data, original schema preserved, plus
│  (Postgres)      │  _load_date, _source_system columns for lineage
└────────┬─────────┘
         │ Transform (pandas / PySpark): clean, dedupe, standardize
         ▼
┌─────────────────┐
│  SILVER          │  Cleaned data, joined, correct data types,
│  (Postgres)      │  business rules applied, still at detailed grain
└────────┬─────────┘
         │ Load (Star Schema build)
         ▼
┌─────────────────┐
│  GOLD            │  Fact + Dimension tables, optimized for BI,
│  (Postgres)      │  KPIs pre-aggregated where useful
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Power BI        │  Dashboards per domain
└─────────────────┘

Orchestration: Airflow/Prefect coordinates the full pipeline (schedule, retry, logging, alerting)
CI/CD: GitHub Actions runs tests on every push/PR
```

**Postgres schema naming convention:**
- `bronze.<source_table_name>`
- `silver.<cleaned_table_name>`
- `gold.fact_<subject>`, `gold.dim_<entity>`

---

## 3. Business Questions & KPIs per Domain

### Domain 1 — Sales Performance
**Business questions:**
- How does revenue trend by month/quarter/year, by region, by product line?
- Which products generate the highest sales volume / profitability?
- Which sales reps perform best?
- How do order patterns (order size, frequency) change over time?

**Key KPIs:** Total Revenue, Order Count, Average Order Value, Revenue Growth %, Top N Products, Sales by Territory

**Related source tables:** `Sales.SalesOrderHeader`, `SalesOrderDetail`, `Product`, `SalesTerritory`, `SalesPerson`

**Expected Gold output:** `fact_sales`, `dim_product`, `dim_customer`, `dim_date`, `dim_territory`, `dim_salesperson`

---

### Domain 2 — Customer Analysis
**Business questions:**
- How can customers be segmented by purchasing behavior (RFM: Recency, Frequency, Monetary)?
- What is the retention rate vs. new customer rate over time?
- Which customers have the highest Customer Lifetime Value (CLV)?

**Key KPIs:** Customer Count, New vs Returning Customer, RFM Segment, Customer Lifetime Value, Churn Rate

**Related source tables:** `Sales.Customer`, `Person.Person`, `SalesOrderHeader`

**Expected Gold output:** `fact_customer_orders`, `dim_customer` (extended with RFM segment), plus an aggregate table `gold.customer_rfm_summary`

---

### Domain 3 — Production / Inventory
**Business questions:**
- What is the current inventory level by warehouse/product? Any stockout or overstock risk?
- Are production work orders completed on time?
- How is raw material cost trending?

**Key KPIs:** Inventory Level, Stockout Rate, Work Order On-Time %, Scrap Rate, Production Cost

**Related source tables:** `Production.Product`, `WorkOrder`, `TransactionHistory`, `ProductInventory`, `Location`

**Expected Gold output:** `fact_inventory`, `fact_production`, `dim_product`, `dim_location`, `dim_date`

---

### Domain 4 — Purchasing / Supplier
**Business questions:**
- Which vendors offer the best cost / most reliable on-time delivery?
- How does purchase cost trend over time and by vendor?
- Should the company consolidate purchasing to fewer vendors (dependency risk)?

**Key KPIs:** Total Purchase Cost, Vendor On-Time Delivery %, Average Lead Time, Cost per Vendor

**Related source tables:** `Purchasing.PurchaseOrderHeader`, `PurchaseOrderDetail`, `Vendor`, `ProductVendor`

**Expected Gold output:** `fact_purchasing`, `dim_vendor`, `dim_product`, `dim_date`

---

## 4. Phase Roadmap

### Phase 0 — Environment & Repo Setup
- [ ] Create Git repo, standard folder structure (src/, tests/, docs/, notebooks/)
- [ ] `.gitignore`, `requirements.txt`, initial `README.md`
- [ ] Docker Compose for local Postgres
- [ ] Connect VS Code ↔ SQL Server ↔ Postgres (test connection)
- **Definition of Done:** Repo pushed to GitHub, both DBs reachable from a Python script

### Phase 1 — Data Discovery & Profiling *(already started)*
- [ ] Run scripts to list tables, row counts, sizes
- [ ] Inspect column structure and data types
- [ ] Map foreign-key relationships per domain
- [ ] Document findings in `docs/data_dictionary.md`
- **DoD:** Complete documentation of source tables for all 4 domains

### Phase 2 — Architecture & Spec Finalization
- [ ] Finalize the business spec (this document)
- [ ] Design a detailed ERD for the Gold layer (star schema) per domain
- [ ] Set up Bronze/Silver/Gold schemas in Postgres (DDL scripts)
- **DoD:** DDL scripts runnable, ERD drawn (dbdiagram.io or draw.io)

### Phase 3 — Domain 1: Sales Performance (Bronze → Gold → BI)
- [ ] Extract: Python script reading Sales.* tables from SQL Server → Bronze
- [ ] Transform: clean + join → Silver
- [ ] Load: build fact_sales + dimensions → Gold
- [ ] Unit tests for transform logic (pytest)
- [ ] Power BI: connect to Gold, build Sales dashboard
- [ ] Git: branch `feature/domain-sales`, PR, merge, tag `v0.1-sales`
- **DoD:** Sales dashboard running in Power BI, tests passing, code merged to main

### Phase 4 — Domain 2: Customer Analysis
- [ ] Extract/Transform/Load (reuse framework from Phase 3)
- [ ] Compute RFM segmentation (Python logic)
- [ ] Power BI Customer dashboard
- [ ] Git tag `v0.2-customer`
- **DoD:** Customer dashboard working, RFM segments displaying correctly

### Phase 5 — Domain 3: Production/Inventory
- [ ] Extract/Transform/Load
- [ ] Power BI Inventory/Production dashboard
- [ ] Git tag `v0.3-production`
- **DoD:** Production dashboard working

### Phase 6 — Domain 4: Purchasing/Supplier
- [ ] Extract/Transform/Load
- [ ] Power BI Purchasing dashboard
- [ ] Git tag `v0.4-purchasing`
- **DoD:** Purchasing dashboard working

### Phase 7 — Orchestration & Automation
- [ ] Set up Airflow (or Prefect) — a DAG running the full pipeline across all 4 domains
- [ ] Configure scheduling, retry, logging, failure alerts
- [ ] Dockerize the full pipeline
- **DoD:** A single command (or trigger) runs the full Bronze-to-Gold pipeline for all 4 domains

### Phase 8 — Testing, CI/CD & Documentation
- [ ] Unit test coverage for all transform logic
- [ ] GitHub Actions: run tests automatically on push/PR
- [ ] Complete README: architecture, setup instructions, dashboard screenshots
- [ ] Final tag `v1.0`
- **DoD:** Repo is fully self-contained — anyone cloning it can run it, README is complete, CI is green

---

## 5. Success Criteria (Final Target)

- ✅ Public Git repo with a clear commit history per phase/domain
- ✅ Full 3-tier Data Warehouse (Bronze/Silver/Gold) on Postgres
- ✅ 4 working Power BI dashboards connected directly to the Gold layer
- ✅ Pipeline runs automatically via an orchestration tool
- ✅ Test coverage in place, CI/CD passing
- ✅ README complete enough for someone else (e.g., a recruiter) to understand and re-run the project

---

## 6. Notes
- Each domain should be completed end-to-end (Bronze→Gold→BI) before moving to the next one, to avoid spreading effort too thin.
- Phase 7 (Orchestration) is intentionally scheduled after at least 2 domains are done, so there's an actual pipeline worth orchestrating.
- Prioritize "working" over "polished/optimized" early on — avoid over-engineering from the start.

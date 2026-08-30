# AdventureWorks Analytics Platform — Phase Checklist

This file stores the actionable task checklist for each phase. Use it as the working execution tracker.

Status legend:
- [ ] Not started
- [ ] In progress
- [x] Done

---

## Phase 0 — Environment & Foundation

### Repo & project setup
- [x] Confirm repository structure for the new AdventureWorks project
- [x] Keep repo separate from the old Python project
- [x] Create .gitignore
- [x] Create README.md
- [x] Create .env.example
- [x] Create requirements.txt
- [x] Create docker-compose.yml for PostgreSQL
- [x] Create folder structure: src/, tests/, docs/, notebooks/, scripts/, config/

### Python environment
- [x] Create virtual environment
- [x] Install Python dependencies
- [x] Validate Python version compatibility
- [x] Test import of required libraries

### SQL Server connectivity
- [x] Confirm AdventureWorks2012 database is available
- [x] Validate SQL Server server name / instance / credentials
- [x] Create connection config for SQL Server
- [x] Test a simple query against AdventureWorks2012
- [x] Inspect metadata for key tables

### PostgreSQL connectivity
- [x] Start local PostgreSQL instance via Docker
- [x] Create target database for the warehouse
- [x] Create schemas: bronze, silver, gold
- [x] Validate connection from Python to PostgreSQL

### Bronze ingestion test
- [ ] Select a first source table (example: Sales.Customer)
- [ ] Extract sample data from SQL Server
- [ ] Load raw data into Bronze schema
- [ ] Add lineage columns: _load_date, _source_system
- [ ] Validate row counts
- [ ] Validate data types and null handling
- [ ] Document the successful raw-load test

### Definition of Done for Phase 0
- [x] SQL Server connect works
- [x] PostgreSQL connect works
- [ ] Bronze raw load works for at least one source table
- [ ] Project foundation is stable enough to begin Phase 1

---

## Phase 1 — Data Discovery & Profiling

### Source inventory
- [ ] List all major tables in relevant domains
- [ ] Review row counts and table sizes
- [ ] Review schema for Sales, Customer, Production, Purchasing tables
- [ ] Identify key fact tables and dimension tables

### Column profiling
- [ ] Review table columns and types
- [ ] Check null proportions and anomalies
- [ ] Flag duplicate or inconsistent values
- [ ] Check date ranges and key patterns

### Relationship mapping
- [ ] Map primary keys and foreign keys
- [ ] Review joins between core tables
- [ ] Document business relationships between entities

### Data dictionary
- [ ] Create a source-to-target mapping document
- [ ] Create a data dictionary for key tables
- [ ] Document assumptions and business rules

### Deliverables
- [ ] Profiling scripts
- [ ] Schema inventory report
- [ ] Data dictionary
- [ ] Source-to-target notes

---

## Phase 2 — Architecture & Spec Finalization

- [ ] Finalize warehouse design
- [ ] Define Bronze/Silver/Gold schemas
- [ ] Create DDL scripts for warehouse tables
- [ ] Define Gold star schema for Sales
- [ ] Define Gold star schema for Customer
- [ ] Define Gold star schema for Production / Inventory
- [ ] Define Gold star schema for Purchasing / Supplier
- [ ] Draw ERD or star schema diagrams
- [ ] Validate architecture with business stakeholders

---

## Phase 3 — Domain 1: Sales Performance

### Source extraction
- [ ] Extract SalesOrderHeader
- [ ] Extract SalesOrderDetail
- [ ] Extract Product
- [ ] Extract Customer
- [ ] Extract Territory
- [ ] Extract SalesPerson

### Bronze layer
- [ ] Load raw sales tables into bronze
- [ ] Add loading metadata
- [ ] Validate source row counts

### Silver layer
- [ ] Clean sales data
- [ ] Normalize date fields
- [ ] Standardize names and categories
- [ ] Handle nulls and duplicates
- [ ] Join relevant entities

### Gold layer
- [ ] Build fact_sales
- [ ] Build dim_product
- [ ] Build dim_customer
- [ ] Build dim_date
- [ ] Build dim_territory
- [ ] Build dim_salesperson
- [ ] Validate grain and KPI logic

### BI and validation
- [ ] Connect Power BI to Gold layer
- [ ] Create sales dashboard
- [ ] Validate KPI numbers
- [ ] Write unit tests
- [ ] Merge feature branch into dev

---

## Phase 4 — Domain 2: Customer Analysis

- [ ] Extract customer and order history data
- [ ] Load to Bronze
- [ ] Clean and join customer data
- [ ] Build customer dimension and fact tables
- [ ] Compute RFM segmentation
- [ ] Compute CLV logic
- [ ] Create customer dashboard
- [ ] Validate segment quality
- [ ] Merge feature branch into dev

---

## Phase 5 — Domain 3: Production / Inventory

- [ ] Extract Production and Inventory tables
- [ ] Load to Bronze
- [ ] Build Silver datasets
- [ ] Build fact_inventory and fact_production
- [ ] Build dim_product and dim_location
- [ ] Compute stockout / overstock indicators
- [ ] Build dashboard
- [ ] Validate business KPIs
- [ ] Merge feature branch into dev

---

## Phase 6 — Domain 4: Purchasing / Supplier

- [ ] Extract vendor and purchasing tables
- [ ] Load to Bronze
- [ ] Clean and join purchasing data
- [ ] Build fact_purchasing
- [ ] Build dim_vendor and dim_product
- [ ] Compute supplier KPIs
- [ ] Build dashboard
- [ ] Validate cost and timing metrics
- [ ] Merge feature branch into dev

---

## Phase 7 — Orchestration & Automation

- [ ] Choose orchestration tool: Airflow or Prefect
- [ ] Create DAG / pipeline definition
- [ ] Set schedule and retry logic
- [ ] Add logging and failure alerts
- [ ] Run full pipeline end-to-end
- [ ] Validate orchestration success
- [ ] Dockerize key components

---

## Phase 8 — Testing, CI/CD & Documentation

- [ ] Add unit tests for transform logic
- [ ] Add integration tests for load scripts
- [ ] Create GitHub Actions workflow
- [ ] Validate CI passes on push/PR
- [ ] Update README with project setup instructions
- [ ] Add architecture explanation and screenshots
- [ ] Finalize project documentation
- [ ] Tag final release (example: v1.0)

---

## Working Notes
- We should not start domain-specific analytics before Phase 0 is completed
- We should validate each phase before moving to the next one
- If scope or architecture changes, update both Plan.md and this checklist
- This file should be the main execution tracker during project work

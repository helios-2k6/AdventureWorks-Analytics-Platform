# AdventureWorks Analytics Platform — Phase Checklist

This file stores the actionable task checklist for each phase. Use it as the working execution tracker.

Status legend:
- [ ] Not started
- [ ] In progress
- [x] Done

## Shared working rules for all phases, sessions, and environments
This is the project operating standard. It applies across any chat, tool session, terminal, or working environment. Use it as the default way we plan, execute, review, and confirm work.

- Scope must be agreed before execution.
- Every task must have a clear output, owner, and evidence.
- Before starting a task, the task scope, expected result, and acceptance criteria must be explicit.
- If a task is ambiguous, it must be marked as Needs clarification before any detailed work begins.
- Progress is reviewed and confirmed before moving to the next step.
- Status values: Not started / In progress / Done / Blocked / Needs clarification.
- No phase is considered complete without review and explicit confirmation.
- If there is no clear owner or acceptance rule, the task is not ready for execution.
- These rules apply in every session and environment; they are not limited to one chat, one tool, or one phase.

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
- [x] Select a first source table (example: Sales.Customer)
- [x] Extract sample data from SQL Server
- [x] Load raw data into Bronze schema
- [x] Add lineage columns: _load_date, _source_system
- [x] Validate row counts
- [x] Validate data types and null handling
- [x] Document the successful raw-load test

### Definition of Done for Phase 0
- [x] SQL Server connect works
- [x] PostgreSQL connect works
- [x] Bronze raw load works for at least one source table
- [x] Project foundation is stable enough to begin Phase 1

---

## Phase 1 — Data Discovery & Profiling

### Phase 1 task tracker

| Main task | Item task | Output / deliverable | Status | Confirm (Y/N) | Owner | Notes | Evidence | Dependencies |
|---|---|---|---|---|---|---|---|---|
| Source inventory | List major tables in Sales, Customer, Production, Purchasing | Source inventory list | Done | Y | AI / User | Key AdventureWorks tables identified | SQL metadata + report | SQL Server access |
| Source inventory | Review row counts and table sizes | Table size summary | Done | Y | AI / User | Row counts captured for Sales/Person/Production/Purchasing | Phase1_Data_Discovery_Report.md | Source list |
| Source inventory | Review schema for Sales, Customer, Production, Purchasing tables | Schema review notes | Done | Y | AI / User | Main columns/types reviewed for key tables | Metadata query / report | Source list |
| Source inventory | Identify key fact tables and dimension tables | Fact/dimension shortlist | Done | Y | AI / User | Sales orders, customer, product, purchase order, production work order identified | Report + data dictionary | Schema review |
| Column profiling | Review table columns and types | Column profile summary | Done | Y | AI / User | Top business tables profiled with metadata columns | Report and script output | Source list |
| Column profiling | Check null proportions and anomalies | Null/anomaly summary | In progress | N | AI / User | Next step: validate nulls on critical columns | Profiling output | Source tables |
| Column profiling | Flag duplicate or inconsistent values | Data quality issues list | In progress | N | AI / User | Need targeted validation on customer/product keys | Findings notes | Source tables |
| Column profiling | Check date ranges and key patterns | Date range / key validation | In progress | N | AI / User | Focus on date fields and IDs | Query output | Source tables |
| Relationship mapping | Map primary keys and foreign keys | PK/FK mapping | Done | Y | AI / User | Relationship mapping captured from metadata | Phase1_Data_Discovery_Report.md | Schema review |
| Relationship mapping | Review joins between core tables | Join mapping notes | Done | Y | AI / User | Base joins documented for sales, production, purchasing | Report / dictionary | PK/FK map |
| Relationship mapping | Document business relationships between entities | Business relationship summary | Done | Y | AI / User | Relationship summary added to report | Report / notes doc | Join mapping |
| Data dictionary | Create source-to-target mapping document | Source-to-target matrix | In progress | N | AI / User | Draft mapping exists in business context, to be formalized | Notes doc | Source inventory |
| Data dictionary | Create data dictionary for key tables | Key table dictionary | Done | Y | AI / User | Data dictionary created for major entities | docs/data_dictionary_phase1.md | Profiling outputs |
| Data dictionary | Document assumptions and business rules | Assumptions log | Done | Y | AI / User | Included in data dictionary | data_dictionary_phase1.md | Source understanding |
| Deliverables | Prepare profiling scripts | Reusable SQL/Python scripts | Done | Y | AI / User | Script created for source profiling | scripts/validation/source_profile.py | Profiling tasks |
| Deliverables | Prepare schema inventory report | Inventory report | Done | Y | AI / User | Inventory report generated | docs/Phase1_Data_Discovery_Report.md | Source inventory |
| Deliverables | Prepare data dictionary document | Data dictionary doc | Done | Y | AI / User | Final draft generated | docs/data_dictionary_phase1.md | Data dictionary |
| Deliverables | Prepare source-to-target notes | Source-to-target notes | In progress | N | AI / User | Final review before Phase 2 | Notes doc | Mapping + dictionary |

### Phase 1 exit criteria
- Required source tables are inventoried
- Core schema and row-count profiling is documented
- Business relationships and keys are mapped
- Key data dictionary entries exist
- Deliverables are reviewed and approved before moving to Phase 2

---
---

## Phase 2 — Architecture & Spec Finalization

### Phase 2 task tracker

| Main task | Item task | Output / deliverable | Status | Confirm (Y/N) | Owner | Notes | Evidence | Dependencies |
|---|---|---|---|---|---|---|---|---|
| Warehouse architecture | Finalize source-to-target architecture | Architecture flow and layer design | Done | Y | AI / User | Source → Bronze → Silver → Gold → Power BI approved | phase2_architecture_spec.md | Phase 1 profiling results |
| Warehouse architecture | Define Bronze / Silver / Gold responsibilities | Layer design notes | Done | Y | AI / User | Bronze raw retention, Silver cleaning, Gold KPI-ready model | Architecture spec | Source inventory |
| Schema design | Define naming conventions | Naming standard for schemas and tables | Done | Y | AI / User | `bronze.*`, `silver.*`, `gold.fact_*`, `gold.dim_*` | Architecture spec | Layer design |
| Schema design | Define Sales star schema | Sales fact + dimensions | Done | Y | AI / User | Fact sales plus customer/product/date/territory/salesperson dims | Architecture spec | Source relationships |
| Schema design | Define Customer star schema | Customer fact + dimensions | Done | Y | AI / User | Fact customer orders and customer/date/product dimensions | Architecture spec | Source relationships |
| Schema design | Define Production / Inventory schema | Production + inventory fact tables | Done | Y | AI / User | Fact production and fact inventory with dim product/location/date | Architecture spec | Source relationships |
| Schema design | Define Purchasing / Supplier schema | Purchasing fact + dimensions | Done | Y | AI / User | Fact purchasing with vendor/product/date dims | Architecture spec | Source relationships |
| Data modeling | Define grain for each fact table | Grain definition per domain | Done | Y | AI / User | Sales line-item, customer order event, inventory balance/movement, purchasing line-item | Architecture spec | Domain design |
| Data modeling | Draw ERD / star schema diagram | Diagram and schema docs | Done | Y | AI / User | Phase 2 folder contains schema concept and star-schema notes | phase2_star_schema.md | Domain schema design |
| DDL design | Create warehouse DDL scripts | PostgreSQL schema and table scripts | Done | Y | AI / User | Initial bronze/silver/gold DDL scripts created | scripts/schema/*.sql | Finalized architecture |
| Validation | Validate architecture with stakeholders | Final architecture sign-off | Done | Y | AI / User | Architecture is approved for Phase 3 start | Phase 2 review documentation | Finalized design |

### Phase 2 exit criteria
- Source-to-target architecture is finalized and reviewed
- Bronze / Silver / Gold responsibilities are clearly defined
- Fact tables and dimension tables are mapped for all 4 domains
- Grain for each fact table is explicitly documented
- Naming convention is consistent across warehouse schemas and tables
- ERD or star schema diagrams are created and stored in the Phase 2 folder
- DDL scripts for warehouse objects are ready for execution in PostgreSQL
- Architecture is approved before starting Phase 3 implementation

---

## Phase 3 — Domain 1: Sales Performance

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

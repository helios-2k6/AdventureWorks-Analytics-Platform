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

### Session Context & Git Reference
**Current Status** (Last Updated: 2026-09-02)

| Item | Value |
|------|-------|
| **Current Branch** | `main` |
| **Latest Commit** | `ad84e63` - Merge feature/phase3-sales-performance into main |
| **Remote Status** | ✅ Pushed to origin (main is up to date) |
| **Phase** | Phase 3 — Sales Performance (Done) |

**Key Accomplishments in This Session**
- ✅ Fixed Issue #001: Salesperson name data quality
  - Problem: gold.dim_salesperson.salesperson_name had IDs ("274") instead of real names ("Stephen Jiang")
  - Solution: Added Person.Person join in Silver layer transformation
  - Result: All 17 salespeople now display real names in Gold
  
- ✅ Created comprehensive issue management structure
  - `docs/issues/issue_001_salesperson_name_quality/` with root cause analysis, validation results, and fix script
  - `docs/issues/ISSUES_INDEX.md` for tracking all project issues
  
- ✅ Created Power BI setup guides
  - POWERBI_SETUP_GUIDE.md (Steps 1-6)
  - POWERBI_STEP4_DETAILED.md (Visualizations)
  - POWERBI_CARD1_ULTRA_DETAILED.md (Card building)
  - POWERBI_COLUMN_CORRECTION.md (Column references)

**Code Changes Made**
1. `scripts/transformation/silver/sales_silver_clean.py` - Added person_frame join logic
2. `src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py` - Added Person extraction to extraction_map

**Validation Results**
- ✅ All 17 salespeople verified with real names
- ✅ Revenue metrics preserved ($109.8M)
- ✅ Fact-dimension referential integrity maintained
- ✅ Power BI ready for dashboard visualization

**Next Steps for New Sessions**
1. **Pull latest code**: `git pull origin main`
2. **Review issue folder**: `docs/issues/issue_001_salesperson_name_quality/README.md`
3. **Phase 3 completion confirmed**: Dashboard visualizations, KPI validation, and unit tests are all complete
4. **Completed post-Phase 3 actions**:
   - [x] Build Dashboard Visualizations (Power BI)
   - [x] Validate KPI Metrics
   - [x] Merge feature branch into main

**Reference Documents**
- Phase 3 Task Tracker: This file (line ~490+)
- Issue Documentation: `docs/issues/issue_001_salesperson_name_quality/`
- Git Branch: `main` (contains the merged Phase 3 delivery)
- Architecture: `docs/internal/phase2_architecture_spec.md`
- Project Plan: `docs/project/Plan.md`

**Environment Setup Reminder**
```powershell
# Activate Python environment
cd "a:\Workspace\DataEngineer"
. python\.venv\Scripts\Activate.ps1

# Navigate to project
cd "AdventureWorks Analytics Platform"

# Check git status
git status
git log --oneline -5
```

**Database Status**
- PostgreSQL: Running on localhost:5432
- Database: `adventureworks_warehouse`
- Schemas: bronze (raw), silver (cleaned), gold (analytics-ready)
- Gold Tables Ready:
  - fact_sales: 121,317 rows (line-item grain)
  - dim_date, dim_customer, dim_product, dim_territory, dim_salesperson (all populated with cleaned data)

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

### Phase 3 task tracker

| Main task | Item task | Output / deliverable | Status | Confirm (Y/N) | Owner | Notes | Evidence | Dependencies |
|---|---|---|---|---|---|---|---|---|
| Bronze extraction | Extract SalesOrderHeader from SQL Server | bronze.sales_order_header table (~31K rows) | Done | Y | AI / User | Canonical job loads this table via SalesBronzeIngestionJob and it matches the source row count in live validation | src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py | SQL Server access |
| Bronze extraction | Extract SalesOrderDetail from SQL Server | bronze.sales_order_detail table (~121K rows) | Done | Y | AI / User | Canonical job includes SalesOrderDetail extraction and live source-to-target row parity is confirmed | src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py | SQL Server access |
| Bronze extraction | Extract Customer from SQL Server | bronze.customer table (~20K rows) | Done | Y | AI / User | Customer extraction is included in the source-to-bronze orchestration map and passes live validation | src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py | SQL Server access |
| Bronze extraction | Extract SalesTerritory from SQL Server | bronze.sales_territory table (~10 rows) | Done | Y | AI / User | Territory extraction is implemented and validated against the source table count | src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py | SQL Server access |
| Bronze extraction | Extract SalesPerson from SQL Server | bronze.sales_person table (~17 rows) | Done | Y | AI / User | SalesPerson extraction is included in the same orchestration job and passes live validation | src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py | SQL Server access |
| Bronze extraction | Extract Product from Production schema | bronze.product table (~504 rows) | Done | Y | AI / User | Production.Product is mapped and loaded by SalesBronzeIngestionJob with live count parity | src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py | SQL Server access |
| Bronze loading | Load and validate all Bronze tables | 6 bronze tables with lineage metadata | Done | Y | AI / User | Live output confirms all six tables loaded successfully with row-count parity and validation passed | src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py + tests/test_bronze_ingestion_job.py | Bronze extraction |
| Bronze validation | Verify referential integrity in Bronze | Row count and NULL summary report | Done | Y | AI / User | Live Bronze job output shows all six tables passed validation; lineage metadata columns are present | src/features/Sales_Performance/domain/bronze/bronze_validator.py | Bronze loading |
| Bronze validation | Start required warehouse services | SQL Server + PostgreSQL instances up and reachable | Done | Y | AI / User | Docker PostgreSQL is running and SQL Server instance is reachable; validation executed successfully | docker-compose.yml + environment config | Bronze validation |
| Silver transformation | Clean and standardize sales_order_header | silver.sales_order_header_clean table | Done | Y | AI / User | Dates and numeric fields standardized; duplicate SalesOrderID rows removed; live count 31,465 | scripts/transformation/silver/sales_silver_clean.py | Bronze tables |
| Silver transformation | Clean and standardize sales_order_detail | silver.sales_order_detail_clean table | Done | Y | AI / User | Numeric fields standardized and duplicate SalesOrderDetailID rows removed; live count 121,317 | scripts/transformation/silver/sales_silver_clean.py | Bronze tables |
| Silver transformation | Clean and standardize customer | silver.customer_clean table | Done | Y | AI / User | Keys and account references standardized; live count 19,820; customer_name uses account reference until Person source is loaded | scripts/transformation/silver/sales_silver_clean.py | Bronze tables |
| Silver transformation | Clean and standardize sales_territory | silver.sales_territory_clean table | Done | Y | AI / User | Territory names trimmed and keys deduplicated; live count 10 | scripts/transformation/silver/sales_silver_clean.py | Bronze tables |
| Silver transformation | Clean and standardize sales_person | silver.sales_person_clean table | Done | Y | AI / User | Salesperson keys and numeric fields standardized; live count 17; name uses BusinessEntityID until Person source is loaded | scripts/transformation/silver/sales_silver_clean.py | Bronze tables |
| Silver transformation | Clean and standardize product | silver.product_clean table | Done | Y | AI / User | Product names trimmed and discontinued flag derived; live count 504 | scripts/transformation/silver/sales_silver_clean.py | Bronze tables |
| Silver validation | Validate Silver layer quality | Deduplication and join validation report | Done | Y | AI / User | Live validation passed: counts preserved, no duplicate keys, required NULL checks are zero, and all five cross-table joins have zero orphan rows | scripts/transformation/silver/validate_silver.py + phase3_silver_validation.md | Silver transformation |
| Gold dimensions | Build dim_date calendar dimension | gold.dim_date table (1,127 rows for source date range) | Done | Y | AI / User | Generated date key/calendar attributes from Silver order dates and added PK | scripts/warehouse/postgres/gold/sales_gold_load.py | Silver tables |
| Gold dimensions | Build dim_customer from Silver | gold.dim_customer table (19,820 rows) | Done | Y | AI / User | Loaded from silver.customer_clean with unique customer key | scripts/warehouse/postgres/gold/sales_gold_load.py | Silver tables |
| Gold dimensions | Build dim_product from Silver | gold.dim_product table (504 rows) | Done | Y | AI / User | Loaded from silver.product_clean with unique product key | scripts/warehouse/postgres/gold/sales_gold_load.py | Silver tables |
| Gold dimensions | Build dim_territory from Silver | gold.dim_territory table (10 rows) | Done | Y | AI / User | Loaded from silver.sales_territory_clean with unique territory key | scripts/warehouse/postgres/gold/sales_gold_load.py | Silver tables |
| Gold dimensions | Build dim_salesperson from Silver | gold.dim_salesperson table (17 rows) | Done | Y | AI / User | Loaded from silver.sales_person_clean with unique salesperson key | scripts/warehouse/postgres/gold/sales_gold_load.py | Silver tables |
| Gold fact table | Build fact_sales from Silver detail + header | gold.fact_sales table (121,317 rows at line-item grain) | Done | Y | AI / User | Joined detail/header, calculated date key and sales measures, added five FKs | scripts/warehouse/postgres/gold/sales_gold_load.py | Gold dimensions |
| Gold validation | Verify fact table grain and integrity | Grain validation and FK referential check report | Done | Y | AI / User | Fact grain is unique and all five dimension joins have zero orphan rows | docs/ToDoCheckList/Phase_3_Sales_Performance/phase3_gold_validation.md | Gold fact table |
| KPI validation | Pre-calculate expected KPIs | KPI baseline values (revenue, AOV, counts) | Done | Y | AI / User | Independent Silver join baseline calculated for revenue, orders, line items, units, AOV, price, discount and customers | scripts/warehouse/postgres/gold/validate_sales_kpis.py | Gold tables |
| KPI validation | Validate KPI calculations in Gold | KPI validation report (actual vs expected) | Done | Y | AI / User | All 9 KPIs match the independent Silver baseline with 0% variance, within the 2% tolerance | docs/ToDoCheckList/Phase_3_Sales_Performance/phase3_kpi_validation.md | Gold fact/dims |
| Bug fix | Fix Issue #001: Salesperson name data quality | issue_001_salesperson_name_quality/ | Done | Y | AI / User | Root cause: Person.Person not joined in Silver. Fixed by adding person_frame join in clean_sales_person(). All 17 names verified. | docs/issues/issue_001_salesperson_name_quality/ + commit 43f76d3 | Gold tables |
| Documentation | Create issue management structure | docs/issues/ with ISSUES_INDEX.md and folder organization | Done | Y | AI / User | Comprehensive issue tracking system created; ready for future issues | docs/issues/FOLDER_STRUCTURE_GUIDE.md + ISSUES_INDEX.md | Issue reporting |
| Documentation | Create Power BI setup guides | 5 Power BI setup and configuration guides | Done | Y | AI / User | Detailed guides for connection, import, relationships, visualizations, and column reference | docs/ToDoCheckList/Phase_3_Sales_Performance/PowerBI/ | Phase 3 planning |
| Power BI dashboard | Connect Power BI to PostgreSQL Gold layer | BI connection and data model | Done | Y | AI / User | PostgreSQL Gold layer was validated and dashboard is connected/ready for reporting | docs/reports/sales_performance_dashboard.pbix | Gold tables |
| Power BI dashboard | Build sales performance dashboard | Dashboard with 8+ sales visualizations | Done | Y | AI / User | Sales performance dashboard is built and ready for KPI review | docs/reports/sales_performance_dashboard.pbix | BI connection |
| Power BI dashboard | Validate dashboard KPI metrics | Dashboard metrics validation checklist | Done | Y | AI / User | Power BI dashboard KPIs match the Gold/Silver validated baseline within tolerance; evidence stored in phase3_kpi_validation.md | docs/ToDoCheckList/Phase_3_Sales_Performance/phase3_kpi_validation.md | BI dashboard |
| Testing | Write unit tests for Gold layer | tests/test_sales_gold.py | Done | Y | AI / User | Gold-layer unit tests cover grain, dimensions, FK logic, and metric calculations | tests/test_sales_gold.py | Gold tables |
| Testing | Run test suite and document results | Test execution report with coverage | Done | Y | AI / User | pytest tests/test_sales_gold.py passed with 18 tests green; report saved in phase3_kpi_validation.md | docs/ToDoCheckList/Phase_3_Sales_Performance/phase3_kpi_validation.md | Unit tests |
| Deliverables | Finalize Phase 3 documentation | phase3_analysis.md + phase3_implementation_checklist.md | Done | Y | AI / User | Analysis and task breakdown completed; issue documentation and Power BI guides added | docs/ToDoCheckList/Phase_3_Sales_Performance/ | Phase planning |
| Code review | Peer review Phase 3 code | Code review approval | Done | Y | AI / User | Phase 3 logic and validation evidence were reviewed in the project environment; the branch is pushed and ready for merge | Commit f1d66e9 + KPI validation evidence | All code |
| Git | Push code to remote | Commits on origin/feature/phase3-sales-performance | Done | Y | AI / User | Phase 3 commit and validation report are on the remote branch | git push origin feature/phase3-sales-performance | Code review approved |
| Merge | Merge feature branch to dev | Merge commit on dev branch | Not started | N | AI / User | Merge after this checkpoint if you want the feature branch folded into dev | git log dev | Dashboard validation |

### Phase 3 exit criteria
- All 6 Bronze source tables are extracted and loaded with metadata lineage (_source_system, _source_table, _load_date, _record_hash)
- Bronze row counts match source exactly (100% validation)
- All Bronze tables have primary key constraints and proper data types
- All 6 Silver tables are cleaned, standardized, and deduplicated
- Silver deduplication logic is validated (no unexpected row loss)
- All 5 Gold dimension tables are built with proper indexes and primary keys
- Gold fact_sales table is built at transaction-level grain (1 row = 1 sales order line item = 121K rows)
- Referential integrity is validated (no orphaned foreign keys, all FK constraints pass)
- All KPIs are calculated in Gold layer and validated against manual baseline (within ±2% tolerance)
- Power BI dashboard is connected to Gold layer and displays correct metrics
- Unit test suite passes with ≥80% code coverage
- Code has been peer-reviewed and approved
- Feature branch is merged to dev with --no-ff commit
- All deliverables are stored in docs/ToDoCheckList/Phase_3_Sales_Performance/

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

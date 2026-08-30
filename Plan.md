# AdventureWorks Analytics Platform — Project Plan

## 1. Project Goal
Build a complete data engineering project based on the AdventureWorks2012 OLTP database, using a Medallion architecture (Bronze → Silver → Gold), loading data into PostgreSQL and preparing it for Power BI reporting.

## 2. Working Language Agreement
- Project discussions may be conducted in either English or Vietnamese.
- The assistant will primarily respond in Vietnamese, while also helping improve the English phrasing when needed.
- We will keep communication clear and practical, and we will confirm major decisions before implementation starts.

## 3. Project Scope
The long-term goal is to build a full data platform covering four business domains:
1. Sales Performance
2. Customer Analysis
3. Production / Inventory
4. Purchasing / Supplier

The initial focus is on establishing the technical foundation and the data pipeline before moving into business-focused analytics.

## 4. Git Workflow
- Main branch: main
- Development branch: dev
- Feature branches: feature/...

Standard flow:
1. Create a feature branch
2. Implement the work
3. Commit the code
4. Merge into dev
5. Merge dev into main

## 5. Phase Roadmap

### Phase 0 — Environment & Foundation
Objective:
- Create the project structure
- Configure the Git workflow
- Set up the Python environment
- Connect to the SQL Server AdventureWorks2012 database
- Connect to a local PostgreSQL instance
- Validate raw data ingestion into the Bronze layer

Deliverables:
- Git repository structure
- .gitignore
- requirements.txt
- README.md
- .env.example
- docker-compose.yml
- project folder layout (src/, tests/, docs/, notebooks/)
- Python scripts for SQL Server and PostgreSQL connectivity
- Bronze schema creation
- basic end-to-end raw data load test

Definition of Done:
- Python can successfully connect to AdventureWorks2012 on SQL Server
- Python can successfully connect to the local PostgreSQL database
- Raw source tables can be extracted and inserted into Bronze successfully
- The project is ready for Phase 1

### Phase 1 — Data Discovery & Profiling
Objective:
- Inspect source tables
- Map columns and relationships
- Identify data quality issues
- Document the data dictionary

Deliverables:
- Data profiling scripts
- Schema inventory report
- Data dictionary document
- Source-to-target mapping notes

### Phase 2 — Architecture & Spec Finalization
Objective:
- Finalize the warehouse design
- Create Medallion schemas and DDL scripts
- Define the Gold star schema for each domain

Deliverables:
- Bronze / Silver / Gold schema setup
- DDL scripts
- ERD or star schema documentation

### Phase 3 — Domain 1: Sales Performance
Objective:
- Build the end-to-end Bronze → Silver → Gold pipeline
- Create fact and dimension tables for sales
- Prepare a Power BI-ready dataset

Deliverables:
- Sales ETL pipeline
- Unit tests
- Dashboard foundation

### Phase 4 — Domain 2: Customer Analysis
Objective:
- Build customer analytics using Sales.Customer and order history
- Compute key metrics and segmentation

Deliverables:
- Customer fact and dimension tables
- RFM / CLV logic
- Customer dashboard

### Phase 5 — Domain 3: Production / Inventory
Objective:
- Build inventory and production analytics

Deliverables:
- Inventory and production pipeline
- Dashboard and KPI outputs

### Phase 6 — Domain 4: Purchasing / Supplier
Objective:
- Build purchasing and supplier analytics

Deliverables:
- Purchasing fact and dimension tables
- Supplier dashboard and KPI outputs

### Phase 7 — Orchestration & Automation
Objective:
- Automate the end-to-end pipeline using Airflow or Prefect
- Add scheduling, retries, alerts, and logging

Deliverables:
- Pipeline orchestration scripts
- Monitoring and alerting setup
- Dockerized environment

### Phase 8 — Testing, CI/CD & Documentation
Objective:
- Ensure a stable and reusable project
- Add GitHub Actions for CI
- Finalize the README and portfolio documentation

Deliverables:
- Unit test coverage
- CI pipeline configuration
- Final project documentation

## 6. Technical Architecture
Source:
- SQL Server AdventureWorks2012 (OLTP)

Target:
- PostgreSQL data warehouse

Pattern:
- Bronze: raw data with lineage columns
- Silver: cleaned and standardized data
- Gold: fact and dimension tables optimized for analytics

Reporting:
- Power BI

## 7. Stack Recommendation
- Python
- pandas
- SQLAlchemy
- pyodbc / msodbcsql
- PostgreSQL
- Docker
- pytest
- GitHub Actions
- Airflow or Prefect (later)

## 8. Decision Rules
- Do not begin domain-specific analytics before Phase 0 is complete
- Keep the architecture simple and production-like, without over-engineering too early
- Prioritize correctness, reproducibility, and documentation
- Use Git branching clearly for each workstream
- We will discuss architecture before implementation to avoid avoidable mistakes

## 9. Working Principles
- We will proceed step by step
- We will validate each critical stage before moving to the next one
- We will keep the plan in this file and follow it consistently
- If a decision changes, we will update this file

## 10. Immediate Next Step
Create and validate the foundation for Phase 0:
- Repository structure
- Python environment
- SQL Server connectivity
- PostgreSQL setup
- Bronze ingestion test

This is the first milestone for building the project in a stable and correct way.

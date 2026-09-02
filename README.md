# AdventureWorks Analytics Platform

This repository contains the AdventureWorks data engineering and analytics platform for extraction, profiling, transformation, validation, and dashboard reporting.

## Current status
- Phase 3 (Sales Performance) is complete and validated.
- KPI checks passed against the independent Silver-layer baseline.
- Gold-layer unit tests passed successfully.
- The completion has been merged into `main` and pushed to origin.

## Project goal
Build a clean medallion-style warehouse solution around AdventureWorks data with:
- Bronze: raw source ingestion and landing
- Silver: cleaning, normalization, and quality handling
- Gold: analytics-ready dimensions, facts, and KPIs
- Dashboard: executive-facing sales performance reporting

## Dashboard preview
![Sales Performance Dashboard](Dashboard/SalesPerformanceDashboard.png)

## Repository structure

- docs/: project planning, architecture, checklist, specs, and issue tracking
- src/: application code and shared pipeline utilities
  - src/core/: connectivity, configuration, and core logic
  - src/utils/: logger and helper utilities
- scripts/: operational jobs and database assets
  - scripts/source/: source-system extraction and profiling scripts
    - scripts/source/sqlserver/: SQL Server-specific profiling and extraction jobs
  - scripts/ingestion/: ingestion jobs
    - scripts/ingestion/bronze/: bronze ingestion scripts
  - scripts/warehouse/: warehouse setup and database objects
    - scripts/warehouse/postgres/: PostgreSQL warehouse schema and setup scripts
- tests/: automation and validation tests
- notebooks/: exploratory and analysis notebooks
- config/: environment and configuration assets
- Dashboard/: exported dashboard assets and preview images
- docker-compose.yml: local PostgreSQL warehouse setup
- main.py: quick sanity-check entry point for connectivity and setup validation
- requirements.txt: project dependencies

## Branch workflow
- main: production-ready state
- dev: integration branch for active development
- feature/phase3-sales-performance: completed sales-performance work for the current delivery

## Working rules
The project follows a shared working standard applied across all sessions and environments:
- scope must be agreed before execution
- each task must have clear output, owner, and evidence
- ambiguous work is marked as Needs clarification before deep execution begins
- progress must be reviewed before moving to the next phase
- no phase is considered complete without explicit confirmation

## Notes
- This repository is intentionally separate from the legacy Python project folder.
- The Python folder remains untouched for historical or experimental work.
- The dashboard image in this README reflects the validated Phase 3 sales dashboard output.

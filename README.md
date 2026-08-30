# AdventureWorks Analytics Platform

This repository contains the AdventureWorks data engineering platform for extraction, profiling, transformation, and analytics workflows.

## Project goal
Build a clean medallion-style warehouse solution around AdventureWorks data with:
- Bronze: raw source ingestion
- Silver: cleaning and standardization
- Gold: analytics-ready datasets

## Repository structure

- docs/: project planning, architecture, checklist, specs
- src/: application code and shared pipeline utilities
  - src/core/: connectivity, config, core logic
  - src/utils/: logger and helper utilities
- scripts/: operational jobs and database assets
  - scripts/db/: SQL setup scripts
  - scripts/ingestion/: extraction and bronze ingestion scripts
  - scripts/validation/: validation checks
- tests/: automation and validation tests
- notebooks/: exploratory and analysis notebooks
- config/: environment and configuration assets
- docker-compose.yml: local PostgreSQL warehouse setup
- main.py: quick sanity-check entry point for connectivity and setup validation
- requirements.txt: project dependencies

## Branch workflow
- main: production-ready state
- dev: integration branch for active development
- feature/adventureworks-pipeline: feature work for ETL and analytics pipeline

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

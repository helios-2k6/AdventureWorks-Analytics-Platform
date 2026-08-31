# Architecture Refactor Summary: Shared vs Feature Separation

## Overview
The codebase has been refactored to separate reusable platform infrastructure from feature-specific business logic. The canonical source of truth is now in the shared and feature layers, and the stale duplicate connector and bronze domain folders were removed after verification.

---

## Current Architecture Structure

### 1. Shared / Reusable Platform Layer
This layer contains infrastructure that is reusable across all features and should remain free of business-specific logic.

```
src/shared/
├── connectors/
│   ├── __init__.py
│   ├── base_connector.py
│   ├── sql_server_connector.py
│   └── postgres_connector.py
├── services/
│   ├── __init__.py
│   └── connection_health_service.py
├── __init__.py
└── __pycache__/
```

Responsibilities:
- Database connection lifecycle management
- Shared configuration and connection logic
- Health checks and readiness probes
- Reusable platform services for all features

---

### 2. Feature-Specific Business Layer
This layer contains feature-specific ETL workflows and domain logic.

```
src/features/
└── Sales_Performance/
    ├── __init__.py
    ├── domain/
    │   └── bronze/
    │       ├── __init__.py
    │       ├── sales_extractor.py
    │       ├── bronze_loader.py
    │       └── bronze_validator.py
    ├── jobs/
    │   ├── __init__.py
    │   └── sales_bronze_ingestion_job.py
    └── __pycache__/
```

Responsibilities:
- Sales-specific ETL flow
- Extraction, loading, and validation logic
- Business logic stays isolated from shared infrastructure
- Future features can live beside it under src/features/

---

### 3. Orchestration Layer
The application entry point that orchestrates jobs and services.

```
src/app/
├── __init__.py
└── app.py
```

Responsibilities:
- Initializes dependencies
- Calls health checks
- Invokes feature jobs
- Keeps orchestration logic thin and separate from business logic

---

### 4. Core / Legacy Shells
The remaining src/core package is not the source of truth anymore. It only contains support files such as configuration and a deprecated app shell, not the real implementation.

```
src/core/
├── __init__.py
├── app/
│   ├── __init__.py
│   └── app.py
├── config.py
└── __pycache__/
```

The real implementation lives under src/app, src/shared, and src/features/Sales_Performance.

---

## Canonical Rule
Features depend on shared infrastructure, and shared infrastructure does not depend on feature logic.

This is the intended dependency pattern:

```
app
  ↓
feature job
  ↓
shared connectors / services
```

---

## Backward Compatibility Status
Duplicate legacy folders were intentionally removed after verification.

Current compatibility surface is intentionally minimal and only includes package entry points where needed:

- src/jobs/__init__.py → exports PlatformBootstrapJob and SalesBronzeIngestionJob
- src/services/__init__.py → exports ConnectionHealthService
- src/core/app/app.py → deprecated wrapper to App

This is a reduced compatibility footprint compared with the earlier transition state.

---

## Migration Path

### Phase 1: ✅ Complete
- Shared platform layer created in src/shared
- Feature layer created in src/features/Sales_Performance
- App orchestration updated to canonical imports
- Duplicate connector and bronze domain folders removed
- Tests validated successfully

### Phase 2: Optional Future
- Add additional feature folders under src/features/
- Expand shared services as needed
- Keep feature code isolated and share only through src/shared

---

## Benefits of This Structure

### 1. Clear separation of concerns
- Shared platform code is stable and reusable
- Feature code is isolated and independently evolvable
- No circular dependency between features

### 2. Scalability
- Easy to add new features without touching shared code
- Keeps the main platform reusable and consistent

### 3. Testability
- Shared services can be tested in isolation
- Feature jobs can be tested without cross-feature coupling

### 4. Maintainability
- Canonical paths are easy to locate and reason about
- The structure is aligned with the feature-based architecture

---

## Verification

### Latest test status
```
pytest -q tests/test_architecture_contract.py tests/test_bronze_ingestion_job.py
Result: 4 passed in 1.09s ✅
```

### Key test coverage
- Application entry point instantiation
- Platform bootstrap job existence
- Connection health service instantiation
- Sales bronze ingestion job orchestration

---

## File Changes Summary

### Canonical implementation locations
- src/app/app.py
- src/shared/connectors/
- src/shared/services/
- src/features/Sales_Performance/

### Removed duplicate content
- src/core/connectors/
- src/domain/bronze/
- legacy connector re-export files in src/core
- legacy bronze re-export files in src/domain

### Remaining package-level compatibility points
- src/jobs/
- src/services/
- src/core/app/

These are intentionally minimal and do not duplicate the true implementation logic.

---

## Final Notes
- Feature folder naming matches the branch naming convention: Sales_Performance
- Shared modules are the real reusable source of truth
- The project is ready for the next feature expansion phase without reintroducing duplicate layers
- The current structure is intentionally clean and easy to extend

---

Last Updated: 2026-08-31
Branch: feature/phase3-sales-performance
Status: Ready for continued feature development

# Phase 4B - Refactored Bronze Pipeline Run Evidence

## 1. Run Information

| Item | Value |
|---|---|
| Run date | 2026-09-04 |
| Repository | `A:\Workspace\DataEngineer\AdventureWorks Analytics Platform` |
| Python environment | `.venv\Scripts\python.exe` |
| Entry point | `main.py` |
| Source system | SQL Server `localhost\HELIOS / AdventureWorks2012` |
| Warehouse | PostgreSQL `localhost:5432 / adventureworks_warehouse` |
| Batch size | `10,000` |
| Retry attempts | `3` |
| Pipeline result | `ok` |

## 2. Refactored Workflow

### 2.1. End-to-end workflow

```mermaid
flowchart TD
  A[main.py] --> B[App.run()]
  B --> C[get_settings()]
  C --> D[ConnectionHealthService.check_all()]
  D --> D1[SQLServerConnector]
  D --> D2[PostgreSQLConnector]
  D1 --> E{Health OK?}
  D2 --> E
  E -->|No| Z[Return degraded result]
  E -->|Yes| F[PlatformBootstrapJob.run()]
  F --> G[SalesBronzeIngestionJob.run(full)]
  G --> H[SalesBronzeJob]
  H --> I[DomainBronzeJob.run()]
  I --> J[Create run/load identity]
  J --> K[Create bronze_staging table identity]
  K --> L[SalesExtractor.iter_table_batches()]
  L --> L1[SQL Server cursor fetchmany(batch_size)]
  L1 --> L2[Stable ORDER BY ordering_key]
  L2 --> L3[Lineage and deterministic record hash]
  L3 --> M[BronzeValidator.partition_rows()]
  M -->|Schema/system error| N[FAILED; no quarantine; no load]
  M -->|Row-level error| O[PostgresQuarantineService]
  M -->|Valid rows| P{Rejected threshold OK?}
  O --> P
  P -->|No| Q[FAILED; staging not published]
  P -->|Yes| R[PostgresReconciliationService]
  R -->|Matching durable batch| S[SKIP idempotent write]
  R -->|No durable batch| T[BronzeLoader transaction]
  T --> T1[Write valid rows to bronze_staging]
  T1 --> T2[Write checkpoint and batch registry]
  T2 --> T3[COMMIT or ROLLBACK]
  T3 --> U[PostgresAuditService batch audit]
  S --> U
  U --> V{All batches complete?}
  V -->|No| L
  V -->|Yes| W[BronzeValidator.validate_staging()]
  W -->|Fail| X[FAILED; preserve published Bronze]
  W -->|Pass| Y[PostgresPublishService atomic swap]
  Y --> Y1[Move validated table to bronze schema]
  Y1 --> Y2[Mark publish/audit complete]
  Y2 --> AA[Return IngestionResult]
  N --> AB[Mark staging FAILED]
  Q --> AB
  X --> AB
  AB --> AA
  AC[StagingCleanupJob] -. scheduled lifecycle .-> AD[ACTIVE / PUBLISHED / FAILED / ABANDONED]
  AD -. retention policy .-> AE[Expire and cleanup]
```

### 2.2. Component responsibilities, step by step

#### Step 1 - Application entry point

`main.py` is intentionally thin. It creates `App` and delegates execution to `App.run()`.

```text
main.py -> App() -> App.run()
```

The entry point does not contain extraction, validation, SQL, retry, or publish logic.

#### Step 2 - Configuration snapshot

`get_settings()` creates the typed configuration snapshot used by the application.

Responsibilities:

- Read `.env` and process environment variables.
- Parse batch and retry settings.
- Select SQL Server and PostgreSQL connection details.
- Keep passwords in `SecretStr` and out of safe summaries.
- Provide the same settings instance to connectors, jobs, and repositories.

The observed run used `batch_size=10000` and `retry_max_attempts=3`.

#### Step 3 - Connection health gate

`ConnectionHealthService.check_all()` checks both external systems before Bronze execution:

- `SQLServerConnector` checks the AdventureWorks source.
- `PostgreSQLConnector` checks the warehouse.
- Each connector is disconnected after the check.

If a connection fails, the application returns a degraded health result. In the observed run both connections returned `ok`.

#### Step 4 - Platform bootstrap

`PlatformBootstrapJob.run()` executes the platform bootstrap boundary and returns its status. The observed result was:

```json
{
  "status": "ok",
  "message": "bootstrap job executed"
}
```

#### Step 5 - Domain routing

`SalesBronzeIngestionJob` is the compatibility wrapper. It delegates to `SalesBronzeJob`, which owns the five Sales `TableSpec` definitions:

- `Sales.SalesOrderHeader` -> `bronze.sales_order_header`
- `Sales.SalesOrderDetail` -> `bronze.sales_order_detail`
- `Sales.Customer` -> `bronze.customer`
- `Sales.SalesTerritory` -> `bronze.sales_territory`
- `Sales.SalesPerson` -> `bronze.sales_person`

`SalesBronzeJob` injects the production services used by the shared `DomainBronzeJob`:

- `PostgresAuditService`
- `PostgresQuarantineService`
- `PostgresReconciliationService`
- `PostgresPublishService`
- `PostgresCheckpointManager`

#### Step 6 - Run and staging identity

For each table, `DomainBronzeJob` creates a logical run/load identity and a run-specific staging identity.

The physical table is created in the dedicated schema:

```text
bronze_staging.<target_table>__<run_fragment>__<load_fragment>
```

PostgreSQL limits identifiers to 63 characters. Therefore, long UUID fragments are replaced by deterministic hash fragments while the complete run/load IDs remain available in audit metadata.

#### Step 7 - Source extraction and batching

`SalesExtractor.iter_table_batches()` reads SQL Server through a cursor.

For each batch it:

- Uses `fetchmany(Settings.batch_size)` instead of `fetchall()`.
- Applies stable `ORDER BY TableSpec.ordering_key`.
- Produces batch number, lower bound, and upper bound.
- Adds `_source_system`, `_source_table`, `_load_date`, and `_record_hash`.

This keeps source reads bounded and makes rerun identity deterministic.

#### Step 8 - Row validation and quarantine

`BronzeValidator.partition_rows()` separates the batch before writing:

- Valid rows continue to staging.
- A row-level primary-key error becomes a `RejectedRecord`.
- `PostgresQuarantineService` persists rejected identity, key, hash, reason, and timestamp.
- Raw rejected payload is not written to application logs or the rejected-record contract.
- Missing required columns are schema errors: the batch fails closed and is not converted into quarantine rows.

The cumulative rejected count is passed to batch audit, table audit, result, and rejection-threshold validation.

#### Step 9 - Durable reconciliation before write

`PostgresReconciliationService` checks the durable batch registry before a write:

- Existing batch with the same content hash -> `SKIP`.
- No matching batch evidence -> proceed with write/retry.
- Existing batch with a different content hash -> fail closed to prevent source drift or duplicate data.

This is the protection used after timeout or an uncertain client response.

#### Step 10 - Atomic staging write and checkpoint

For production loaders, `BronzeLoader.load_batch_transactionally()` uses one database transaction:

```text
BEGIN
  write valid rows to bronze_staging
  write checkpoint
  write batch registry/content hash
COMMIT
```

If any part fails, the transaction rolls back. The checkpoint cannot move ahead of committed data.

#### Step 11 - Batch retry and audit

`execute_with_retry()` retries only transient read/write errors. All attempts keep the same logical batch ID.

After a successful commit or idempotent skip, `PostgresAuditService` records batch evidence including:

- Batch identity and bounds.
- Rows read, written, and rejected.
- Attempt count.
- Status and commit timestamp.
- Content hash.

Table-load and pipeline-run audit records are persisted in PostgreSQL as well.

#### Step 12 - Full-table validation

After all source batches complete, `BronzeValidator.validate_staging()` validates the complete candidate table:

- Required columns and lineage columns.
- Source-table lineage values.
- Primary-key null policy.
- Duplicate primary keys.
- Source/target row reconciliation.
- Rejected threshold.

If validation fails, the candidate staging table is marked failed and the previous published Bronze remains unchanged.

#### Step 13 - Atomic publish

`PostgresPublishService` publishes only a validation-passed staging table:

- Validate target and staging identifiers.
- Verify the staging table exists.
- Rename the current published table as a previous version when present.
- Move the staging table from `bronze_staging` to `bronze`.
- Rename it to the official target table.
- Commit the swap as one PostgreSQL transaction.

The observed run published all five tables successfully.

#### Step 14 - Standard result

`DomainBronzeJob` returns an `IngestionResult` dictionary for each table. The result contains identity, status, row counts, rejected count, attempts, timestamps, error information, staging name, validation report, and publish state.

The application combines health, bootstrap, and Bronze results into the final application status.

#### Step 15 - Cleanup lifecycle

`StagingCleanupJob` is the lifecycle cleanup component. It is designed to run as a scheduled operational job:

- `ACTIVE`: retain while the run is active.
- `PUBLISHED`: remove after audit completion.
- `FAILED` or `ABANDONED`: retain for 24 hours.
- After retention: expire and remove the staging object.

The observed pipeline run completed the publish path. Cleanup policy is independently tested with an injected evaluation time, so retention tests do not require waiting 24 hours.

## 3. Step-by-Step Output

### Step 1 - Settings

```text
environment: development
debug: false
log_level: INFO
sql_server_host: localhost\HELIOS
sql_server_database: AdventureWorks2012
sql_server_auth_mode: windows
postgres_host: localhost
postgres_port: 5432
postgres_database: adventureworks_warehouse
batch_size: 10000
retry_max_attempts: 3
```

Passwords are not included in the output. `Settings.safe_summary()` is used for the displayed configuration.

### Step 2 - Connection Health

```json
{
  "status": "ok",
  "connections": [
    {
      "name": "sql_server",
      "status": "ok",
      "message": "sql_server connection successful"
    },
    {
      "name": "postgres",
      "status": "ok",
      "message": "postgres connection successful"
    }
  ]
}
```

### Step 3 - Bootstrap

```json
{
  "status": "ok",
  "message": "bootstrap job executed"
}
```

### Step 4 - Bronze Pipeline

All five Sales Bronze tables completed successfully. Source and target counts matched, validation passed, and each staging result was published.

| Target table | Source rows | Target rows | Rejected | Attempts | Validation | Published |
|---|---:|---:|---:|---:|---|---|
| `sales_order_header` | 31,465 | 31,465 | 0 | 1 | `true` | `true` |
| `sales_order_detail` | 121,317 | 121,317 | 0 | 1 | `true` | `true` |
| `customer` | 19,820 | 19,820 | 0 | 1 | `true` | `true` |
| `sales_territory` | 10 | 10 | 0 | 1 | `true` | `true` |
| `sales_person` | 17 | 17 | 0 | 1 | `true` | `true` |
| **Total** | **162,629** | **162,629** | **0** |  |  |  |

Example physical staging identifier from the run:

```text
bronze_staging.sales_order_header__id_6abc684bbbeb7f2f__id_437f0d18bcb98177
```

The run/load UUID fragments are shortened with deterministic hash fragments when required to stay within PostgreSQL's 63-character identifier limit. Full run/load identity remains available in audit metadata.

### Step 5 - Application Result

```json
{
  "status": "ok",
  "health": "ok",
  "bootstrap": "ok",
  "bronze_ok": true
}
```

## 4. Production Behaviors Verified

- SQL Server and PostgreSQL connectivity passed.
- Bronze reads source data with cursor batching and stable ordering.
- Valid rows are written to run-specific tables in `bronze_staging`.
- Row-level rejected records are isolated and persisted through `PostgresQuarantineService`.
- Pipeline, table-load, and batch-load audit records are persisted in PostgreSQL.
- Checkpoint and batch registry writes use the transaction-aware loader boundary.
- Full-table validation runs before publication.
- PostgreSQL atomic publish moves validated staging into the published `bronze` schema.
- Retry is limited to transient failures.
- Database reconciliation checks durable batch evidence before retry.
- Failed or abandoned staging follows the cleanup retention lifecycle.
- Connector error logs exclude passwords and raw exception payloads.

## 5. Validation Evidence

### Full regression

```powershell
cd "A:\Workspace\DataEngineer\AdventureWorks Analytics Platform"
.\.venv\Scripts\python.exe -m pytest -q
```

Result:

```text
90 passed in 58.06s
```

### Additional integration evidence

| Area | Test result |
|---|---:|
| PostgreSQL atomic publish and reconciliation | 3 passed |
| Persistent audit and rejected records | 2 passed |
| Dedicated `bronze_staging` schema | 1 passed |
| Transactional checkpoint commit/rollback | 2 passed |
| Log redaction and settings safety | 9 passed |
| W4.6.5 cleanup lifecycle | 19 passed |

`git diff --check` passed and diagnostics reported no errors for the changed runtime files.

## 6. Note

The pipeline run emitted a pandas `FutureWarning` about concatenation behavior with empty or all-NA entries. The warning did not affect the result: all five Bronze tables completed with status `SUCCESS`, validation passed, and publication completed.

This document is an execution snapshot for the refactored Bronze workflow as of 2026-09-04.

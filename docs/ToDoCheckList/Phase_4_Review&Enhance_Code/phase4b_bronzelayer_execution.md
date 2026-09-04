# Phase 4B - Bronze Layer Impact and Execution Plan

## 1. Purpose

This document translates the Bronze decisions from the Phase 4 review into an implementation scope, impact analysis, task breakdown, and verifiable acceptance criteria.

Phase 4B includes:

1. Change the Bronze extractor to `fetchmany(10_000)`.
2. Create staging and batch audit.
3. Implement row-level quarantine.
4. Implement full-table validation and publish.
5. Implement retry, idempotency, and reconciliation.
6. Run Bronze regression tests.

Phase 4B builds on the completed W0-W3 foundation:

- Centralized `Settings` and dependency injection.
- Domain ownership split across Sales, Production, and Person.
- Immutable `TableSpec`.
- Shared result, retry, staging, audit, and checkpoint contracts.

## 2. Current baseline

| Area | Current baseline | Impact/risk |
|---|---|---|
| Extractor | `SalesExtractor.extract_table()` uses `cursor.fetchall()` and creates one DataFrame for the entire table | Memory grows with source size; no batch identity or resume boundary |
| Query ordering | Current query is `SELECT * FROM schema.table` without stable `ORDER BY` | Rerun and incremental progress are not deterministic |
| Bronze loader | `BronzeLoader.load()` writes directly to the target with `to_sql()` | Published Bronze may be replaced/appended before the run completes |
| Domain runner | `DomainBronzeJob` currently shares only basic extract/load/validate mechanics | No runtime run/load/batch audit, quarantine, retry, or publish gate |
| Validation | `BronzeValidator` mainly checks row-count parity; `validate_table()` is not fully used | Schema, lineage, required fields, and rejected thresholds do not block publish |
| Staging | `StagingManager` is currently a database-independent in-memory contract | No real staging table or atomic publish/swap |
| Audit | `AuditService` stores run/table/batch records in memory | Evidence is lost on restart; no database audit per batch/attempt |
| Retry | Classifier/retry policy contract exists | Not connected to read/write transactions or unknown-commit reconciliation |
| Checkpoint | `CheckpointManager` contract exists | Checkpoints are not written transactionally after successful batch commit |
| Tests | Foundation and full regression passed before Phase 4B | Acceptance tests are needed for batching, quarantine, publish safety, and rerun |

## 3. Impact analysis

### 3.1. Source extraction impact

Affected files/symbols:

- `src/features/Sales_Performance/domain/bronze/sales_extractor.py`
- `SalesExtractor.extract_table()`
- Domain jobs that call the extractor through `DomainBronzeJob`
- SQL Server connector cursor lifecycle

Required changes:

- Use `fetchmany(Settings.batch_size)` instead of `fetchall()` in the canonical Bronze path.
- Build the query with the ordering key from `TableSpec`.
- Return a batch iterator or batch result with bounds instead of one DataFrame for the whole table.
- Create lineage and `_record_hash` deterministically for each batch.
- Close the cursor safely when the source is exhausted or an exception occurs.

Compatibility impact:

- Keep an `extract_table()` wrapper if existing callers still require one DataFrame during migration.
- Add the batch API under a clear name, for example `iter_table_batches(spec, load_date)`.
- Existing fake-cursor tests must support `fetchmany()`.

### 3.2. Staging and batch audit impact

Affected files/symbols:

- `src/shared/ingestion/staging_manager.py`
- `src/shared/ingestion/audit_service.py`
- `src/shared/ingestion/ingestion_models.py`
- `BronzeLoader` and `DomainBronzeJob`

Required changes:

- Each run has a `run_id`; each table load has a `load_id`; each batch has a stable `batch_id`.
- Create staging tables from validated target and run/load identity values.
- Write valid rows only to staging, never directly to published Bronze.
- Record lower/upper bounds, counts, attempt count, status, and commit timestamp for every batch.
- An audit failure must not erase the data-commit state; the audit-failure policy must be explicit.

Database impact:

- Add DDL/migrations for pipeline run, table load, batch load, and staging metadata.
- Add a cleanup/expire policy for failed or abandoned run staging.
- Add indexes/unique protection for logical batch identity.

### 3.3. Row-level quarantine impact

Affected files/symbols:

- Bronze validation/loading boundary.
- `src/shared/ingestion/ingestion_models.py` result counts/status.
- PostgreSQL Bronze schema or rejected-record DDL.

Required changes:

- Distinguish row-level data errors from schema/system errors.
- Store isolatable row errors in `bronze.rejected_records` with reason, record key, source hash, and run/load/batch identity.
- Continue valid rows from the same batch into staging.
- Do not write full payloads to application logs; store raw payload in quarantine only when policy allows it.
- Include rejected counts in result and audit records.

Do not quarantine:

- Missing source table/column.
- Authentication or connection failure.
- Invalid query or contract failure.
- A failure that prevents safe identification of the record boundary.

### 3.4. Full-table validation and publish impact

Affected files/symbols:

- `BronzeValidator`.
- `StagingManager.publish()`.
- `BronzeLoader`/domain runner publish flow.
- Bronze DDL and integration tests.

Minimum validation gate:

- Source/staging row count or reconciliation count.
- Required columns and expected schema.
- Lineage columns and source-table value.
- Primary-key/null policy.
- Rejected threshold.
- Duplicate/idempotency-key policy.
- Batch-audit completeness.

Publish rule:

```text
source batches
  -> validated staging
      -> full-table validation
          -> validation pass: atomic publish/swap
          -> validation fail: keep previous Bronze, cleanup/expire staging
```

Published Bronze must not be dropped or replaced before all staging data passes validation.

### 3.5. Retry, idempotency, and reconciliation impact

Affected files/symbols:

- `src/shared/ingestion/retry_policy.py`.
- `src/shared/ingestion/checkpoint_manager.py`.
- `src/shared/ingestion/ingestion_models.py`.
- Transaction boundary in the Bronze loader/staging writer.

Mandatory rules:

- Retry transient errors only.
- Preserve `run_id`, `load_id`, and `batch_id` across all attempts.
- Retry one atomic batch; never blindly retry a partial write.
- Advance the checkpoint only after a successful data commit.
- If commit outcome is unknown, query audit/staging/idempotency keys and reconcile before retrying.
- Retry exhaustion must return `FAILED` and must not publish staging.

### 3.6. Test and operational impact

Add database-independent unit tests for mechanics and database-backed integration tests for transaction and publish behavior.

Required operational evidence:

- Run ID and table/load/batch IDs.
- Rows read/written/rejected.
- Attempt count and error class.
- Staging name/version.
- Validation and publish outcomes.
- Cleanup result after a failed run.

## 4. Task execution plan

### W4.1 - Batch extractor

| ID | Task | Output | Acceptance criteria | Status |
|---|---|---|---|---|
| 4.1.1 | Add `TableSpec` batch reader | `iter_table_batches()` or equivalent abstraction | Cursor uses `fetchmany(Settings.batch_size)` | Done |
| 4.1.2 | Add stable ordering | Query uses validated `ORDER BY spec.ordering_key` | Same input produces the same batch order | Done |
| 4.1.3 | Add batch bounds | Batch result has lower/upper key and batch number | Bounds match row data and audit | Done |
| 4.1.4 | Move lineage/hash into batch path | DataFrame batch contains complete metadata | Hash does not depend on run timestamp | Done |
| 4.1.5 | Preserve compatibility wrapper | Existing API callers remain functional | Existing Bronze tests pass | Done |

W4.1 implementation evidence:

- `SalesExtractor.iter_table_batches()` reads with `fetchmany(self.settings.batch_size)`.
- Canonical domain execution passes `TableSpec` and generates stable `ORDER BY` queries.
- Each yielded `ExtractionBatch` contains the DataFrame, batch number, lower bound, and upper bound.
- Lineage and deterministic `_record_hash` are added per batch.
- `extract_table()` remains available as a compatibility wrapper that aggregates batches.
- Validation: `python -m pytest tests/test_bronze_batch_extractor.py tests/test_bronze_ingestion_job.py tests/test_phase4a_w2_domain_ownership.py -q` -> `10 passed`.
- Full regression: `python -m pytest -q` -> `60 passed`.

### W4.2 - Staging and batch audit

| ID | Task | Output | Acceptance criteria | Status |
|---|---|---|---|---|
| 4.2.1 | Design staging naming/DDL | Run/load-specific staging table | Identifiers are validated; no SQL injection | Not started |
| 4.2.2 | Write valid rows to staging | Staging writer | Published Bronze is untouched before publish | Not started |
| 4.2.3 | Write batch audit | Batch audit record/service | Counts, bounds, attempts, status, and commit time are complete | Not started |
| 4.2.4 | Add cleanup/expire | Cleanup policy | Failed/abandoned staging does not remain indefinitely | Not started |
| 4.2.5 | Test transaction boundary | Fake and database transaction tests | Data commit and checkpoint ordering are proven | Not started |

### W4.3 - Row-level quarantine

| ID | Task | Output | Acceptance criteria | Status |
|---|---|---|---|---|
| 4.3.1 | Define rejected-record contract | `bronze.rejected_records` schema/model | Identity, key/hash, reason, and timestamp are present | Not started |
| 4.3.2 | Split valid/rejected rows | Row validation boundary | Valid rows continue; rejected rows are not silently dropped | Not started |
| 4.3.3 | Classify errors | Row/system/schema error policy | System/schema errors fail closed | Not started |
| 4.3.4 | Add threshold | Rejected threshold configuration/result | Threshold exceeded means `FAILED`, with no publish | Not started |
| 4.3.5 | Test quarantine/redaction | Unit/integration tests | No full payload in logs; reason is queryable | Not started |

### W4.4 - Full-table validation and publish

| ID | Task | Output | Acceptance criteria | Status |
|---|---|---|---|---|
| 4.4.1 | Extend Bronze validation | Full staging validation report | Schema, lineage, keys, counts, and threshold are checked | Not started |
| 4.4.2 | Create publish boundary | Atomic publish/swap | Previous Bronze remains unchanged on validation/build failure | Not started |
| 4.4.3 | Block partial publish | Publish guard | Unvalidated staging cannot be published | Not started |
| 4.4.4 | Return standard result | Table/run result | Status, counts, attempts, timestamps, and errors are present | Not started |
| 4.4.5 | Test publish preservation | Regression/integration test | Failed run does not remove valid existing Bronze | Not started |

### W4.5 - Retry/idempotency/reconciliation

| ID | Task | Output | Acceptance criteria | Status |
|---|---|---|---|---|
| 4.5.1 | Connect retry policy to read/write atomic unit | Retry executor integration | Only transient errors are retried | Not started |
| 4.5.2 | Preserve logical identity | Identity propagation | Attempts use the same run/load/batch IDs | Not started |
| 4.5.3 | Write checkpoint after commit | Transactional checkpoint | Checkpoint does not advance before data commit | Not started |
| 4.5.4 | Reconcile unknown commit | Reconciliation service | No blind append after timeout/unknown commit | Not started |
| 4.5.5 | Protect against duplicates | Unique key/upsert/reconciliation rule | Rerunning the same input creates no duplicates | Not started |
| 4.5.6 | Test exhaustion/rerun | Retry and idempotency tests | Exhaustion means `FAILED`, with no publish | Not started |

### W4.6 - Bronze regression

| ID | Task | Output | Acceptance criteria | Status |
|---|---|---|---|---|
| 4.6.1 | Update fake-cursor tests | `fetchmany()` fixtures | Batch size, order, and bounds are tested | Not started |
| 4.6.2 | Run Foundation regression | W0-W3 tests | Existing contracts are not broken and coverage does not decrease | Not started |
| 4.6.3 | Run Bronze unit tests | Bronze mechanics tests | Unit tests pass without a live database | Not started |
| 4.6.4 | Run Bronze integration tests | PostgreSQL/SQL Server tests | Service readiness is recorded; failures are classified clearly | Not started |
| 4.6.5 | Check rerun/failure behavior | Acceptance scenario report | Publish safety, quarantine, retry, and cleanup pass | Not started |

## 5. Dependencies and execution order

```text
W4.1 batch extractor
    -> W4.2 staging + batch audit
        -> W4.3 quarantine
            -> W4.4 full validation + publish
                -> W4.5 retry/idempotency/reconciliation
                    -> W4.6 Bronze regression
```

Do not implement production retry before staging identity, transaction boundaries, and checkpoint ordering are tested. Do not publish Bronze directly from the batch writer.

## 6. Test matrix

| Scenario | Test type | Expected result |
|---|---|---|
| Source contains more than one batch | Unit | `fetchmany(10000)` creates the correct batches and `fetchall()` is not used |
| Stable ordering | Unit | Batch order follows `TableSpec.ordering_key` |
| Empty source | Unit | Success result with zero counts; no invalid publish is created |
| Row-level invalid data | Unit/integration | Row is quarantined; valid rows still enter staging |
| Schema/missing column | Unit/integration | Table is `FAILED`; whole table is not quarantined and is not published |
| Staging write failure before commit | Unit/integration | Batch is rolled back; checkpoint does not advance |
| Transient read/write failure | Unit | Same batch identity is retried and attempt count increases |
| Deterministic error | Unit | No retry; result is `FAILED` |
| Unknown commit outcome | Integration | Reconcile before retry; no duplicate |
| Rejected threshold exceeded | Unit/integration | `FAILED`; staging is cleaned/expired and previous Bronze is preserved |
| Full validation failure | Integration | Existing published Bronze remains unchanged |
| Full validation pass | Integration | Staging is atomically published as Bronze |
| Rerun with the same input | Integration | No duplicate logical records |
| Audit write | Unit/integration | Complete run/table/batch evidence without secrets |

## 7. Commands and evidence

From the repository root, use the standard environment:

```powershell
cd "A:\Workspace\DataEngineer\AdventureWorks Analytics Platform"
.\.venv\Scripts\Activate.ps1
```

Foundation and regression commands:

```powershell
python -m pytest tests/test_settings.py tests/test_phase4a_w0_contract.py tests/test_phase4a_w2_domain_ownership.py tests/test_ingestion_models.py tests/test_retry_policy.py tests/test_staging_manager.py tests/test_checkpoint_manager.py tests/test_audit_service.py -q
python -m pytest -q
```

Bronze-focused command after the test files are created:

```powershell
python -m pytest tests/test_bronze_batch_extractor.py tests/test_bronze_staging.py tests/test_bronze_quarantine.py tests/test_bronze_publish.py tests/test_bronze_retry.py -q
```

Every task marked `Done` must record:

- File/symbol changed.
- Command executed.
- Pass/fail count.
- Database/service prerequisite, if applicable.
- Evidence for rollback, checkpoint, quarantine, retry, and publish safety when relevant.

## 8. Phase 4B Definition of Done

- [ ] Bronze extractor uses `fetchmany(Settings.batch_size)` and stable `ORDER BY`.
- [ ] Every run/table/batch has logical identity and batch audit.
- [ ] Valid rows are written to run-specific staging, never directly to published Bronze.
- [ ] Row-level errors are quarantined with reason and identity; nothing is silently dropped.
- [ ] Schema/system errors fail closed and are not converted into quarantine rows.
- [ ] Full-table validation runs before publish.
- [ ] Existing Bronze remains unchanged when extraction, validation, or publish fails.
- [ ] Staging is published only after validation passes and through an atomic boundary.
- [ ] Retry applies only to transient errors and preserves logical identity.
- [ ] Checkpoints advance only after successful data commit.
- [ ] Unknown commit outcomes are reconciled before retry.
- [ ] Rerunning the same input does not create duplicate records.
- [ ] Retry exhaustion returns `FAILED` and does not publish.
- [ ] Audit contains counts, bounds, attempts, timestamps, and errors.
- [ ] Secrets and full payloads do not appear in application logs.
- [ ] Bronze unit tests run independently of a database.
- [ ] Bronze integration/regression tests pass, or an environment blocker is recorded clearly.
- [ ] README, checklist, and evidence reflect the actual Bronze runtime.

## 9. Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| Source table lacks a suitable key/order | Batches are not deterministic | Require `TableSpec.ordering_key`; fail before extraction if missing |
| Cursor holds a connection for too long | Connection/resource pressure | Context manager, batch fetching, cursor close, and timeout policy |
| Too many quarantined rows | Bronze quality is insufficient | Explicit threshold, rejected-count audit, and no silent publish |
| Unknown commit | Duplicate data | Reconcile staging/audit/unique key before retry |
| Orphaned staging after crash | Storage/audit pollution | Cleanup/expire job and abandoned-run audit |
| Audit write failure | Evidence is lost | Separate data-commit/audit policy and sanitized fallback logging |
| Published Bronze replaced too early | Data availability loss | Full-table validation and atomic publish gate |
| Batch API breaks existing callers | Regression | Compatibility wrapper and API tests |

## 10. Evidence log

| Date | Task | Files/symbols | Validation command | Result | Status |
|---|---|---|---|---|---|
| 2026-09-04 | Create English Phase 4B impact and execution document | `docs/ToDoCheckList/Phase_4_Review&Enhance_Code/phase4b_bronzelayer_execution_en.md` | Markdown review | Created | Done |

## 11. Related documents

- `docs/internal/phase4_enhancement_execution_plan_spec.md`
- `docs/internal/phase4_review_enhance_spec.md`
- `docs/project/PHASE_4A_FOUNDATION_EXECUTION_VI.md`
- `docs/ToDoCheckList/Phase_4_Review&Enhance_Code/phase4a_foundation_execution.md`
- `src/shared/ingestion/ingestion_models.py`
- `src/shared/ingestion/retry_policy.py`
- `src/shared/ingestion/staging_manager.py`
- `src/shared/ingestion/checkpoint_manager.py`
- `src/shared/ingestion/audit_service.py`

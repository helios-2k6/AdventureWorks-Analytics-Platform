from datetime import datetime
import hashlib
import time
from typing import Callable, Dict, Iterable, Optional, TypeVar

import pandas as pd

from src.core.settings import Settings, get_settings
from src.shared.ingestion.ingestion_models import TableSpec
from src.shared.ingestion.audit_service import AuditService
from src.shared.ingestion.ingestion_models import (
    BatchLoadAudit,
    ExecutionIdentity,
    IngestionResult,
    IngestionStatus,
    RunAudit,
    TableLoadAudit,
    deterministic_batch_id,
    utc_now,
)
from src.shared.ingestion.reconciliation_service import ReconciliationService
from src.shared.ingestion.retry_policy import RetryPolicy, execute_with_retry
from src.shared.ingestion.quarantine_service import QuarantineService
from src.shared.ingestion.staging_manager import StagingManager

Component = TypeVar("Component")


class DomainBronzeJob:
    """Run shared Bronze mechanics for the specs owned by one domain."""

    def __init__(
        self,
        table_specs: Iterable[TableSpec],
        extractor_factory: Callable[..., Component],
        loader_factory: Callable[..., Component],
        validator_factory: Callable[..., Component],
        settings: Optional[Settings] = None,
        staging_manager: StagingManager | None = None,
        audit_service: AuditService | None = None,
        retry_policy: RetryPolicy | None = None,
        sleeper: Callable[[float], None] | None = None,
        quarantine_service: QuarantineService | None = None,
        rejected_threshold: int | None = None,
        reconciliation_service=None,
        publish_service=None,
        checkpoint_manager=None,
    ):
        self.settings = settings or get_settings()
        self.table_specs = tuple(table_specs)
        self.extractor = extractor_factory(settings=self.settings)
        self.loader = loader_factory(settings=self.settings)
        self.validator = validator_factory()
        self.staging_manager = staging_manager or StagingManager()
        self.audit_service = audit_service or AuditService()
        self.retry_policy = retry_policy or RetryPolicy(
            max_attempts=self.settings.retry_max_attempts,
            initial_delay_seconds=self.settings.retry_initial_delay_seconds,
            max_delay_seconds=self.settings.retry_max_delay_seconds,
        )
        self.sleeper = sleeper or time.sleep
        self.reconciliation = reconciliation_service or ReconciliationService(
            self.staging_manager
        )
        self.publish_service = publish_service
        self.checkpoint_manager = checkpoint_manager
        self.quarantine_service = quarantine_service or QuarantineService()
        self.rejected_threshold = rejected_threshold

    def run(self, mode: str = "full", load_date: Optional[datetime] = None) -> Dict[str, Dict]:
        if load_date is None:
            load_date = datetime.now()

        results = {}
        for spec in self.table_specs:
            table_identity = ExecutionIdentity.create()
            staging = self.staging_manager.create(
                spec.target_table,
                table_identity.run_id,
                table_identity.load_id,
            )
            started_at = utc_now()
            self.audit_service.record_run(
                RunAudit(
                    table_identity.run_id,
                    "bronze",
                    mode,
                    IngestionStatus.RETRYING,
                    started_at,
                )
            )
            rows_read = 0
            rows_written = 0
            rows_rejected = 0
            batch_frames = []
            success = True
            attempt_count = 1
            batch_error = None
            for batch in self.extractor.iter_table_batches(spec, load_date):
                batch_id = deterministic_batch_id(
                    spec.source_name,
                    spec.ordering_key,
                    batch.lower_bound,
                    batch.upper_bound,
                    load_date,
                )
                content_hash = self._content_hash(batch.dataframe)
                rows_read += batch.row_count
                try:
                    valid_dataframe, rejected_records = self.validator.partition_rows(
                        batch.dataframe,
                        spec,
                        ExecutionIdentity(
                            table_identity.run_id, table_identity.load_id, batch_id
                        ),
                    )
                except Exception as error:  # noqa: BLE001 - schema errors fail closed
                    success = False
                    batch_error = error
                    self.audit_service.record_batch(
                        BatchLoadAudit(
                            batch_id=batch_id,
                            load_id=table_identity.load_id,
                            batch_number=batch.batch_number,
                            lower_bound=str(batch.lower_bound) if batch.lower_bound is not None else None,
                            upper_bound=str(batch.upper_bound) if batch.upper_bound is not None else None,
                            rows_read=batch.row_count,
                            rows_written=0,
                            rows_rejected=0,
                            attempt_count=1,
                            status=IngestionStatus.FAILED,
                            committed_at=None,
                        )
                    )
                    break
                for rejected_record in rejected_records:
                    self.quarantine_service.record(rejected_record)
                batch_rejected = len(rejected_records)
                rows_rejected += batch_rejected
                if (
                    self.rejected_threshold is not None
                    and rows_rejected > self.rejected_threshold
                ):
                    success = False
                    batch_error = ValueError(
                        f"Rejected row threshold exceeded for {spec.source_name}: "
                        f"rejected_count={rows_rejected}, "
                        f"threshold={self.rejected_threshold}"
                    )
                    break
                if valid_dataframe.empty:
                    self.audit_service.record_batch(
                        BatchLoadAudit(
                            batch_id=batch_id,
                            load_id=table_identity.load_id,
                            batch_number=batch.batch_number,
                            lower_bound=str(batch.lower_bound) if batch.lower_bound is not None else None,
                            upper_bound=str(batch.upper_bound) if batch.upper_bound is not None else None,
                            rows_read=batch.row_count,
                            rows_written=0,
                            rows_rejected=batch_rejected,
                            attempt_count=1,
                            status=IngestionStatus.QUARANTINED,
                            committed_at=None,
                        )
                    )
                    continue
                batch_frames.append(valid_dataframe)
                reconciliation = self.reconciliation.resolve(
                    staging.name, batch_id, content_hash
                )
                if reconciliation == "SKIP":
                    written, batch_success = batch.row_count, True
                    batch_attempts = 1
                else:
                    try:
                        staging_schema = getattr(
                            self.loader, "staging_schema", spec.target_schema
                        )
                        if (
                            self.checkpoint_manager is not None
                            and hasattr(self.loader, "load_batch_transactionally")
                        ):
                            load_operation = lambda: self.loader.load_batch_transactionally(
                                valid_dataframe,
                                staging_schema,
                                staging.name,
                                batch_id,
                                batch.upper_bound,
                                self.checkpoint_manager,
                                content_hash,
                                "replace" if batch.batch_number == 1 else "append",
                            )
                        else:
                            load_operation = lambda: self.loader.load(
                                valid_dataframe,
                                staging_schema,
                                staging.name,
                                if_exists="replace" if batch.batch_number == 1 else "append",
                            )
                        (written, batch_success), batch_attempts, _ = execute_with_retry(
                            load_operation,
                            self.retry_policy,
                            self.sleeper,
                        )
                    except Exception as error:  # noqa: BLE001 - result boundary records failure
                        written, batch_success = 0, False
                        batch_attempts = self.retry_policy.max_attempts
                        batch_error = error
                attempt_count = max(attempt_count, batch_attempts)
                success = success and batch_success
                rows_written += written
                if batch_success:
                    self.staging_manager.write_batch(
                        staging.name,
                        batch_id,
                        batch.batch_number,
                        written,
                        batch.lower_bound,
                        batch.upper_bound,
                        content_hash,
                    )
                self.audit_service.record_batch(
                    BatchLoadAudit(
                        batch_id=batch_id,
                        load_id=table_identity.load_id,
                        batch_number=batch.batch_number,
                        lower_bound=str(batch.lower_bound) if batch.lower_bound is not None else None,
                        upper_bound=str(batch.upper_bound) if batch.upper_bound is not None else None,
                        rows_read=batch.row_count,
                        rows_written=written,
                        rows_rejected=batch_rejected,
                        attempt_count=batch_attempts,
                        status=(IngestionStatus.SUCCESS if batch_success else IngestionStatus.FAILED),
                        committed_at=utc_now() if batch_success else None,
                        content_hash=content_hash,
                    )
                )
                if not batch_success:
                    break

            self.audit_service.record_table_load(
                TableLoadAudit(
                    load_id=table_identity.load_id,
                    run_id=table_identity.run_id,
                    stage="bronze",
                    source_table=spec.source_name,
                    target_table=spec.target_name,
                    status=(IngestionStatus.SUCCESS if success else IngestionStatus.FAILED),
                    rows_read=rows_read,
                    rows_written=rows_written,
                    rows_rejected=rows_rejected,
                    attempt_count=1,
                    started_at=started_at,
                    finished_at=utc_now(),
                )
            )

            finished_at = utc_now()
            validation_report = None
            validation_ok = False
            error_type = None
            error_message = None
            if batch_error is not None:
                error_type = type(batch_error).__name__
                error_message = str(batch_error)
            if success and batch_frames:
                try:
                    staged_dataframe = pd.concat(batch_frames, ignore_index=True)
                    validation_report = self.validator.validate_staging(
                        staged_dataframe,
                        spec,
                        source_count=rows_read - rows_rejected,
                        rejected_count=rows_rejected,
                        rejected_threshold=self.rejected_threshold,
                    )
                    validation_ok = validation_report["validation_passed"]
                    if not validation_ok:
                        error_type = "ValidationError"
                        error_message = "; ".join(validation_report.get("issues", []))
                    if validation_ok:
                        self.staging_manager.mark_validated(
                            staging.name, validation_report
                        )
                        if self.publish_service is not None:
                            self.publish_service.publish(
                                spec.target_table, staging.name, validation_report
                            )
                        self.staging_manager.publish(spec.target_table, staging.name)
                        self.staging_manager.mark_audit_complete(staging.name)
                except Exception as error:  # noqa: BLE001 - result boundary records failure
                    error_type = type(error).__name__
                    error_message = str(error)
            elif not batch_frames:
                validation_report = {
                    "validation_passed": rows_read == 0,
                    "empty_source": rows_read == 0,
                    "issues": (
                        ["Source returned zero rows; publish was skipped"]
                        if rows_read == 0
                        else ["No valid rows remained after quarantine; publish was skipped"]
                    ),
                }
                if rows_read and batch_error is None:
                    error_type = "ValidationError"
                    error_message = validation_report["issues"][0]

            if not success or (rows_read and not validation_ok):
                self.staging_manager.mark_failed(staging.name)

            status = (
                IngestionStatus.SUCCESS
                if success and validation_ok
                else IngestionStatus.FAILED
            )
            if status is IngestionStatus.SUCCESS and rows_rejected:
                status = IngestionStatus.SUCCESS_WITH_REJECTIONS
            if not batch_frames and success:
                status = IngestionStatus.SUCCESS
            ingestion_result = IngestionResult(
                identity=table_identity,
                stage="bronze",
                source_table=spec.source_name,
                target_table=spec.target_name,
                status=status,
                rows_read=rows_read,
                rows_written=rows_written,
                rows_rejected=rows_rejected,
                attempt_count=attempt_count,
                started_at=started_at,
                finished_at=finished_at,
                error_type=error_type,
                error_message=error_message,
            )
            result = ingestion_result.to_dict()
            result.update(
                {
                    "source_count": rows_read,
                    "target_count": rows_written,
                    "validation_passed": validation_ok,
                    "validation_report": validation_report,
                    "staging_name": staging.name,
                    "published": (
                        self.staging_manager.published_staging(spec.target_table)
                        == staging.name
                    ),
                }
            )
            results[spec.target_table] = result
            self.audit_service.record_run(
                RunAudit(
                    table_identity.run_id,
                    "bronze",
                    mode,
                    status,
                    started_at,
                    finished_at,
                    1 if status is IngestionStatus.FAILED else 0,
                )
            )

        return results

    @staticmethod
    def _content_hash(dataframe) -> str:
        values = pd.util.hash_pandas_object(dataframe, index=True).values.tobytes()
        columns = "\x1f".join(str(column) for column in dataframe.columns).encode()
        return hashlib.sha256(columns + values).hexdigest()

from datetime import datetime
from typing import Callable, Dict, Iterable, Optional, TypeVar
from uuid import uuid4

from src.core.settings import Settings, get_settings
from src.shared.ingestion.ingestion_models import TableSpec
from src.shared.ingestion.audit_service import AuditService
from src.shared.ingestion.ingestion_models import (
    BatchLoadAudit,
    ExecutionIdentity,
    IngestionStatus,
    TableLoadAudit,
    utc_now,
)
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
    ):
        self.settings = settings or get_settings()
        self.table_specs = tuple(table_specs)
        self.extractor = extractor_factory(settings=self.settings)
        self.loader = loader_factory(settings=self.settings)
        self.validator = validator_factory()
        self.staging_manager = staging_manager or StagingManager()
        self.audit_service = audit_service or AuditService()

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
            rows_read = 0
            rows_written = 0
            success = True
            for batch in self.extractor.iter_table_batches(spec, load_date):
                batch_id = str(uuid4())
                rows_read += batch.row_count
                written, batch_success = self.loader.load(
                    batch.dataframe,
                    spec.target_schema,
                    staging.name,
                    if_exists="replace" if batch.batch_number == 1 else "append",
                )
                success = success and batch_success
                rows_written += written
                self.staging_manager.write_batch(
                    staging.name,
                    batch_id,
                    batch.batch_number,
                    written,
                    batch.lower_bound,
                    batch.upper_bound,
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
                        attempt_count=1,
                        status=(IngestionStatus.SUCCESS if batch_success else IngestionStatus.FAILED),
                        committed_at=utc_now() if batch_success else None,
                    )
                )

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
                    attempt_count=1,
                    started_at=started_at,
                    finished_at=utc_now(),
                )
            )

            target_count = rows_written
            validation_ok = self.validator.validate(
                source_count=rows_read,
                target_count=target_count,
                source_table=spec.source_name,
                bronze_table=staging.name,
            )
            results[spec.target_table] = {
                "source_table": spec.source_name,
                "source_count": rows_read,
                "target_count": target_count,
                "validation_passed": validation_ok,
                "status": "SUCCESS" if (success and validation_ok) else "FAILED",
            }

        return results

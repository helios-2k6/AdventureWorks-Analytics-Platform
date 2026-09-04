from datetime import datetime, timezone

from src.shared.ingestion.audit_service import AuditService
from src.shared.ingestion.ingestion_models import (
    BatchLoadAudit,
    IngestionStatus,
    RunAudit,
    TableLoadAudit,
)
import pytest


def test_audit_service_keeps_run_table_and_batch_history():
    now = datetime.now(timezone.utc)
    service = AuditService()

    service.record_run(RunAudit("run-1", "sales", "full", IngestionStatus.SUCCESS, now))
    service.record_table_load(
        TableLoadAudit(
            "load-1", "run-1", "bronze", "Sales.Customer",
            "bronze.customer", IngestionStatus.SUCCESS,
        )
    )
    service.record_batch(
        BatchLoadAudit(
            "batch-1", "load-1", 1, upper_bound="100",
            status=IngestionStatus.SUCCESS, committed_at=now,
        )
    )

    assert service.runs[0].run_id == "run-1"
    assert service.table_loads[0].load_id == "load-1"
    assert service.batches[0].batch_id == "batch-1"
    assert service.latest_batch("load-1").batch_id == "batch-1"


def test_audit_service_rejects_duplicate_batch_identity():
    service = AuditService()
    audit = BatchLoadAudit("batch-1", "load-1", 1)

    service.record_batch(audit)
    with pytest.raises(ValueError, match="already exists"):
        service.record_batch(audit)

from src.shared.ingestion.ingestion_models import (
    BatchLoadAudit,
    RunAudit,
    TableLoadAudit,
)


class AuditService:
    """Database-independent audit repository contract."""

    def __init__(self):
        self.runs: list[RunAudit] = []
        self.table_loads: list[TableLoadAudit] = []
        self.batches: list[BatchLoadAudit] = []

    def record_run(self, audit: RunAudit) -> RunAudit:
        self.runs.append(audit)
        return audit

    def record_table_load(self, audit: TableLoadAudit) -> TableLoadAudit:
        self.table_loads.append(audit)
        return audit

    def record_batch(self, audit: BatchLoadAudit) -> BatchLoadAudit:
        self.batches.append(audit)
        return audit
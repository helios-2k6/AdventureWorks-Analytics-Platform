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
        self._batch_ids: set[str] = set()

    def record_run(self, audit: RunAudit) -> RunAudit:
        self.runs.append(audit)
        return audit

    def record_table_load(self, audit: TableLoadAudit) -> TableLoadAudit:
        self.table_loads.append(audit)
        return audit

    def record_batch(self, audit: BatchLoadAudit) -> BatchLoadAudit:
        if audit.batch_id in self._batch_ids:
            raise ValueError(f"batch audit already exists: {audit.batch_id}")
        self._batch_ids.add(audit.batch_id)
        self.batches.append(audit)
        return audit

    def batches_for_load(self, load_id: str) -> tuple[BatchLoadAudit, ...]:
        return tuple(batch for batch in self.batches if batch.load_id == load_id)

    def latest_batch(self, load_id: str) -> BatchLoadAudit | None:
        batches = self.batches_for_load(load_id)
        return batches[-1] if batches else None
from src.core.settings import Settings, get_settings
from src.shared.connectors.postgres_connector import PostgreSQLConnector
from src.shared.ingestion.postgres_ingestion_schema import ensure_ingestion_schema
from src.shared.ingestion.ingestion_models import (
    BatchLoadAudit,
    RunAudit,
    TableLoadAudit,
    IngestionStatus,
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


class PostgresAuditService:
    """Durable PostgreSQL audit repository used as the production source of truth."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        ensure_ingestion_schema(self.settings)

    def record_run(self, audit: RunAudit) -> RunAudit:
        with PostgreSQLConnector(settings=self.settings) as connection:
            connection.execute_query(
                """
                INSERT INTO bronze.pipeline_run_audit
                    (run_id, pipeline_name, mode, status, started_at, finished_at, error_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (run_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    finished_at = EXCLUDED.finished_at,
                    error_count = EXCLUDED.error_count
                """,
                (audit.run_id, audit.pipeline_name, audit.mode, audit.status.value,
                 audit.started_at, audit.finished_at, audit.error_count),
            )
        return audit

    def record_table_load(self, audit: TableLoadAudit) -> TableLoadAudit:
        with PostgreSQLConnector(settings=self.settings) as connection:
            connection.execute_query(
                """
                INSERT INTO bronze.table_load_audit
                    (load_id, run_id, stage, source_table, target_table, status,
                     rows_read, rows_written, rows_rejected, attempt_count,
                     error_type, error_message, started_at, finished_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (load_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    rows_read = EXCLUDED.rows_read,
                    rows_written = EXCLUDED.rows_written,
                    rows_rejected = EXCLUDED.rows_rejected,
                    attempt_count = EXCLUDED.attempt_count,
                    error_type = EXCLUDED.error_type,
                    error_message = EXCLUDED.error_message,
                    finished_at = EXCLUDED.finished_at
                """,
                (audit.load_id, audit.run_id, audit.stage, audit.source_table,
                 audit.target_table, audit.status.value, audit.rows_read,
                 audit.rows_written, audit.rows_rejected, audit.attempt_count,
                 audit.error_type, audit.error_message, audit.started_at,
                 audit.finished_at),
            )
        return audit

    def record_batch(self, audit: BatchLoadAudit) -> BatchLoadAudit:
        with PostgreSQLConnector(settings=self.settings) as connection:
            cursor = connection.execute_query(
                """
                INSERT INTO bronze.batch_load_audit
                    (batch_id, load_id, batch_number, lower_bound, upper_bound,
                     rows_read, rows_written, rows_rejected, attempt_count,
                     status, committed_at, content_hash)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (batch_id) DO NOTHING
                """,
                (audit.batch_id, audit.load_id, audit.batch_number,
                 audit.lower_bound, audit.upper_bound, audit.rows_read,
                 audit.rows_written, audit.rows_rejected, audit.attempt_count,
                 audit.status.value, audit.committed_at, audit.content_hash),
            )
            if cursor.rowcount == 0:
                raise ValueError(f"batch audit already exists: {audit.batch_id}")
        return audit

    def batches_for_load(self, load_id: str) -> tuple[BatchLoadAudit, ...]:
        with PostgreSQLConnector(settings=self.settings) as connection:
            rows = connection.fetch_results(
                """
                SELECT batch_id, load_id, batch_number, lower_bound, upper_bound,
                       rows_read, rows_written, rows_rejected, attempt_count,
                       status, committed_at, content_hash
                FROM bronze.batch_load_audit
                WHERE load_id = %s ORDER BY batch_number
                """,
                (load_id,),
            )
        return tuple(self._batch_from_row(row) for row in rows)

    def get_run(self, run_id: str) -> RunAudit | None:
        with PostgreSQLConnector(settings=self.settings) as connection:
            rows = connection.fetch_results(
                """
                SELECT run_id, pipeline_name, mode, status, started_at,
                       finished_at, error_count
                FROM bronze.pipeline_run_audit WHERE run_id = %s
                """,
                (run_id,),
            )
        if not rows:
            return None
        row = rows[0]
        return RunAudit(
            run_id=row[0], pipeline_name=row[1], mode=row[2],
            status=IngestionStatus(row[3]), started_at=row[4],
            finished_at=row[5], error_count=row[6],
        )

    def get_table_load(self, load_id: str) -> TableLoadAudit | None:
        with PostgreSQLConnector(settings=self.settings) as connection:
            rows = connection.fetch_results(
                """
                SELECT load_id, run_id, stage, source_table, target_table,
                       status, rows_read, rows_written, rows_rejected,
                       attempt_count, error_type, error_message, started_at,
                       finished_at
                FROM bronze.table_load_audit WHERE load_id = %s
                """,
                (load_id,),
            )
        if not rows:
            return None
        row = rows[0]
        return TableLoadAudit(
            load_id=row[0], run_id=row[1], stage=row[2], source_table=row[3],
            target_table=row[4], status=IngestionStatus(row[5]), rows_read=row[6],
            rows_written=row[7], rows_rejected=row[8], attempt_count=row[9],
            error_type=row[10], error_message=row[11], started_at=row[12],
            finished_at=row[13],
        )

    def _batch_from_row(self, row) -> BatchLoadAudit:
        return BatchLoadAudit(
            batch_id=row[0], load_id=row[1], batch_number=row[2],
            lower_bound=row[3], upper_bound=row[4], rows_read=row[5],
            rows_written=row[6], rows_rejected=row[7], attempt_count=row[8],
            status=IngestionStatus(row[9]), committed_at=row[10],
            content_hash=row[11],
        )
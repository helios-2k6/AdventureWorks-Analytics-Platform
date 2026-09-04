from datetime import datetime, timezone

from src.shared.ingestion.ingestion_models import (
    ExecutionIdentity,
    IngestionResult,
    IngestionStatus,
)


def test_ingestion_result_serializes_shared_contract():
    identity = ExecutionIdentity.create()
    result = IngestionResult(
        identity=identity,
        stage="bronze",
        source_table="Sales.SalesOrderDetail",
        target_table="bronze.sales_order_detail",
        status=IngestionStatus.SUCCESS_WITH_REJECTIONS,
        rows_read=10,
        rows_written=9,
        rows_rejected=1,
        finished_at=datetime.now(timezone.utc),
    )

    payload = result.to_dict()

    assert payload["run_id"] == identity.run_id
    assert payload["batch_id"] == identity.batch_id
    assert payload["status"] == "SUCCESS_WITH_REJECTIONS"
    assert payload["rows_rejected"] == 1
    assert payload["error_message"] is None


def test_execution_identity_is_stable_when_reused_for_retry():
    identity = ExecutionIdentity.create()
    first = IngestionResult(identity, "bronze", "source", "target")
    retry = IngestionResult(identity, "bronze", "source", "target", attempt_count=2)

    assert first.identity == retry.identity
    assert first.attempt_count == 1
    assert retry.attempt_count == 2

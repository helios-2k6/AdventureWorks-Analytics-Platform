import pytest

from src.shared.ingestion.staging_manager import StagingManager


def test_staging_requires_validation_before_publish_and_preserves_previous_publish():
    manager = StagingManager()
    old = manager.create("fact_sales", "old-run", "old-load")
    manager.mark_validated(old.name)
    manager.publish("fact_sales", old.name)

    new = manager.create("fact_sales", "new-run", "new-load")
    with pytest.raises(RuntimeError, match="validated"):
        manager.publish("fact_sales", new.name)

    assert manager.published_staging("fact_sales") == old.name

    manager.mark_validated(new.name)
    manager.publish("fact_sales", new.name)
    assert manager.published_staging("fact_sales") == new.name


def test_staging_rejects_unsafe_identifiers():
    manager = StagingManager()

    with pytest.raises(ValueError, match="Invalid staging identifier"):
        manager.create("fact_sales;drop", "run-1")


def test_staging_tracks_batches_and_rejects_duplicate_batch_identity():
    manager = StagingManager()
    staging = manager.create("sales_order_detail", "run-1", "load-1")

    batch = manager.write_batch(
        staging.name,
        "batch-1",
        batch_number=1,
        rows_written=2,
        lower_bound=1,
        upper_bound=2,
    )

    assert batch.rows_written == 2
    assert manager.get(staging.name).rows_written == 2
    assert manager.get(staging.name).batch_ids == ("batch-1",)

    with pytest.raises(ValueError, match="already written"):
        manager.write_batch(staging.name, "batch-1", 1, 2)

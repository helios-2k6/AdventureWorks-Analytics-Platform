import pytest

from src.shared.ingestion.staging_manager import StagingManager


def test_staging_requires_validation_before_publish_and_preserves_previous_publish():
    manager = StagingManager()
    old = manager.create("fact_sales", "old-run")
    manager.mark_validated(old.name)
    manager.publish("fact_sales", old.name)

    new = manager.create("fact_sales", "new-run")
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

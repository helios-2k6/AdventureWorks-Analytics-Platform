import pytest

from src.shared.ingestion.checkpoint_manager import CheckpointManager


def test_checkpoint_cannot_advance_before_commit():
    manager = CheckpointManager()

    with pytest.raises(RuntimeError, match="before data commit"):
        manager.advance("batch-1", 100)

    manager.mark_committed("batch-1")
    checkpoint = manager.advance("batch-1", 100)

    assert checkpoint.upper_bound == 100
    assert manager.get("batch-1") == checkpoint

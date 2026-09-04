from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Checkpoint:
    batch_id: str
    upper_bound: Any


class CheckpointManager:
    """In-memory checkpoint contract; persistence can be injected later."""

    def __init__(self):
        self._committed_batches: set[str] = set()
        self._checkpoints: dict[str, Checkpoint] = {}

    def mark_committed(self, batch_id: str) -> None:
        self._committed_batches.add(batch_id)

    def advance(self, batch_id: str, upper_bound: Any) -> Checkpoint:
        if batch_id not in self._committed_batches:
            raise RuntimeError("checkpoint cannot advance before data commit")
        checkpoint = Checkpoint(batch_id, upper_bound)
        self._checkpoints[batch_id] = checkpoint
        return checkpoint

    def get(self, batch_id: str) -> Checkpoint | None:
        return self._checkpoints.get(batch_id)
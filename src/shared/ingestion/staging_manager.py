import re
from dataclasses import dataclass
from typing import Any


_STAGING_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class StagingTable:
    name: str
    target_table: str
    run_id: str
    load_id: str
    published: bool = False
    validated: bool = False
    rows_written: int = 0
    batch_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class StagingBatch:
    staging_name: str
    batch_id: str
    batch_number: int
    rows_written: int
    lower_bound: Any = None
    upper_bound: Any = None


class StagingManager:
    """Database-independent staging/publish contract for unit tests."""

    def __init__(self):
        self._staging: dict[str, StagingTable] = {}
        self._published: dict[str, str] = {}

    def create(
        self,
        target_table: str,
        run_id: str,
        load_id: str | None = None,
    ) -> StagingTable:
        self._validate_identifier(target_table)
        self._validate_identifier(run_id.replace("-", "_"))
        resolved_load_id = load_id or run_id
        self._validate_identifier(resolved_load_id.replace("-", "_"))
        name = (
            f"{target_table}__staging__{run_id.replace('-', '_')}__"
            f"{resolved_load_id.replace('-', '_')}"
        )
        staging = StagingTable(
            name=name,
            target_table=target_table,
            run_id=run_id,
            load_id=resolved_load_id,
        )
        self._staging[name] = staging
        return staging

    def write_batch(
        self,
        staging_name: str,
        batch_id: str,
        batch_number: int,
        rows_written: int,
        lower_bound: Any = None,
        upper_bound: Any = None,
    ) -> StagingBatch:
        if not batch_id or batch_number < 1 or rows_written < 0:
            raise ValueError("batch identity, number, and row count are invalid")
        staging = self._staging[staging_name]
        if batch_id in staging.batch_ids:
            raise ValueError(f"batch already written to staging: {batch_id}")
        batch = StagingBatch(
            staging_name,
            batch_id,
            batch_number,
            rows_written,
            lower_bound,
            upper_bound,
        )
        self._staging[staging_name] = StagingTable(
            name=staging.name,
            target_table=staging.target_table,
            run_id=staging.run_id,
            load_id=staging.load_id,
            published=staging.published,
            validated=staging.validated,
            rows_written=staging.rows_written + rows_written,
            batch_ids=staging.batch_ids + (batch_id,),
        )
        return batch

    def get(self, staging_name: str) -> StagingTable:
        return self._staging[staging_name]

    def mark_validated(self, staging_name: str) -> StagingTable:
        staging = self._staging[staging_name]
        validated = StagingTable(
            name=staging.name,
            target_table=staging.target_table,
            run_id=staging.run_id,
            load_id=staging.load_id,
            published=False,
            validated=True,
            rows_written=staging.rows_written,
            batch_ids=staging.batch_ids,
        )
        self._staging[staging_name] = validated
        return validated

    def publish(self, target_table: str, staging_name: str) -> None:
        self._validate_identifier(target_table)
        staging = self._staging[staging_name]
        if not staging.validated:
            raise RuntimeError("staging must be validated before publish")
        self._published[target_table] = staging_name

    def published_staging(self, target_table: str) -> str | None:
        return self._published.get(target_table)

    def cleanup(self, staging_name: str) -> None:
        self._staging.pop(staging_name, None)

    @staticmethod
    def _validate_identifier(identifier: str) -> None:
        if not _STAGING_IDENTIFIER.fullmatch(identifier):
            raise ValueError(f"Invalid staging identifier: {identifier!r}")
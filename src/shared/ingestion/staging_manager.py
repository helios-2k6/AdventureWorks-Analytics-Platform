import re
from dataclasses import dataclass


_STAGING_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class StagingTable:
    name: str
    published: bool = False
    validated: bool = False


class StagingManager:
    """Database-independent staging/publish contract for unit tests."""

    def __init__(self):
        self._staging: dict[str, StagingTable] = {}
        self._published: dict[str, str] = {}

    def create(self, target_table: str, run_id: str) -> StagingTable:
        self._validate_identifier(target_table)
        self._validate_identifier(run_id.replace("-", "_"))
        name = f"{target_table}__staging__{run_id.replace('-', '_')}"
        staging = StagingTable(name=name)
        self._staging[name] = staging
        return staging

    def mark_validated(self, staging_name: str) -> StagingTable:
        staging = self._staging[staging_name]
        validated = StagingTable(staging.name, published=False, validated=True)
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
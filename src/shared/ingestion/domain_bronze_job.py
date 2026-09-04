from datetime import datetime
from typing import Callable, Dict, Iterable, Optional, TypeVar

from src.core.settings import Settings, get_settings
from src.shared.ingestion.ingestion_models import TableSpec

Component = TypeVar("Component")


class DomainBronzeJob:
    """Run shared Bronze mechanics for the specs owned by one domain."""

    def __init__(
        self,
        table_specs: Iterable[TableSpec],
        extractor_factory: Callable[..., Component],
        loader_factory: Callable[..., Component],
        validator_factory: Callable[..., Component],
        settings: Optional[Settings] = None,
    ):
        self.settings = settings or get_settings()
        self.table_specs = tuple(table_specs)
        self.extractor = extractor_factory(settings=self.settings)
        self.loader = loader_factory(settings=self.settings)
        self.validator = validator_factory()

    def run(self, mode: str = "full", load_date: Optional[datetime] = None) -> Dict[str, Dict]:
        if load_date is None:
            load_date = datetime.now()

        results = {}
        for spec in self.table_specs:
            df = self.extractor.extract_table(
                spec.source_schema,
                spec.source_table,
                load_date,
            )
            source_count = len(df)
            target_count, success = self.loader.load(
                df,
                spec.target_schema,
                spec.target_table,
                if_exists="replace" if mode == "full" else "append",
            )
            validation_ok = self.validator.validate(
                source_count=source_count,
                target_count=target_count,
                source_table=spec.source_name,
                bronze_table=spec.target_name,
            )
            results[spec.target_table] = {
                "source_table": spec.source_name,
                "source_count": source_count,
                "target_count": target_count,
                "validation_passed": validation_ok,
                "status": "SUCCESS" if (success and validation_ok) else "FAILED",
            }

        return results

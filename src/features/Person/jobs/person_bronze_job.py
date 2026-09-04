from src.core.settings import Settings
from src.features.Sales_Performance.domain.bronze.bronze_loader import BronzeLoader
from src.features.Sales_Performance.domain.bronze.bronze_validator import BronzeValidator
from src.features.Sales_Performance.domain.bronze.sales_extractor import SalesExtractor
from src.shared.ingestion.domain_bronze_job import DomainBronzeJob
from src.shared.ingestion.ingestion_models import TableSpec


PERSON_TABLE_SPECS = (
    TableSpec(
        "Person", "Person", "bronze", "person",
        "BusinessEntityID", ("BusinessEntityID",), "BusinessEntityID",
    ),
)


class PersonBronzeJob(DomainBronzeJob):
    def __init__(self, settings: Settings | None = None):
        super().__init__(
            PERSON_TABLE_SPECS,
            settings=settings,
            extractor_factory=SalesExtractor,
            loader_factory=BronzeLoader,
            validator_factory=BronzeValidator,
        )

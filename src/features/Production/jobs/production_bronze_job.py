from src.core.settings import Settings
from src.features.Sales_Performance.domain.bronze.bronze_loader import BronzeLoader
from src.features.Sales_Performance.domain.bronze.bronze_validator import BronzeValidator
from src.features.Sales_Performance.domain.bronze.sales_extractor import SalesExtractor
from src.shared.ingestion.domain_bronze_job import DomainBronzeJob
from src.shared.ingestion.ingestion_models import TableSpec


PRODUCTION_TABLE_SPECS = (
    TableSpec(
        "Production", "Product", "bronze", "product",
        "ProductID", ("ProductID",), "ProductID",
    ),
)


class ProductionBronzeJob(DomainBronzeJob):
    def __init__(self, settings: Settings | None = None):
        super().__init__(
            PRODUCTION_TABLE_SPECS,
            settings=settings,
            extractor_factory=SalesExtractor,
            loader_factory=BronzeLoader,
            validator_factory=BronzeValidator,
        )

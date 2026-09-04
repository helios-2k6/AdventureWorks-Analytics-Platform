from src.core.settings import Settings
from src.features.Sales_Performance.domain.bronze.bronze_loader import BronzeLoader
from src.features.Sales_Performance.domain.bronze.bronze_validator import BronzeValidator
from src.features.Sales_Performance.domain.bronze.sales_extractor import SalesExtractor
from src.shared.ingestion.domain_bronze_job import DomainBronzeJob
from src.shared.ingestion.ingestion_models import TableSpec


SALES_TABLE_SPECS = (
    TableSpec(
        "Sales", "SalesOrderHeader", "bronze", "sales_order_header",
        "SalesOrderID", ("SalesOrderID",), "SalesOrderID",
    ),
    TableSpec(
        "Sales", "SalesOrderDetail", "bronze", "sales_order_detail",
        "SalesOrderDetailID", ("SalesOrderDetailID",), "SalesOrderDetailID",
    ),
    TableSpec(
        "Sales", "Customer", "bronze", "customer",
        "CustomerID", ("CustomerID",), "CustomerID",
    ),
    TableSpec(
        "Sales", "SalesTerritory", "bronze", "sales_territory",
        "TerritoryID", ("TerritoryID",), "TerritoryID",
    ),
    TableSpec(
        "Sales", "SalesPerson", "bronze", "sales_person",
        "BusinessEntityID", ("BusinessEntityID",), "BusinessEntityID",
    ),
)


class SalesBronzeJob(DomainBronzeJob):
    def __init__(self, settings: Settings | None = None):
        super().__init__(
            SALES_TABLE_SPECS,
            settings=settings,
            extractor_factory=SalesExtractor,
            loader_factory=BronzeLoader,
            validator_factory=BronzeValidator,
        )

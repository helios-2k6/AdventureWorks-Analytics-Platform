from datetime import datetime
from typing import Dict, Optional

from src.domain.bronze.bronze_loader import BronzeLoader
from src.domain.bronze.bronze_validator import BronzeValidator
from src.domain.bronze.sales_extractor import SalesExtractor


class SalesBronzeIngestionJob:
    """ETL orchestration for loading sales source tables into Bronze."""

    def __init__(self):
        self.extractor = SalesExtractor()
        self.loader = BronzeLoader()
        self.validator = BronzeValidator()

    def run(self, mode: str = "full", load_date: Optional[datetime] = None) -> Dict[str, Dict]:
        if load_date is None:
            load_date = datetime.now()

        extraction_map = [
            ("Sales", "SalesOrderHeader", "sales_order_header"),
            ("Sales", "SalesOrderDetail", "sales_order_detail"),
            ("Sales", "Customer", "customer"),
            ("Sales", "SalesTerritory", "sales_territory"),
            ("Sales", "SalesPerson", "sales_person"),
            ("Production", "Product", "product"),
        ]

        results = {}

        for source_schema, source_table, bronze_table in extraction_map:
            df = self.extractor.extract_table(source_schema, source_table, load_date)
            source_count = len(df)
            target_count, success = self.loader.load(df, "bronze", bronze_table, if_exists="replace" if mode == "full" else "append")

            validation_ok = self.validator.validate(
                source_count=source_count,
                target_count=target_count,
                source_table=f"{source_schema}.{source_table}",
                bronze_table=f"bronze.{bronze_table}",
            )

            results[bronze_table] = {
                "source_table": f"{source_schema}.{source_table}",
                "source_count": source_count,
                "target_count": target_count,
                "validation_passed": validation_ok,
                "status": "SUCCESS" if (success and validation_ok) else "FAILED",
            }

        return results

"""Backward-compatible re-export of the sales bronze ingestion job.

New code should import from src.features.Sales_Performance.jobs.sales_bronze_ingestion_job
"""

from src.features.Sales_Performance.jobs.sales_bronze_ingestion_job import SalesBronzeIngestionJob

__all__ = ["SalesBronzeIngestionJob"]

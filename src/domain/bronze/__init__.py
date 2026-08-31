"""Backward-compatible re-export of bronze domain models.

New code should import from src.features.Sales_Performance.domain.bronze
"""

from src.features.Sales_Performance.domain.bronze.bronze_loader import BronzeLoader
from src.features.Sales_Performance.domain.bronze.bronze_validator import BronzeValidator
from src.features.Sales_Performance.domain.bronze.sales_extractor import SalesExtractor

__all__ = ["BronzeLoader", "BronzeValidator", "SalesExtractor"]

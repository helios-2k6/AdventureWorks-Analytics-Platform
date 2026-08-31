"""Backward-compatible re-export of the sales extractor.

New code should import from src.features.Sales_Performance.domain.bronze.sales_extractor
"""

from src.features.Sales_Performance.domain.bronze.sales_extractor import SalesExtractor

__all__ = ["SalesExtractor"]

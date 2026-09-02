"""Domain layer for business logic and domain-specific processing.

Note: This layer is being deprecated in favor of src.features.* packages.
Bronze domain classes are re-exported here for backward compatibility.
"""

from src.domain.bronze.bronze_loader import BronzeLoader
from src.domain.bronze.bronze_validator import BronzeValidator
from src.domain.bronze.sales_extractor import SalesExtractor

__all__ = ["BronzeLoader", "BronzeValidator", "SalesExtractor"]

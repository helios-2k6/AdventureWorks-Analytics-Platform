"""Backward-compatible re-export of the bronze validator.

New code should import from src.features.Sales_Performance.domain.bronze.bronze_validator
"""

from src.features.Sales_Performance.domain.bronze.bronze_validator import BronzeValidator

__all__ = ["BronzeValidator"]

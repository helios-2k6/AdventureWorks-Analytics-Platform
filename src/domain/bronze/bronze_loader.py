"""Backward-compatible re-export of the bronze loader.

New code should import from src.features.Sales_Performance.domain.bronze.bronze_loader
"""

from src.features.Sales_Performance.domain.bronze.bronze_loader import BronzeLoader

__all__ = ["BronzeLoader"]

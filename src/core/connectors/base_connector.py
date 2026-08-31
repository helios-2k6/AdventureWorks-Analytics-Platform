"""Backward-compatible re-export of the base connector.

New code should import from src.shared.connectors.base_connector
"""

from src.shared.connectors.base_connector import BaseConnector

__all__ = ["BaseConnector"]

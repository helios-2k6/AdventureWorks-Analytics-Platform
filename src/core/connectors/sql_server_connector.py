"""Backward-compatible re-export of the SQL Server connector.

New code should import from src.shared.connectors.sql_server_connector
"""

from src.shared.connectors.sql_server_connector import SQLServerConnector

__all__ = ["SQLServerConnector"]

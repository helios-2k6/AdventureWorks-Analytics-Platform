"""Backward-compatible re-export of the PostgreSQL connector.

New code should import from src.shared.connectors.postgres_connector
"""

from src.shared.connectors.postgres_connector import PostgreSQLConnector

__all__ = ["PostgreSQLConnector"]

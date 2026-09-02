import logging
import os

import pyodbc

from src.shared.connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class SQLServerConnector(BaseConnector):
    """SQL Server connection handler for AdventureWorks2012."""

    def __init__(self, use_windows_auth: bool = True):
        super().__init__()
        self.host = os.getenv("SQL_SERVER_HOST")
        self.port = os.getenv("SQL_SERVER_PORT", 1433)
        self.database = os.getenv("SQL_SERVER_DATABASE", "AdventureWorks2012")
        self.username = os.getenv("SQL_SERVER_USERNAME")
        self.password = os.getenv("SQL_SERVER_PASSWORD")
        self.driver = os.getenv("SQL_SERVER_DRIVER", "ODBC Driver 17 for SQL Server")
        self.use_windows_auth = use_windows_auth

    def connect(self) -> bool:
        try:
            if self.use_windows_auth:
                connection_string = (
                    f"Driver={{{self.driver}}};"
                    f"Server={self.host};"
                    f"Database={self.database};"
                    f"Trusted_Connection=yes;"
                )
            else:
                connection_string = (
                    f"Driver={{{self.driver}}};"
                    f"Server={self.host},{self.port};"
                    f"Database={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                )

            self.connection = pyodbc.connect(connection_string)
            logger.info("Connected to SQL Server: %s/%s", self.host, self.database)
            return True
        except Exception as exc:  # pragma: no cover - logging branch
            logger.error("Failed to connect to SQL Server: %s", exc)
            self.connection = None
            return False

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from SQL Server")

    def execute_query(self, query: str):
        if not self.connection:
            raise RuntimeError("Not connected to SQL Server")
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()

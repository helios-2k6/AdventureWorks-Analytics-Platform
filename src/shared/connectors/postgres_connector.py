import logging
import os
from typing import Optional

import psycopg2

from src.shared.connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class PostgreSQLConnector(BaseConnector):
    """PostgreSQL connection handler for the analytics warehouse."""

    def __init__(self):
        super().__init__()
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = os.getenv("POSTGRES_PORT", 5432)
        self.database = os.getenv("POSTGRES_DATABASE", "adventureworks_warehouse")
        self.username = os.getenv("POSTGRES_USERNAME", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")

    def connect(self) -> bool:
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
            )
            logger.info("Connected to PostgreSQL: %s/%s", self.host, self.database)
            return True
        except Exception as exc:  # pragma: no cover - logging branch
            logger.error("Failed to connect to PostgreSQL: %s", exc)
            self.connection = None
            return False

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from PostgreSQL")

    def execute_query(self, query: str, params: Optional[tuple] = None):
        if not self.connection:
            raise RuntimeError("Not connected to PostgreSQL")
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetch_results(self, query: str, params: Optional[tuple] = None):
        cursor = self.execute_query(query, params)
        try:
            return cursor.fetchall()
        finally:
            cursor.close()

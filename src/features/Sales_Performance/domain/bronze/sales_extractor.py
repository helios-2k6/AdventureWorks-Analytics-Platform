from datetime import datetime
import hashlib
import json
from typing import Optional

import pandas as pd

from src.shared.connectors.sql_server_connector import SQLServerConnector


class SalesExtractor:
    """Extract sales-domain source tables from SQL Server."""

    def __init__(self, source_system: str = "AdventureWorks2012"):
        self.source_system = source_system

    def extract_table(self, source_schema: str, source_table: str, load_date: Optional[datetime] = None):
        if load_date is None:
            load_date = datetime.now()

        full_table_name = f"{source_schema}.{source_table}"

        with SQLServerConnector() as sql_conn:
            cursor = sql_conn.connection.cursor()
            try:
                cursor.execute(f"SELECT * FROM {full_table_name}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
            finally:
                cursor.close()

        normalized_rows = [tuple(row) for row in rows]
        df = pd.DataFrame(normalized_rows, columns=columns)
        df["_source_system"] = self.source_system
        df["_source_table"] = full_table_name
        df["_load_date"] = load_date

        def compute_record_hash(row: pd.Series) -> str:
            payload = row.drop(labels=["_source_system", "_source_table", "_load_date"], errors="ignore").to_dict()
            normalized = json.dumps(payload, default=str, sort_keys=True)
            return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

        df["_record_hash"] = df.apply(compute_record_hash, axis=1)
        return df

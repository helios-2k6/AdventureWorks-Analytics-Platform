from datetime import datetime
from typing import Optional

import pandas as pd

from src.core.connectors import SQLServerConnector


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

        df = pd.DataFrame(rows, columns=columns)
        df["_source_system"] = self.source_system
        df["_source_table"] = full_table_name
        df["_load_date"] = load_date
        return df

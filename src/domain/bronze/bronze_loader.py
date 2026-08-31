from typing import Tuple

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from src.core.connectors import PostgreSQLConnector


class BronzeLoader:
    """Load DataFrames into PostgreSQL Bronze tables."""

    def load(self, df: pd.DataFrame, target_schema: str, target_table: str, if_exists: str = "replace") -> Tuple[int, bool]:
        with PostgreSQLConnector() as pg_conn:
            engine = create_engine(
                "postgresql://",
                creator=lambda: pg_conn.connection,
                poolclass=StaticPool,
            )
            df.to_sql(
                target_table,
                engine,
                schema=target_schema,
                if_exists=if_exists,
                index=False,
                method="multi",
                chunksize=1000,
            )
            return len(df), True

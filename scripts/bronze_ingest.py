"""Bronze ingestion utilities for AdventureWorks Phase 0."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from src.connectors import PostgreSQLConnector, SQLServerConnector


def bronze_ingest_table(source_table: str, source_system: str = "AdventureWorks2012") -> int:
    """Load a source SQL Server table into the bronze schema with lineage columns."""
    table_name = source_table.replace('.', '_').lower()
    bronze_table = f"bronze.{table_name}"

    with SQLServerConnector() as sql_conn:
        cursor = sql_conn.connection.cursor()
        try:
            cursor.execute(f"SELECT TOP 1 * FROM {source_table}")
            if cursor.description is None:
                raise ValueError(f"Table {source_table} not found or empty")
            cursor.execute(f"SELECT * FROM {source_table}")
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
        finally:
            cursor.close()

    if not rows:
        raise ValueError(f"Source table {source_table} has no rows")

    row_values = [tuple(row) for row in rows]
    df = pd.DataFrame(row_values, columns=columns)
    df = df.copy()
    df['_load_date'] = datetime.utcnow().date()
    df['_source_system'] = source_system

    columns = list(df.columns)
    quoted_columns = [f'"{str(col)}"' for col in columns]

    with PostgreSQLConnector() as pg_conn:
        pg_conn.execute_query(f"DROP TABLE IF EXISTS {bronze_table}")
        create_columns = ', '.join(f'"{str(col)}" TEXT' for col in columns)
        pg_conn.execute_query(f"CREATE TABLE {bronze_table} ({create_columns})")

        insert_sql = (
            f"INSERT INTO {bronze_table} ({', '.join(quoted_columns)}) "
            f"VALUES ({', '.join(['%s'] * len(columns))})"
        )
        values = [tuple(row) for row in df.itertuples(index=False, name=None)]

        with pg_conn.connection.cursor() as cursor:
            cursor.executemany(insert_sql, values)
            pg_conn.connection.commit()

        pg_conn.execute_query(
            """
            INSERT INTO bronze.load_audit (table_name, source_system, row_count, status)
            VALUES (%s, %s, %s, %s)
            """,
            (table_name, source_system, len(df), 'success')
        )

    return len(df)

from uuid import uuid4

from psycopg2 import sql

from src.core.settings import Settings, get_settings
from src.shared.connectors.postgres_connector import PostgreSQLConnector
from src.shared.ingestion.postgres_ingestion_schema import ensure_ingestion_schema


class PostgresPublishService:
    """Atomically promote a validated staging table into published Bronze."""

    staging_schema = "bronze_staging"
    published_schema = "bronze"

    def __init__(
        self,
        settings: Settings | None = None,
        staging_schema: str | None = None,
        published_schema: str | None = None,
    ):
        self.settings = settings or get_settings()
        self.staging_schema = staging_schema or type(self).staging_schema
        self.published_schema = published_schema or type(self).published_schema
        ensure_ingestion_schema(self.settings)

    def publish(
        self,
        target_table: str,
        staging_table: str,
        validation_report: dict | None = None,
    ) -> str:
        if validation_report is None or not validation_report.get("validation_passed"):
            raise ValueError("staging validation must pass before PostgreSQL publish")
        self._validate_identifier(target_table)
        self._validate_identifier(staging_table)

        with PostgreSQLConnector(settings=self.settings) as connection:
            cursor = connection.connection.cursor()
            try:
                cursor.execute(
                    "SELECT to_regclass(%s)",
                    (f"{self.staging_schema}.{staging_table}",),
                )
                if cursor.fetchone()[0] is None:
                    raise ValueError(f"staging table does not exist: {staging_table}")

                cursor.execute(
                    "SELECT to_regclass(%s)",
                    (f"{self.published_schema}.{target_table}",),
                )
                if cursor.fetchone()[0] is not None:
                    backup_table = f"{target_table}__previous__{uuid4().hex}"
                    self._validate_identifier(backup_table)
                    cursor.execute(
                        sql.SQL("ALTER TABLE {}.{} RENAME TO {}").format(
                            sql.Identifier(self.published_schema),
                            sql.Identifier(target_table),
                            sql.Identifier(backup_table),
                        )
                    )

                cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} SET SCHEMA {}").format(
                        sql.Identifier(self.staging_schema),
                        sql.Identifier(staging_table),
                        sql.Identifier(self.published_schema),
                    )
                )
                cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} RENAME TO {}").format(
                        sql.Identifier(self.published_schema),
                        sql.Identifier(staging_table),
                        sql.Identifier(target_table),
                    )
                )
                connection.connection.commit()
            except Exception:
                connection.connection.rollback()
                raise
            finally:
                cursor.close()
        return f"{self.published_schema}.{target_table}"

    @staticmethod
    def _validate_identifier(identifier: str) -> None:
        if not identifier or not identifier.replace("_", "a").isalnum():
            raise ValueError(f"Invalid publish identifier: {identifier!r}")
        if not (identifier[0].isalpha() or identifier[0] == "_"):
            raise ValueError(f"Invalid publish identifier: {identifier!r}")


class PostgresSilverPublishService(PostgresPublishService):
    """Atomically promote a validated Silver staging table into Silver."""

    staging_schema = "silver_staging"
    published_schema = "silver"
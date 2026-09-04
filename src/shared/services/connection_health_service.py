from typing import Any, Dict, List

from src.shared.connectors.postgres_connector import PostgreSQLConnector
from src.shared.connectors.sql_server_connector import SQLServerConnector
from src.core.settings import Settings, get_settings


class ConnectionHealthService:
    """Service for checking whether configured connections are healthy."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def _check_connector(self, name: str, connector: Any) -> Dict[str, Any]:
        try:
            connected = connector.connect()
            if connected:
                return {
                    "name": name,
                    "status": "ok",
                    "message": f"{name} connection successful",
                }
            return {
                "name": name,
                "status": "failed",
                "message": f"{name} connection failed",
            }
        except Exception as exc:  # pragma: no cover - defensive branch
            return {
                "name": name,
                "status": "failed",
                "message": f"{name} connection error: {exc}",
            }
        finally:
            connector.disconnect()

    def check_all(self) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = [
            self._check_connector(
                "sql_server", SQLServerConnector(settings=self.settings)
            ),
            self._check_connector(
                "postgres", PostgreSQLConnector(settings=self.settings)
            ),
        ]

        overall_status = "ok" if all(item["status"] == "ok" for item in results) else "degraded"
        return {
            "status": overall_status,
            "connections": results,
        }

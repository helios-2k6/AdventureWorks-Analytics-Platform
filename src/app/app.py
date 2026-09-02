from src.jobs.platform_bootstrap import PlatformBootstrapJob
from src.features.Sales_Performance.jobs.sales_bronze_ingestion_job import SalesBronzeIngestionJob
from src.shared.services.connection_health_service import ConnectionHealthService


class App:
    """Application bootstrap and orchestration entry point."""

    def __init__(self, bootstrap_job=None, health_service=None, bronze_job=None):
        self.bootstrap_job = bootstrap_job or PlatformBootstrapJob()
        self.health_service = health_service or ConnectionHealthService()
        self.bronze_job = bronze_job or SalesBronzeIngestionJob()
        self._running = False

    def run(self):
        """Run the application workflow using job and service classes."""
        self._running = True
        health_result = self.health_service.check_all()
        bootstrap_result = self.bootstrap_job.run()
        bronze_result = self.bronze_job.run(mode="full")
        bronze_ok = all(
            item.get("status") == "SUCCESS" for item in bronze_result.values()
        )
        overall_status = (
            "ok"
            if health_result.get("status") == "ok"
            and bootstrap_result.get("status") == "ok"
            and bronze_ok
            else "degraded"
        )
        return {
            "status": overall_status,
            "health": health_result,
            "bootstrap": bootstrap_result,
            "bronze": bronze_result,
        }

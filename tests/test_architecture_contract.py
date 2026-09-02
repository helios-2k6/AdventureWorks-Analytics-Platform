from src.app.app import App
from src.jobs.platform_bootstrap import PlatformBootstrapJob
from src.shared.services.connection_health_service import ConnectionHealthService


def test_application_entrypoint_exists():
    app = App()
    assert app is not None
    assert hasattr(app, "run")


def test_platform_bootstrap_job_exists():
    job = PlatformBootstrapJob()
    assert job is not None
    assert hasattr(job, "run")


def test_connection_service_exists():
    service = ConnectionHealthService()
    assert service is not None
    assert hasattr(service, "check_all")

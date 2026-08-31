from src.jobs.sales_bronze_ingestion_job import SalesBronzeIngestionJob


def test_sales_bronze_ingestion_job_exists():
    job = SalesBronzeIngestionJob()
    assert job is not None
    assert hasattr(job, "run")

"""Compatibility wrapper for Bronze ingestion.

This script intentionally delegates all real processing to the new class-based
job implementation so the project keeps a single source of truth for ETL logic.
"""

import argparse
import sys

from src.jobs.sales_bronze_ingestion_job import SalesBronzeIngestionJob
from src.utils.logger import setup_logging

logger = setup_logging(__name__)


def main():
    """CLI entry point retained for compatibility with legacy usage."""
    parser = argparse.ArgumentParser(
        description="Bronze extraction for sales domain"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="full",
        help="Extraction mode",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level",
    )
    args = parser.parse_args()

    job = SalesBronzeIngestionJob()
    logger.info("Starting Bronze ingestion via class-based job")
    results = job.run(mode=args.mode)

    failed = sum(1 for item in results.values() if item.get("status") not in ["SUCCESS"])
    if failed:
        logger.error("Bronze ingestion completed with failures")
        sys.exit(1)

    logger.info("Bronze ingestion completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Deprecated compatibility wrapper for Bronze ingestion.

This script is retained only for backward compatibility. All real ETL logic must
live in the canonical class-based job implementation in
`src.features.Sales_Performance.jobs.sales_bronze_ingestion_job`. New work should not be added here.
"""

import argparse
import sys

from src.features.Sales_Performance.jobs.sales_bronze_ingestion_job import SalesBronzeIngestionJob
from src.utils.logger import setup_logging

logger = setup_logging(__name__)


def main():
    """Deprecated CLI entry point retained for backward compatibility."""
    logger.warning(
        "DEPRECATION WARNING: %s is a compatibility wrapper only. "
        "Use src.features.Sales_Performance.jobs.sales_bronze_ingestion_job.SalesBronzeIngestionJob as the canonical ingestion path.",
        __file__,
    )
    parser = argparse.ArgumentParser(
        description="Deprecated compatibility wrapper for Bronze extraction. Use the class-based job instead."
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

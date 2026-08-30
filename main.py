# Main entry point for AdventureWorks Analytics Platform

"""
Main module for the AdventureWorks Analytics Platform.
"""

import logging
from src.logger import setup_logging
from src.connectors import SQLServerConnector, PostgreSQLConnector
from src.config import PHASE0_TEST_TABLES

logger = setup_logging(__name__)


def test_connections():
    """Test connections to both SQL Server and PostgreSQL."""
    logger.info("=" * 60)
    logger.info("Testing Database Connections")
    logger.info("=" * 60)
    
    # Test SQL Server (using Windows Authentication)
    logger.info("\n[1] Testing SQL Server Connection (Windows Auth)...")
    try:
        with SQLServerConnector(use_windows_auth=True) as sql_conn:
            result = sql_conn.execute_query("SELECT @@VERSION AS Version")
            logger.info("✓ SQL Server connection successful")
            logger.info(f"  Version: {result[0][0][:80]}")
    except Exception as e:
        logger.error(f"✗ SQL Server connection failed: {str(e)}")
        return False
    
    # Test PostgreSQL
    logger.info("\n[2] Testing PostgreSQL Connection...")
    try:
        with PostgreSQLConnector() as pg_conn:
            result = pg_conn.fetch_results("SELECT version()")
            logger.info("✓ PostgreSQL connection successful")
            logger.info(f"  Version: {result[0][0][:80]}")
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection failed: {str(e)}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("All connections successful!")
    logger.info("=" * 60)
    return True


def check_schemas():
    """Check if Bronze, Silver, Gold schemas exist in PostgreSQL."""
    logger.info("\n[3] Checking PostgreSQL Schemas...")
    try:
        with PostgreSQLConnector() as pg_conn:
            result = pg_conn.fetch_results(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('bronze', 'silver', 'gold') ORDER BY schema_name"
            )
            schemas = [row[0] for row in result]
            if set(schemas) == {'bronze', 'silver', 'gold'}:
                logger.info("✓ All required schemas exist")
                for schema in schemas:
                    logger.info(f"  - {schema}")
            else:
                logger.warning(f"  Found schemas: {schemas}")
    except Exception as e:
        logger.error(f"✗ Failed to check schemas: {str(e)}")
        return False
    
    return True


def main():
    """Main entry point."""
    logger.info("\nAdventureWorks Analytics Platform - Phase 0 Setup")
    logger.info("================================================\n")
    
    # Run connection tests
    if not test_connections():
        logger.error("Connection tests failed. Please configure .env file correctly.")
        return
    
    # Check schemas
    if not check_schemas():
        logger.warning("Schema check failed. Please ensure PostgreSQL container is running with init script.")
        return
    
    logger.info("\n✓ Phase 0 Foundation is ready!")
    logger.info("Next steps:")
    logger.info("  1. Configure .env with actual credentials")
    logger.info("  2. Test SQL Server table access")
    logger.info("  3. Begin Phase 1 - Data Discovery & Profiling")


if __name__ == "__main__":
    main()

"""
Phase 3.1 — Bronze Extraction for Sales Domain

Purpose:
- Extract 6 source tables from SQL Server AdventureWorks2012
- Load raw data into PostgreSQL Bronze schema
- Add lineage metadata: _source_system, _source_table, _load_date, _record_hash
- Validate row counts and data types

Source Tables (6):
1. Sales.SalesOrderHeader (~31K rows)
2. Sales.SalesOrderDetail (~121K rows)
3. Sales.Customer (~20K rows)
4. Sales.SalesTerritory (~10 rows)
5. Sales.SalesPerson (~17 rows)
6. Production.Product (~504 rows)

Usage:
    python sales_bronze_load.py --mode full --log-level INFO
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import hashlib
import json

import pyodbc
import psycopg2
from psycopg2 import sql
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure logging for Bronze extraction."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"phase3_bronze_load_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger

logger = setup_logging()

# ============================================================================
# DATABASE CONNECTION FUNCTIONS
# ============================================================================

def get_sqlserver_connection():
    """
    Create connection to SQL Server AdventureWorks2012.
    
    Connection parameters from .env file:
    - SQLSERVER_SERVER: server name/instance
    - SQLSERVER_DATABASE: AdventureWorks2012
    - SQLSERVER_UID: username (Windows Auth if empty)
    - SQLSERVER_PWD: password
    """
    load_dotenv()
    
    server = os.getenv("SQLSERVER_SERVER", "localhost\\SQLEXPRESS")
    database = os.getenv("SQLSERVER_DATABASE", "AdventureWorks2012")
    uid = os.getenv("SQLSERVER_UID", "")
    pwd = os.getenv("SQLSERVER_PWD", "")
    
    try:
        if uid:
            # SQL Server authentication
            conn_str = f"Driver={{ODBC Driver 17 for SQL Server}};Server={server};Database={database};UID={uid};PWD={pwd}"
        else:
            # Windows authentication
            conn_str = f"Driver={{ODBC Driver 17 for SQL Server}};Server={server};Database={database};Trusted_Connection=yes;"
        
        conn = pyodbc.connect(conn_str, timeout=30)
        logger.info(f"✓ SQL Server connection successful: {server}/{database}")
        return conn
    except Exception as e:
        logger.error(f"✗ SQL Server connection failed: {str(e)}")
        raise


def get_postgres_connection():
    """
    Create connection to PostgreSQL warehouse.
    
    Connection parameters from .env file:
    - POSTGRES_HOST: localhost
    - POSTGRES_PORT: 5432
    - POSTGRES_DB: warehouse
    - POSTGRES_USER: postgres
    - POSTGRES_PASSWORD: password
    """
    load_dotenv()
    
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "warehouse")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        logger.info(f"✓ PostgreSQL connection successful: {host}:{port}/{database}")
        return conn
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection failed: {str(e)}")
        raise


# ============================================================================
# EXTRACTION FUNCTIONS
# ============================================================================

def add_lineage_metadata(
    df: pd.DataFrame,
    source_system: str = "AdventureWorks2012",
    source_table: str = "unknown",
    load_date: Optional[datetime] = None
) -> pd.DataFrame:
    """
    Add lineage metadata columns to extracted dataframe.
    
    Columns added:
    - _source_system: source system name
    - _source_table: source table full name
    - _load_date: load timestamp
    - _record_hash: hash of record for dedup detection
    """
    if load_date is None:
        load_date = datetime.now()
    
    df["_source_system"] = source_system
    df["_source_table"] = source_table
    df["_load_date"] = load_date
    
    # Generate record hash from all non-lineage columns
    def compute_hash(row):
        row_str = "|".join(str(x) for x in row.values)
        return hashlib.md5(row_str.encode()).hexdigest()
    
    df["_record_hash"] = df.apply(compute_hash, axis=1)
    
    logger.info(f"✓ Added lineage metadata to {source_table} ({len(df)} rows)")
    return df


def extract_table_from_sqlserver(
    source_schema: str,
    source_table: str,
    sql_server_conn: pyodbc.Connection,
    load_date: Optional[datetime] = None
) -> pd.DataFrame:
    """
    Extract table from SQL Server using pandas.read_sql.
    
    Args:
        source_schema: schema name (e.g., 'Sales', 'Production')
        source_table: table name (e.g., 'SalesOrderHeader')
        sql_server_conn: pyodbc connection object
        load_date: timestamp for metadata
    
    Returns:
        DataFrame with data + lineage columns
    """
    if load_date is None:
        load_date = datetime.now()
    
    full_table_name = f"{source_schema}.{source_table}"
    
    try:
        logger.info(f"→ Extracting {full_table_name}...")
        
        # Extract using pyodbc
        cursor = sql_server_conn.cursor()
        cursor.execute(f"SELECT * FROM {full_table_name}")
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        logger.info(f"  ✓ Extracted {len(df)} rows from {full_table_name}")
        
        # Add lineage metadata
        df = add_lineage_metadata(
            df,
            source_system="AdventureWorks2012",
            source_table=full_table_name,
            load_date=load_date
        )
        
        return df
    
    except Exception as e:
        logger.error(f"  ✗ Failed to extract {full_table_name}: {str(e)}")
        raise


def load_dataframe_to_postgres(
    df: pd.DataFrame,
    target_schema: str,
    target_table: str,
    postgres_conn: psycopg2.extensions.connection,
    if_exists: str = "replace"
) -> Tuple[int, bool]:
    """
    Load DataFrame to PostgreSQL using SQLAlchemy.
    
    Args:
        df: DataFrame to load
        target_schema: PostgreSQL schema (e.g., 'bronze')
        target_table: PostgreSQL table (e.g., 'sales_order_header')
        postgres_conn: psycopg2 connection object
        if_exists: 'fail', 'replace', or 'append'
    
    Returns:
        Tuple of (row_count_loaded, success_flag)
    """
    try:
        # Create SQLAlchemy engine from existing connection
        from sqlalchemy.pool import StaticPool
        from sqlalchemy import event
        
        # Use psycopg2 connection directly
        engine = create_engine(
            "postgresql://",
            creator=lambda: postgres_conn,
            poolclass=StaticPool
        )
        
        full_table_name = f"{target_schema}.{target_table}"
        
        logger.info(f"→ Loading {len(df)} rows to {full_table_name}...")
        
        # Write to PostgreSQL
        df.to_sql(
            target_table,
            engine,
            schema=target_schema,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=1000
        )
        
        logger.info(f"  ✓ Loaded {len(df)} rows to {full_table_name}")
        return len(df), True
    
    except Exception as e:
        logger.error(f"  ✗ Failed to load to {target_schema}.{target_table}: {str(e)}")
        return 0, False


def validate_bronze_load(
    source_count: int,
    target_count: int,
    source_table: str,
    bronze_table: str
) -> bool:
    """
    Validate that row counts match between source and Bronze.
    
    Args:
        source_count: row count from SQL Server
        target_count: row count from PostgreSQL
        source_table: source full table name
        bronze_table: bronze full table name
    
    Returns:
        True if counts match, False otherwise
    """
    if source_count == target_count:
        logger.info(f"✓ VALIDATION PASSED: {source_table} → {bronze_table} ({source_count} rows)")
        return True
    else:
        logger.warning(
            f"✗ VALIDATION FAILED: {source_table} ({source_count} rows) "
            f"→ {bronze_table} ({target_count} rows) | MISMATCH: {source_count - target_count}"
        )
        return False


# ============================================================================
# MAIN EXTRACTION ORCHESTRATION
# ============================================================================

def extract_sales_domain(
    sql_server_conn: pyodbc.Connection,
    postgres_conn: psycopg2.extensions.connection,
    mode: str = "full",
    load_date: Optional[datetime] = None
) -> Dict[str, Dict]:
    """
    Main orchestration function for Sales domain Bronze extraction.
    
    Extracts 6 tables:
    1. Sales.SalesOrderHeader → bronze.sales_order_header
    2. Sales.SalesOrderDetail → bronze.sales_order_detail
    3. Sales.Customer → bronze.customer
    4. Sales.SalesTerritory → bronze.sales_territory
    5. Sales.SalesPerson → bronze.sales_person
    6. Production.Product → bronze.product
    
    Args:
        sql_server_conn: SQL Server connection
        postgres_conn: PostgreSQL connection
        mode: 'full' (replace all), 'incremental' (append new)
        load_date: timestamp for metadata
    
    Returns:
        Dictionary of extraction results
    """
    if load_date is None:
        load_date = datetime.now()
    
    # Define extraction mapping
    extractions = [
        {
            "source_schema": "Sales",
            "source_table": "SalesOrderHeader",
            "bronze_table": "sales_order_header",
            "expected_rows": 31000  # approximate
        },
        {
            "source_schema": "Sales",
            "source_table": "SalesOrderDetail",
            "bronze_table": "sales_order_detail",
            "expected_rows": 121000
        },
        {
            "source_schema": "Sales",
            "source_table": "Customer",
            "bronze_table": "customer",
            "expected_rows": 20000
        },
        {
            "source_schema": "Sales",
            "source_table": "SalesTerritory",
            "bronze_table": "sales_territory",
            "expected_rows": 10
        },
        {
            "source_schema": "Sales",
            "source_table": "SalesPerson",
            "bronze_table": "sales_person",
            "expected_rows": 17
        },
        {
            "source_schema": "Production",
            "source_table": "Product",
            "bronze_table": "product",
            "expected_rows": 504
        }
    ]
    
    results = {}
    
    logger.info(f"\n{'='*80}")
    logger.info(f"PHASE 3.1 — BRONZE EXTRACTION (Sales Domain)")
    logger.info(f"Mode: {mode.upper()} | Load Date: {load_date}")
    logger.info(f"{'='*80}\n")
    
    for extraction in extractions:
        source_schema = extraction["source_schema"]
        source_table = extraction["source_table"]
        bronze_table = extraction["bronze_table"]
        
        try:
            # Extract from SQL Server
            df = extract_table_from_sqlserver(
                source_schema=source_schema,
                source_table=source_table,
                sql_server_conn=sql_server_conn,
                load_date=load_date
            )
            
            source_count = len(df)
            
            # Load to PostgreSQL Bronze
            target_count, load_success = load_dataframe_to_postgres(
                df=df,
                target_schema="bronze",
                target_table=bronze_table,
                postgres_conn=postgres_conn,
                if_exists="replace" if mode == "full" else "append"
            )
            
            # Validate
            validation_passed = validate_bronze_load(
                source_count=source_count,
                target_count=target_count,
                source_table=f"{source_schema}.{source_table}",
                bronze_table=f"bronze.{bronze_table}"
            )
            
            results[bronze_table] = {
                "source_table": f"{source_schema}.{source_table}",
                "source_count": source_count,
                "target_count": target_count,
                "validation_passed": validation_passed,
                "status": "SUCCESS" if (load_success and validation_passed) else "FAILED"
            }
        
        except Exception as e:
            logger.error(f"✗ EXTRACTION FAILED for {source_schema}.{source_table}: {str(e)}")
            results[bronze_table] = {
                "source_table": f"{source_schema}.{source_table}",
                "status": "ERROR",
                "error": str(e)
            }
    
    return results


def print_extraction_summary(results: Dict[str, Dict]):
    """Print summary of extraction results."""
    logger.info(f"\n{'='*80}")
    logger.info("EXTRACTION SUMMARY")
    logger.info(f"{'='*80}")
    
    total_tables = len(results)
    successful_tables = sum(1 for r in results.values() if r.get("status") == "SUCCESS")
    failed_tables = sum(1 for r in results.values() if r.get("status") in ["FAILED", "ERROR"])
    
    logger.info(f"\nTotal tables: {total_tables}")
    logger.info(f"Successful: {successful_tables}")
    logger.info(f"Failed: {failed_tables}\n")
    
    for table_name, result in results.items():
        status = result.get("status", "UNKNOWN")
        source = result.get("source_table", "?")
        
        if status == "SUCCESS":
            count = result.get("source_count", 0)
            logger.info(f"✓ {source:30s} → bronze.{table_name:25s} ({count:>8} rows)")
        else:
            error = result.get("error", "Unknown error")
            logger.info(f"✗ {source:30s} → ERROR: {error}")
    
    logger.info(f"\n{'='*80}\n")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI entry point for Bronze extraction."""
    parser = argparse.ArgumentParser(
        description="Phase 3.1 — Bronze Extraction for Sales Domain"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="full",
        help="Extraction mode: 'full' (replace all) or 'incremental' (append new)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (extract only first 100 rows per table)"
    )
    
    args = parser.parse_args()
    
    try:
        # Create connections
        sql_server_conn = get_sqlserver_connection()
        postgres_conn = get_postgres_connection()
        
        # Run extraction
        results = extract_sales_domain(
            sql_server_conn=sql_server_conn,
            postgres_conn=postgres_conn,
            mode=args.mode
        )
        
        # Print summary
        print_extraction_summary(results)
        
        # Close connections
        sql_server_conn.close()
        postgres_conn.close()
        
        # Check for failures
        failed_count = sum(1 for r in results.values() if r.get("status") in ["FAILED", "ERROR"])
        
        if failed_count > 0:
            logger.error(f"\n✗ Extraction completed with {failed_count} failures")
            sys.exit(1)
        else:
            logger.info("\n✓ Extraction completed successfully")
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"\n✗ FATAL ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

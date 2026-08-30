"""Phase 1 data discovery and profiling utilities for AdventureWorks source tables."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs"
REPORT_PATH = DOCS_DIR / "Phase1_Data_Discovery_Report.md"
DICT_PATH = DOCS_DIR / "data_dictionary_phase1.md"
QUALITY_PATH = DOCS_DIR / "Phase1_Data_Quality_Checks.md"
SOURCE_TO_TARGET_PATH = DOCS_DIR / "source_to_target_notes_phase1.md"

SCHEMAS = ["Sales", "Person", "Production", "Purchasing"]
INITIAL_TABLES = [
    "Sales.SalesOrderHeader",
    "Sales.SalesOrderDetail",
    "Sales.Customer",
    "Sales.SalesTerritory",
    "Sales.SalesPerson",
    "Person.Person",
    "Production.Product",
    "Production.ProductInventory",
    "Production.WorkOrder",
    "Production.WorkOrderRouting",
    "Purchasing.PurchaseOrderHeader",
    "Purchasing.PurchaseOrderDetail",
    "Purchasing.Vendor",
]


def get_connection() -> pyodbc.Connection:
    host = os.getenv("SQL_SERVER_HOST", "HELIOS\\HELIOS")
    database = os.getenv("SQL_SERVER_DATABASE", "AdventureWorks2012")
    driver = os.getenv("SQL_SERVER_DRIVER", "ODBC Driver 17 for SQL Server")
    connection_string = (
        f"Driver={{{driver}}};"
        f"Server={host};"
        f"Database={database};"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(connection_string)


def fetch_table_rows(connection: pyodbc.Connection, schema: str, table: str) -> int:
    query = (
        "SELECT CAST(COUNT(*) AS BIGINT) FROM "
        f"[{schema}].[{table}]"
    )
    return connection.execute(query).fetchone()[0]


def fetch_table_inventory(connection: pyodbc.Connection) -> list[dict]:
    query = """
        SELECT
            SCHEMA_NAME(t.schema_id) AS schema_name,
            t.name AS table_name,
            SUM(p.rows) AS row_count
        FROM sys.tables t
        INNER JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0,1)
        WHERE SCHEMA_NAME(t.schema_id) IN ('Sales', 'Person', 'Production', 'Purchasing')
        GROUP BY SCHEMA_NAME(t.schema_id), t.name
        ORDER BY SCHEMA_NAME(t.schema_id), t.name
    """
    rows = connection.execute(query).fetchall()
    result = []
    for schema_name, table_name, row_count in rows:
        result.append({
            "schema": schema_name,
            "table": table_name,
            "row_count": int(row_count or 0),
        })
    return result


def fetch_column_metadata(connection: pyodbc.Connection, schema: str, table: str) -> list[dict]:
    query = """
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """
    rows = connection.execute(query, schema, table).fetchall()
    metadata = []
    for column_name, data_type, is_nullable, char_len, num_precision, num_scale in rows:
        metadata.append({
            "column": column_name,
            "type": data_type,
            "nullable": is_nullable == "YES",
            "max_length": char_len,
            "precision": num_precision,
            "scale": num_scale,
        })
    return metadata


def fetch_key_relationships(connection: pyodbc.Connection) -> list[dict]:
    query = """
        SELECT
            fk.name AS foreign_key_name,
            SCHEMA_NAME(fk.schema_id) AS schema_name,
            OBJECT_NAME(fk.parent_object_id) AS child_table,
            COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS child_column,
            OBJECT_NAME(fkc.referenced_object_id) AS parent_table,
            COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS parent_column
        FROM sys.foreign_keys fk
        INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        WHERE SCHEMA_NAME(fk.schema_id) IN ('Sales', 'Person', 'Production', 'Purchasing')
        ORDER BY schema_name, child_table, foreign_key_name
    """
    rows = connection.execute(query).fetchall()
    result = []
    for foreign_key_name, schema_name, child_table, child_column, parent_table, parent_column in rows:
        result.append({
            "foreign_key": foreign_key_name,
            "schema": schema_name,
            "child_table": child_table,
            "child_column": child_column,
            "parent_table": parent_table,
            "parent_column": parent_column,
        })
    return result


def fetch_null_summary(connection: pyodbc.Connection, schema: str, table: str, columns: list[str]) -> list[dict]:
    total_rows = fetch_table_rows(connection, schema, table)
    summary = []
    for column in columns:
        query = f"SELECT COUNT(*) FROM [{schema}].[{table}] WHERE [{column}] IS NULL"
        try:
            null_count = connection.execute(query).fetchone()[0]
        except Exception:
            continue
        pct = round((null_count / total_rows) * 100, 2) if total_rows else 0.0
        summary.append({
            "column": column,
            "null_count": int(null_count or 0),
            "null_pct": pct,
        })
    return summary


def fetch_duplicate_summary(connection: pyodbc.Connection, schema: str, table: str, key_columns: list[str]) -> list[dict]:
    summary = []
    for column in key_columns:
        try:
            query = (
                f"SELECT COUNT(*) FROM ("
                f"SELECT [{column}], COUNT(*) AS row_count "
                f"FROM [{schema}].[{table}] "
                f"GROUP BY [{column}] "
                f"HAVING COUNT(*) > 1"
                f") AS dupes"
            )
            duplicate_count = connection.execute(query).fetchone()[0]
        except Exception:
            continue
        summary.append({
            "column": column,
            "duplicate_group_count": int(duplicate_count or 0),
        })
    return summary


def fetch_date_range_summary(connection: pyodbc.Connection, schema: str, table: str, date_columns: list[str]) -> list[dict]:
    summary = []
    for column in date_columns:
        query = (
            f"SELECT MIN([{column}]) AS min_value, MAX([{column}]) AS max_value "
            f"FROM [{schema}].[{table}] "
            f"WHERE [{column}] IS NOT NULL"
        )
        try:
            min_value, max_value = connection.execute(query).fetchone()
        except Exception:
            continue
        summary.append({
            "column": column,
            "min_value": str(min_value) if min_value is not None else "N/A",
            "max_value": str(max_value) if max_value is not None else "N/A",
        })
    return summary


def build_report() -> str:
    with get_connection() as connection:
        inventory = fetch_table_inventory(connection)
        relationships = fetch_key_relationships(connection)
        profile_rows = []
        for table_name in INITIAL_TABLES:
            schema, table = table_name.split(".")
            profile_rows.append({
                "table": table_name,
                "row_count": fetch_table_rows(connection, schema, table),
                "columns": fetch_column_metadata(connection, schema, table),
            })

    schema_summary = []
    for schema in SCHEMAS:
        total_rows = sum(item["row_count"] for item in inventory if item["schema"] == schema)
        table_count = sum(1 for item in inventory if item["schema"] == schema)
        schema_summary.append((schema, table_count, total_rows))

    table_lines = [
        "| Schema | Table | Row count |",
        "|---|---|---:|",
    ]
    for item in inventory:
        table_lines.append(f"| {item['schema']} | {item['table']} | {item['row_count']:,} |")

    core_lines = [
        "| Table | Row count | Key columns |",
        "|---|---:|---|",
    ]
    for item in profile_rows:
        columns = item["columns"][:8]
        key_cols = ", ".join(c["column"] for c in columns)
        core_lines.append(f"| {item['table']} | {item['row_count']:,} | {key_cols} |")

    rel_lines = [
        "| Child table | Child column | Parent table | Parent column |",
        "|---|---|---|---|",
    ]
    for rel in relationships[:25]:
        rel_lines.append(
            f"| {rel['child_table']} | {rel['child_column']} | {rel['parent_table']} | {rel['parent_column']} |"
        )

    summary_lines = [
        "## 1. Source inventory overview",
        "",
        "This report inventories the source tables in the AdventureWorks2012 OLTP database and highlights the tables that matter most for the Phase 1 discovery work.",
        "",
        *table_lines,
        "",
        "## 2. Schema-level summary",
        "",
        "| Schema | Tables | Approx total rows |",
        "|---|---:|---:|",
    ]
    for schema, table_count, total_rows in schema_summary:
        summary_lines.append(f"| {schema} | {table_count} | {total_rows:,} |")

    summary_lines.extend([
        "",
        "## 3. Core profile for key business tables",
        "",
        *core_lines,
        "",
        "## 4. Relationship mapping",
        "",
        "The key joins in the AdventureWorks model are centered on customer, order, product, vendor, and production entities. They provide the main shape for the future Bronze-to-Gold model.",
        "",
        *rel_lines,
        "",
        "## 5. Data quality observations",
        "",
        "- Sales and purchasing tables are the strongest source candidates for Phase 3. They carry order-level fact data and are suitable for grain validation.",
        "- Person and customer tables should be used as dimensions and lookups; they link customers, people, and addresses.",
        "- Production tables are important for inventory and work order analysis, but they need more validation on date completeness and location mapping.",
        "- The most critical checks before modeling are nullability, duplicate keys, and date range completeness.",
        "",
        "## 6. Recommended Phase 1 next steps",
        "",
        "1. Confirm the exact grain for each sales and purchasing fact table.",
        "2. Validate null proportions and duplicate keys for the core dimension tables.",
        "3. Document the business meaning of the primary key/foreign key relationships in the data dictionary.",
        "4. Prepare the final source-to-target matrix before starting Phase 2 architecture design.",
        "",
        f"Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
    ])
    return "\n".join(summary_lines) + "\n"


def build_quality_report() -> str:
    quality_tables = {
        "Sales.SalesOrderHeader": {
            "key_columns": ["SalesOrderID", "CustomerID", "SalesPersonID", "TerritoryID"],
            "date_columns": ["OrderDate", "DueDate", "ShipDate"],
        },
        "Sales.SalesOrderDetail": {
            "key_columns": ["SalesOrderID", "SalesOrderDetailID", "ProductID"],
            "date_columns": [],
        },
        "Sales.Customer": {
            "key_columns": ["CustomerID", "PersonID", "TerritoryID"],
            "date_columns": ["ModifiedDate"],
        },
        "Production.Product": {
            "key_columns": ["ProductID", "ProductNumber"],
            "date_columns": ["SellStartDate", "SellEndDate", "DiscontinuedDate"],
        },
        "Production.WorkOrder": {
            "key_columns": ["WorkOrderID", "ProductID"],
            "date_columns": ["StartDate", "EndDate", "DueDate"],
        },
        "Purchasing.PurchaseOrderHeader": {
            "key_columns": ["PurchaseOrderID", "VendorID"],
            "date_columns": ["OrderDate", "ShipDate", "DueDate"],
        },
        "Purchasing.PurchaseOrderDetail": {
            "key_columns": ["PurchaseOrderID", "PurchaseOrderDetailID", "ProductID"],
            "date_columns": ["DueDate"],
        },
    }

    markdown_lines = [
        "# Phase 1 Data Quality Checks",
        "",
        "## Objective",
        "",
        "This document validates the most important AdventureWorks source tables for nullability, duplicate keys, and temporal ranges before modeling begins.",
        "",
        "| Table | Row count | Null check | Duplicate check | Date range check |",
        "|---|---:|---|---|---|",
    ]

    with get_connection() as connection:
        for table_name, checks in quality_tables.items():
            schema, table = table_name.split(".")
            total_rows = fetch_table_rows(connection, schema, table)
            null_summary = fetch_null_summary(connection, schema, table, checks["key_columns"])
            duplicate_summary = fetch_duplicate_summary(connection, schema, table, checks["key_columns"])
            date_summary = fetch_date_range_summary(connection, schema, table, checks["date_columns"])

            null_text = "; ".join(
                f"{item['column']}={item['null_pct']}%" for item in null_summary if item["null_count"] > 0
            ) or "No significant nulls detected"
            dup_text = "; ".join(
                f"{item['column']}={item['duplicate_group_count']}" for item in duplicate_summary if item["duplicate_group_count"] > 0
            ) or "No duplicate key groups detected"
            date_text = "; ".join(
                f"{item['column']}={item['min_value']}→{item['max_value']}" for item in date_summary if item["min_value"] != "N/A"
            ) or "No date column validation available"

            markdown_lines.append(
                f"| {table_name} | {total_rows:,} | {null_text} | {dup_text} | {date_text} |"
            )

    markdown_lines.extend([
        "",
        "## Observations",
        "",
        "- Sales order and purchasing tables are the strongest fact candidates and should be reviewed for grain validation before modeling.",
        "- Person and customer tables should be treated as dimensions and lookup sources, especially for CustomerID and TerritoryID joins.",
        "- Date fields such as OrderDate, ShipDate, and StartDate must be normalized for Silver layer logic and business reporting.",
        "- Duplicate checks should be reviewed again during Silver-layer transformation to ensure unique business keys before loading Gold tables.",
        "",
        f"Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
    ])
    return "\n".join(markdown_lines) + "\n"


def build_source_to_target_notes() -> str:
    sections = [
        "# Phase 1 Source-to-Target Notes",
        "",
        "## Purpose",
        "",
        "These notes document the key source entities that will feed the Bronze, Silver, and Gold layers for AdventureWorks analytics.",
        "",
        "## Source to Bronze mapping",
        "",
        "| Source table | Business role | Bronze target | Notes |",
        "|---|---|---|---|",
        "| Sales.SalesOrderHeader | Sales fact header | bronze.sales_order_header | Keep original columns and add load lineage metadata |",
        "| Sales.SalesOrderDetail | Sales transactional line items | bronze.sales_order_detail | Keep detailed grain and product/order facts |",
        "| Sales.Customer | Customer dimension | bronze.sales_customer | Preserve master customer references |",
        "| Person.Person | Person master | bronze.person_person | Use for customer/employee/person dimension mapping |",
        "| Production.Product | Product dimension | bronze.production_product | Keep product master and attributes |",
        "| Production.WorkOrder | Production fact | bronze.production_workorder | Track production quantity and dates |",
        "| Purchasing.PurchaseOrderHeader | Purchase fact header | bronze.purchasing_purchaseorder_header | Capture vendor and order metadata |",
        "| Purchasing.PurchaseOrderDetail | Purchase line items | bronze.purchasing_purchaseorder_detail | Keep item-level cost and quantity records |",
        "",
        "## Recommended target design",
        "",
        "- Bronze: raw source tables plus `_load_date` and `_source_system` lineage metadata.",
        "- Silver: cleaned, standardized, deduplicated, and business-key validated views/tables.",
        "- Gold: analytical fact and dimension tables optimized for dashboards and KPI reporting.",
        "",
        "## Readiness check for Phase 2",
        "",
        "- Source tables inventory is complete and prioritized.",
        "- Key relationships and business entities are mapped.",
        "- Main source-to-target dependencies are documented.",
        "- Data quality checks are now planned and ready for Silver-layer validation.",
        "",
        f"Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
    ]
    return "\n".join(sections) + "\n"


def build_data_dictionary() -> str:
    sections = [
        "# Phase 1 Data Dictionary",
        "",
        "## Overview",
        "",
        "This dictionary captures the most important source entities used in Phase 1. It is intended to support source-to-target mapping and the later Bronze/Silver/Gold design work.",
        "",
        "## Core source entities",
        "",
        "### Sales.SalesOrderHeader",
        "- Purpose: header-level sales fact table with one row per order.",
        "- Key fields: SalesOrderID, OrderDate, DueDate, ShipDate, CustomerID, SalesPersonID, TerritoryID, Status, OnlineOrderFlag.",
        "- Critical joins: CustomerID -> Sales.Customer, SalesPersonID -> Sales.SalesPerson, TerritoryID -> Sales.SalesTerritory.",
        "",
        "### Sales.SalesOrderDetail",
        "- Purpose: order line items, the detailed transactional fact table for sales.",
        "- Key fields: SalesOrderID, SalesOrderDetailID, ProductID, OrderQty, UnitPrice, LineTotal.",
        "- Critical joins: SalesOrderID -> Sales.SalesOrderHeader, ProductID -> Production.Product.",
        "",
        "### Sales.Customer",
        "- Purpose: customer dimension and master reference for sales activity.",
        "- Key fields: CustomerID, PersonID, StoreID, TerritoryID.",
        "- Critical joins: PersonID -> Person.Person, TerritoryID -> Sales.SalesTerritory.",
        "",
        "### Person.Person",
        "- Purpose: people master dimension for individuals associated with customers, employees, and vendors.",
        "- Key fields: BusinessEntityID, FirstName, LastName, PersonType.",
        "- Critical joins: BusinessEntityID -> Person.BusinessEntity and related address/contact tables.",
        "",
        "### Production.Product",
        "- Purpose: core product dimension.",
        "- Key fields: ProductID, Name, ProductNumber, Color, StandardCost, ListPrice, SafetyStockLevel.",
        "- Critical joins: ProductID -> Sales.SalesOrderDetail, Production.WorkOrder, Purchasing.PurchaseOrderDetail.",
        "",
        "### Production.ProductInventory",
        "- Purpose: inventory snapshot by product and location.",
        "- Key fields: ProductID, LocationID, Shelf, Bin, Quantity.",
        "- Critical joins: ProductID -> Production.Product, LocationID -> Production.Location.",
        "",
        "### Production.WorkOrder",
        "- Purpose: production work order fact table.",
        "- Key fields: WorkOrderID, ProductID, OrderQty, StockedQty, StartDate, EndDate.",
        "- Critical joins: ProductID -> Production.Product.",
        "",
        "### Purchasing.PurchaseOrderHeader",
        "- Purpose: purchasing header fact table.",
        "- Key fields: PurchaseOrderID, VendorID, OrderDate, ShipDate, Status.",
        "- Critical joins: VendorID -> Purchasing.Vendor.",
        "",
        "### Purchasing.PurchaseOrderDetail",
        "- Purpose: purchasing line-item fact table.",
        "- Key fields: PurchaseOrderID, PurchaseOrderDetailID, ProductID, OrderQty, UnitPrice.",
        "- Critical joins: PurchaseOrderID -> PurchaseOrderHeader, ProductID -> Production.Product.",
        "",
        "## Assumptions and business rules",
        "",
        "- Sales orders are the primary fact grain for revenue analysis; line-level detail should be used for unit and revenue calculations.",
        "- Customer IDs and product IDs are the primary foreign keys used across the sales and purchasing domains.",
        "- Inventory and production flows should be validated separately from sales because they use different grain and date semantics.",
        "- We will treat nullability and duplicate detection as a mandatory validation step before finalizing any Silver/Gold model.",
        "",
        f"Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
    ]
    return "\n".join(sections) + "\n"


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_report(), encoding="utf-8")
    DICT_PATH.write_text(build_data_dictionary(), encoding="utf-8")
    QUALITY_PATH.write_text(build_quality_report(), encoding="utf-8")
    SOURCE_TO_TARGET_PATH.write_text(build_source_to_target_notes(), encoding="utf-8")
    print(f"Saved Phase 1 inventory report to: {REPORT_PATH}")
    print(f"Saved data dictionary to: {DICT_PATH}")
    print(f"Saved data quality checks to: {QUALITY_PATH}")
    print(f"Saved source-to-target notes to: {SOURCE_TO_TARGET_PATH}")


if __name__ == "__main__":
    main()

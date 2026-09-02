"""Silver transformations for the AdventureWorks sales domain."""

from __future__ import annotations

from typing import Dict

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from src.shared.connectors.postgres_connector import PostgreSQLConnector


SILVER_TABLES = {
    "sales_order_header": "sales_order_header_clean",
    "sales_order_detail": "sales_order_detail_clean",
    "customer": "customer_clean",
    "sales_territory": "sales_territory_clean",
    "sales_person": "sales_person_clean",
    "product": "product_clean",
}


def _warehouse_engine(connection):
    return create_engine("postgresql://", creator=lambda: connection, poolclass=StaticPool)


def _read_bronze(source_table: str, engine) -> pd.DataFrame:
    return pd.read_sql_query(f'SELECT * FROM bronze."{source_table}"', engine)


def _rename_columns(frame: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    return frame.rename(columns={source: target for source, target in mapping.items() if source in frame.columns})


def _deduplicate(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    return frame.drop_duplicates(subset=[key], keep="last").reset_index(drop=True)


def _select_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    return frame.loc[:, columns]


def clean_sales_order_header(frame: pd.DataFrame) -> pd.DataFrame:
    result = _rename_columns(
        frame,
        {
            "SalesOrderID": "sales_order_id",
            "OrderDate": "order_date",
            "DueDate": "due_date",
            "ShipDate": "ship_date",
            "CustomerID": "customer_id",
            "SalesPersonID": "salesperson_id",
            "TerritoryID": "territory_id",
            "SubTotal": "subtotal",
            "TaxAmt": "tax_amt",
            "Freight": "freight",
            "TotalDue": "total_due",
            "OnlineOrderFlag": "is_online_order",
            "Status": "status_code",
            "_source_system": "_source_system",
            "_load_date": "_load_date",
        },
    )
    for column in ["order_date", "due_date", "ship_date"]:
        result[column] = pd.to_datetime(result[column], errors="coerce").dt.date
    for column in ["subtotal", "tax_amt", "freight", "total_due"]:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    result = _deduplicate(result, "sales_order_id")
    return _select_columns(result, [
        "sales_order_id", "order_date", "due_date", "ship_date", "customer_id",
        "salesperson_id", "territory_id", "subtotal", "tax_amt", "freight",
        "total_due", "is_online_order", "status_code", "_source_system", "_load_date",
    ])


def clean_sales_order_detail(frame: pd.DataFrame) -> pd.DataFrame:
    result = _rename_columns(
        frame,
        {
            "SalesOrderID": "sales_order_id",
            "SalesOrderDetailID": "sales_order_detail_id",
            "ProductID": "product_id",
            "OrderQty": "order_qty",
            "UnitPrice": "unit_price",
            "UnitPriceDiscount": "unit_price_discount",
            "LineTotal": "line_total",
            "_source_system": "_source_system",
            "_load_date": "_load_date",
        },
    )
    result["order_qty"] = pd.to_numeric(result["order_qty"], errors="coerce").astype("Int64")
    for column in ["unit_price", "unit_price_discount", "line_total"]:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    result = _deduplicate(result, "sales_order_detail_id")
    return _select_columns(result, [
        "sales_order_id", "sales_order_detail_id", "product_id", "order_qty",
        "unit_price", "unit_price_discount", "line_total", "_source_system", "_load_date",
    ])


def clean_customer(frame: pd.DataFrame) -> pd.DataFrame:
    result = _rename_columns(
        frame,
        {
            "CustomerID": "customer_id",
            "PersonID": "person_id",
            "StoreID": "store_id",
            "TerritoryID": "territory_id",
            "AccountNumber": "account_number",
            "_source_system": "_source_system",
            "_load_date": "_load_date",
        },
    )
    result["customer_name"] = result["account_number"].astype("string").str.strip()
    result = _deduplicate(result, "customer_id")
    return _select_columns(result, [
        "customer_id", "person_id", "store_id", "territory_id", "account_number",
        "customer_name", "_source_system", "_load_date",
    ])


def clean_sales_territory(frame: pd.DataFrame) -> pd.DataFrame:
    result = _rename_columns(
        frame,
        {
            "TerritoryID": "territory_id",
            "Name": "territory_name",
            "CountryRegionCode": "country_region_code",
            "Group": "territory_group",
            "_source_system": "_source_system",
            "_load_date": "_load_date",
        },
    )
    result["territory_name"] = result["territory_name"].astype("string").str.strip()
    result = _deduplicate(result, "territory_id")
    return _select_columns(result, [
        "territory_id", "territory_name", "country_region_code", "territory_group",
        "_source_system", "_load_date",
    ])


def clean_sales_person(frame: pd.DataFrame, person_frame: pd.DataFrame = None) -> pd.DataFrame:
    result = _rename_columns(
        frame,
        {
            "BusinessEntityID": "business_entity_id",
            "TerritoryID": "territory_id",
            "SalesQuota": "sales_quota",
            "Bonus": "bonus",
            "CommissionPct": "commission_pct",
            "_source_system": "_source_system",
            "_load_date": "_load_date",
        },
    )
    result["salesperson_id"] = result["business_entity_id"]
    
    # If person_frame provided, join to get real names
    if person_frame is not None:
        person_clean = _rename_columns(
            person_frame,
            {
                "BusinessEntityID": "business_entity_id",
                "FirstName": "first_name",
                "LastName": "last_name",
            },
        )
        person_clean = person_clean[["business_entity_id", "first_name", "last_name"]]
        result = result.merge(person_clean, on="business_entity_id", how="left")
        result["salesperson_name"] = (
            result["first_name"].fillna("") + " " + result["last_name"].fillna("")
        ).str.strip()
        result = result.drop(columns=["first_name", "last_name"], errors="ignore")
    else:
        # Fallback: use ID if person data not available
        result["salesperson_name"] = result["business_entity_id"].astype("string")
    
    result = _deduplicate(result, "salesperson_id")
    return _select_columns(result, [
        "salesperson_id", "business_entity_id", "territory_id", "sales_quota", "bonus",
        "commission_pct", "salesperson_name", "_source_system", "_load_date",
    ])


def clean_product(frame: pd.DataFrame) -> pd.DataFrame:
    result = _rename_columns(
        frame,
        {
            "ProductID": "product_id",
            "Name": "product_name",
            "ProductNumber": "product_number",
            "ProductLine": "product_line",
            "Class": "class",
            "Style": "style",
            "ListPrice": "list_price",
            "StandardCost": "standard_cost",
            "DiscontinuedDate": "discontinued_date",
            "_source_system": "_source_system",
            "_load_date": "_load_date",
        },
    )
    for column in ["list_price", "standard_cost"]:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    result["product_name"] = result["product_name"].astype("string").str.strip()
    result["is_discontinued"] = result["discontinued_date"].notna()
    result = _deduplicate(result, "product_id")
    return _select_columns(result, [
        "product_id", "product_name", "product_number", "product_line", "class", "style",
        "list_price", "standard_cost", "is_discontinued", "_source_system", "_load_date",
    ])


CLEANERS = {
    "sales_order_header": clean_sales_order_header,
    "sales_order_detail": clean_sales_order_detail,
    "customer": clean_customer,
    "sales_territory": clean_sales_territory,
    "sales_person": clean_sales_person,
    "product": clean_product,
}


def run() -> Dict[str, Dict[str, int]]:
    """Transform all Bronze sales tables and replace their Silver outputs."""
    results = {}
    with PostgreSQLConnector() as pg_conn:
        engine = _warehouse_engine(pg_conn.connection)
        
        # Read Person data once if available
        person_frame = None
        try:
            person_frame = _read_bronze("person", engine)
        except Exception:
            print("⚠️ Warning: Person table not found in Bronze. Using fallback names.")
        
        for source_table, target_table in SILVER_TABLES.items():
            bronze_frame = _read_bronze(source_table, engine)
            
            # Pass person_frame to clean_sales_person if this is sales_person table
            if source_table == "sales_person" and person_frame is not None:
                silver_frame = CLEANERS[source_table](bronze_frame, person_frame)
            else:
                silver_frame = CLEANERS[source_table](bronze_frame)
            
            silver_frame.to_sql(target_table, engine, schema="silver", if_exists="replace", index=False, method="multi", chunksize=1000)
            results[target_table] = {
                "source_count": len(bronze_frame),
                "target_count": len(silver_frame),
            }
    return results


if __name__ == "__main__":
    print(run())

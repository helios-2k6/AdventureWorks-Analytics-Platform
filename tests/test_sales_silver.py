import pandas as pd

from scripts.transformation.silver.sales_silver_clean import (
    clean_product,
    clean_sales_order_detail,
    clean_sales_order_header,
)


def test_clean_sales_order_header_renames_casts_and_deduplicates():
    frame = pd.DataFrame(
        {
            "SalesOrderID": [1, 1],
            "OrderDate": ["2024-01-02", "2024-01-03"],
            "DueDate": ["2024-01-05", "2024-01-06"],
            "ShipDate": ["2024-01-04", "2024-01-05"],
            "CustomerID": [10, 10],
            "SalesPersonID": [20, 20],
            "TerritoryID": [1, 1],
            "SubTotal": ["10.00", "12.00"],
            "TaxAmt": ["1.00", "1.20"],
            "Freight": ["2.00", "2.00"],
            "TotalDue": ["13.00", "15.20"],
            "OnlineOrderFlag": [True, True],
            "Status": [5, 5],
            "_source_system": ["AdventureWorks2012", "AdventureWorks2012"],
            "_load_date": ["2026-08-31", "2026-08-31"],
        }
    )

    result = clean_sales_order_header(frame)

    assert len(result) == 1
    assert result.iloc[0]["sales_order_id"] == 1
    assert str(result.iloc[0]["order_date"]) == "2024-01-03"
    assert result.iloc[0]["total_due"] == 15.20


def test_clean_sales_order_detail_converts_numeric_fields():
    frame = pd.DataFrame(
        {
            "SalesOrderID": [1],
            "SalesOrderDetailID": [11],
            "ProductID": [100],
            "OrderQty": ["2"],
            "UnitPrice": ["5.50"],
            "UnitPriceDiscount": ["0.10"],
            "LineTotal": ["11.00"],
            "_source_system": ["AdventureWorks2012"],
            "_load_date": ["2026-08-31"],
        }
    )

    result = clean_sales_order_detail(frame)

    assert result.iloc[0]["order_qty"] == 2
    assert result.iloc[0]["unit_price"] == 5.50
    assert result.iloc[0]["line_total"] == 11.00


def test_clean_product_sets_discontinued_flag_and_trims_name():
    frame = pd.DataFrame(
        {
            "ProductID": [100],
            "Name": ["  Road Bike  "],
            "ProductNumber": ["BK-1"],
            "ProductLine": ["R"],
            "Class": ["H"],
            "Style": ["U"],
            "ListPrice": ["100.00"],
            "StandardCost": ["50.00"],
            "DiscontinuedDate": ["2025-01-01"],
            "_source_system": ["AdventureWorks2012"],
            "_load_date": ["2026-08-31"],
        }
    )

    result = clean_product(frame)

    assert result.iloc[0]["product_name"] == "Road Bike"
    assert bool(result.iloc[0]["is_discontinued"]) is True
    assert "discontinued_date" not in result.columns

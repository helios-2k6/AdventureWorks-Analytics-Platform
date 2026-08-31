import pandas as pd

from scripts.warehouse.postgres.gold.sales_gold_load import build_dim_date, build_fact_sales


def test_build_dim_date_creates_date_keys_and_calendar_attributes():
    headers = pd.DataFrame({"order_date": ["2011-05-31", "2011-06-01"]})

    result = build_dim_date(headers)

    assert result["date_id"].tolist() == [20110531, 20110601]
    assert result["month_name"].tolist() == ["May", "June"]
    assert result["is_weekend"].tolist() == [False, False]


def test_build_fact_sales_preserves_line_item_grain_and_calculates_discount():
    details = pd.DataFrame(
        {
            "sales_order_id": [1, 1],
            "sales_order_detail_id": [10, 11],
            "product_id": [100, 101],
            "order_qty": [2, 1],
            "unit_price": [5.0, 10.0],
            "unit_price_discount": [0.1, 0.0],
            "line_total": [9.0, 10.0],
        }
    )
    headers = pd.DataFrame(
        {
            "sales_order_id": [1],
            "order_date": ["2011-05-31"],
            "customer_id": [20],
            "territory_id": [1],
            "salesperson_id": [None],
        }
    )

    result = build_fact_sales(details, headers)

    assert len(result) == 2
    assert result["sales_order_detail_id"].is_unique
    assert result.iloc[0]["order_date_id"] == 20110531
    assert result.iloc[0]["discount_amount"] == 1.0
    assert result.iloc[0]["net_sales"] == 9.0
    assert str(result["salesperson_id"].dtype) == "Int64"

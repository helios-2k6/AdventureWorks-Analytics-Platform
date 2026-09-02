"""Quality validation for the AdventureWorks sales Silver layer."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.shared.connectors.postgres_connector import PostgreSQLConnector


TABLE_CHECKS = {
    "sales_order_header_clean": {
        "bronze": "sales_order_header",
        "key": "sales_order_id",
        "not_null": ["sales_order_id", "order_date", "customer_id"],
    },
    "sales_order_detail_clean": {
        "bronze": "sales_order_detail",
        "key": "sales_order_detail_id",
        "not_null": ["sales_order_detail_id", "sales_order_id", "product_id", "order_qty", "unit_price"],
    },
    "customer_clean": {
        "bronze": "customer",
        "key": "customer_id",
        "not_null": ["customer_id", "customer_name"],
    },
    "sales_territory_clean": {
        "bronze": "sales_territory",
        "key": "territory_id",
        "not_null": ["territory_id", "territory_name"],
    },
    "sales_person_clean": {
        "bronze": "sales_person",
        "key": "salesperson_id",
        "not_null": ["salesperson_id", "salesperson_name"],
    },
    "product_clean": {
        "bronze": "product",
        "key": "product_id",
        "not_null": ["product_id", "product_name", "list_price"],
    },
}


JOIN_CHECKS = {
    "detail_to_header": (
        "SELECT COUNT(*) FROM silver.sales_order_detail_clean detail "
        "LEFT JOIN silver.sales_order_header_clean header "
        "ON detail.sales_order_id = header.sales_order_id "
        "WHERE header.sales_order_id IS NULL"
    ),
    "detail_to_product": (
        "SELECT COUNT(*) FROM silver.sales_order_detail_clean detail "
        "LEFT JOIN silver.product_clean product ON detail.product_id = product.product_id "
        "WHERE product.product_id IS NULL"
    ),
    "header_to_customer": (
        "SELECT COUNT(*) FROM silver.sales_order_header_clean header "
        "LEFT JOIN silver.customer_clean customer ON header.customer_id = customer.customer_id "
        "WHERE customer.customer_id IS NULL"
    ),
    "header_to_territory": (
        "SELECT COUNT(*) FROM silver.sales_order_header_clean header "
        "LEFT JOIN silver.sales_territory_clean territory ON header.territory_id = territory.territory_id "
        "WHERE header.territory_id IS NOT NULL AND territory.territory_id IS NULL"
    ),
    "header_to_salesperson": (
        "SELECT COUNT(*) FROM silver.sales_order_header_clean header "
        "LEFT JOIN silver.sales_person_clean person ON header.salesperson_id = person.salesperson_id "
        "WHERE header.salesperson_id IS NOT NULL AND person.salesperson_id IS NULL"
    ),
}


def _count(pg: PostgreSQLConnector, query: str) -> int:
    return int(pg.fetch_results(query)[0][0])


def validate(pg: PostgreSQLConnector) -> dict[str, Any]:
    tables = {}
    for table, config in TABLE_CHECKS.items():
        bronze_count = _count(pg, f'SELECT COUNT(*) FROM bronze."{config["bronze"]}"')
        silver_count = _count(pg, f'SELECT COUNT(*) FROM silver."{table}"')
        duplicate_count = _count(
            pg,
            f'SELECT COUNT(*) FROM (SELECT "{config["key"]}" FROM silver."{table}" '
            f'GROUP BY "{config["key"]}" HAVING COUNT(*) > 1) duplicates',
        )
        null_counts = {
            column: _count(pg, f'SELECT COUNT(*) FROM silver."{table}" WHERE "{column}" IS NULL')
            for column in config["not_null"]
        }
        tables[table] = {
            "bronze_count": bronze_count,
            "silver_count": silver_count,
            "count_match": bronze_count == silver_count,
            "duplicate_key_groups": duplicate_count,
            "null_counts": null_counts,
        }

    joins = {name: _count(pg, query) for name, query in JOIN_CHECKS.items()}
    passed = all(
        result["count_match"]
        and result["duplicate_key_groups"] == 0
        and all(value == 0 for value in result["null_counts"].values())
        for result in tables.values()
    ) and all(value == 0 for value in joins.values())
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "tables": tables, "joins": joins, "passed": passed}


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 3 Silver Validation Report",
        "",
        f"Generated at: {report['generated_at']}",
        "",
        "## Table quality checks",
        "",
        "| Silver table | Bronze rows | Silver rows | Count match | Duplicate key groups | NULL checks |",
        "|---|---:|---:|---|---:|---|",
    ]
    for table, result in report["tables"].items():
        null_text = "; ".join(f"{column}={count}" for column, count in result["null_counts"].items())
        lines.append(
            f"| {table} | {result['bronze_count']:,} | {result['silver_count']:,} | "
            f"{'PASS' if result['count_match'] else 'FAIL'} | {result['duplicate_key_groups']} | {null_text} |"
        )
    lines.extend(["", "## Join integrity", "", "| Join check | Orphan rows | Status |", "|---|---:|---|"])
    for name, count in report["joins"].items():
        lines.append(f"| {name} | {count:,} | {'PASS' if count == 0 else 'FAIL'} |")
    lines.extend(["", f"## Result", "", f"**{'PASS' if report['passed'] else 'FAIL'}**"])
    return "\n".join(lines) + "\n"


def main() -> dict[str, Any]:
    with PostgreSQLConnector() as pg:
        report = validate(pg)
    output = Path(__file__).resolve().parents[3] / "docs" / "ToDoCheckList" / "Phase_3_Sales_Performance" / "phase3_silver_validation.md"
    output.write_text(render_report(report), encoding="utf-8")
    print(render_report(report))
    return report


if __name__ == "__main__":
    main()

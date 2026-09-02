"""Validate sales KPIs in Gold against an independent Silver baseline."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.shared.connectors.postgres_connector import PostgreSQLConnector


KPI_QUERY = """
SELECT
    COALESCE(SUM(net_sales), 0),
    COUNT(DISTINCT sales_order_id),
    COUNT(*),
    COALESCE(SUM(order_qty), 0),
    COALESCE(SUM(discount_amount), 0),
    COALESCE(SUM(unit_price * order_qty), 0),
    COUNT(DISTINCT customer_id)
FROM gold.fact_sales
"""

BASELINE_QUERY = """
SELECT
    COALESCE(SUM(detail.line_total), 0),
    COUNT(DISTINCT detail.sales_order_id),
    COUNT(*),
    COALESCE(SUM(detail.order_qty), 0),
    COALESCE(SUM(detail.order_qty * detail.unit_price - detail.line_total), 0),
    COALESCE(SUM(detail.unit_price * detail.order_qty), 0),
    COUNT(DISTINCT header.customer_id)
FROM silver.sales_order_detail_clean detail
JOIN silver.sales_order_header_clean header
  ON detail.sales_order_id = header.sales_order_id
"""


def _as_float(value: Any) -> float:
    return float(value or 0)


def _metrics(row: tuple) -> dict[str, float]:
    total_revenue, total_orders, total_line_items, total_units, discount_amount, gross_sales, customer_count = row
    return {
        "total_revenue": _as_float(total_revenue),
        "total_orders": _as_float(total_orders),
        "total_line_items": _as_float(total_line_items),
        "total_units": _as_float(total_units),
        "average_order_value": _as_float(total_revenue) / _as_float(total_orders) if total_orders else 0.0,
        "average_item_price": _as_float(gross_sales) / _as_float(total_units) if total_units else 0.0,
        "discount_amount": _as_float(discount_amount),
        "discount_rate": _as_float(discount_amount) / _as_float(gross_sales) if gross_sales else 0.0,
        "customer_count": _as_float(customer_count),
    }


def _variance(actual: float, expected: float) -> float:
    if expected == 0:
        return 0.0 if actual == 0 else 1.0
    return abs(actual - expected) / abs(expected)


def validate(pg: PostgreSQLConnector) -> dict[str, Any]:
    gold = _metrics(pg.fetch_results(KPI_QUERY)[0])
    baseline = _metrics(pg.fetch_results(BASELINE_QUERY)[0])
    comparisons = {
        name: {
            "gold": round(gold[name], 6),
            "baseline": round(baseline[name], 6),
            "variance_pct": round(_variance(gold[name], baseline[name]) * 100, 6),
            "within_tolerance": _variance(gold[name], baseline[name]) <= 0.02,
        }
        for name in gold
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "comparisons": comparisons,
        "passed": all(item["within_tolerance"] for item in comparisons.values()),
    }


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 3 Sales KPI Validation Report",
        "",
        f"Generated at: {report['generated_at']}",
        "",
        "Gold KPIs are compared with an independent baseline calculated from Silver detail joined to Silver header.",
        "",
        "| KPI | Gold | Silver baseline | Variance | Within 2% |",
        "|---|---:|---:|---:|---|",
    ]
    for name, item in report["comparisons"].items():
        lines.append(
            f"| {name} | {item['gold']:,.6f} | {item['baseline']:,.6f} | "
            f"{item['variance_pct']:.6f}% | {'PASS' if item['within_tolerance'] else 'FAIL'} |"
        )
    lines.extend(["", "## Result", "", f"**{'PASS' if report['passed'] else 'FAIL'}**", ""])
    return "\n".join(lines)


def main() -> dict[str, Any]:
    with PostgreSQLConnector() as pg:
        report = validate(pg)
    output = Path(__file__).resolve().parents[4] / "docs" / "ToDoCheckList" / "Phase_3_Sales_Performance" / "phase3_kpi_validation.md"
    output.write_text(render_report(report), encoding="utf-8")
    print(render_report(report))
    return report


if __name__ == "__main__":
    main()

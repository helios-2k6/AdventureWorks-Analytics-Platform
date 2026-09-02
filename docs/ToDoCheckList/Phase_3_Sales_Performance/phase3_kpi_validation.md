# Phase 3 Sales KPI Validation Report

Generated at: 2026-09-02T07:14:03.135051+00:00

Gold KPIs are compared with an independent baseline calculated from Silver detail joined to Silver header.

| KPI | Gold | Silver baseline | Variance | Within 2% |
|---|---:|---:|---:|---|
| total_revenue | 109,846,381.399703 | 109,846,381.399703 | 0.000000% | PASS |
| total_orders | 31,465.000000 | 31,465.000000 | 0.000000% | PASS |
| total_line_items | 121,317.000000 | 121,317.000000 | 0.000000% | PASS |
| total_units | 274,914.000000 | 274,914.000000 | 0.000000% | PASS |
| average_order_value | 3,491.065673 | 3,491.065673 | 0.000000% | PASS |
| average_item_price | 401.485153 | 401.485153 | 0.000000% | PASS |
| discount_amount | 527,507.913512 | 527,507.913512 | 0.000000% | PASS |
| discount_rate | 0.004779 | 0.004779 | 0.000000% | PASS |
| customer_count | 19,119.000000 | 19,119.000000 | 0.000000% | PASS |

## Result

**PASS**

## Validation Summary

The following checks were verified after the Gold layer build and before using the dashboard data:

- Fact sales grain: confirmed at line-item grain with unique `sales_order_detail_id`; row count matches the expected 121,317 rows.
- Dimension key integrity: dimension tables were checked for unique keys and referential integrity against the fact table; no orphan keys were found.
- KPI logic: Gold metrics were compared against an independent Silver baseline using the same business definitions; variance was 0.000000% for all KPIs.
- Warehouse accuracy: the Gold layer remains consistent with the Silver source data for revenue, order counts, item counts, unit counts, and customer counts.
- Unit tests: the project-level Gold tests now pass, validating the logic behind dashboard metrics and data transformation rules.

### Evidence

Commands executed successfully:

```powershell
Set-Location 'A:\Workspace\DataEngineer\AdventureWorks Analytics Platform'
$env:PYTHONPATH='.'
.\.venv64\Scripts\python.exe scripts/warehouse/postgres/gold/validate_sales_kpis.py
.\.venv64\Scripts\python.exe -m pytest tests/test_sales_gold.py -q
```

Result: KPI validation passed and 18 Gold-layer tests passed in 2.21s.

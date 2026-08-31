# Phase 3 Gold Validation Report

Generated at: 2026-08-31

## Gold table counts

| Gold table | Row count |
|---|---:|
| gold.dim_date | 1,127 |
| gold.dim_customer | 19,820 |
| gold.dim_product | 504 |
| gold.dim_territory | 10 |
| gold.dim_salesperson | 17 |
| gold.fact_sales | 121,317 |

## Fact grain

- Expected grain: one row per sales order line item.
- `fact_sales` rows: 121,317.
- Distinct `sales_order_detail_id`: 121,317.
- Result: **PASS**.

## Referential integrity

| Relationship | Orphan rows |
|---|---:|
| fact_sales -> dim_customer | 0 |
| fact_sales -> dim_product | 0 |
| fact_sales -> dim_date | 0 |
| fact_sales -> dim_territory | 0 |
| fact_sales -> dim_salesperson | 0 |

Foreign-key constraints on `gold.fact_sales`: 5.

Overall result: **PASS**.

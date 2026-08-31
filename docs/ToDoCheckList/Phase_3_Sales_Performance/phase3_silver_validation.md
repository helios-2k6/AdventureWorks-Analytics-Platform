# Phase 3 Silver Validation Report

Generated at: 2026-08-31T15:40:51.559237+00:00

## Table quality checks

| Silver table | Bronze rows | Silver rows | Count match | Duplicate key groups | NULL checks |
|---|---:|---:|---|---:|---|
| sales_order_header_clean | 31,465 | 31,465 | PASS | 0 | sales_order_id=0; order_date=0; customer_id=0 |
| sales_order_detail_clean | 121,317 | 121,317 | PASS | 0 | sales_order_detail_id=0; sales_order_id=0; product_id=0; order_qty=0; unit_price=0 |
| customer_clean | 19,820 | 19,820 | PASS | 0 | customer_id=0; customer_name=0 |
| sales_territory_clean | 10 | 10 | PASS | 0 | territory_id=0; territory_name=0 |
| sales_person_clean | 17 | 17 | PASS | 0 | salesperson_id=0; salesperson_name=0 |
| product_clean | 504 | 504 | PASS | 0 | product_id=0; product_name=0; list_price=0 |

## Join integrity

| Join check | Orphan rows | Status |
|---|---:|---|
| detail_to_header | 0 | PASS |
| detail_to_product | 0 | PASS |
| header_to_customer | 0 | PASS |
| header_to_territory | 0 | PASS |
| header_to_salesperson | 0 | PASS |

## Result

**PASS**

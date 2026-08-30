# Phase 1 Source-to-Target Notes

## Purpose

These notes document the key source entities that will feed the Bronze, Silver, and Gold layers for AdventureWorks analytics.

## Source to Bronze mapping

| Source table | Business role | Bronze target | Notes |
|---|---|---|---|
| Sales.SalesOrderHeader | Sales fact header | bronze.sales_order_header | Keep original columns and add load lineage metadata |
| Sales.SalesOrderDetail | Sales transactional line items | bronze.sales_order_detail | Keep detailed grain and product/order facts |
| Sales.Customer | Customer dimension | bronze.sales_customer | Preserve master customer references |
| Person.Person | Person master | bronze.person_person | Use for customer/employee/person dimension mapping |
| Production.Product | Product dimension | bronze.production_product | Keep product master and attributes |
| Production.WorkOrder | Production fact | bronze.production_workorder | Track production quantity and dates |
| Purchasing.PurchaseOrderHeader | Purchase fact header | bronze.purchasing_purchaseorder_header | Capture vendor and order metadata |
| Purchasing.PurchaseOrderDetail | Purchase line items | bronze.purchasing_purchaseorder_detail | Keep item-level cost and quantity records |

## Recommended target design

- Bronze: raw source tables plus `_load_date` and `_source_system` lineage metadata.
- Silver: cleaned, standardized, deduplicated, and business-key validated views/tables.
- Gold: analytical fact and dimension tables optimized for dashboards and KPI reporting.

## Readiness check for Phase 2

- Source tables inventory is complete and prioritized.
- Key relationships and business entities are mapped.
- Main source-to-target dependencies are documented.
- Data quality checks are now planned and ready for Silver-layer validation.

Generated at: 2026-08-30 14:11:12 UTC

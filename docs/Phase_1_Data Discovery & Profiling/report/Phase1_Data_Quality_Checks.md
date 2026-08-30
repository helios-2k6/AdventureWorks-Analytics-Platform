# Phase 1 Data Quality Checks

## Objective

This document validates the most important AdventureWorks source tables for nullability, duplicate keys, and temporal ranges before modeling begins.

| Table | Row count | Null check | Duplicate check | Date range check |
|---|---:|---|---|---|
| Sales.SalesOrderHeader | 31,465 | SalesPersonID=87.9% | CustomerID=7470; SalesPersonID=18; TerritoryID=10 | OrderDate=2011-05-31 00:00:00→2014-06-30 00:00:00; DueDate=2011-06-12 00:00:00→2014-07-12 00:00:00; ShipDate=2011-06-07 00:00:00→2014-07-07 00:00:00 |
| Sales.SalesOrderDetail | 121,317 | No significant nulls detected | SalesOrderID=21209; ProductID=266 | No date column validation available |
| Sales.Customer | 19,820 | PersonID=3.54% | PersonID=1; TerritoryID=10 | ModifiedDate=2014-09-12 11:15:07.263000→2014-09-12 11:15:07.263000 |
| Production.Product | 504 | No significant nulls detected | No duplicate key groups detected | SellStartDate=2008-04-30 00:00:00→2013-05-30 00:00:00; SellEndDate=2012-05-29 00:00:00→2013-05-29 00:00:00 |
| Production.WorkOrder | 72,591 | No significant nulls detected | ProductID=238 | StartDate=2011-06-03 00:00:00→2014-06-02 00:00:00; EndDate=2011-06-13 00:00:00→2014-06-17 00:00:00; DueDate=2011-06-14 00:00:00→2014-06-13 00:00:00 |
| Purchasing.PurchaseOrderHeader | 4,012 | No significant nulls detected | VendorID=82 | OrderDate=2011-04-16 00:00:00→2014-09-22 00:00:00; ShipDate=2011-04-25 00:00:00→2014-10-17 00:00:00 |
| Purchasing.PurchaseOrderDetail | 8,845 | No significant nulls detected | PurchaseOrderID=2362; ProductID=213 | DueDate=2011-04-30 00:00:00→2014-10-22 00:00:00 |

## Observations

- Sales order and purchasing tables are the strongest fact candidates and should be reviewed for grain validation before modeling.
- Person and customer tables should be treated as dimensions and lookup sources, especially for CustomerID and TerritoryID joins.
- Date fields such as OrderDate, ShipDate, and StartDate must be normalized for Silver layer logic and business reporting.
- Duplicate checks should be reviewed again during Silver-layer transformation to ensure unique business keys before loading Gold tables.

Generated at: 2026-08-30 14:11:12 UTC

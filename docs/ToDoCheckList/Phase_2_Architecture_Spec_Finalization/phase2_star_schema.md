# Phase 2 — Gold Star Schema & Grain Decisions

## 1. Objective

This document records the final gold-layer modeling direction for each domain before implementation starts in Phase 3.

---

## 2. Core modeling rules

- Fact tables store measurable business events
- Dimension tables store descriptive attributes
- Each fact table must have a clearly documented grain
- Each fact table must join to dimensions using surrogate or business keys
- All date-based metrics should use a proper `dim_date` table

---

## 3. Sales domain

### Fact table
- `gold.fact_sales`

### Grain
- one row = one sales order line item

### Dimensions
- `gold.dim_customer`
- `gold.dim_product`
- `gold.dim_date`
- `gold.dim_territory`
- `gold.dim_salesperson`

### Example measures
- `line_total`
- `net_sales`
- `discount_amount`
- `order_qty`

---

## 4. Customer domain

### Fact table
- `gold.fact_customer_orders`

### Grain
- one row = one customer order event

### Dimensions
- `gold.dim_customer`
- `gold.dim_date`
- `gold.dim_product`

### KPIs
- RFM score
- customer lifetime value
- new vs returning customer

---

## 5. Production / Inventory domain

### Fact tables
- `gold.fact_production`
- `gold.fact_inventory`

### Grain
- `fact_production`: one row = one work order or production event
- `fact_inventory`: one row = one product/location/date balance or movement

### Dimensions
- `gold.dim_product`
- `gold.dim_location`
- `gold.dim_date`

---

## 6. Purchasing / Supplier domain

### Fact table
- `gold.fact_purchasing`

### Grain
- one row = one purchase order line item

### Dimensions
- `gold.dim_vendor`
- `gold.dim_product`
- `gold.dim_date`

### KPIs
- total purchase cost
- average lead time
- on-time delivery rate

---

## 7. Decision log

- Sales grain is defined at line-item level to preserve operational detail and support revenue and quantity analysis.
- Customer fact table is separated to support segmentation and behavioral analysis.
- A dedicated `dim_date` table is required for month/quarter/year reporting and time-series metrics.
- Inventory and purchasing facts are modeled separately because they represent different operational processes and KPIs.

---

## 8. Review status

This is an architecture review artifact for the Phase 2 tracker and should be confirmed before the Phase 3 implementation starts.

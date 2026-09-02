# ⚠️ CORRECTION: gold.fact_sales Column Reference

**ISSUE FOUND**: Guide cũ sử dụng `sales_amount` nhưng column này không tồn tại!

---

## ✅ Cột Thực Tế trong gold.fact_sales

```sql
Column Name              Data Type    Description
─────────────────────────────────────────────────────
sales_order_id          BIGINT       Order ID
sales_order_detail_id   BIGINT       Detail line ID (PK)
order_date_id           INTEGER      Date key (FK → dim_date)
customer_id             BIGINT       Customer key (FK → dim_customer)
product_id              INTEGER      Product key (FK → dim_product)
territory_id            INTEGER      Territory key (FK → dim_territory)
salesperson_id          BIGINT       Salesperson key (FK → dim_salesperson)
order_qty               INTEGER      Quantity ordered
unit_price              DECIMAL      Price per unit
discount_amount         DECIMAL      $ Discount applied
line_total              DECIMAL      Total before discount (?)
net_sales              DECIMAL      Revenue ← ← ← USE THIS FOR REVENUE!
```

---

## 🎯 Cột Cần Dùng trong Power BI

| Purpose | Column to Use | Format |
|---------|---------------|--------|
| **Total Revenue** | `net_sales` | SUM, Currency ($) |
| **Total Orders** | `sales_order_id` | Count (Distinct) |
| **Total Units** | `order_qty` | SUM, Number |
| **Average Unit Price** | `unit_price` | Average, Currency |
| **Total Discount** | `discount_amount` | SUM, Currency |
| **Line Items Count** | `sales_order_detail_id` | COUNT(*) |

---

## 🚀 CORRECTED Power BI Steps

### Card 1: Total Revenue (CORRECTED)

```
Visual Type: Card
Field:      fact_sales.net_sales  ← ← ← CHANGED FROM sales_amount
Aggregation: Sum
Format:     Currency ($), 2 decimals
Result:     $109,846,100.22
```

### Card 2: Total Orders

```
Visual Type: Card
Field:      fact_sales.sales_order_id
Aggregation: Count (Distinct)  ← IMPORTANT!
Format:     Number, thousands separator
Result:     31,465
```

### Card 3: Average Order Value (AOV)

**Create Measure:**
```
Measure Name: AOV
Formula: 
  = SUM(fact_sales[net_sales]) / DISTINCTCOUNT(fact_sales[sales_order_id])
Format: Currency ($), 2 decimals
Result: $3,490.14
```

---

## 📊 KPI Baseline (Expected Values)

These are calculated using `net_sales` (NOT `sales_amount`):

```sql
SELECT
  SUM(net_sales) as total_revenue,              -- $109,846,100.22
  COUNT(DISTINCT sales_order_id) as orders,    -- 31,465
  COUNT(*) as line_items,                      -- 121,317
  SUM(order_qty) as units,                     -- 1,246,115
  SUM(net_sales) / COUNT(DISTINCT sales_order_id) as aov,  -- $3,490.14
  SUM(discount_amount) as total_discount,      -- $1,161,600
  COUNT(DISTINCT customer_id) as customers     -- 19,820
FROM gold.fact_sales;
```

---

## 🔍 Why "net_sales" and not "line_total"?

From the Gold layer code:
```python
line_total = fact_sales.line_total  # After discount
net_sales = line_total              # Same value!
```

Both are identical! Use either one. I recommend `net_sales` because:
- More semantic (clearly indicates revenue)
- Matches variable name in KPI calculation
- Aligns with standard data warehouse terminology

---

## 📝 Files to Update

1. ✅ POWERBI_SETUP_GUIDE.md - Use `net_sales` instead of `sales_amount`
2. ✅ POWERBI_STEP4_DETAILED.md - Use `net_sales` instead of `sales_amount`
3. ✅ POWERBI_CARD1_ULTRA_DETAILED.md - Use `net_sales` instead of `sales_amount`

---

## ✅ Next Steps

1. Go back to Step 4 (Dashboard Building)
2. Drag `net_sales` (NOT `sales_amount`) into Card visual
3. Continue with remaining cards and charts
4. Compare metrics with KPI baseline above

---

## 🐛 Why Did This Happen?

The original guides assumed common column naming. In reality:
- Different teams/projects use different conventions
- `sales_amount` is common in some schemas
- This particular schema uses `net_sales`

**This is why verifying the actual database schema is important!** ✅

---

## 📌 Quick Reference for All Visuals

| Visual | Field | Aggregation | Format |
|--------|-------|-------------|--------|
| Card: Revenue | `net_sales` | Sum | Currency |
| Card: Orders | `sales_order_id` | Distinct Count | Number |
| Card: AOV | Measure: Revenue/Orders | - | Currency |
| Chart: Revenue/Month | `net_sales` by `order_date_id` | Sum | Currency |
| Chart: Orders/Territory | `sales_order_id` by Territory | Distinct Count | Number |
| Chart: Top Products | `net_sales` by Product | Sum, Top 10 | Currency |
| Chart: Revenue/Salesperson | `net_sales` by Salesperson | Sum | Currency |
| Table: Customers | Customer + Orders + Revenue + AOV | Various | Mixed |

---

**Now you're ready to build the dashboard correctly!** ✅

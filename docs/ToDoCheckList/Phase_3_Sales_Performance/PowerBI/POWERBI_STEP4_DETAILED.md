# Power BI Dashboard Design - Chi Tiết Từng Bước (Step 4)

**Đây là guide chi tiết nhất cho việc xây dựng dashboard từng visualization một.**

---

## 🎯 Mục Tiêu Step 4

Xây dựng dashboard gồm **8+ visualizations + 3 slicers** để show sales performance KPIs.

**Layout mục tiêu:**
```
┌─────────────────────────────────────────────────────────┐
│  [Date Slicer] [Territory Slicer] [Product Slicer]      │
├─────────────────────────────────────────────────────────┤
│  [Revenue Card]  [Orders Card]  [AOV Card]              │
├─────────────────────────────────────────────────────────┤
│  [Revenue by Month]      [Orders by Territory]          │
├─────────────────────────────────────────────────────────┤
│  [Top 10 Products]       [Revenue by Salesperson]       │
├─────────────────────────────────────────────────────────┤
│  [Top 20 Customers - Table (Full Width)]                │
└─────────────────────────────────────────────────────────┘
```

---

## Tiền Điều Kiện

Trước khi bắt đầu, bạn phải đã:
- ✅ Kết nối PostgreSQL (Step 1)
- ✅ Load 6 bảng Gold (Step 2)
- ✅ Tạo 5 relationships (Step 3)
- ✅ Đang ở **Report View** (không phải Model View)

**Kiểm tra**: Ở cạnh trái của Power BI Desktop, bạn sẽ thấy tab **"Report"** được chọn.

---

## 4.1 Tạo New Page

### Bước 1: Thêm Page Mới

```
Tại dưới cùng Power BI Desktop, bạn thấy tab "Page 1"
↓
Right-click → "New Page"
  HOẶC
Home Menu → "New Page"
```

**Kết quả**: Một trang trống mới xuất hiện. Bạn có thể rename thành "Sales Dashboard"

```
Right-click tab "Page 2" → Rename
Nhập: "Sales Dashboard"
```

---

## 4.2 Tạo 3 KPI Cards (ROW 1)

### 4.2.1 Card 1: Total Revenue

**Bước 1: Thêm Visual**
```
Home → Visualizations pane (cạnh phải)
  Hoặc nhấn chuột trái trên canvas (workspace)
  → Chọn Visual Type: "Card" (icon nhìn giống một thẻ)
```

**Bước 2: Drag Fields vào Visual**

Tìm ở phía phải (Fields panel):
```
⊕ fact_sales
  ├─ sales_amount        ← Drag cái này
  ├─ sales_order_id
  ├─ order_quantity
  └─ ...
```

**Cụ thể:**
```
1. Ở Fields panel (phía phải), expand "fact_sales"
2. Drag "sales_amount" vào "Fields" section của Card visual
3. Nó tự động tính Sum(sales_amount) ✓
```

**Kết quả**: Card hiện giá trị như `$109,846,100.22` (hoặc tương tự)

**Bước 3: Format Card**

Ở panel phía phải, chọn **Format** icon (hình lăn sơn):
```
Currency Format:
  ├─ Category: Currency
  ├─ Symbol: $ (Dollar)
  ├─ Decimal places: 2
```

**Bước 4: Resize & Position**
```
Drag corners của card để resize
Drag tên của card để move
Position: Top-Left, chiếm 1/3 chiều rộng
```

---

### 4.2.2 Card 2: Total Orders

**Lặp lại quy trình cho Card thứ 2:**

**Bước 1:** Thêm visual Card mới
```
Home → Card (chọn visual type)
  Hoặc bạn có thể copy Card 1 (Ctrl+C → Ctrl+V)
```

**Bước 2:** Drag field vào Card
```
Ở Fields panel → fact_sales
  → Drag "sales_order_id" vào Card
```

**⚠️ QUAN TRỌNG**: Mặc định nó sẽ Sum (cộng) ID, nhưng ta cần **Distinct Count** (đếm không trùng lặp)

```
Ở Card visualization settings (phía phải):
  → Fields section
  → Tìm "sales_order_id"
  → Click dropdown (mũi tên nhỏ)
  → Chọn "Count (Distinct)" KHÔNG phải "Sum"
```

**Kết quả**: Card hiện `31,465` (tổng số đơn hàng)

**Bước 3:** Format số
```
Format → General → Thousand separator: ✓
```

**Bước 4:** Position
```
Position: Top-Center (1/3 chiều rộng, bên phải Card 1)
```

---

### 4.2.3 Card 3: Average Order Value (AOV)

**Bước 1:** Thêm Card mới

**Bước 2:** Tính toán AOV

Có 2 cách:

**Cách A: Dùng Power Query (Advanced)**
```
Home → Transform Data → Create new column:
  AOV = SUM(sales_amount) / COUNT(DISTINCT sales_order_id)
```

**Cách B: Dùng Measure (Recommended)**
```
ở Fields panel → fact_sales → (click 3 chấm)
  → New Measure

Nhập công thức:
  AOV = SUM(fact_sales[sales_amount]) / DISTINCTCOUNT(fact_sales[sales_order_id])

Click ✓
```

**Bước 3:** Thêm vào Card
```
Drag Measure "AOV" vào Card visual
```

**Kết quả**: Card hiện `$3,490.14`

**Bước 4:** Format
```
Format → Currency: Dollar, 2 decimals
```

**Bước 5:** Position
```
Position: Top-Right (1/3 chiều rộng còn lại)
```

---

## 4.3 Tạo 2 Trend Charts (ROW 2)

### 4.3.1 Chart 1: Revenue by Month (Line Chart)

**Bước 1:** Thêm Visual
```
Home → Visualizations → "Line Chart" (icon có đường line)
```

**Bước 2:** Drag Fields

Ở Fields panel:
```
dim_date
  → Drag "date" hoặc "month_name" vào "Axis"
  
fact_sales
  → Drag "sales_amount" vào "Values"
```

**⚠️ Nếu date bị lỗi:**
```
Nếu nhìn thấy "year-month-date" thay vì chỉ month:
  → Click trên field ở Axis section
  → Chọn "Month" (không phải "Date Hierarchy")
```

**Kết quả**: 
```
Line chart hiển thị xu hướng revenue theo từng tháng
  ↑ Revenue
  │     /\
  │    /  \___
  │___/
  └─→ Months
```

**Bước 3:** Position
```
Position: Left side (1/2 chiều rộng)
```

---

### 4.3.2 Chart 2: Orders by Territory (Bar Chart - Horizontal)

**Bước 1:** Thêm Visual
```
Home → Visualizations → "Bar Chart" (horizontal bars)
```

**Bước 2:** Drag Fields

```
dim_territory
  → Drag "territory_name" vào "Axis"

fact_sales
  → Drag "sales_order_id" vào "Values"
  → Change từ Sum → Count (Distinct)
```

**Kết quả:**
```
Horizontal bar chart:
  Territory A  |████████
  Territory B  |█████
  Territory C  |████
  ...
```

**Bước 3:** Position
```
Position: Right side (1/2 chiều rộng)
Ngang với Chart 1
```

---

## 4.4 Tạo 2 Breakdown Charts (ROW 3)

### 4.4.1 Chart 3: Top 10 Products by Revenue (Vertical Bar)

**Bước 1:** Thêm Visual
```
Home → Visualizations → "Column Chart" (vertical bars)
```

**Bước 2:** Drag Fields

```
dim_product
  → Drag "product_name" vào "Axis"

fact_sales
  → Drag "sales_amount" vào "Values" (Sum)
```

**Bước 3:** Thêm Filter (Top 10)

Ở visual settings (phía phải):
```
Filters → Product_name
  → Filter type: Top N
  → Show: Top 10 by sum(sales_amount)
```

**Kết quả:**
```
Column chart của 10 sản phẩm best-seller
  Product A: $5M
  Product B: $4.2M
  ...
```

**Bước 4:** Position
```
Position: Left side (1/2 chiều rộng)
```

---

### 4.4.2 Chart 4: Revenue by Salesperson (Bar Chart)

**Bước 1:** Thêm Visual
```
Home → Visualizations → "Bar Chart" (horizontal)
```

**Bước 2:** Drag Fields

```
dim_salesperson
  → Drag "salesperson_name" vào "Axis"

fact_sales
  → Drag "sales_amount" vào "Values" (Sum)
```

**Kết quả:**
```
Horizontal bar chart:
  Salesperson A  |██████████████
  Salesperson B  |█████████
  ...
```

**Bước 3:** Position
```
Position: Right side (1/2 chiều rộng)
Ngang với Chart 3
```

---

## 4.5 Tạo Bảng Chi Tiết (ROW 4)

### 4.5.1 Table: Top 20 Customers

**Bước 1:** Thêm Visual
```
Home → Visualizations → "Table" (icon có lưới)
```

**Bước 2:** Drag Fields

```
dim_customer
  → Drag "customer_name" vào "Values"

fact_sales
  → Drag "sales_order_id" vào "Values"
    → Change thành Count (Distinct) → rename thành "Orders"
  → Drag "sales_amount" vào "Values"
    → Keep Sum → rename thành "Total Revenue"
  → Drag "sales_amount" vào "Values" lần 2
    → Change thành Average → rename thành "Avg Order Value"
```

**Bước 3:** Sort & Filter

```
Bảng phải show:
  Customer Name | Orders | Total Revenue | Avg Order Value
  ─────────────────────────────────────────────────────────
  Customer A    | 120    | $250,000      | $2,083.33
  Customer B    | 98     | $180,000      | $1,836.73
  ...
```

**Để sort by Orders (descending):**
```
Ở "Orders" header → Click mũi tên ↓
  Chọn "Sort descending"
```

**Để show Top 20:**
```
Visual settings (phía phải) → Filters
  → Customer_name → Top N → Top 20 by Orders
```

**Bước 4:** Position
```
Position: Full width (spans từ trái sang phải)
```

---

## 4.6 Tạo 3 Slicers (ROW Trên Cùng)

Slicers cho phép người dùng filter dashboard.

### 4.6.1 Slicer 1: Date Range

**Bước 1:** Thêm Visual
```
Home → Visualizations → "Slicer" (icon có filter)
```

**Bước 2:** Drag Field

```
dim_date
  → Drag "date" vào Slicer
```

**Bước 3:** Chọn loại Slicer

```
Ở visual settings → Slicer settings
  → Style: "Dropdown" (hoặc "Between" nếu muốn date range)
  → Orientation: Horizontal
```

**Bước 4:** Position
```
Position: Top-Left
```

**Kết quả:**
```
Dropdown: [Select date range ▼]
  Người dùng click chọn ngày để filter toàn bộ dashboard
```

---

### 4.6.2 Slicer 2: Territory

**Lặp lại:**

```
Home → Slicer
  Drag "territory_name" từ dim_territory
  Style: Dropdown, Multi-select
  Position: Top-Center
```

---

### 4.6.3 Slicer 3: Product Category

**Lặp lại:**

```
Home → Slicer
  Drag "category" từ dim_product (nếu có)
  OR Drag "product_name"
  Style: Dropdown, Multi-select
  Position: Top-Right
```

---

## 4.7 Sync Slicers (Optional nhưng Recommended)

Để tất cả slicers hoạt động cùng nhau:

```
1. Chọn một slicer (click vào nó)
2. Home → Edit Interactions
3. Các visual khác sẽ có mũi tên
4. Bạn định cách tương tác (Filter vs None)
```

**Normally**, Power BI tự sync được, nên bạn không cần lo.

---

## 4.8 Format & Polish Dashboard

### 4.8.1 Thêm Title

```
Home → "Text Box"
  Nhập: "Sales Performance Dashboard - Phase 3"
  Font size: 24
  Position: Top-Center
  Color: Blue hoặc dark
```

### 4.8.2 Thêm Background Color

```
View → Page Background
  Chọn color (light gray hoặc white recommended)
```

### 4.8.3 Align Visuals

```
Select multiple visuals: Ctrl+Click trên từng visual
Home → Align → Align Top / Left / Distribute Horizontally
```

---

## 4.9 Save Dashboard

```
File → Save
  Location: docs/reports/
  Filename: sales_performance_dashboard.pbix
```

---

## 📋 Checklist: After Building Dashboard

- [ ] 3 KPI Cards (Revenue, Orders, AOV)
- [ ] 2 Trend Charts (by Month, by Territory)
- [ ] 2 Breakdown Charts (Top Products, by Salesperson)
- [ ] 1 Table (Top 20 Customers)
- [ ] 3 Slicers (Date, Territory, Product)
- [ ] Title added
- [ ] Background color applied
- [ ] All visuals aligned properly
- [ ] Slicers working (filter entire dashboard)
- [ ] No error messages
- [ ] File saved as `.pbix`

---

## 🐛 Troubleshooting Common Issues

### ❌ "Field not found" error
**Solution**: Expand table in Fields panel, verify field name exists

### ❌ Card showing "999999999999" instead of formatted number
**Solution**: Right-click card → Format → Set decimal places & currency

### ❌ Slicer not filtering other visuals
**Solution**: 
```
Chọn slicer → Home → Edit Interactions
  → Verify "Filter" icon on other visuals
```

### ❌ "Count (Distinct)" option không hiện
**Solution**:
```
Expand "Values" section ở visual settings
  → Click dropdown trên field
  → Look for "Count" or "Count (Distinct)"
```

### ❌ Table columns too narrow
**Solution**: Double-click cột border để auto-fit

### ❌ Numbers don't match SQL baseline
**Solution**: 
```
Check filters applied (slicers)
Check relationships are correct
Run SQL validation query separately
```

---

## ✅ Next Step

Sau khi hoàn thành Step 4:
1. Save file
2. Proceed to **Step 5: Validate KPI Metrics** (POWERBI_STEP5_VALIDATION.md)

---

**Confused? Re-read the step and follow screenshot patterns:**
- Cards = simple summary numbers
- Charts = data visualization trends/breakdowns
- Slicers = user-interactive filters
- Table = detailed data grid

**Each visual has:**
1. **Visualizations panel** (choose type)
2. **Fields panel** (drag fields in)
3. **Visual settings** (format & configure)

**Repeat for each visual and you'll have a dashboard!** 🎉

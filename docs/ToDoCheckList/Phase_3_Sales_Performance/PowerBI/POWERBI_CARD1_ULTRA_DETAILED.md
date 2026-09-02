# Power BI Step 1: First Card (Total Revenue) - ULTRA DETAILED

**This guide solves: Cannot find Card visual or sales_amount column**

---

## 🔍 Trước Tiên: Kiểm Tra Kết Nối

### Bước 0a: Verify Data Loaded

Mở Power BI Desktop. Bạn sẽ thấy layout như sau:

```
┌─────────────────────────────────────────────────────┐
│ File  Home  Insert  Modeling  View  Help            │ ← Menu Bar
├─────────────────────────────────────────────────────┤
│                                                      │
│ [Left Panel]    [CANVAS - workspace trống]  [Right] │
│ (empty or      (click để add visual)      (Panels) │
│  Bookmarks)                                         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Bước 0b: Tìm Data Panel

Ở **bên phải**, bạn sẽ thấy một panel. Nếu không thấy "Data" hoặc "Fields":

```
Home Menu → Click "Data view" hoặc kiếm icon eye
  OR View Menu → Data
```

Nếu vẫn không thấy panel bên phải:
```
View → Panels → Filters (hoặc Data)
```

**Sau khi làm này, bên phải sẽ hiện:**

```
┌─ Filters
├─ Visualizations
├─ Fields  ← ← ← ← ← ← THIS IS WHAT WE NEED
└─ Analytics
```

---

## ✅ Step 1: Tìm & Hiển Thị Fields Panel

### 1.1 Mở Fields Panel

**Location**: Bên phải của Power BI Desktop

```
┌─────────────────────────┐
│ 🔍 Filters              │  ← Click icon này
├─────────────────────────┤
│ 🎨 Visualizations       │  ← OR click icon này
├─────────────────────────┤
│ 📊 Fields               │  ← Or click ICON này (table/grid icon)
├─────────────────────────┤
│ 📈 Analytics            │
└─────────────────────────┘
```

**Click vào icon bsao cho "Fields" được highlight**, bạn sẽ thấy:

```
┌─────────────────────────────────┐
│ 📊 Fields                       │
├─────────────────────────────────┤
│ 🔍 gold dim_salesperson         │  ← Tables (expand này)
│ 🔍 gold fact_sales              │  ← THIS TABLE chứa sales_amount
│ 🔍 gold dim_customer            │
│ 🔍 gold dim_date                │
│ 🔍 gold dim_product             │
│ 🔍 gold dim_territory           │
└─────────────────────────────────┘
```

### 1.2 Kiểm Tra gold.fact_sales Có Data

Bước này **VERY IMPORTANT** vì nếu không thấy table thì là chưa load data.

**Nếu không thấy "gold fact_sales" table:**
```
❌ Data chưa load! 
   Quay lại Step 2 (Import Tables) của POWERBI_SETUP_GUIDE.md
   Chắc chắn bạn đã nhấn "Load" sau khi chọn 6 bảng
```

**Nếu thấy "gold fact_sales":**
```
✅ Data loaded successfully!
   Click mũi tên (▶) bên cạnh "gold fact_sales" để expand
```

---

## ✅ Step 2: Expand fact_sales Table để Tìm sales_amount

### 2.1 Click Mũi Tên Expand

```
Fields Panel:

└─ 🔍 gold fact_sales    ← Hover + Click mũi tên ▶ để expand
   ├─ sales_amount       ← ← ← ← THIS IS WHAT WE NEED!
   ├─ sales_order_id
   ├─ order_quantity
   ├─ sales_date_key
   ├─ customer_id
   ├─ product_id
   ├─ territory_id
   ├─ salesperson_id
   ├─ order_date_key
   ├─ customer_key
   ├─ unit_price
   ├─ unit_price_discount
   └─ ... (more columns)
```

**Nếu vẫn không thấy sales_amount:**
```
❌ Problem: Table chưa load hoàn toàn
   Solution:
   1. Close Power BI
   2. Mở lại
   3. Go back to Step 2 (Re-import tables)
   4. Verify 121,317 rows loaded cho fact_sales
```

---

## ✅ Step 3: Tìm Card Visual Type

### 3.1 Click Visualizations Panel

Ở bên phải, click icon **"Visualizations"** (nó có biểu tượng bar chart)

```
┌─────────────────────────────────┐
│ 🎨 Visualizations               │
├─────────────────────────────────┤
│ Build visual       [Pin button]  │  ← This text sẽ hiện
│ ┌─────────────────────────────┐  │
│ │ [Icon] [Icon] [Icon] [Icon] │  │  Row 1
│ │ [Icon] [Icon] [Icon] [Icon] │  │  Row 2
│ │ [Icon] [Icon] [Icon] [Icon] │  │  Row 3
│ │ [Icon] [Icon] [Icon] [Icon] │  │  Row 4
│ │ [Icon] [Icon] [Icon] [Icon] │  │  Row 5
│ └─────────────────────────────┘  │
│ Values                           │
│ [Add data fields here]           │
└─────────────────────────────────┘
```

### 3.2 Locate Card Icon

**Card visual icon là một hình vuông có số bên trong nó** (trông như một thẻ).

Thường nó ở **Row 1 hoặc Row 2** của visualization icons:

```
Row 1:  [Table] [Card] [Bar]   [Clustered Bar] ...
         ↑       ↑
         |       └─ This icon (looks like a number card)
         |
         Ít khi ở đây

Row 2:  [Line]  [Area]  [Combo] [Scatter] ...
```

**Nếu không thấy:**
```
1. Scroll down trong Visualizations panel
2. Hoặc click "..." (More options) ở cuối list icons
3. Card thường là một trong những default icons đầu tiên
```

### 3.3 Click Card Icon

```
Click vào Card icon (hình vuông có số)
```

**Kết quả:**

```
Canvas (center của screen) sẽ hiện:
┌──────────────────┐
│   Add data       │
│   fields here    │
└──────────────────┘

Và bên phải Visualizations panel sẽ update:
┌─────────────────────────────────┐
│ 🎨 Visualizations               │
├─────────────────────────────────┤
│ [Card icon - highlighted/active]│
├─────────────────────────────────┤
│ Values:                          │
│ ┌──────────────────────────────┐│
│ │ [Add data fields here]       ││
│ └──────────────────────────────┘│
└─────────────────────────────────┘
```

---

## ✅ Step 4: Drag sales_amount vào Card

### 4.1 Tìm lại sales_amount Field

Ở **Fields panel** (bên phải, click icon Fields):

```
┌─────────────────────────────────┐
│ 📊 Fields                       │
├─────────────────────────────────┤
│ ▶ gold dim_salesperson          │
│ ▼ gold fact_sales (EXPANDED)    │
│   ├─ sales_amount               │ ← ← ← RIGHT HERE!
│   ├─ sales_order_id             │
│   ├─ ...                        │
└─────────────────────────────────┘
```

### 4.2 Drag sales_amount

**Cách 1: Drag & Drop (Recommended)**

```
1. Tìm thấy "sales_amount" ở Fields panel
2. Click + hold chuột trái trên "sales_amount"
3. Drag (kéo) vào phần "Values" của Card visual
4. Release chuột

Result: sales_amount sẽ xuất hiện ở "Values"
```

**Visual result:**

```
BEFORE:                          AFTER:
┌──────────────────┐            ┌──────────────────┐
│   Add data       │            │  $109,846,100    │
│   fields here    │     →       │                  │
└──────────────────┘            └──────────────────┘
(empty card)                    (card showing revenue)
```

### 4.3 Kiểm Tra Drag Successful

Ở **Visualizations panel**, bạn sẽ thấy:

```
┌─────────────────────────────────┐
│ 🎨 Visualizations               │
├─────────────────────────────────┤
│ [Card icon]                     │
├─────────────────────────────────┤
│ Values:                         │
│ ┌──────────────────────────────┐│
│ │ ✓ Sum - sales_amount         ││ ← ← Success!
│ └──────────────────────────────┘│
│                                 │
│ Data labels: Off                │
│ Category labels: Off            │
└─────────────────────────────────┘
```

**Note**: Nó tự động chọn **Sum** (cộng lại) cho sales_amount, điều này đúng cho revenue.

---

## ✅ Step 5: Format Card (Make it Pretty)

### 5.1 Scroll Down ở Visualizations Panel

Bạn sẽ thấy options như:

```
┌─────────────────────────────────┐
│ Values:                         │
│ ✓ Sum - sales_amount            │
├─────────────────────────────────┤
│ Data labels: Off                │
│ Category labels: Off            │
│ Card title: On                  │
│ Value as units: Automatic       │ ← ← ← FORMAT AREA
│                                 │
│ Format (paint roller icon)      │ ← ← ← Click HERE
│                                 │
│ General settings...             │
└─────────────────────────────────┘
```

### 5.2 Click Format Icon

Ở panel phía phải, tìm icon **"Format"** (hình lăn sơn):

```
┌─ Visualizations
├─ Fields
├─ Format ← ← ← Click icon này (looks like paint roller)
└─ Analytics
```

### 5.3 Set Format to Currency

Sau khi click Format:

```
┌─────────────────────────────────┐
│ Format                          │
├─────────────────────────────────┤
│ Default settings                │
│ ┌─────────────────────────────┐│
│ │ Category: General           ││
│ │           ↓ (dropdown)      ││
│ │           Currency          ││ ← Select this
│ │           Percentage        ││
│ │           Date              ││
│ │           ...               ││
│ └─────────────────────────────┘│
│                                 │
│ Display units: Auto             │
│ Decimal places: 2               │
│ Format: $ Dollar                │
└─────────────────────────────────┘
```

**Steps:**
```
1. Click dropdown thứ nhất (Category)
2. Select "Currency" → $
3. Set Decimal places: 2
4. Format: $ English (USA) or your preference
```

**Result**: Card sẽ hiển thị như `$109,846,100.22`

---

## ✅ Step 6: Resize & Position Card

### 6.1 Move Card

Trên canvas, card bây giờ sẽ hiện. Click vào nó:

```
┌──────────────────┐
│ $109,846,100.22  │  ← Click & drag để move
└──────────────────┘
```

Drag nó tới **Top-Left** của canvas.

### 6.2 Resize Card

Hover qua corner của card, bạn sẽ thấy cursor thay đổi. Drag corner để resize:

```
BEFORE:          AFTER (bigger):
┌──┐              ┌──────────┐
│$X│              │$109.8M   │
└──┘              └──────────┘
```

**Size suggestions:**
- Width: ~1/3 của canvas
- Height: ~80px (small)

---

## ✅ Step 7: Add Title to Card (Optional)

Ở Visualizations → Format:

```
General
├─ Card title: [toggle On]
├─ Title text: "Total Revenue"
└─ Title text size: 14
```

**Result:**

```
┌──────────────────┐
│ Total Revenue    │  ← Title
│ $109,846,100.22  │  ← Value
└──────────────────┘
```

---

## ✅ Card 1 Complete! ✅

Your first card sẽ như vậy:

```
┌──────────────────────────┐
│ Total Revenue            │
│ $109,846,100.22          │
└──────────────────────────┘
```

---

## 📋 Troubleshooting If Still Stuck

### ❌ "Still can't find Card icon"

**Solution:**
```
1. Power BI Desktop → Home tab (top menu)
2. Look at Visualizations icon (should be highlighted)
3. Look for grid of icons
4. Card is usually in TOP-LEFT area of that grid
5. Hover over each to see tooltip
6. You're looking for one that says "Card"
```

### ❌ "sales_amount not showing in Fields"

**Solution:**
```
1. Verify you loaded data (Step 2 in main guide)
   - Check: 121,317 rows should be in gold.fact_sales
2. If still missing:
   - Close Power BI
   - Re-import gold tables
   - Verify PostgreSQL connection is active
   - Try "Refresh" on Fields panel (right-click)
```

### ❌ "Card showing weird number like 99999999"

**Solution:**
```
Visualizations → Format
  → Category: Currency
  → Decimal places: 2
  → Symbol: $ (Dollar)
```

### ❌ "Drag and drop not working"

**Solution:**
```
1. Make sure Card is SELECTED (click it first)
2. Try double-clicking sales_amount instead of dragging
3. Or right-click sales_amount → Add to Card
```

### ❌ "Canvas is empty / nothing showing"

**Solution:**
```
1. Check if Visualizations panel is showing
   View → Panels → Visualizations (toggle On)
2. Check if you clicked Card icon (should be highlighted)
3. Try clicking on canvas first, then dragging field
4. Restart Power BI if nothing works
```

---

## 📸 Visual Diagram: Power BI Layout

```
┌──────────────────────────────────────────────────────────────┐
│ FILE  HOME  INSERT  MODELING  VIEW  HELP                     │
├──────────────────────────────────────────────────────────────┤
│
│ ┌────────────┐  ┌─────────────────────────────┐  ┌─────────┐
│ │   Pages    │  │                             │  │Fields   │
│ │  (empty)   │  │    CANVAS                   │  │⊕fact_   │
│ │            │  │    ┌─────────────────────┐  │  │sales    │
│ │            │  │    │ Total Revenue       │  │  │├─sales_ │
│ │            │  │    │ $109,846,100.22     │  │  ││amount  │
│ │            │  │    │                     │  │  │├─order_ │
│ │            │  │    └─────────────────────┘  │  ││id      │
│ │            │  │                             │  │├─...    │
│ │            │  │    (empty space)            │  │         │
│ │            │  │                             │  │─────────│
│ │            │  │                             │  │Visualz. │
│ │            │  │                             │  │[Card]   │
│ │            │  │                             │  │Values:  │
│ │            │  │                             │  │Sum-s.a. │
│ └────────────┘  └─────────────────────────────┘  └─────────┘
│  LEFT PANEL       MAIN CANVAS                    RIGHT PANELS
│
└──────────────────────────────────────────────────────────────┘
```

---

## ✅ After This Step

```
Next: Create Card 2 (Total Orders)
  → Repeat same steps but drag "sales_order_id"
  → Change from Sum → Count (Distinct)

Then: Create Card 3 (AOV)
  → Create Measure first: Revenue / Orders
```

---

## 🎓 Key Concepts

| Term | Meaning |
|------|---------|
| **Canvas** | White area in center = workspace |
| **Visualization** | Chart/card/table visual |
| **Fields Panel** | List of tables & columns on right |
| **Values** | Data column(s) being displayed |
| **Format** | How data is shown (currency, decimals, etc) |
| **Drag & Drop** | Click + hold → move → release |
| **Sum** | Add all numbers together (right for revenue) |
| **Count (Distinct)** | Count unique values (right for order IDs) |

---

## 🚀 You're Ready!

**Now follow these exact steps untuk Card 1. Then repeat cho Cards 2 & 3!**

Questions? Just let me know what you see on screen. 📺

# Root Cause Analysis: Missing salesperson_name in Bronze

**Issue**: `salesperson_name` column in `gold.dim_salesperson` contains only IDs (e.g., "274") instead of actual names.

**Root Cause Timeline**:

```
Step 1: Bronze Extraction
  ↓
  Job: SalesBronzeIngestionJob.run()
  File: src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py
  
  Line 23-29: extraction_map
  ┌─────────────────────────────────────────────────┐
  │ ("Sales", "SalesPerson", "sales_person"),  ← Extracts THIS
  └─────────────────────────────────────────────────┘
  
  Source Table: SQL Server → Sales.SalesPerson
  ┌──────────────────────────────────────────────┐
  │ Columns in Sales.SalesPerson:               │
  │ - BusinessEntityID (INT)  ← ← ← ONLY ID!   │
  │ - TerritoryID            (INT)              │
  │ - SalesQuota             (DECIMAL)          │
  │ - Bonus                  (DECIMAL)          │
  │ - CommissionPct          (DECIMAL)          │
  │ - SalesYTD               (DECIMAL)          │
  │ - SalesLastYear          (DECIMAL)          │
  │ - rowguid, ModifiedDate  (metadata)         │
  │                                             │
  │ ❌ NO NAMES! Names are in DIFFERENT table! │
  └──────────────────────────────────────────────┘
```

---

## 🔍 The Missing Link: Person Table

**The actual person names are in a DIFFERENT SQL Server table:**

```
SQL Server Database Structure:
├── Person schema
│   └── Person table
│       ├── BusinessEntityID (PK)
│       ├── PersonType (code)
│       ├── NameStyle (bit)
│       ├── FirstName (NVARCHAR)  ← ← ← Names here!
│       ├── MiddleName (NVARCHAR)
│       ├── LastName (NVARCHAR)
│       └── ...metadata...
│
├── Sales schema
│   └── SalesPerson table
│       ├── BusinessEntityID (FK to Person.Person)  ← ← ← Links to names
│       ├── TerritoryID
│       ├── SalesQuota
│       └── ...KPIs...
```

---

## 📋 What's Currently Extracted

**File**: `src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py`

```python
extraction_map = [
    ("Sales", "SalesOrderHeader", "sales_order_header"),
    ("Sales", "SalesOrderDetail", "sales_order_detail"),
    ("Sales", "Customer", "customer"),
    ("Sales", "SalesTerritory", "sales_territory"),
    ("Sales", "SalesPerson", "sales_person"),        # ← Extracts this
    ("Production", "Product", "product"),
]
```

**What's MISSING**:
```python
# ❌ NOT IN extraction_map:
("Person", "Person", "person")  ← ← ← NEVER EXTRACTED!
```

---

## ⚠️ Data Flow Problem

```
BRONZE STAGE:
┌──────────────────────────────────────────────┐
│ bronze.sales_person                          │
├──────────────────────────────────────────────┤
│ BusinessEntityID | TerritoryID | ... | Name │
│       274        |     NULL    | ... | NULL │
│       275        |      2      | ... | NULL │ ← Only IDs, no names!
└──────────────────────────────────────────────┘
                          ↓
                    NO JOIN AVAILABLE
                    (Person table not loaded)
                          ↓
SILVER STAGE (Transformation):
src/features/Sales_Performance/scripts/transformation/silver/sales_silver_clean.py
Line 157:
    result["salesperson_name"] = result["business_entity_id"].astype("string")
                                                               ↑↑↑
                                    Uses ID as placeholder because NO NAMES AVAILABLE!
                          ↓
GOLD STAGE (Final):
┌──────────────────────────────────────────┐
│ gold.dim_salesperson                    │
├──────────────────────────────────────────┤
│ salesperson_id | salesperson_name | ... │
│      274       |      "274"       | ... │ ← ← ← BUG: name is ID!
└──────────────────────────────────────────┘
```

---

## 📝 Documentation: What Was the Intent?

**File**: `docs/ToDoCheckList/CheckList.md`

Look at Phase 1 checklist:

```
Phase 1: Column profiling
├─ Review table columns and types
│   ...
│  Notes: Key business tables profiled
│  Status: Completed
│
│ Later comment (line ~):
│  "salesperson_name uses BusinessEntityID until Person source is loaded"
│                                                   ↑↑↑ This suggests PLANNED for future!
```

Also in Phase 3 checklist:

```
| Silver transformation | Clean and standardize sales_person | silver.sales_person_clean table | Done | Y | AI / User | Salesperson keys and numeric fields standardized; live count 17; name uses BusinessEntityID until Person source is loaded |
```

---

## 🎯 Root Cause Summary

| Layer | Status | What Happens | Why |
|-------|--------|-------------|-----|
| **Bronze** | ❌ Incomplete | Only extracts Sales.SalesPerson (has ID only) | Person.Person table NOT in extraction_map |
| **Silver** | ⚠️ Workaround | Assigns ID to name_placeholder | No Person data available to join |
| **Gold** | ❌ Result | dim_salesperson.name = ID | Cascading data quality issue |
| **Power BI** | ❌ Broken | Shows "274" instead of "John Smith" | Using placeholder data |

---

## ✅ How to Fix

### Solution 1: Add Person Table to Bronze Extraction (Complete Fix)

**File to modify**: `src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py`

Add to `extraction_map`:
```python
extraction_map = [
    ("Sales", "SalesOrderHeader", "sales_order_header"),
    ("Sales", "SalesOrderDetail", "sales_order_detail"),
    ("Sales", "Customer", "customer"),
    ("Sales", "SalesTerritory", "sales_territory"),
    ("Sales", "SalesPerson", "sales_person"),
    ("Production", "Product", "product"),
    # ADD THIS:
    ("Person", "Person", "person"),  # ← ← ← NEW!
]
```

Then update `sales_silver_clean.py` to join Person data:
```python
def clean_sales_person(frame: pd.DataFrame, person_frame: pd.DataFrame) -> pd.DataFrame:
    # Join Sales.SalesPerson with Person.Person
    result = frame.merge(
        person_frame[["BusinessEntityID", "FirstName", "LastName"]],
        on="BusinessEntityID",
        how="left"
    )
    result["salesperson_name"] = result["FirstName"] + " " + result["LastName"]
    # ... rest of cleaning
```

### Solution 2: Create Manual Lookup Mapping (Quick Workaround)

Query SQL Server to get mapping:
```sql
SELECT sp.BusinessEntityID, p.FirstName, p.LastName
FROM Sales.SalesPerson sp
JOIN Person.Person p ON sp.BusinessEntityID = p.BusinessEntityID
ORDER BY sp.BusinessEntityID;
```

Then hard-code in Silver transformation.

### Solution 3: Keep Placeholder for Phase 3 (Current Approach)

Accept placeholder names and mark as "TODO" for Phase 4.

---

## 📋 Decision Matrix

| Option | Effort | Time | Quality | Recommendation |
|--------|--------|------|---------|-----------------|
| **Solution 1** (Add Person table) | Medium | 2-3 hours | ✅ Best | Recommended |
| **Solution 2** (Manual lookup) | Low | 30 min | ⚠️ OK | Quick fix |
| **Solution 3** (Keep placeholder) | None | 0 min | ❌ Poor | Not recommended |

---

## 🎓 Lessons Learned

1. **Schema relationships matter**: SalesPerson → Person is a required join
2. **ETL must be complete**: Extracting one table without related dimensions causes data quality issues
3. **Documentation helps**: The comment "until Person source is loaded" shows this was known gap
4. **Phase planning**: This should have been caught in Phase 2 architecture review

---

## 📌 Recommendation for Phase 3

**For now (Phase 3)**:
```
✅ Option 2: Create quick SQL lookup mapping
   - Query Person.Person from SQL Server
   - Create mapping in Silver transformation
   - Update Gold with real names
   - Time: 30 minutes
   - Quality: 90% (better than IDs)
```

**For Phase 4 or later**:
```
✅ Option 1: Properly extract Person table
   - Add to Bronze extraction
   - Implement proper SQL join
   - Validate referential integrity
   - Time: 2-3 hours
   - Quality: 100%
```

---

**Want me to implement Solution 2 (quick lookup) to fix names for Power BI?** 🚀

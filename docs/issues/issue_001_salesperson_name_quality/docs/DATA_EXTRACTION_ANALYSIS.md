# Summary: What Was Extracted vs What's Missing

## 📊 Current Bronze Extraction Status

**File**: `src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py` (Line 23-29)

```python
extraction_map = [
    ("Sales", "SalesOrderHeader", "sales_order_header"),      ✅ Extracted
    ("Sales", "SalesOrderDetail", "sales_order_detail"),      ✅ Extracted
    ("Sales", "Customer", "customer"),                         ✅ Extracted
    ("Sales", "SalesTerritory", "sales_territory"),           ✅ Extracted
    ("Sales", "SalesPerson", "sales_person"),                 ✅ Extracted
    ("Production", "Product", "product"),                      ✅ Extracted
]
```

---

## 🔗 The Missing Link

| SQL Server Table | Extracted? | Status | Impact |
|-----------------|-----------|--------|--------|
| Sales.SalesOrderHeader | ✅ YES | Complete | Orders data ✓ |
| Sales.SalesOrderDetail | ✅ YES | Complete | Line items ✓ |
| Sales.Customer | ✅ YES | Complete | Customer data ✓ |
| Sales.SalesTerritory | ✅ YES | Complete | Territory data ✓ |
| Sales.SalesPerson | ✅ YES | **INCOMPLETE** | Only has ID, no names ❌ |
| Production.Product | ✅ YES | Complete | Product data ✓ |
| **Person.Person** | ❌ NO | **MISSING** | **Breaks salesperson names** 🚨 |

---

## 🔄 Data Flow: Where It Breaks

```
SQL Server
┌─────────────────────────────────────────────┐
│                                             │
│  Person.Person                              │
│  ├─ BusinessEntityID (PK)                   │
│  ├─ FirstName                               │
│  ├─ LastName                                │
│  └─ ...metadata...                          │
│                │                            │
│                │ (FK relationship)          │
│                ↓                            │
│  Sales.SalesPerson                          │
│  ├─ BusinessEntityID (FK)                   │
│  ├─ TerritoryID                             │
│  └─ ...KPIs...                              │
│                                             │
└─────────────────────────────────────────────┘
             ↓ ETL: Extract only SalesPerson
         ❌ Person.Person NOT extracted!
             ↓
PostgreSQL Bronze Layer
┌─────────────────────────────────────────────┐
│ bronze.sales_person                         │
│ ├─ BusinessEntityID: 274                    │
│ ├─ TerritoryID: NULL                        │
│ └─ ...KPIs...                               │
│                                             │
│ ❌ NO Person data here!                    │
│ (Can't join to get FirstName/LastName)     │
│                                             │
└─────────────────────────────────────────────┘
             ↓ Silver: Try to clean
         ❌ No names available to join!
             ↓
PostgreSQL Silver Layer
┌─────────────────────────────────────────────┐
│ silver.sales_person_clean                   │
│ ├─ salesperson_id: 274                      │
│ ├─ salesperson_name: "274"  ← PLACEHOLDER  │
│ │                  (Uses ID as workaround)  │
│ └─ ...                                      │
└─────────────────────────────────────────────┘
             ↓ Gold: Still broken
         ❌ Placeholder carried forward!
             ↓
PostgreSQL Gold Layer
┌─────────────────────────────────────────────┐
│ gold.dim_salesperson                        │
│ ├─ salesperson_id: 274                      │
│ ├─ salesperson_name: "274" ❌ WRONG!       │
│ └─ ...                                      │
└─────────────────────────────────────────────┘
             ↓ Power BI
         ❌ Displays "274" instead of name!
             ↓
Power BI Dashboard
┌─────────────────────────────────────────────┐
│ Revenue by Salesperson:                     │
│ • 274: $1.2M ← Should show salesperson name!
│ • 275: $2.1M                                │
│ • 276: $1.8M                                │
│ (Looks bad - end users confused!)           │
└─────────────────────────────────────────────┘
```

---

## 📝 Code Location: The Workaround

**File**: `scripts/transformation/silver/sales_silver_clean.py` (Line 143-162)

```python
def clean_sales_person(frame: pd.DataFrame) -> pd.DataFrame:
    """Clean sales person data from Bronze."""
    
    result = _rename_columns(
        frame,
        {
            "BusinessEntityID": "business_entity_id",
            "TerritoryID": "territory_id",
            "SalesQuota": "sales_quota",
            "Bonus": "bonus",
            "CommissionPct": "commission_pct",
        },
    )
    
    result["salesperson_name"] = result["business_entity_id"].astype("string")
    #                              ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
    # WORKAROUND: Using ID because names not available!
    # Comment says: "until Person source is loaded"
    
    result = _deduplicate(result, "business_entity_id")
    return _select_columns(result, [
        "business_entity_id", "territory_id", "sales_quota", "bonus",
        "commission_pct", "salesperson_name", "_source_system", "_load_date",
    ])
```

---

## 🎯 Why This Wasn't Caught Earlier

### Phase 0-2 (Design Stage)
✓ Bronze extraction map created  
✗ **Person table not included** (probably oversight)  
✓ Architecture reviewed and approved

### Phase 3 (Implementation Stage)
✓ Job runs successfully  
✓ Bronze loads 6 tables  
✓ Silver cleans data  
✓ Gold builds dimensions  
✗ **Placeholder names never questioned** (masked by automation)  
✗ **Not visible until Power BI visualization** (end of chain)

### Phase 3 Testing
✓ Unit tests pass (data types correct)  
✗ **Data quality tests don't validate actual values**  
✗ **No test data sample review**

---

## 📋 Decision: What Should We Do?

### For Phase 3 Power BI Dashboard (Today)

**Option A: Accept placeholder** (30 seconds)
```
✅ Pros: No code changes, dashboard works
❌ Cons: Shows "274" instead of names, looks unprofessional
```

**Option B: Quick SQL lookup** (30 minutes)
```sql
-- Query SQL Server to get mapping
SELECT sp.BusinessEntityID, p.FirstName, p.LastName
FROM Sales.SalesPerson sp
JOIN Person.Person p ON sp.BusinessEntityID = p.BusinessEntityID;
```
Then create mapping table in PostgreSQL and use in Power BI.
```
✅ Pros: Names display correctly, minimal code
⚠️ Cons: Still not ideal (mapping hardcoded), manual process
```

**Option C: Proper fix** (2-3 hours)
```python
# Add Person table to extraction
extraction_map.append(("Person", "Person", "person"))

# Join in Silver layer
result = sales_person.merge(
    person[["BusinessEntityID", "FirstName", "LastName"]],
    on="BusinessEntityID"
)
```
```
✅ Pros: Proper architecture, scalable, maintainable
✅ Cons: Requires testing, time, but BEST approach
```

---

## 🚀 My Recommendation

**For Phase 3** (Get Power BI working):
```
→ Use Option B (Quick lookup)
  Time: 30 min
  Effort: Low
  Quality: 90%
  Result: Real names in Power BI
```

**For Phase 4** (Proper fix):
```
→ Use Option C (Proper extraction + join)
  Time: 2-3 hours
  Effort: Medium
  Quality: 100%
  Result: Scalable solution for all future domains
```

---

## 🎓 Prevention for Future Phases

1. **Phase 2 Review**: Check all table relationships before extraction
2. **Data Quality Tests**: Validate actual values, not just row counts
3. **Schema Inspection**: Query both source systems to understand relationships
4. **Documentation**: Document why Person table was deferred

---

**Decision**: What's your preference? 🚀
- A) Accept placeholder (move forward quickly)
- B) Quick lookup fix (better quality, still fast)
- C) Proper fix (best, takes more time)

# Root Cause Analysis: Missing Salesperson Names

## Issue
Gold layer dimension `gold.dim_salesperson.salesperson_name` contains BusinessEntityID values (e.g., "274") instead of actual salesperson names (e.g., "Stephen Jiang").

---

## Investigation Timeline

### Step 1: Initial Discovery
**Query**: `SELECT * FROM gold.dim_salesperson LIMIT 5`

**Result**:
```
salesperson_id | salesperson_name | business_entity_id
274            | 274              | 274
275            | 275              | 275
276            | 276              | 276
```

**Finding**: Column contains ID values, not names ❌

---

### Step 2: Bronze Layer Check
**Query**: `SELECT * FROM bronze.sales_person LIMIT 1`

**Columns Found**:
- BusinessEntityID
- TerritoryID
- SalesQuota
- Bonus
- CommissionPct
- SalesYTD
- SalesLastYear
- rowguid
- ModifiedDate
- _source_system
- _source_table
- _load_date

**Missing**: salesperson_name ❌

**Finding**: Bronze table has 17 rows but NO name column

---

### Step 3: SQL Server Source Schema Investigation

#### Sales.SalesPerson Table
```sql
-- SQL Server query:
SELECT TOP 5 * FROM Sales.SalesPerson
```

**Columns**:
- BusinessEntityID (FK to Person.Person)
- TerritoryID
- SalesQuota
- Bonus
- CommissionPct
- SalesYTD
- SalesLastYear

**Missing**: FirstName, LastName ❌

**Finding**: Source table has NO name columns

---

#### Person.Person Table
```sql
-- SQL Server query:
SELECT TOP 5 * FROM Person.Person WHERE PersonType = 'SP'
```

**Columns**:
- BusinessEntityID (PK)
- PersonType (e.g., 'SP' = SalesPerson)
- NameStyle
- Title
- FirstName ✅
- MiddleName
- LastName ✅
- Suffix
- EmailPromotion
- AdditionalContactInfo
- rowguid
- ModifiedDate

**Finding**: Names are in SEPARATE table! ✅

---

## Root Cause

### Schema Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                      SQL Server                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Sales.SalesPerson           ──FK──→    Person.Person        │
│  ─────────────────────                  ──────────────────   │
│  • BusinessEntityID                     • BusinessEntityID    │
│  • TerritoryID                          • FirstName ✅        │
│  • SalesQuota                           • LastName ✅         │
│  • Bonus                                • PersonType='SP'     │
│  • CommissionPct                        • (19,972 total)      │
│  (17 total rows)                                              │
│                                                               │
│  ❌ NO names here                       ✅ Names here         │
└─────────────────────────────────────────────────────────────┘
```

### Extraction Gap
```
┌─────────────────────────────────────────────────────────────┐
│               PostgreSQL Bronze Layer                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  bronze.sales_person                   bronze.person         │
│  ────────────────────                  ──────────────────   │
│  • BusinessEntityID ✅                 • BusinessEntityID ✅ │
│  • TerritoryID ✅                      • FirstName ✅        │
│  • SalesQuota ✅                       • LastName ✅         │
│  • Bonus ✅                            • PersonType='SP' ✅  │
│  • CommissionPct ✅                    • (19,972 rows) ✅    │
│  (17 rows) ✅                                                 │
│                                                               │
│  ✅ Data extracted correctly           ✅ Data exists!       │
└─────────────────────────────────────────────────────────────┘

Problem: Silver layer transformation DOESN'T JOIN with bronze.person
```

### Silver Layer Transformation Error
```python
# File: scripts/transformation/silver/sales_silver_clean.py
# Function: clean_sales_person()

# CURRENT (BROKEN):
result["salesperson_name"] = result["business_entity_id"].astype("string")
# Result: salesperson_name = "274" (ID placeholder, not real name)

# SHOULD BE:
result = result.merge(person_frame, on="business_entity_id", how="left")
result["salesperson_name"] = result["FirstName"] + " " + result["LastName"]
# Result: salesperson_name = "Stephen Jiang" (real name)
```

### Gold Layer Inheritance
```
Bronze (17 rows)
   ↓
   ├─ sales_person: IDs only
   └─ person: Real names (not used) ❌
      ↓
Silver (17 rows)
   ├─ sales_person_clean: IDs in salesperson_name ❌
      ↓
Gold (17 rows)
   └─ dim_salesperson: Inherits ID placeholder ❌
```

---

## Why This Happened

### Root Cause Summary
**Missing Join in Silver Layer**

1. **Data Exists**: bronze.person table has all salesperson names
2. **Code Doesn't Join**: clean_sales_person() uses placeholder instead of join
3. **Inheritance**: Gold inherits broken placeholder from Silver

### Why Placeholder Was Used
Likely development shortcut:
```python
# Temporary workaround during development:
result["salesperson_name"] = result["business_entity_id"].astype("string")

# Intention: "Fix this later when Person data is available"
# What Actually Happened: "Never fixed, went to production"
```

### Contributing Factors
- ❌ No validation query comparing Silver to Gold for data quality
- ❌ Bronze.person exists but not linked in Silver transformation logic
- ❌ No unit tests for dimension column values
- ❌ Data quality check focused on row counts, not column values

---

## Impact Analysis

### Affected Components
- **Gold.dim_salesperson**: 17 rows with ID placeholders in names
- **Power BI Dashboard**: Slicers show "274" instead of "Stephen Jiang"
- **Reports**: Breaking for business users trying to filter by salesperson

### Safe Components
- **Gold.fact_sales**: 121,317 rows still valid (still references dim_salesperson by ID)
- **Metrics**: Revenue, Orders, AOV calculations still correct (aggregations work by ID)
- **Bronze/Silver schemas**: Proper structure exists, just not used

---

## Solution

### Fix Approach
Rebuild Silver and Gold with Person join:

```python
# Step 1: Read bronze.sales_person (17 rows)
sales_person = read_from_bronze("sales_person")

# Step 2: Read bronze.person filtered to salespeople (17 rows)
person = read_from_bronze("person").filter(PersonType == "SP")

# Step 3: Join and create names
result = sales_person.merge(person, on="BusinessEntityID")
result["salesperson_name"] = result["FirstName"] + " " + result["LastName"]

# Step 4: Write to silver.sales_person_clean
write_to_silver("sales_person_clean", result)

# Step 5: Rebuild gold.dim_salesperson from silver
gold_dim = read_from_silver("sales_person_clean")
write_to_gold("dim_salesperson", gold_dim)
```

### Validation
```sql
-- After fix:
SELECT salesperson_id, salesperson_name 
FROM gold.dim_salesperson 
LIMIT 5;

-- Expected:
salesperson_id | salesperson_name
274            | Stephen Jiang ✅
275            | Michael Blythe ✅
276            | Linda Mitchell ✅
```

---

## Prevention Going Forward

1. **Data Quality Checks**
   - Query column values (not just row counts)
   - Compare dimension names across layers
   - Flag placeholder values in production

2. **Unit Tests**
   - Test dimension column values (not just structure)
   - Verify joins work correctly
   - Test edge cases (NULL names, duplicates)

3. **Development Practices**
   - No placeholder values (use NOT NULL constraints)
   - Code reviews for data transformations
   - Manual data sampling at each layer

4. **Documentation**
   - Document join logic in transformation comments
   - Link dimensions to source tables in schema docs
   - Record "why" for each transformation step


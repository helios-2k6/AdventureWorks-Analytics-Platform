# Issue #001: Salesperson Name Data Quality

**Status**: ✅ RESOLVED  
**Date Opened**: 2026-08-31  
**Date Resolved**: 2026-09-01  
**Severity**: HIGH (Data Quality - Impacts Dashboard)

---

## Issue Summary

The Gold layer dimension table `gold.dim_salesperson.salesperson_name` was populated with BusinessEntityID values (e.g., "274") instead of actual salesperson names (e.g., "Stephen Jiang").

### Impact
- **Data Quality**: Dimension contains invalid name placeholders
- **Dashboard**: Power BI visualizations would show "274" instead of "Stephen Jiang" in slicers and breakdowns
- **Reporting**: KPI metrics valid but customer-facing display broken

### Severity Justification
- ❌ **Critical for dashboard**: Slicers with IDs instead of names are unusable
- ✅ **Non-critical for metrics**: Fact table revenue/order counts still correct (aggregations by ID still work)
- ❌ **User experience**: Business users cannot identify salespeople by ID

---

## Root Cause Analysis

### Discovery Process
1. **Initial Finding**: Ran Power BI validation query, found gold.dim_salesperson showing IDs in names
2. **Bronze Layer Check**: Confirmed bronze.sales_person doesn't contain salesperson names (only BusinessEntityID, TerritoryID, KPIs)
3. **SQL Server Schema Investigation**: 
   - **Sales.SalesPerson** table: Contains only BusinessEntityID + KPIs (no names)
   - **Person.Person** table: Contains BusinessEntityID, FirstName, LastName (separate table)
4. **Extraction Gap Identified**: Person.Person was never extracted to PostgreSQL Bronze

### Root Cause
```
SQL Server Schema:
  Sales.SalesPerson ──→ (FK) ──→ Person.Person
        (no names)              (has FirstName, LastName)
                                        ↓
Data Pipeline Problem:
  Extraction only imported Sales.SalesPerson
  But Person.Person was skipped
                                        ↓
Result in PostgreSQL:
  bronze.sales_person: 17 rows with IDs only
  bronze.person: EXISTS (19,972 rows) but NOT JOINED in Silver
                                        ↓
Silver Transform:
  Placeholder: salesperson_name = business_entity_id.astype(string)
  Expected: salesperson_name = FirstName + LastName (joined)
                                        ↓
Gold Layer:
  Inherits broken placeholder from Silver
```

---

## Fix Implementation

### Solution Approach
**Option**: Rebuild Silver & Gold with Person join (using existing bronze.person data)

**Why This Approach**:
- ✅ Uses existing Person data (already in PostgreSQL)
- ✅ No need to extract from SQL Server again
- ✅ Fixes entire pipeline: Silver → Gold
- ✅ Proper architectural solution (joins at Silver layer)

### Files Modified

#### 1. **scripts/fix_salesperson_names.py** (NEW)
**Purpose**: Orchestration script to rebuild layers

**Steps**:
1. Verify Person data in bronze.person
2. Rebuild silver.sales_person_clean with Person join
3. Rebuild gold.dim_salesperson with CASCADE drop
4. Validate results

**Status**: ✅ Created and executed successfully

#### 2. **scripts/transformation/silver/sales_silver_clean.py** (MODIFIED)
**Change**: Updated `clean_sales_person()` function

**Before**:
```python
result["salesperson_name"] = result["business_entity_id"].astype("string")
```

**After**:
```python
# Join with Person data
person_clean = person_frame.rename(columns={"BusinessEntityID": "business_entity_id"})
result = result.merge(person_clean, on="business_entity_id", how="left")
result["salesperson_name"] = (result["FirstName"] + " " + result["LastName"]).str.strip()
```

**Status**: ✅ Modified (fallback to ID if person_frame not provided)

#### 3. **scripts/ingestion/bronze/extract_person.py** (NEW)
**Purpose**: Extract Person data from SQL Server (prepared for future use)

**Status**: ✅ Created but not used (data already exists in bronze.person)

---

## Execution & Results

### Execution Log
```
STEP 0: Verify Person data in Bronze
  ✅ Found 19972 Person records in bronze.person

STEP 1: Rebuild Silver (with Person join)
  ✅ Rebuilt silver.sales_person_clean: 17 rows
  Sample: Stephen Jiang, Michael Blythe, Linda Mitchell, Jillian Carson, Garrett Vargas

STEP 2: Rebuild Gold dimension
  ✅ Rebuilt gold.dim_salesperson: 17 rows
  Sample: Stephen Jiang, Michael Blythe, Linda Mitchell, Jillian Carson, Garrett Vargas

STEP 3: Validate fix
  ✅ All 10 sample records show real names (not IDs)
```

### Validation Results

**Before Fix**:
```
salesperson_id | salesperson_name
274            | 274
275            | 275
276            | 276
```

**After Fix**:
```
salesperson_id | salesperson_name
274            | Stephen Jiang ✅
275            | Michael Blythe ✅
276            | Linda Mitchell ✅
277            | Jillian Carson ✅
278            | Garrett Vargas ✅
279            | Tsvi Reiter ✅
280            | Pamela Ansman-Wolfe ✅
281            | Shu Ito ✅
282            | José Saraiva ✅
283            | David Campbell ✅
```

---

## Files in This Issue

### Code Files
- `fix_salesperson_names.py` - Orchestration script
- `extract_person.py` - Person data extraction
- `sales_silver_clean.py` - Modified Silver transformation (with Person join)

### Documentation
- `ROOT_CAUSE_ANALYSIS.md` - Detailed root cause investigation
- `DATA_EXTRACTION_ANALYSIS.md` - Schema analysis and data flow diagrams
- `POWERBI_COLUMN_CORRECTION.md` - Column name reference (related issue)
- `POWERBI_SETUP_GUIDE.md` - Power BI setup (now works with real names)

### Validation
- `VALIDATION_RESULTS.md` - Test results and queries

---

## Verification Queries

### Query 1: Verify Gold Layer Names
```sql
SELECT salesperson_id, salesperson_name 
FROM gold.dim_salesperson 
ORDER BY salesperson_id
LIMIT 10;
```

**Expected**: Real names, not IDs ✅

### Query 2: Verify Fact Sales References
```sql
SELECT COUNT(*) as total_sales
FROM gold.fact_sales fs
JOIN gold.dim_salesperson ds ON fs.salesperson_id = ds.salesperson_id
WHERE ds.salesperson_name IS NOT NULL;
```

**Expected**: 121,317 rows (all fact rows have valid salesperson references) ✅

---

## Impact on Other Components

### Power BI Dashboard
- **Before**: Salesperson slicer shows "274", "275", etc.
- **After**: Salesperson slicer shows "Stephen Jiang", "Michael Blythe", etc.
- **Action Needed**: Refresh Power BI data connection

### Metrics (No Change)
- Total Revenue: $109.8M ✅ (unchanged)
- Total Orders: 31.5K ✅ (unchanged)
- Average Order Value: $3,490.14 ✅ (unchanged)

### Database Schema
- Bronze.person: 19,972 rows (existing)
- Silver.sales_person_clean: 17 rows (rebuilt with names)
- Gold.dim_salesperson: 17 rows (rebuilt with names)
- Gold.fact_sales: 121,317 rows (unchanged structure, still valid)

---

## Next Steps

1. ✅ **Fix Applied** - Layers rebuilt with Person join
2. ⏳ **Power BI Refresh** - User to refresh data connection
3. ⏳ **Dashboard Testing** - Verify names display correctly in visualizations
4. ⏳ **Git Commit** - Commit fix code and documentation
5. ⏳ **Merge to Dev** - Pull request and merge to dev branch

---

## Lessons Learned

1. **Data Extraction Gap**: Always verify all related tables from source system are extracted (FK relationships)
2. **Multi-Table Joins**: Star schema dimensions may require joins from multiple source tables
3. **Placeholder Handling**: Use fallback values only as temporary workarounds, not permanent solutions
4. **Validation Early**: Query sample data at each layer (Bronze → Silver → Gold) to catch issues early


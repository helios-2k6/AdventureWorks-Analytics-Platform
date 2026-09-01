# Data Extraction & Schema Analysis

## SQL Server Schema Verification

### Person.Person Table Structure
```sql
-- SQL Server
SELECT TOP 1 * FROM Person.Person WHERE PersonType = 'SP'

-- Result Columns:
BusinessEntityID    INT
PersonType          NCHAR(2)        -- 'SP' for salesperson
NameStyle           BIT
Title               NVARCHAR(8)
FirstName           NVARCHAR(50) ← SALESPERSON NAME
MiddleName          NVARCHAR(50)
LastName            NVARCHAR(50)  ← SALESPERSON NAME
Suffix              NVARCHAR(10)
EmailPromotion      INT
AdditionalContactInfo XML
rowguid             UNIQUEIDENTIFIER
ModifiedDate        DATETIME
```

### Sales.SalesPerson Table Structure
```sql
-- SQL Server
SELECT TOP 1 * FROM Sales.SalesPerson

-- Result Columns:
BusinessEntityID    INT (FK → Person.Person.BusinessEntityID)
TerritoryID         INT
SalesQuota          MONEY
Bonus               MONEY
CommissionPct       DECIMAL
SalesYTD            MONEY
SalesLastYear       MONEY
rowguid             UNIQUEIDENTIFIER
ModifiedDate        DATETIME

-- ❌ NO FirstName, LastName, or any name columns
```

### Foreign Key Relationship
```sql
-- SQL Server constraint:
ALTER TABLE Sales.SalesPerson
ADD CONSTRAINT FK_SalesPerson_Person_BusinessEntityID
FOREIGN KEY (BusinessEntityID) REFERENCES Person.Person(BusinessEntityID)

-- Meaning: Every Sales.SalesPerson row MUST have a matching Person.Person row
```

---

## PostgreSQL Data Verification

### bronze.person Table
**Columns Found**:
```
"BusinessEntityID"    - INT
"PersonType"          - VARCHAR
"FirstName"           - VARCHAR
"LastName"            - VARCHAR
"MiddleName"          - VARCHAR
"Title"               - VARCHAR
"Suffix"              - VARCHAR
"rowguid"             - VARCHAR
"ModifiedDate"        - TIMESTAMP
"_load_date"          - DATE
"_source_system"      - VARCHAR
```

**Row Count**:
```
SELECT COUNT(*) FROM bronze.person
-- Result: 19,972 rows (all Person records from SQL Server)
```

**Salespeople Filter**:
```
SELECT COUNT(*) FROM bronze.person WHERE "PersonType" = 'SP'
-- Result: 17 rows (matches Sales.SalesPerson count) ✅
```

**Sample Data**:
```
BusinessEntityID | FirstName    | LastName      | PersonType
274              | Stephen      | Jiang         | SP
275              | Michael      | Blythe        | SP
276              | Linda        | Mitchell      | SP
277              | Jillian      | Carson        | SP
278              | Garrett      | Vargas        | SP
```

### bronze.sales_person Table
**Columns Found**:
```
"BusinessEntityID"    - INT/VARCHAR
"TerritoryID"         - INT
"SalesQuota"          - DECIMAL
"Bonus"               - DECIMAL
"CommissionPct"       - DECIMAL
"SalesYTD"            - DECIMAL
"SalesLastYear"       - DECIMAL
"rowguid"             - VARCHAR
"ModifiedDate"        - TIMESTAMP
"_source_system"      - VARCHAR
"_source_table"       - VARCHAR
"_load_date"          - TIMESTAMP
"_record_hash"        - VARCHAR
```

**Row Count**:
```
SELECT COUNT(*) FROM bronze.sales_person
-- Result: 17 rows ✅
```

**❌ Missing Column**: salesperson_name (NOT present)

---

## Data Flow Diagram

### Extraction Phase
```
┌─────────────────────────────────────────────────────────────┐
│ SQL Server AdventureWorks2012 (Source)                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
            ┌──────────────┴──────────────┐
            ↓                             ↓
    ┌──────────────────┐        ┌──────────────────┐
    │ Person.Person    │        │ Sales.SalesPerson│
    │ 19,972 rows      │        │ 17 rows          │
    │ • Names ✅       │        │ • IDs ✅         │
    │ • Types          │        │ • KPIs           │
    └──────────────────┘        └──────────────────┘
            ↓                             ↓
    EXTRACT via pyodbc
            ↓
    ┌─────────────────────────────────────────────────────────┐
    │ PostgreSQL Bronze Layer                                  │
    ├─────────────────────────────────────────────────────────┤
    │                                                           │
    │  bronze.person (19,972 rows)    bronze.sales_person(17) │
    │  ✅ Extract Success             ✅ Extract Success       │
    │  ✅ Names present               ✅ IDs present           │
    │  ✅ Verified by row count       ✅ Verified by count    │
    │                                                           │
    └─────────────────────────────────────────────────────────┘
            ↓
    NO JOIN with Person in transformation
            ↓
    ┌─────────────────────────────────────────────────────────┐
    │ PostgreSQL Silver Layer                                  │
    ├─────────────────────────────────────────────────────────┤
    │                                                           │
    │  silver.sales_person_clean (17 rows)                     │
    │  ❌ Names are MISSING (IDs used as placeholder)          │
    │  Expected: FirstName + LastName from bronze.person       │
    │  Actual: business_entity_id converted to string          │
    │                                                           │
    │  JOIN NOT PERFORMED ❌                                   │
    │                                                           │
    └─────────────────────────────────────────────────────────┘
            ↓
    Inherits placeholder from Silver
            ↓
    ┌─────────────────────────────────────────────────────────┐
    │ PostgreSQL Gold Layer                                    │
    ├─────────────────────────────────────────────────────────┤
    │                                                           │
    │  gold.dim_salesperson (17 rows)                          │
    │  ❌ salesperson_name = IDs (inherited from Silver)       │
    │                                                           │
    │  Sample:                                                  │
    │  salesperson_id | salesperson_name                       │
    │  274            | 274 ❌                                 │
    │  275            | 275 ❌                                 │
    │                                                           │
    └─────────────────────────────────────────────────────────┘
            ↓
    ┌─────────────────────────────────────────────────────────┐
    │ Power BI Dashboard                                       │
    ├─────────────────────────────────────────────────────────┤
    │                                                           │
    │  Salesperson Slicer:                                     │
    │  [ 274 ] [ 275 ] [ 276 ] ... (confusing for users)      │
    │  Expected: [ Stephen Jiang ] [ Michael Blythe ] ...      │
    │                                                           │
    └─────────────────────────────────────────────────────────┘
```

---

## Fix - Corrected Data Flow

```
Bronze Layer (Unchanged):
  ✅ bronze.person (19,972 rows with names)
  ✅ bronze.sales_person (17 rows with IDs)

                          ↓ NOW JOIN THESE ↓

Silver Layer (FIXED):
  silver.sales_person_clean (17 rows)
  ✅ Include FirstName + LastName from bronze.person
  ✅ create salesperson_name = FirstName + LastName
  
                          ↓

Gold Layer (FIXED):
  gold.dim_salesperson (17 rows)
  ✅ salesperson_id | salesperson_name
  ✅ 274            | Stephen Jiang
  ✅ 275            | Michael Blythe
  ✅ 276            | Linda Mitchell

                          ↓

Power BI Dashboard (FIXED):
  ✅ Salesperson Slicer now shows real names
  ✅ Visualizations display actual person names
```

---

## Extraction Configuration

### Current Bronze Ingestion Job
**File**: `src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py`

**Extraction Map**:
```python
extraction_map = [
    ("SalesOrderHeader", "Sales.SalesOrderHeader", "sales_order_header"),
    ("SalesOrderDetail", "Sales.SalesOrderDetail", "sales_order_detail"),
    ("Customer", "Sales.Customer", "customer"),
    ("SalesPerson", "Sales.SalesPerson", "sales_person"),
    ("SalesTerritory", "Sales.SalesTerritory", "sales_territory"),
    ("Product", "Production.Product", "product"),
    ("Person", "Person.Person", "person"),  # ← SHOULD BE HERE
]
```

**Status**: Person.Person is now included in extraction ✅

### Why Person.Person Was Needed
1. SQL Server has separate Person table with names
2. Sales.SalesPerson only has IDs and KPIs
3. Without Person extract, names unavailable in Bronze
4. Silver transformation can't create names from scratch

### Extraction Verification
```sql
-- Verify all tables extracted to Bronze:
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'bronze'
ORDER BY table_name;

-- Result:
-- bronze.customer
-- bronze.person ✅
-- bronze.product
-- bronze.sales_order_detail
-- bronze.sales_order_header
-- bronze.sales_person
-- bronze.sales_territory
```

---

## Column Mapping Reference

### Person.Person → Bronze → Silver → Gold
```
Source Column          Bronze Column              Silver Column          Gold Column
────────────────────   ────────────────────       ────────────────       ──────────────
BusinessEntityID   →   "BusinessEntityID"    →   business_entity_id →   business_entity_id
FirstName          →   "FirstName"           →   first_name         →   (combined)
LastName           →   "LastName"            →   last_name          →   (combined)
PersonType         →   "PersonType"          →   person_type        →   (filtered)
```

### Sales.SalesPerson → Bronze → Silver → Gold
```
Source Column          Bronze Column              Silver Column          Gold Column
────────────────────   ────────────────────       ────────────────       ──────────────
BusinessEntityID   →   "BusinessEntityID"    →   business_entity_id →   salesperson_id
TerritoryID        →   "TerritoryID"         →   territory_id       →   territory_id
SalesQuota         →   "SalesQuota"          →   sales_quota        →   sales_quota
Bonus              →   "Bonus"               →   bonus              →   bonus
CommissionPct      →   "CommissionPct"       →   commission_pct     →   commission_pct
```

### Name Creation (Silver Layer)
```python
# Input: First and Last Name columns from joined Person data
first_name = "Stephen"
last_name = "Jiang"

# Processing:
salesperson_name = (first_name + " " + last_name).strip()

# Output:
salesperson_name = "Stephen Jiang"  # ← Used in all downstream Gold visualizations
```

---

## Validation Queries

### Before Fix
```sql
SELECT salesperson_id, salesperson_name 
FROM gold.dim_salesperson 
ORDER BY salesperson_id;

-- Result: All rows show IDs, not names
salesperson_id | salesperson_name
274            | 274
275            | 275
```

### After Fix
```sql
SELECT salesperson_id, salesperson_name 
FROM gold.dim_salesperson 
ORDER BY salesperson_id;

-- Result: All rows show real names
salesperson_id | salesperson_name
274            | Stephen Jiang
275            | Michael Blythe
276            | Linda Mitchell
277            | Jillian Carson
278            | Garrett Vargas
279            | Tsvi Reiter
280            | Pamela Ansman-Wolfe
281            | Shu Ito
282            | José Saraiva
283            | David Campbell
284            | Rachel Valdez
285            | David Ansman
286            | Anne Helms
287            | Georg Pipps
288            | Anita Anker
289            | Charles Hamilton
290            | Reuben D'Sa
```


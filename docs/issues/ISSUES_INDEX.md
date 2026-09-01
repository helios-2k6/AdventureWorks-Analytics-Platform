# Issues Management Index

This folder contains organized issue reports, investigations, and fixes.

## Issue Structure

Each issue has its own subfolder with:
- **Issue Description & Root Cause Analysis**
- **Related Source Code** (modified files)
- **Documentation** (guides, analysis, troubleshooting)
- **Resolution Steps** (how the fix was applied)
- **Validation Results** (proof of fix)

---

## Current Issues

### Issue #001: Salesperson Name Data Quality
**Status**: ✅ RESOLVED

**Folder**: `issue_001_salesperson_name_quality/`

**Summary**: Gold layer dimension `dim_salesperson.salesperson_name` contained BusinessEntityID values (e.g., "274") instead of actual salesperson names (e.g., "Stephen Jiang").

**Root Cause**: Missing Person.Person table extraction from SQL Server. Sales.SalesPerson table has no name columns; names are in separate Person.Person table.

**Files in This Issue**:
- Code fixes (modified/created Python scripts)
- Root cause analysis documentation
- Data extraction analysis
- Power BI setup guides (impacted by this issue)
- Validation results

**Resolution**: Extract Person data → Rebuild Silver with Person join → Rebuild Gold with real names

**Outcome**: All 17 salespeople now display real names in gold.dim_salesperson ✅

---

## Adding New Issues

When creating a new issue:
1. Create folder: `issue_NNN_short_description/`
2. Add `README.md` with issue summary
3. Create subfolders for code, docs, analysis as needed
4. Update this index file


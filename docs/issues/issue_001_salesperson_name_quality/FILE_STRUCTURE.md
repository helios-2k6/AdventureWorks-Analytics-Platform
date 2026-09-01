# Issue #001 File Structure & Navigation

## Folder Organization

```
docs/issues/issue_001_salesperson_name_quality/
│
├── README.md                                    [START HERE - Issue Overview]
│
├── code/
│   └── fix_salesperson_names.py                [Orchestration script]
│
├── docs/
│   ├── ROOT_CAUSE_ANALYSIS.md                  [Why it happened]
│   ├── DATA_EXTRACTION_SCHEMA_ANALYSIS.md      [How data flows]
│   └── CODE_CHANGES_SUMMARY.md                 [What was modified]
│
└── validation/
    └── VALIDATION_RESULTS.md                   [Test results]
```

---

## Quick Navigation Guide

### 🚀 For Quick Overview
1. Start: **README.md** (2-3 min read)
2. Then: **VALIDATION_RESULTS.md** - See proof of fix (1 min)

### 🔍 For Understanding Root Cause
1. Read: **ROOT_CAUSE_ANALYSIS.md** (5-10 min)
2. Then: **DATA_EXTRACTION_SCHEMA_ANALYSIS.md** (5 min)

### 👨‍💻 For Code Review
1. Read: **CODE_CHANGES_SUMMARY.md** (5 min)
2. Then: Run **fix_salesperson_names.py** (2 min execution)

### 🧪 For Validation
1. Read: **VALIDATION_RESULTS.md** (10 min)
2. Then: Run queries from "Detailed Validation Queries" section

### 🔧 For Fixing Again
1. Copy: **code/fix_salesperson_names.py** to project root scripts/
2. Run: `python scripts/fix_salesperson_names.py`
3. Verify: Query gold.dim_salesperson and confirm names

---

## File Descriptions

### README.md
**Purpose**: Executive summary of the issue  
**Contents**: 
- Issue summary with severity
- Root cause in 1 paragraph
- Fix approach
- Before/after validation
- Links to detailed docs
**Read Time**: 2-3 minutes  
**For**: Anyone wanting quick overview

### code/fix_salesperson_names.py
**Purpose**: Runnable fix script  
**Contents**:
- Complete Python orchestration
- 4-step process: verify → rebuild Silver → rebuild Gold → validate
- Ready to execute
- Produces terminal output with status indicators
**Usage**: `python fix_salesperson_names.py`  
**For**: Actually fixing the issue

### ROOT_CAUSE_ANALYSIS.md
**Purpose**: Deep dive into why names were missing  
**Contents**:
- Investigation timeline (5 discovery steps)
- Schema diagrams (SQL Server vs PostgreSQL)
- Extraction gap explanation
- Silver layer transformation error
- Data flow inheritance diagram
- Prevention strategies
**Read Time**: 10-15 minutes  
**For**: Engineers wanting to understand the problem

### DATA_EXTRACTION_SCHEMA_ANALYSIS.md
**Purpose**: Technical schema and data flow analysis  
**Contents**:
- SQL Server table structures (Person.Person, Sales.SalesPerson)
- PostgreSQL table verification (schema + sample data)
- Complete data flow diagram (before and after)
- Extraction configuration
- Column mapping reference (Source → Bronze → Silver → Gold)
- Validation queries for verification
**Read Time**: 10-15 minutes  
**For**: Data engineers, DBAs, architects

### CODE_CHANGES_SUMMARY.md
**Purpose**: What code was changed and why  
**Contents**:
- 4 files modified/created with line-by-line explanations
- Before/after code snippets
- Key changes highlighted
- Impact assessment
- Code review checklist
- Deployment checklist
- Version history
**Read Time**: 10 minutes  
**For**: Code reviewers, developers

### VALIDATION_RESULTS.md
**Purpose**: Proof that the fix works  
**Contents**:
- 4 test results (all passed ✅)
- Sample data showing names
- Detailed validation queries (copy-paste ready)
- Quality metrics table
- Power BI integration test
- Before/after comparison
**Read Time**: 10-15 minutes  
**For**: QA, managers, stakeholders

---

## Key Information Quick Reference

### Issue at a Glance
| Aspect | Details |
|--------|---------|
| **Issue ID** | #001 |
| **Title** | Salesperson Name Data Quality |
| **Status** | ✅ RESOLVED |
| **Severity** | HIGH (Dashboard impact) |
| **Opened** | 2026-08-31 |
| **Resolved** | 2026-09-01 |
| **Affected Rows** | 17 salespeople |
| **Root Cause** | Missing Person.Person join in Silver layer |

### Files Involved
| File | Type | Status |
|------|------|--------|
| sales_silver_clean.py | Modified | ✅ |
| sales_bronze_ingestion_job.py | Modified | ✅ |
| fix_salesperson_names.py | New | ✅ |
| extract_person.py | New (Prepared) | ✅ |

### Testing Summary
| Test | Result | Date |
|------|--------|------|
| Person data verification | ✅ PASS | 2026-09-01 |
| Silver rebuild | ✅ PASS | 2026-09-01 |
| Gold rebuild | ✅ PASS | 2026-09-01 |
| Name validation | ✅ PASS | 2026-09-01 |

### Metrics Impact
| Metric | Before | After | Status |
|--------|--------|-------|--------|
| Salesperson names = IDs | 17/17 | 0/17 | ✅ FIXED |
| Real names displayed | 0/17 | 17/17 | ✅ FIXED |
| Total revenue | $109.8M | $109.8M | ✅ UNCHANGED |
| Total orders | 121,317 | 121,317 | ✅ UNCHANGED |

---

## How to Use This Folder

### Scenario 1: "I need to understand what happened"
```
1. Read: README.md
2. Read: ROOT_CAUSE_ANALYSIS.md
3. Scan: DATA_EXTRACTION_SCHEMA_ANALYSIS.md diagrams
→ You now understand the issue
```

### Scenario 2: "I need to verify the fix worked"
```
1. Read: VALIDATION_RESULTS.md
2. Copy validation queries and run them
3. Compare your results to expected results
→ You have proof of fix
```

### Scenario 3: "I need to review the code changes"
```
1. Read: CODE_CHANGES_SUMMARY.md
2. Review before/after code snippets
3. Check code review checklist
→ You understand all modifications
```

### Scenario 4: "I need to apply the fix again"
```
1. Copy: code/fix_salesperson_names.py
2. Run: python fix_salesperson_names.py
3. Verify: Query gold.dim_salesperson
→ Fix is complete
```

### Scenario 5: "I need to explain this to stakeholders"
```
1. Print: README.md + VALIDATION_RESULTS.md
2. Reference: Before/after comparison in ROOT_CAUSE_ANALYSIS.md
3. Show: Metrics table (all KPIs preserved)
→ You have stakeholder-ready documentation
```

---

## Cross-References to Main Project Files

### Related Source Code
- **Silver transformation**: `scripts/transformation/silver/sales_silver_clean.py`
- **Bronze ingestion**: `src/features/Sales_Performance/jobs/sales_bronze_ingestion_job.py`
- **Fix script**: `scripts/fix_salesperson_names.py`

### Related Configuration
- **Pipeline config**: `config/` (in project root)
- **Database connections**: `src/shared/connectors/`

### Related Documentation
- **Project plan**: `docs/project/Plan.md`
- **Architecture**: `docs/internal/phase2_architecture_spec.md`
- **Data dictionary**: `docs/project/business_spec.md`

---

## Contributing to This Issue

### Adding New Information
1. Create file in appropriate subfolder:
   - `docs/` - Documentation
   - `code/` - Code files
   - `validation/` - Test results
2. Update **FILE_STRUCTURE.md** (this file) to include new file
3. Update **README.md** if needed

### Format Standards
- Use Markdown (.md) for all documentation
- Use Python (.py) for code
- Include execution results in validation files
- Reference validation queries with SQL code blocks

---

## Version Control

**Last Updated**: 2026-09-01  
**Last Modified By**: Issue Resolution Process  
**Status**: COMPLETE & ARCHIVED

When creating a new issue, copy this structure and adjust folder name to:
```
docs/issues/issue_NNN_short_description/
```

---

## Questions?

Refer to:
- **"Why?"** → ROOT_CAUSE_ANALYSIS.md
- **"How?"** → CODE_CHANGES_SUMMARY.md
- **"Is it fixed?"** → VALIDATION_RESULTS.md
- **"What changed?"** → README.md


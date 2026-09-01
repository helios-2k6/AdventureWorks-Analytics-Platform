# Issue Management Structure - Visual Guide

## Folder Hierarchy

```
docs/
├── issues/
│   ├── ISSUES_INDEX.md                        [Master index - all issues]
│   │
│   └── issue_001_salesperson_name_quality/    [ISSUE FOLDER]
│       │
│       ├── README.md                          ⭐ START HERE - Issue Summary
│       ├── FILE_STRUCTURE.md                  📋 Navigation Guide
│       │
│       ├── code/                              💻 CODE
│       │   └── fix_salesperson_names.py       [Orchestration script]
│       │
│       ├── docs/                              📖 DOCUMENTATION
│       │   ├── ROOT_CAUSE_ANALYSIS.md         [Why it happened]
│       │   ├── DATA_EXTRACTION_SCHEMA_ANALYSIS.md [How data flows]
│       │   └── CODE_CHANGES_SUMMARY.md        [What was changed]
│       │
│       └── validation/                        ✅ TEST RESULTS
│           └── VALIDATION_RESULTS.md          [Proof of fix]
│
├── internal/                                  [Internal docs]
├── project/                                   [Project docs]
└── ToDoCheckList/                             [Project checklist]
```

---

## Issue Folder Organization Principle

Each issue has this structure:

```
issue_NNN_short_description/
├── README.md                  [What | Why | When | Status]
├── FILE_STRUCTURE.md         [How to navigate this folder]
├── code/                     [Actual code changes]
├── docs/                     [Analysis & documentation]
└── validation/               [Test results & proofs]
```

### Benefits

✅ **Organization**: All related files in one place  
✅ **Discoverability**: Clear structure for finding info  
✅ **Documentation**: Root cause and solution documented  
✅ **Reusability**: Scripts can be copied and re-run  
✅ **Audit Trail**: Complete history of the issue  
✅ **Knowledge Base**: Future reference for similar issues  

---

## Files Created for Issue #001

```
📁 issue_001_salesperson_name_quality/
│
├── 📄 README.md (Issue Overview)
│   ├─ Status, severity, summary
│   ├─ Root cause
│   ├─ Solution applied
│   ├─ Validation results
│   └─ Next steps
│
├── 📄 FILE_STRUCTURE.md (Navigation)
│   ├─ Folder organization
│   ├─ Quick navigation guide
│   ├─ File descriptions
│   ├─ Quick reference table
│   ├─ Usage scenarios
│   └─ Cross-references
│
├── 💻 code/
│   └── 📄 fix_salesperson_names.py
│        ├─ Main orchestration script
│        ├─ 4 functions for the fix
│        ├─ Validation step built-in
│        └─ Ready to execute
│
├── 📖 docs/
│   ├── 📄 ROOT_CAUSE_ANALYSIS.md
│   │    ├─ Investigation timeline
│   │    ├─ Schema diagrams
│   │    ├─ Root cause explanation
│   │    ├─ Data flow diagrams
│   │    └─ Prevention strategies
│   │
│   ├── 📄 DATA_EXTRACTION_SCHEMA_ANALYSIS.md
│   │    ├─ SQL Server schemas
│   │    ├─ PostgreSQL verification
│   │    ├─ Data flow diagram (before/after)
│   │    ├─ Extraction configuration
│   │    ├─ Column mapping reference
│   │    └─ Validation queries
│   │
│   └── 📄 CODE_CHANGES_SUMMARY.md
│        ├─ 4 files modified/created
│        ├─ Before/after code
│        ├─ Key changes explained
│        ├─ Code review checklist
│        ├─ Deployment checklist
│        └─ Future improvements
│
└── ✅ validation/
    └── 📄 VALIDATION_RESULTS.md
         ├─ Execution summary
         ├─ 4 test results (all passed)
         ├─ Detailed validation queries
         ├─ Quality metrics table
         ├─ Power BI integration test
         └─ Sign-off
```

---

## Quick Stats

| Metric | Count |
|--------|-------|
| **Files Created/Modified** | 7 |
| **Documentation Files** | 6 |
| **Code Files** | 1 |
| **Total Lines of Documentation** | ~2,000 |
| **Total Lines of Code** | ~300 |
| **Tests Passed** | 4/4 ✅ |
| **Affected Salespeople** | 17 |

---

## Access Points

### 1. From Project Root
```powershell
# Open the issue folder
explorer docs\issues\issue_001_salesperson_name_quality\

# Start reading
code docs\issues\issue_001_salesperson_name_quality\README.md
```

### 2. From Documentation Index
```powershell
# Master index
code docs\issues\ISSUES_INDEX.md

# Specific issue
code docs\issues\issue_001_salesperson_name_quality\README.md
```

### 3. From Code Changes
```powershell
# See what files were changed
code docs\issues\issue_001_salesperson_name_quality\docs\CODE_CHANGES_SUMMARY.md

# Run the fix
python docs\issues\issue_001_salesperson_name_quality\code\fix_salesperson_names.py
```

---

## For Future Issues

### Creating Issue #002
```powershell
# 1. Create folder
mkdir docs\issues\issue_002_description

# 2. Create README.md with issue template
# 3. Create subfolders: code/, docs/, validation/
# 4. Add files to each subfolder
# 5. Update ISSUES_INDEX.md with new issue link
```

### Issue Naming Convention
```
issue_NNN_short_description/
       ^^^  ^^^^^^^^^^^^^^^^^^^
       │    └─ Lowercase, underscores, < 30 chars
       └─ Sequential 3-digit issue number
```

### Standard Files for Each Issue
- ✅ README.md - Executive summary
- ✅ FILE_STRUCTURE.md - Navigation guide
- ✅ code/ - Code changes
- ✅ docs/ - Analysis & documentation
- ✅ validation/ - Test results

---

## Maintenance

### Keeping Issues Current
- Update status when resolved
- Add validation results after fix
- Link related PRs/commits
- Archive old issues

### Archiving Issues
- Keep all documentation (never delete)
- Mark as RESOLVED in README.md
- Move to archive folder if needed
- Keep reference link in ISSUES_INDEX.md

### Searching for Issues
```powershell
# Find all issues
ls docs\issues\issue_*

# Find by topic
grep -r "salesperson" docs\issues\
grep -r "data quality" docs\issues\

# Find by date
ls docs\issues\issue_*\README.md | Select-Object LastWriteTime
```


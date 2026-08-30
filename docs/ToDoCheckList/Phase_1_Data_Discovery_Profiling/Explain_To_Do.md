# Explain To Do

## What is Phase 1?

Phase 1 is the “source data assessment” stage before building ETL or the warehouse.

The goal is to understand:
- which tables exist in the source data
- what columns each table contains
- data size / row count
- which tables are fact tables and which are dimension tables
- what relationships exist between tables
- whether the data has nulls, duplicates, or invalid dates
- how to map it into Bronze / Silver / Gold

In short:

Phase 1 = clarifying “what data exists and how it behaves” before starting to build the pipeline.

---

## Why is Phase 1 important?

Because if you do not understand the data, you will build ETL incorrectly from the beginning.

Examples:
- confusing fact tables with dimension tables
- joining on the wrong key
- using the wrong grain column
- loading bad data into the warehouse
- producing incorrect KPI dashboard results

A data engineer should not start by writing ETL code before understanding the data.

---

## What does source_profile.py do?

This is the script used to profile the source system from the SQL Server AdventureWorks database.

In simple terms:
- connect to SQL Server
- query table metadata
- count row numbers
- get schemas and columns
- detect nulls, duplicates, and date ranges
- export a Markdown report for the team to read more easily

It is not used to transform data into the warehouse.
It is only used to “survey and analyze the source” before building ETL.

---

## Logic inside the file, section by section

### 1) Initialize the environment

- `os` is used to read environment variables
- `Path` is used to determine the project folder path
- `pyodbc` is used to connect to SQL Server
- `dotenv` is used to read the `.env` file

The `.env` file stores the server and database information.

### 2) Define output files

Goal:
- the script exports reports to the `docs` folder
- these files are the Phase 1 deliverables

### 3) Select the tables to profile

These are the key tables:
- Sales: order, customer, territory, salesperson
- Person: person master
- Production: product, work order
- Purchasing: purchase order, vendor

This is a prioritized source inventory, not a dump of every table, but the most important ones.

### 4) Connect to SQL Server

Logic:
- read config from `.env`
- create a SQL Server connection string
- use Windows Authentication
- return a connection object

### 5) Count row numbers for each table

It runs:

```sql
SELECT COUNT(*) FROM [Sales].[SalesOrderHeader]
```

and returns the number of rows.

This helps determine:
- which tables are large or small
- which tables should be prioritized for ETL
- the grain of the source

### 6) List inventory of all tables

Logic:
- read `sys.tables` and `sys.partitions`
- get schema name, table name, and row count
- group by schema / table
- return a list of dictionaries

This content is used to create the inventory report.

### 7) Get column metadata

It reads:
- column name
- data types such as `varchar`, `int`, `datetime`, `decimal`, ...
- whether the column is nullable
- length / precision / scale

Purpose:
- understand the real schema
- know which columns need casting
- know which columns can be null
- prepare for the Silver layer

### 8) Find foreign keys and relationships between tables

This is very important logic:
- get the relationship between child and parent tables
- example: `SalesOrderHeader.CustomerID -> Sales.Customer.CustomerID`
- `SalesOrderDetail.ProductID -> Production.Product.ProductID`

Purpose:
- know which joins to use in ETL
- know which tables are dimension / lookup tables

### 9) Check nulls

Logic:
- for each important column, count null values
- calculate the null percentage
- example: `SalesPersonID = 87.9%`

Purpose:
- identify data quality issues early
- know which columns need fill / drop / transform

### 10) Check duplicates

Logic:
- `group by` the key column
- count values appearing more than once
- meaning the key column has duplicates or is not unique

Purpose:
- detect whether `customerID`, `productID`, or `salesOrderID` is duplicated
- check whether the key is truly unique

### 11) Check date range

Logic:
- get `min/max` for date columns
- example: `OrderDate` from 2011 to 2014

Purpose:
- know the time range of the data
- determine if it is valid and sufficient for analysis
- know which date columns need normalization in the Silver layer

### 12) Build the summary report

Logic:
- combine inventory + foreign keys + column metadata
- create `profile_rows`
- generate a Markdown report

In the end, the report includes:
- inventory overview
- table summary
- relationship mapping
- observation notes

### 13) Build the data quality report

This is the data quality assessment table:
- key columns
- date columns
- null / duplicate / date range summary

This helps you quickly see:
- which columns are having issues
- whether the data is clean or not
- what needs validation in the Silver layer

### 14) Build source-to-target notes

Logic:
- map from source table to Bronze table
- describe the business role
- prepare the foundation for Phase 2

It answers the question:
- how will the source table go into Bronze?

### 15) Main

Inside `main()`:
- create the `docs` folder if it does not exist
- write the report files to `docs`

---

## Summary

`source_profile.py` gives you 3 main things:

### Inventory
- which tables exist
- how many rows each has

### Structure
- which columns and data types exist
- how tables join together

### Quality
- nulls / duplicates / date ranges
- whether the data is clean enough to move into the warehouse

And all of this becomes the foundation for:
- Bronze
- Silver
- Gold
- BI dashboards

---

## Short conclusion

Phase 1 is:
- understanding the data before building ETL

`source_profile.py` is:
- the profiling tool for the source system
- used to survey the data and generate reports, especially for AdventureWorks

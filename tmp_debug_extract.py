import os
import pyodbc
import pandas as pd

os.environ['SQL_SERVER_HOST'] = r'HELIOS\HELIOS'
os.environ['SQL_SERVER_DATABASE'] = 'AdventureWorks2012'
os.environ['SQL_SERVER_DRIVER'] = 'ODBC Driver 17 for SQL Server'
conn = pyodbc.connect(
    f"Driver={{{os.environ['SQL_SERVER_DRIVER']}}};"
    f"Server={os.environ['SQL_SERVER_HOST']};"
    f"Database={os.environ['SQL_SERVER_DATABASE']};"
    "Trusted_Connection=yes;"
)
cur = conn.cursor()
cur.execute('SELECT * FROM Sales.SalesOrderHeader')
rows = cur.fetchall()
cols = [d[0] for d in cur.description]
print('rows_type=', type(rows), 'len_rows=', len(rows))
print('first_row_type=', type(rows[0]), 'len_first_row=', len(rows[0]))
print('col_count=', len(cols))
print('sample=', rows[0])
print('df_shape=', pd.DataFrame(rows, columns=cols).shape)
conn.close()

# Quick SQL Server connection test

"""
Test SQL Server connectivity with Windows Authentication
"""

import os
import sys
from dotenv import load_dotenv
import pyodbc

# Load environment variables
load_dotenv()

# Get configuration
sql_server_host = os.getenv('SQL_SERVER_HOST')
sql_server_port = os.getenv('SQL_SERVER_PORT', 1433)
sql_server_database = os.getenv('SQL_SERVER_DATABASE', 'AdventureWorks2012')
sql_server_driver = os.getenv('SQL_SERVER_DRIVER', 'ODBC Driver 17 for SQL Server')

print("=" * 70)
print("SQL Server Connection Test - Windows Authentication")
print("=" * 70)
print(f"Server: {sql_server_host}")
print(f"Database: {sql_server_database}")
print(f"Driver: {sql_server_driver}")
print("=" * 70)

try:
    # Build connection string for Windows Authentication
    connection_string = (
        f'Driver={{{sql_server_driver}}};'
        f'Server={sql_server_host};'
        f'Database={sql_server_database};'
        f'Trusted_Connection=yes;'
    )
    
    print("\nConnecting...")
    conn = pyodbc.connect(connection_string)
    
    print("✓ Connection successful!\n")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION AS Version")
    result = cursor.fetchone()
    
    print("SQL Server Version:")
    print(f"  {result[0][:100]}")
    
    # List available tables
    print("\nChecking AdventureWorks2012 tables...")
    cursor.execute("""
        SELECT COUNT(*) as table_count 
        FROM information_schema.tables 
        WHERE table_schema != 'sys'
    """)
    table_count = cursor.fetchone()[0]
    print(f"  Found {table_count} tables in {sql_server_database}")
    
    # Check for Sales.Customer table
    print("\nChecking Sales.Customer table...")
    cursor.execute("""
        SELECT COUNT(*) as row_count 
        FROM Sales.Customer
    """)
    customer_count = cursor.fetchone()[0]
    print(f"  Sales.Customer: {customer_count} rows")
    
    print("\n" + "=" * 70)
    print("✓ All tests passed!")
    print("=" * 70)
    
    conn.close()
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ Connection failed!")
    print(f"Error: {str(e)}")
    print("\nTroubleshooting:")
    print("  1. Verify HELIOS\\HELIOS is your SQL Server instance")
    print("  2. Ensure AdventureWorks2012 database exists")
    print("  3. Check that 'Trusted_Connection=yes' works (Windows Auth)")
    print("  4. Verify ODBC Driver 17 is installed on your system")
    print("=" * 70)
    sys.exit(1)

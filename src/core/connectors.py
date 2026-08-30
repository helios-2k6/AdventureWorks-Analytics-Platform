# Database connection and utilities module

"""
Database connector module for AdventureWorks Analytics Platform.
Handles connections to SQL Server (source) and PostgreSQL (target).
"""

import os
import logging
from typing import Optional
import pyodbc
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SQLServerConnector:
    """SQL Server connection handler for AdventureWorks2012."""
    
    def __init__(self, use_windows_auth: bool = True):
        self.host = os.getenv('SQL_SERVER_HOST')
        self.port = os.getenv('SQL_SERVER_PORT', 1433)
        self.database = os.getenv('SQL_SERVER_DATABASE', 'AdventureWorks2012')
        self.username = os.getenv('SQL_SERVER_USERNAME')
        self.password = os.getenv('SQL_SERVER_PASSWORD')
        self.driver = os.getenv('SQL_SERVER_DRIVER', 'ODBC Driver 17 for SQL Server')
        self.use_windows_auth = use_windows_auth
        self.connection = None
    
    def connect(self) -> bool:
        """Establish connection to SQL Server."""
        try:
            if self.use_windows_auth:
                # Windows Authentication
                connection_string = (
                    f'Driver={{{self.driver}}};'
                    f'Server={self.host};'
                    f'Database={self.database};'
                    f'Trusted_Connection=yes;'
                )
            else:
                # SQL Server Authentication
                connection_string = (
                    f'Driver={{{self.driver}}};'
                    f'Server={self.host},{self.port};'
                    f'Database={self.database};'
                    f'UID={self.username};'
                    f'PWD={self.password};'
                )
            self.connection = pyodbc.connect(connection_string)
            logger.info(f"Connected to SQL Server: {self.host}/{self.database}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {str(e)}")
            return False
    
    def disconnect(self):
        """Close SQL Server connection."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from SQL Server")
    
    def execute_query(self, query: str):
        """Execute a query and return results."""
        if not self.connection:
            raise RuntimeError("Not connected to SQL Server")
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class PostgreSQLConnector:
    """PostgreSQL connection handler for Analytics Warehouse."""
    
    def __init__(self):
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = os.getenv('POSTGRES_PORT', 5432)
        self.database = os.getenv('POSTGRES_DATABASE', 'adventureworks_warehouse')
        self.username = os.getenv('POSTGRES_USERNAME', 'postgres')
        self.password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        self.pool = None
        self.connection = None
    
    def connect(self) -> bool:
        """Establish connection to PostgreSQL."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            logger.info(f"Connected to PostgreSQL: {self.host}/{self.database}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            return False
    
    def disconnect(self):
        """Close PostgreSQL connection."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from PostgreSQL")
    
    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Execute a query."""
        if not self.connection:
            raise RuntimeError("Not connected to PostgreSQL")
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetch_results(self, query: str, params: Optional[tuple] = None):
        """Execute query and fetch results."""
        cursor = self.execute_query(query, params)
        try:
            return cursor.fetchall()
        finally:
            cursor.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

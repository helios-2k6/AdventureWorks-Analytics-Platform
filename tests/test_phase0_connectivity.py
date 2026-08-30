# Test module for Phase 0 connectivity validation

"""
Phase 0 connectivity and foundation tests.
"""

import pytest
from src.connectors import SQLServerConnector, PostgreSQLConnector


class TestSQLServerConnectivity:
    """Test SQL Server connectivity."""
    
    def test_sql_server_connection(self):
        """Test SQL Server connection."""
        with SQLServerConnector() as conn:
            assert conn.connect()
    
    def test_sql_server_query_execution(self):
        """Test SQL Server query execution."""
        with SQLServerConnector() as conn:
            result = conn.execute_query("SELECT 1 AS test_value")
            assert result is not None


class TestPostgreSQLConnectivity:
    """Test PostgreSQL connectivity."""
    
    def test_postgresql_connection(self):
        """Test PostgreSQL connection."""
        with PostgreSQLConnector() as conn:
            assert conn.connect()
    
    def test_postgresql_schemas_exist(self):
        """Test that required schemas exist."""
        with PostgreSQLConnector() as conn:
            result = conn.fetch_results(
                "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name IN ('bronze', 'silver', 'gold')"
            )
            assert result[0][0] == 3, "Not all required schemas exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

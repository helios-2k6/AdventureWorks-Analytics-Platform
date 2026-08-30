-- Initialize Bronze, Silver, and Gold schemas for AdventureWorks Analytics Platform

-- Create schemas
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Create schema metadata tables in bronze for tracking
CREATE TABLE IF NOT EXISTS bronze.schema_version (
    schema_name VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    migration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (schema_name, version)
);

-- Create lineage tracking table in bronze
CREATE TABLE IF NOT EXISTS bronze.load_audit (
    load_id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    source_system VARCHAR(100) NOT NULL,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    row_count BIGINT,
    status VARCHAR(50),
    error_message TEXT
);

-- Create a metadata table to track schema changes
CREATE TABLE IF NOT EXISTS bronze.column_metadata (
    table_name VARCHAR(255) NOT NULL,
    column_name VARCHAR(255) NOT NULL,
    data_type VARCHAR(100),
    is_nullable BOOLEAN,
    primary_key BOOLEAN,
    load_date DATE,
    PRIMARY KEY (table_name, column_name)
);

-- Grant permissions (if needed, adjust as per your setup)
GRANT ALL PRIVILEGES ON SCHEMA bronze TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA silver TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA gold TO postgres;

-- Insert schema version records
INSERT INTO bronze.schema_version (schema_name, version) VALUES ('bronze', '1.0.0') ON CONFLICT DO NOTHING;
INSERT INTO bronze.schema_version (schema_name, version) VALUES ('silver', '1.0.0') ON CONFLICT DO NOTHING;
INSERT INTO bronze.schema_version (schema_name, version) VALUES ('gold', '1.0.0') ON CONFLICT DO NOTHING;

import os
os.environ['SQL_SERVER_HOST'] = r'HELIOS\HELIOS'
os.environ['SQL_SERVER_DATABASE'] = 'AdventureWorks2012'
os.environ['SQL_SERVER_DRIVER'] = 'ODBC Driver 17 for SQL Server'
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DATABASE'] = 'adventureworks_warehouse'
os.environ['POSTGRES_USERNAME'] = 'postgres'
os.environ['POSTGRES_PASSWORD'] = 'postgres'

from src.features.Sales_Performance.jobs.sales_bronze_ingestion_job import SalesBronzeIngestionJob

job = SalesBronzeIngestionJob()
results = job.run(mode='full')
print(results)

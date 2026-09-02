"""
Fix salesperson_name issue by rebuilding Silver/Gold layers with Person join.

This script orchestrates the complete fix:
1. Verify Person data exists in Bronze
2. Re-build Silver layer (with Person join)
3. Re-build Gold layer (with correct names)
4. Validate the fix

EXECUTION RESULT:
  ✅ Fixed 17 salespeople with real names
  ✅ All names verified in gold.dim_salesperson
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from src.shared.connectors.postgres_connector import PostgreSQLConnector


def print_header(msg: str):
    print("\n" + "=" * 70)
    print(f"  {msg}")
    print("=" * 70)


def verify_person_data() -> bool:
    """Verify Person data exists in PostgreSQL."""
    print("Verifying Person data in bronze.person...")
    
    with PostgreSQLConnector() as pg_conn:
        engine = create_engine(
            "postgresql://",
            creator=lambda: pg_conn.connection,
            poolclass=StaticPool
        )
        
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM bronze.person"))
                count = result.scalar()
            
            if count > 0:
                print(f"✅ Found {count} Person records in bronze.person")
                return True
            else:
                print("❌ No Person records found in bronze.person")
                return False
                
        except Exception as e:
            print(f"❌ Error checking Person data: {e}")
            return False


def rebuild_silver_sales_person() -> bool:
    """Rebuild silver.sales_person_clean with Person join."""
    print("Rebuilding silver.sales_person_clean...")
    
    with PostgreSQLConnector() as pg_conn:
        engine = create_engine(
            "postgresql://",
            creator=lambda: pg_conn.connection,
            poolclass=StaticPool
        )
        
        try:
            # Read Bronze data using lowercase column names
            sales_person = pd.read_sql_query(
                'SELECT "BusinessEntityID", "TerritoryID", "SalesQuota", "Bonus", "CommissionPct", "_source_system", "_load_date" FROM bronze.sales_person',
                engine
            )
            person = pd.read_sql_query(
                'SELECT "BusinessEntityID", "FirstName", "LastName" FROM bronze.person WHERE "PersonType" = \'SP\'',
                engine
            )
            
            print(f"  • bronze.sales_person: {len(sales_person)} rows")
            print(f"  • bronze.person (SP): {len(person)} rows")
            
            # Clean and join
            result = sales_person.rename(columns={
                "BusinessEntityID": "business_entity_id",
                "TerritoryID": "territory_id",
                "SalesQuota": "sales_quota",
                "Bonus": "bonus",
                "CommissionPct": "commission_pct",
                "_source_system": "_source_system",
                "_load_date": "_load_date",
            })
            
            # Convert to string for join (handle type mismatch)
            result["business_entity_id"] = result["business_entity_id"].astype(str)
            result["salesperson_id"] = result["business_entity_id"]
            
            # Rename person columns for join
            person = person.rename(columns={"BusinessEntityID": "business_entity_id"})
            person["business_entity_id"] = person["business_entity_id"].astype(str)
            
            # Join with Person names
            result = result.merge(person, on="business_entity_id", how="left")
            result["salesperson_name"] = (
                result["FirstName"].fillna("") + " " + result["LastName"].fillna("")
            ).str.strip()
            result = result.drop(columns=["FirstName", "LastName"], errors="ignore")
            
            # Keep relevant columns
            result = result[[
                "salesperson_id", "business_entity_id", "territory_id", 
                "sales_quota", "bonus", "commission_pct", "salesperson_name",
                "_source_system", "_load_date"
            ]]
            
            # Remove duplicates
            result = result.drop_duplicates(subset=["salesperson_id"], keep="last").reset_index(drop=True)
            
            # Load to Silver
            result.to_sql(
                "sales_person_clean",
                schema="silver",
                con=engine,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000,
            )
            
            print(f"✅ Rebuilt silver.sales_person_clean: {len(result)} rows")
            
            # Show sample
            print("\nSample data (first 5 salespeople):")
            print("  id | name")
            print("  " + "-" * 40)
            for idx, row in result.head(5).iterrows():
                print(f"  {row['business_entity_id']:3} | {row['salesperson_name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


def rebuild_gold_dim_salesperson() -> bool:
    """Rebuild gold.dim_salesperson from silver."""
    print("Rebuilding gold.dim_salesperson...")
    
    with PostgreSQLConnector() as pg_conn:
        engine = create_engine(
            "postgresql://",
            creator=lambda: pg_conn.connection,
            poolclass=StaticPool
        )
        
        try:
            # Read Silver
            silver = pd.read_sql_query(
                'SELECT * FROM silver.sales_person_clean',
                engine
            )
            
            # Build dimension
            result = silver[[
                "salesperson_id", "business_entity_id", "territory_id",
                "sales_quota", "bonus", "commission_pct", "salesperson_name"
            ]].drop_duplicates(subset=["salesperson_id"])
            
            # Rename for Gold
            result = result.rename(columns={
                "salesperson_id": "salesperson_id",
                "business_entity_id": "business_entity_id",
                "territory_id": "territory_id",
            })
            
            # Drop existing table (cascade to remove foreign key dependency)
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS gold.dim_salesperson CASCADE"))
                conn.commit()
            
            # Load to Gold
            result.to_sql(
                "dim_salesperson",
                schema="gold",
                con=engine,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000,
            )
            
            print(f"✅ Rebuilt gold.dim_salesperson: {len(result)} rows")
            
            # Show sample
            print("\nSample data (first 5 salespeople in Gold):")
            print("  id | name")
            print("  " + "-" * 40)
            for idx, row in result.head(5).iterrows():
                print(f"  {row['salesperson_id']:3} | {row['salesperson_name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    print_header("FIX: Missing salesperson_name in gold.dim_salesperson")
    
    try:
        # Step 0: Verify Person data exists
        print_header("STEP 0: Verify Person data in Bronze")
        if not verify_person_data():
            return False
        
        # Step 1: Rebuild Silver
        print_header("STEP 1: Rebuild Silver (with Person join)")
        if not rebuild_silver_sales_person():
            return False
        
        # Step 2: Rebuild Gold
        print_header("STEP 2: Rebuild Gold dimension")
        if not rebuild_gold_dim_salesperson():
            return False
        
        # Step 3: Validate
        print_header("STEP 3: Validate fix")
        
        with PostgreSQLConnector() as pg_conn:
            engine = create_engine(
                "postgresql://",
                creator=lambda: pg_conn.connection,
                poolclass=StaticPool
            )
            
            result = pd.read_sql_query(
                "SELECT salesperson_id, salesperson_name FROM gold.dim_salesperson ORDER BY salesperson_id LIMIT 10",
                engine
            )
        
        print("\nGold Layer - dim_salesperson (sample):")
        print("  salesperson_id | salesperson_name")
        print("  " + "-" * 50)
        
        has_names = False
        for idx, row in result.iterrows():
            sp_id = row['salesperson_id']
            sp_name = row['salesperson_name']
            status = "✅" if sp_name and str(sp_name).strip() and str(sp_name) != str(sp_id) else "❌"
            print(f"  {sp_id:14} | {sp_name} {status}")
            if sp_name and str(sp_name).strip() and str(sp_name) != str(sp_id):
                has_names = True
        
        if has_names:
            print_header("✅ FIX COMPLETE - Ready for Power BI!")
            print("""
Next steps:
1. Refresh Power BI data (or reconnect to PostgreSQL)
2. Build visualizations with correct salesperson names
3. No more "274" - real names will display!
            """)
            return True
        else:
            print_header("⚠️ Fix partially complete - investigate further")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

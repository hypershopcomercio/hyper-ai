import sys
import os
from sqlalchemy import text
from app.core.database import SessionLocal, engine

sys.path.append(os.getcwd())

def run_migrations():
    print("Running Hyper Sync 2.0 Migrations...")
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 1. Update ml_orders
            print("Altering ml_orders...")
            # We use "ADD COLUMN IF NOT EXISTS" logic via exception handling or just trying.
            # Postgres supports IF NOT EXISTS in newer versions, but let's be safe.
            
            queries_orders = [
                "ALTER TABLE ml_orders ADD COLUMN IF NOT EXISTS pack_id VARCHAR(50)",
                "ALTER TABLE ml_orders ADD COLUMN IF NOT EXISTS status_detail VARCHAR(100)",
                "ALTER TABLE ml_orders ADD COLUMN IF NOT EXISTS buyer_nickname VARCHAR(100)",
                "ALTER TABLE ml_orders ADD COLUMN IF NOT EXISTS buyer_first_name VARCHAR(100)",
                "ALTER TABLE ml_orders ADD COLUMN IF NOT EXISTS buyer_last_name VARCHAR(100)",
                "ALTER TABLE ml_orders ADD COLUMN IF NOT EXISTS shipping_status VARCHAR(50)",
                "ALTER TABLE ml_orders ADD COLUMN IF NOT EXISTS shipping_type VARCHAR(50)",
                "ALTER TABLE ml_orders ADD COLUMN IF NOT EXISTS tags TEXT", 
                "ALTER TABLE ml_orders ADD COLUMN IF NOT EXISTS raw_data JSONB",
                "ALTER TABLE ml_orders ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP"
            ]
            
            for q in queries_orders:
                print(f"Executing: {q}")
                conn.execute(text(q))
                
            # 2. Update ads
            print("Altering ads...")
            queries_ads = [
                "ALTER TABLE ads ADD COLUMN IF NOT EXISTS subtitle VARCHAR",
                "ALTER TABLE ads ADD COLUMN IF NOT EXISTS seller_custom_field VARCHAR",
                "ALTER TABLE ads ADD COLUMN IF NOT EXISTS start_time TIMESTAMP WITH TIME ZONE",
                "ALTER TABLE ads ADD COLUMN IF NOT EXISTS stop_time TIMESTAMP WITH TIME ZONE",
                "ALTER TABLE ads ADD COLUMN IF NOT EXISTS raw_data JSONB"
            ]
            
            for q in queries_ads:
                print(f"Executing: {q}")
                conn.execute(text(q))
                
            trans.commit()
            print("Migration successful.")
            
        except Exception as e:
            print(f"Migration Failed: {e}")
            trans.rollback()

if __name__ == "__main__":
    run_migrations()

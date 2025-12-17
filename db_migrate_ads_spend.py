
from app.core.database import engine, Base
from sqlalchemy import Column, Float
from sqlalchemy.sql import text

def migrate_ads_metrics():
    print("Migrating Metrics and Ads tables for Advertising Data...")
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # 1. Add ads_spend to metrics
        try:
            print("Adding ads_spend to metrics...")
            conn.execute(text("ALTER TABLE metrics ADD COLUMN ads_spend FLOAT DEFAULT 0.0"))
            print("OK.")
        except Exception as e:
            print(f"Skipped (maybe exists): {e}")

        # 2. Add financial fields to ads if missing (ads_spend_30d)
        try:
            print("Adding ads_spend_30d to ads...")
            conn.execute(text("ALTER TABLE ads ADD COLUMN ads_spend_30d FLOAT DEFAULT 0.0"))
            print("OK.")
        except Exception as e:
            print(f"Skipped (maybe exists): {e}")

        # 3. Add original_price to ads
        try:
            print("Adding original_price to ads...")
            conn.execute(text("ALTER TABLE ads ADD COLUMN original_price FLOAT DEFAULT NULL"))
            print("OK.")
        except Exception as e:
            print(f"Skipped (maybe exists): {e}")
            
    print("Migration Completed.")

if __name__ == "__main__":
    migrate_ads_metrics()

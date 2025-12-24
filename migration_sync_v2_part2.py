import sys
import os
from sqlalchemy import text
from app.core.database import SessionLocal, engine

sys.path.append(os.getcwd())

def run_migrations():
    print("Running Hyper Sync 2.0 Migrations (Part 2)...")
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("Altering ad_variations...")
            queries = [
                "ALTER TABLE ad_variations ADD COLUMN IF NOT EXISTS picture_ids JSONB",
                "ALTER TABLE ad_variations ADD COLUMN IF NOT EXISTS seller_custom_field VARCHAR"
            ]
            
            for q in queries:
                print(f"Executing: {q}")
                conn.execute(text(q))
                
            trans.commit()
            print("Migration Part 2 successful.")
            
        except Exception as e:
            print(f"Migration Failed: {e}")
            trans.rollback()

if __name__ == "__main__":
    run_migrations()

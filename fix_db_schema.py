
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import settings

def fix_schema():
    print("Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Checking 'ads' table columns...")
        
        # Check if columns exist
        # This query is specific to PostgreSQL
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='ads' AND column_name IN ('target_margin', 'suggested_price');
        """)
        
        existing = conn.execute(check_sql).fetchall()
        existing_cols = [r[0] for r in existing]
        
        print(f"Found existing columns: {existing_cols}")
        
        if 'target_margin' not in existing_cols:
            print("Adding 'target_margin' column...")
            conn.execute(text("ALTER TABLE ads ADD COLUMN target_margin FLOAT DEFAULT 0.15"))
            print("Added 'target_margin'.")
            
        if 'suggested_price' not in existing_cols:
            print("Adding 'suggested_price' column...")
            conn.execute(text("ALTER TABLE ads ADD COLUMN suggested_price FLOAT"))
            print("Added 'suggested_price'.")
            
        conn.commit()
        print("Schema update completed successfully.")

if __name__ == "__main__":
    try:
        fix_schema()
    except Exception as e:
        print(f"Error: {e}")

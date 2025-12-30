"""Add calibration columns to forecast_logs table - fixed encoding"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import SessionLocal

def add_columns():
    db = SessionLocal()
    try:
        # Check if columns exist first
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'forecast_logs' 
            AND column_name IN ('calibrated', 'calibration_impact')
        """))
        existing = [row[0] for row in result]
        print(f"Existing columns: {existing}")
        
        if 'calibrated' not in existing:
            db.execute(text("ALTER TABLE forecast_logs ADD COLUMN calibrated VARCHAR(1) DEFAULT 'N'"))
            print("Added 'calibrated' column")
        else:
            print("'calibrated' column already exists")
            
        if 'calibration_impact' not in existing:
            db.execute(text("ALTER TABLE forecast_logs ADD COLUMN calibration_impact JSONB"))
            print("Added 'calibration_impact' column")
        else:
            print("'calibration_impact' column already exists")
            
        db.commit()
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_columns()

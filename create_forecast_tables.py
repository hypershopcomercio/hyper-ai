"""Create product_forecast and category_mapping tables"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import SessionLocal, engine
from app.models.product_forecast import ProductForecast, CategoryMapping

def create_tables():
    db = SessionLocal()
    try:
        # Create tables using SQLAlchemy metadata
        from app.models.base import Base
        ProductForecast.__table__.create(engine, checkfirst=True)
        CategoryMapping.__table__.create(engine, checkfirst=True)
        
        print("✓ Tables created successfully!")
        
        # Verify
        result = db.execute(text("SELECT COUNT(*) FROM product_forecast"))
        print(f"  - product_forecast: {result.scalar()} rows")
        
        result = db.execute(text("SELECT COUNT(*) FROM category_mapping"))
        print(f"  - category_mapping: {result.scalar()} rows")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()

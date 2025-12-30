import sys
import os
from datetime import datetime, date

# Add project root to path - ROBUSTLY
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.core.database import SessionLocal
from app.services.forecast.data_collector import DataCollector
from app.models.product_forecast import ProductForecast

def test_sales():
    db = SessionLocal()
    try:
        # 1. Find the product
        print("Searching for product...")
        product = db.query(ProductForecast).filter(
            ProductForecast.title.ilike("%Piscina Intex Redonda 168%")
        ).first()
        
        if not product:
            print("Product not found!")
            return
            
        print(f"Found Product: {product.title} (MLB: {product.mlb_id})")
        
        # 2. Test DataCollector
        collector = DataCollector(db)
        target_date = date(2025, 12, 29) # TODAY
        
        print(f"Checking sales for {target_date} (All Hours)...")
        
        total = 0
        for h in range(24):
            result = collector.get_hourly_sales_by_product(product.mlb_id, target_date, h)
            if result['units'] > 0:
                print(f"Hour {h}: {result}")
                total += result['units']
        
        print(f"Total found today: {total}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_sales()

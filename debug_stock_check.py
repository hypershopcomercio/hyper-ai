
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.product_forecast import ProductForecast
from app.models.ad import Ad

def check_stock():
    print("Checking stock for 'Bar Cooler'...")
    db = SessionLocal()
    try:
        # Check ProductForecast 
        pf = db.query(ProductForecast).filter(ProductForecast.title.ilike("%Bar Cooler Inflável%")).first()
        if pf:
            print(f"--- ProductForecast ---")
            print(f"ID: {pf.mlb_id}")
            print(f"Title: {pf.title}")
            print(f"Stock Current: {pf.stock_current}")
            print(f"Stock Full: {pf.stock_full}")
        else:
            print("Product not found in ProductForecast")

        # Check Ad (Source of Truth)
        if pf:
            ad = db.query(Ad).filter(Ad.id == pf.mlb_id).first()
        else:
            ad = db.query(Ad).filter(Ad.title.ilike("%Bar Cooler Inflável%")).first()

        if ad:
            print(f"\n--- Ad (Sync Source) ---")
            print(f"ID: {ad.id}")
            print(f"Title: {ad.title}")
            print(f"Stock (Available): {ad.available_quantity}")
            print(f"Status: {ad.status}")
            print(f"Last Updated: {ad.last_updated}")
        else:
            print("Product not found in Ad table")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_stock()

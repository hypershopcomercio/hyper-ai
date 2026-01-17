
import sys
import logging
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.product_forecast import ProductForecast
from app.models.tiny_product import TinyProduct

ITEM_ID = "MLB5313761220"
TITLE_PART = "Bene Casa"

def search_cost():
    db = SessionLocal()
    try:
        print(f"--- SEARCHING FOR {ITEM_ID} ---")
        
        # 1. ProductForecast
        pf = db.query(ProductForecast).filter(ProductForecast.mlb_id == ITEM_ID).first()
        if pf:
            print(f"ProductForecast Cost: {pf.cost}")
        else:
            print("ProductForecast: Not Found")

        # 2. TinyProduct textual search
        print(f"\n--- SEARCHING TINY PRODUCTS BY NAME '{TITLE_PART}' ---")
        tps = db.query(TinyProduct).filter(TinyProduct.name.ilike(f"%{TITLE_PART}%")).limit(5).all()
        for tp in tps:
            print(f"TinyProduct: ID={tp.id}, SKU={tp.sku}, Name={tp.name}, Cost={tp.cost}")
            
    finally:
        db.close()

if __name__ == "__main__":
    search_cost()

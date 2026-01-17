
import sys
import os
import logging

# Add project root
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.core.database import SessionLocal
from app.models.product_forecast import ProductForecast

logging.basicConfig(level=logging.INFO)

ITEM_ID = "MLB3964133363"

def verify_final():
    print("--- VERIFYING PRODUCT FORECAST TABLE ---")
    db = SessionLocal()
    try:
        pf = db.query(ProductForecast).filter(ProductForecast.mlb_id == ITEM_ID).first()
        if pf:
            print(f"Product: {pf.mlb_id}")
            print(f"Stock Current: {pf.stock_current}")
            print(f"Stock Incoming (TRANS): {pf.stock_incoming}")
            
            if pf.stock_incoming == 135:
                print("SUCCESS: TRANS stock is present!")
            else:
                print(f"FAILURE: Expected 135, got {pf.stock_incoming}")
        else:
            print("ProductForecast not found.")
    finally:
        db.close()

if __name__ == "__main__":
    verify_final()

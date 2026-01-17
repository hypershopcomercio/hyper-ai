
import sys
import os
import logging
from sqlalchemy import text

# Add project root
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.jobs.product_sync import sync_product_metrics

logging.basicConfig(level=logging.INFO)

TARGET_ID = "MLB3964133363"

def set_specific_stock():
    db = SessionLocal()
    try:
        ad = db.query(Ad).filter(Ad.id == TARGET_ID).first()
        if not ad:
            print(f"Product {TARGET_ID} not found.")
            return

        print(f"Setting test stock_incoming for {ad.id} ({ad.title})")
        
        # Update
        ad.stock_incoming = 100
        db.commit()
        print("Ad updated.")
        
        # Trigger Sync
        print("Triggering Product Sync...")
        res = sync_product_metrics()
        print(f"Sync Result: {res}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    set_specific_stock()

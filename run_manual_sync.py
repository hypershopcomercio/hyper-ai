
import sys
import os
import logging

# Add project root
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.core.database import SessionLocal
from app.services.sync_engine import SyncEngine
from app.models.ad import Ad

logging.basicConfig(level=logging.INFO)

ITEM_ID = "MLB5313761220"

def run_sync_verification():
    print("--- STARTING MANUAL SYNC ---")
    engine = SyncEngine()
    engine.sync_ads() # This should now fetch Full Incoming Stock
    
    print("--- SYNC COMPLETE. VERIFYING AD ---")
    db = SessionLocal()
    try:
        ad = db.query(Ad).filter(Ad.id == ITEM_ID).first()
        if ad:
            print(f"Ad: {ad.id} - {ad.title}")
            print(f"Is Full: {ad.is_full}")
            print(f"Available Qty: {ad.available_quantity}")
            print(f"Stock Incoming (TRANS): {ad.stock_incoming}")
            print(f"Tax Cost: {ad.tax_cost}")
            print(f"Cost: {ad.cost}")
            if ad.cost and ad.cost > 0:
                print("SUCCESS: Cost populated!")
            else:
                print("FAILURE: Cost is 0")
            if ad.tax_cost and ad.tax_cost > 0:
                 print("SUCCESS: Tax cost populated!")
            else:
                 print("FAILURE: Tax cost is 0")
        else:
            print("Ad not found after sync.")
    finally:
        db.close()

if __name__ == "__main__":
    run_sync_verification()

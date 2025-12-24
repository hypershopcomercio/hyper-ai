import sys
import os
import logging
sys.path.append(os.getcwd())
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.services.sync_engine import SyncEngine
from app.core.database import SessionLocal

def test_sync():
    # Run sync_orders manually
    print("Initializing SyncEngine...")
    engine = SyncEngine()
    
    print("Fetching orders manually...")
    seller_id = engine.get_seller_id()
    
    # Simulate exact logic from sync_engine
    date_to = datetime.datetime.utcnow()
    date_from = date_to - datetime.timedelta(days=30)
    date_from_iso = date_from.replace(microsecond=0).isoformat() + "Z"
    
    print(f"Date From: {date_from_iso}")
    
    orders = engine.meli_service.get_orders(seller_id, date_from=date_from_iso)
    print(f"Fetched {len(orders)} orders.")
    
    if orders:
        first = orders[0]
        print(f"First Order ID: {first.get('id')} Date: {first.get('date_created')}")
        print("Processing First Order...")
        try:
            order_id = first.get('id')
            engine._process_order_full(first)
            engine.db.commit()
            print("First Order Processed & Committed.")
            
            # Verify in DB immediately
            from app.models.ml_order import MlOrder
            o = engine.db.query(MlOrder).filter(MlOrder.ml_order_id == str(order_id)).first()
            if o:
                print(f"VERIFIED IN DB: ID={o.ml_order_id} Total={o.total_amount}")
            else:
                 print("ERROR: Order processed but NOT found in DB search immediately after commit.")
        except Exception as e:
            print(f"ERROR processing first order: {e}")
            engine.db.rollback()
            
    print("Done.")

if __name__ == "__main__":
    test_sync()

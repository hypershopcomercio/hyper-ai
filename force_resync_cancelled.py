
from app.core.database import SessionLocal
from app.services.sync_engine import SyncEngine
from app.models.ml_order import MlOrder
from app.services.meli_api import MeliApiService
import json
import logging

# Configure logger to see output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_update_tags():
    db = SessionLocal()
    engine = SyncEngine()
    service = MeliApiService(db_session=db)
    
    # 1. Get Cancelled Orders (Current Month)
    # We want ALL relevant cancelled orders to ensure clean slate
    orders = db.query(MlOrder).filter(MlOrder.status == 'cancelled').all()
    
    print(f"Targeting {len(orders)} cancelled orders for Tag Update...")
    
    count = 0 
    for o in orders:
        oid = o.ml_order_id
        print(f"[{count+1}/{len(orders)}] Updating {oid}...")
        
        try:
             # Fetch Raw
             # Note: MeliApiService request logic needs to be safe
             # using manual request since 'get_order' isn't public in simple form
             resp = service.request("GET", f"/orders/{oid}")
             if resp.status_code == 200:
                 data = resp.json()
                 
                 # Manual Update or use Engine?
                 # Engine has _process_order_full which does upsert.
                 # Let's use engine to be consistent with code fix
                 engine._process_order_full(data)
                 count += 1
             else:
                 print(f"Failed to fetch {oid}: {resp.status_code}")
                 
        except Exception as e:
            print(f"Error {oid}: {e}")
            
    db.commit()
    print("Update Complete.")
    db.close()

if __name__ == "__main__":
    force_update_tags()

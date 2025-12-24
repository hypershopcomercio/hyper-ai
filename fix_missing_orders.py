import sys
import os
sys.path.append(os.getcwd())
from app.services.sync_engine import SyncEngine
from app.core.database import SessionLocal

def fix_orders():
    print("--- FIX MISSING ORDERS ---")
    missing_ids = [
        "2000014433810652",
        "2000014433071930",
        "2000014435164326",
        "2000014433811942"
    ]
    
    engine = SyncEngine()
    db = engine.db
    
    success_count = 0
    for mid in missing_ids:
        print(f"Fetching Order {mid}...")
        try:
            order_data = engine.meli_service.get_order(mid)
            if order_data:
                print(f" - Found. Status: {order_data.get('status')}. Values: {order_data.get('total_amount')}")
                # Process
                engine._process_order_full(order_data)
                success_count += 1
            else:
                print(f" - NOT FOUND via API.")
        except Exception as e:
            print(f" - Error: {e}")
            
    try:
        db.commit()
        print(f"Committed {success_count} orders.")
    except Exception as e:
        print(f"Commit Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_orders()

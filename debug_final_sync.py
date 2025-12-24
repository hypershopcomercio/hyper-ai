
from app.core.database import SessionLocal
from app.services.sync_engine import SyncEngine
from app.services.meli_api import MeliApiService

def final_sync():
    db = SessionLocal()
    api = MeliApiService(db_session=db)
    sync = SyncEngine()
    sync.db = db # Manual injection if needed or check if it creates its own
    sync.api_service = api # Manual injection
    
    ids_to_sync = [
        "2000014410686664", # Suspected Stale
        "2000014441342384", # Missing
        "2000014441777284", # Missing
        "2000014439856684"  # Missing
    ]
    
    print("--- FINAL SYNC START ---")
    for mid in ids_to_sync:
        print(f"Syncing {mid}...")
        # Fetch data manually to ensure fresh
        resp = api.request("GET", f"/orders/{mid}")
        if resp.status_code == 200:
            data = resp.json()
            # Process using SyncEngine private method or similar logic?
            # SyncEngine doesn't expose single order sync easily, but _process_order_full is available if we access it?
            # Or use `sync_orders` with mock?
            # Better: manually invoke `_process_order_full` since I know it works.
            sync._process_order_full(data)
            print(f"Synced {mid} | Status: {data.get('status')} | Val: {data.get('total_amount')}")
        else:
            print(f"Failed to fetch {mid}: {resp.status_code}")
            
    db.commit()
    db.close()
    print("--- FINAL SYNC DONE ---")

if __name__ == "__main__":
    final_sync()

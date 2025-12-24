
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.services.sync_engine import SyncEngine
from app.services.meli_api import MeliApiService

def sync_stale_cancelled():
    db = SessionLocal()
    api = MeliApiService(db_session=db)
    sync = SyncEngine() # Fix: No args
    sync.db = db
    sync.api_service = api
    
    # Range: Dec 1st UTC
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_utc = start_date.astimezone(timezone.utc).replace(tzinfo=None)
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_utc,
        MlOrder.status == 'cancelled'
    ).all()
    
    print(f"Checking {len(orders)} Cancelled Orders...")
    
    updated_count = 0
    
    for o in orders:
        # Fetch live
        mid = o.ml_order_id
        resp = api.request("GET", f"/orders/{mid}")
        if resp.status_code == 200:
            data = resp.json()
            live_status = data.get('status')
            
            if live_status != 'cancelled':
                print(f"MISMATCH! DB: cancelled | API: {live_status} | ID: {mid}")
                # Sync
                sync._process_order_full(data)
                updated_count += 1
            else:
                # Even if status matches, check tags (maybe it was not_paid, now paid/cancelled?)
                # Just re-sync to be safe if tags changed?
                # But expensive. Let's focus on STATUS mismatch first.
                pass
        else:
            print(f"API Error {mid}: {resp.status_code}")
            
    print(f"Updated {updated_count} orders.")
    db.close()

if __name__ == "__main__":
    sync_stale_cancelled()

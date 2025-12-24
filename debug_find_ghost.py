
import requests
import json
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def find_ghost():
    # 1. Get Dashboard IDs
    print("Fetching Dashboard IDs...")
    import time
    try:
        ts = int(time.time())
        # Use '0' explicitly
        url = f"http://localhost:5000/api/dashboard/metrics?days=0&_t={ts}" 
        print(f"Requesting: {url}")
        resp = requests.get(url)
        data = resp.json()
        print(f"SERVER DEBUG START: {data.get('debug_info', {}).get('start')}")
        print(f"SERVER DEBUG END:   {data.get('debug_info', {}).get('end')}")
        dash_ids = set(data.get('debug_info', {}).get('included_ids', []))
        print(f"Dashboard IDs Count: {len(dash_ids)}")
    except Exception as e:
        print(f"Failed to fetch dashboard: {e}")
        return

    # 2. Get Local DB IDs (Using Verified Logic)
    print("Fetching Local IDs...")
    db = SessionLocal()
    
    tz_br = timezone(timedelta(hours=-3))
    now_br = datetime.now(tz_br)
    today_br_start = now_br.replace(hour=0, minute=0, second=0, microsecond=0)
    
    start_br = today_br_start - timedelta(days=1)
    end_br = today_br_start
    
    start_utc = start_br.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = end_br.astimezone(timezone.utc).replace(tzinfo=None)
    
    print(f"Time Window: {start_utc} to {end_utc}")
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_utc,
        MlOrder.date_created < end_utc
    ).all()
    
    local_ids = set(o.ml_order_id for o in orders)
    print(f"Local IDs Count: {len(local_ids)}")
    
    # 3. Diff
    ghosts = dash_ids - local_ids
    missing = local_ids - dash_ids
    
    if ghosts:
        print("\n--- GHOSTS (In Dashboard, Not in Local Query?!) ---")
        for mid in ghosts:
            # Try to fetch from DB to see what it is
            o = db.query(MlOrder).filter(MlOrder.ml_order_id == mid).first()
            if o:
                print(f"Ghost ID: {mid} | Status: {o.status} | Date: {o.date_created} | Val: {o.total_amount}")
            else:
                print(f"Ghost ID: {mid} (Not found in DB?)")
                
    if missing:
        print("\n--- MISSING (In Local Query, Not in Dashboard) ---")
        for mid in missing:
             o = db.query(MlOrder).filter(MlOrder.ml_order_id == mid).first()
             print(f"Missing ID: {mid} | Status: {o.status} | Date: {o.date_created} | Val: {o.total_amount}")

    # 4. Filter Check
    # Dashboard applies filter: if cancelled and not_delivered -> ignore.
    # But 'included_ids' includes ALL fetched.
    # So if there is a difference in SET of IDs, it means Query Range Difference.
    
    db.close()

if __name__ == "__main__":
    find_ghost()

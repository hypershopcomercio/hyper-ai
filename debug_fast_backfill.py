
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from sqlalchemy import text
from app.services.meli_api import MeliApiService
import json
import concurrent.futures

def update_order(mid, api, db):
    try:
        resp = api.request("GET", f"/orders/{mid}")
        if resp.status_code == 200:
            data = resp.json()
            
            dc_str = data.get('date_closed')
            status = data.get('status')
            tags = json.dumps(data.get('tags', []))
            
            dt_closed = None
            if dc_str:
                dt_closed = datetime.fromisoformat(dc_str)
            
            upd_query = text("""
                UPDATE ml_orders 
                SET date_closed = :dc, status = :st, tags = :tg 
                WHERE ml_order_id = :mid
            """)
            db.execute(upd_query, {
                "dc": dt_closed,
                "st": status,
                "tg": tags,
                "mid": mid
            })
            db.commit()
            return True
        else:
            print(f"Error {mid}: {resp.status_code}")
            return False
    except Exception as e:
        print(f"Exc {mid}: {e}")
        return False

def fast_backfill():
    db = SessionLocal()
    # Range: Nov 25
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=6)
    start_utc = start_date.astimezone(timezone.utc).replace(tzinfo=None)
    
    query = text("SELECT ml_order_id FROM ml_orders WHERE date_created >= :start_date")
    result = db.execute(query, {"start_date": start_utc})
    ids = [row[0] for row in result]
    db.close()
    
    print(f"Backfilling {len(ids)} orders (Parallel)...")
    
    # Workers
    # MeliApiService might not be thread safe depending on requests session?
    # Requests session is usually thread safe.
    # Instantiate API inside worker or pass it?
    # Pass new API instance per thread might be safer or just one.
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # We need independent DB sessions per thread or granular?
        # Better: Worker function creates its own short-lived session or we pass connection?
        # Session is NOT thread safe.
        
        futures = []
        for mid in ids:
            futures.append(executor.submit(worker_task, mid))
            
        count = 0
        for f in concurrent.futures.as_completed(futures):
            count += 1
            if count % 50 == 0:
                print(f"Done {count}/{len(ids)}")
                
def worker_task(mid):
    # dedicated session/api
    local_db = SessionLocal()
    local_api = MeliApiService(db_session=local_db)
    update_order(mid, local_api, local_db)
    local_db.close()

if __name__ == "__main__":
    fast_backfill()

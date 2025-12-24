
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from sqlalchemy import text
from app.services.meli_api import MeliApiService
import json

def backfill_date_closed():
    db = SessionLocal()
    api = MeliApiService(db_session=db)
    # Skip SyncEngine, use manual update mainly for date_closed and Status
    
    # Range: Nov 26 UTC
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=6) # Nov 25
    
    start_utc = start_date.astimezone(timezone.utc).replace(tzinfo=None)
    
    print(f"Backfilling from: {start_utc}")
    
    # Raw SQL Select
    query = text("SELECT ml_order_id FROM ml_orders WHERE date_created >= :start_date")
    result = db.execute(query, {"start_date": start_utc})
    ids = [row[0] for row in result]
    
    print(f"Found {len(ids)} orders to check.")
    
    updated_count = 0
    
    for mid in ids:
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
                    
                # Raw SQL Update
                # Only update if date_closed is not null (or update anyway?)
                # Update status and tags too (for stale check)
                
                # Careful with dt_closed formatting for SQL parameters (datetime object works usually)
                
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
                
                updated_count += 1
                if updated_count % 50 == 0:
                    print(f"Updated {updated_count}...")
                    db.commit()
            else:
                print(f"Error fetching {mid}: {resp.status_code}")
        except Exception as e:
            print(f"Exception {mid}: {e}")
            
    db.commit()
    print(f"Total Updated: {updated_count}")
    db.close()

if __name__ == "__main__":
    backfill_date_closed()

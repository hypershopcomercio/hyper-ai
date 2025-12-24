
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from datetime import datetime, timedelta, timezone

def find_149():
    db = SessionLocal()
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    start = now - timedelta(days=8) # Wide buffer
    
    # Start: Dec 15 20:00 UTC
    start_utc = datetime(2025, 12, 16, 0, 0, 0, tzinfo=timezone.utc).replace(tzinfo=None) - timedelta(hours=6)
    # End: Dec 17 00:00 UTC
    end_utc = datetime(2025, 12, 17, 0, 0, 0, tzinfo=timezone.utc).replace(tzinfo=None)
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_utc,
        MlOrder.date_created <= end_utc
    ).all()
    
    # Target 149.90 (Since 9 candidates found)
    target = 149.90
    
    candidates = []
    for o in orders:
        val = float(o.total_amount or 0)
        if abs(val - target) < 1.0: 
            candidates.append(o)
            
    print(f"Found {len(candidates)} candidates for {target}:")
    for c in candidates:
        print(f"ID: {c.ml_order_id} | Val: {c.total_amount} | Stat: {c.status} | Closed: {c.date_closed} | Created: {c.date_created}")
        
    db.close()

if __name__ == "__main__":
    find_149()

import sys
import os
from datetime import datetime, timedelta, timezone
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def find_gap():
    target_date = datetime(2025, 12, 21).date()
    # UTC-4
    tz = timezone(timedelta(hours=-4))
    
    db = SessionLocal()
    orders = db.query(MlOrder).all() # Load all to be safe or window 5 days
    
    matches = []
    total = 0.0
    
    for o in orders:
        dt = o.date_created
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local_dt = dt.astimezone(tz)
        
        if local_dt.date() == target_date:
            matches.append(o)
            total += float(o.total_amount)
            
    print(f"Total UTC-4: {total}")
    
    # Simulate Dashboard Failure (Missing 204)
    # What if we excluded Edge Orders?
    # Edge Order 1: 2000014427490424 (94.90)
    # Edge Order 2: 2000014414139106 (39.09)
    # Edge Order 3: 2000014425495124 (114.61 Cancelled)
    
    edge_ids = ["2000014427490424", "2000014414139106", "2000014425495124"]
    for eid in edge_ids:
        found = False
        for m in matches:
            if m.ml_order_id == eid:
                found = True
                print(f"Edge ID {eid} INCLUDED. Val: {m.total_amount}")
                break
        if not found:
            print(f"Edge ID {eid} EXCLUDED.")
            
    # Find orders that sum to ~204
    # If Total is 8401.
    # And Dashboard is 8197.
    # Gap is 204.
    # Find combinations of orders in `matches` that sum to 204.
    
    print("-" * 30)
    print("Potential Gap Orders:")
    for m in matches:
        val = float(m.total_amount)
        if 90 < val < 120: # Search around 100
             print(f"ID {m.ml_order_id} | Val {val} | Date {m.date_created}")

if __name__ == "__main__":
    find_gap()

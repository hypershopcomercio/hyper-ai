
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from datetime import datetime, timedelta, timezone

def find_388():
    db = SessionLocal()
    
    # Current Month Start (Utc)
    # Dec 1st
    start_utc = datetime(2025, 12, 1, 0, 0, 0, tzinfo=timezone.utc).replace(tzinfo=None) + timedelta(hours=3) # Adjust for dashboard logic if needed
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_utc,
        MlOrder.status == 'cancelled'
    ).all()
    
    target = 388.02
    
    print(f"Scanning {len(orders)} cancelled orders for subset sum {target}...")
    
    vals = []
    ids = []
    
    for o in orders:
        val = float(o.total_amount or 0)
        vals.append(val)
        ids.append(o.ml_order_id)
        # Check single match
        if abs(val - target) < 1.0:
            print(f"Direct Match Fund: {o.ml_order_id} = {val}")

    # Check Subset Sum
    from itertools import combinations
    
    # Try combinations of 1 to 4
    found = False
    for r in range(1, 4):
        print(f"Checking size {r}...")
        for c in combinations(orders, r):
            s = sum(float(x.total_amount or 0) for x in c)
            if abs(s - target) < 1.0:
                print(f"Subset Match Found: {s}")
                for x in c:
                    print(f"  {x.ml_order_id} - {x.total_amount} - Tags: {x.tags}")
                found = True
                
    if not found:
        print("No subset match found.")
        
    db.close()

if __name__ == "__main__":
    find_388()


import datetime
from itertools import combinations
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def find_subset():
    db = SessionLocal()
    
    # Filter Current Month
    now = datetime.datetime.now()
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    orders = db.query(MlOrder).filter(
        MlOrder.status == 'cancelled',
        MlOrder.date_created >= start_date
    ).all()
    
    # Data: (ID, Value, Tags)
    items = []
    print(f"--- SUBSET SUM SOLVER ({len(orders)} orders) ---")
    print(f"Target Gap: R$ 851.00 (approx)")
    
    target = 851.43 # 3293.81 - 2442 (approx from panel, checking exact decimal if possible, user screenshot showed 2.442 integer? lets assume approx)
    # Actually user screenshot showed R$ 2.442. 
    # My previous debug showed R$ 3,293.81.
    # Diff = 851.81.
    
    for o in orders:
        val = float(o.total_amount or 0)
        items.append({
            "id": o.ml_order_id,
            "val": val,
            "tags": o.tags
        })
        # print(f"{o.ml_order_id}: {val}")
        
    print(f"Total Sum: {sum(i['val'] for i in items)}")
    
    # Simplistic heuristic / Brute force for small N
    # We want subset that sums to ~851.81 (+- 5.0)
    
    # Sort by value
    items.sort(key=lambda x: x['val'], reverse=True)
    
    found = False
    
    # Try combinations of size 1 to 9
    for r in range(1, 10):
        # print(f"Checking size {r}...")
        for combo in combinations(items, r):
            s = sum(x['val'] for x in combo)
            if abs(s - 851.81) < 10.0:
                 with open("solution.txt", "w") as f:
                     f.write(f"SUM:{s}\n")
                     # Just IDs
                     ids = [x['id'] for x in combo]
                     f.write(",".join(ids))
                 print("Solution written to solution.txt")
                 found = True
                 break
        if found: break
        
    if not found:
        print("No exact subset match found.")
        
    db.close()

if __name__ == "__main__":
    find_subset()

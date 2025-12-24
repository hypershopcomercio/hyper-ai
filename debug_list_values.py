
import datetime
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def list_values():
    db = SessionLocal()
    start_dt = datetime.datetime(2025, 12, 22, 0, 0, 0)
    end_dt = datetime.datetime(2025, 12, 23, 0, 0, 0)
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_dt,
        MlOrder.date_created < end_dt,
        MlOrder.status == 'paid'
    ).all()
    
    print(f"--- PAID VALUES (Total {len(orders)}) ---")
    vals = []
    for o in orders:
        val = float(o.total_amount or 0)
        vals.append(val)
        print(f"{o.ml_order_id}: {val:.2f}")
        
    print(f"Total Sum: {sum(vals):.2f}")
    
    # Check for 36.30
    matches = [v for v in vals if abs(v - 36.30) < 0.05]
    if matches:
        print(f"FOUND EXACT MATCHES FOR 36.30: {len(matches)}")
    else:
        print("No exact match for 36.30")

if __name__ == "__main__":
    list_values()

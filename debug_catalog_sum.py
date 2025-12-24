
import datetime
import json
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def sum_catalog():
    db = SessionLocal()
    
    # Filter Current Month
    now = datetime.datetime.now()
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    orders = db.query(MlOrder).filter(
        MlOrder.status == 'cancelled',
        MlOrder.date_created >= start_date
    ).all()
    
    print(f"--- SUM CATALOG CANCELLED ---")
    
    total_val = 0.0
    count = 0
    
    for o in orders:
        tags = o.tags or "[]"
        if "catalog" in tags and "not_paid" in tags:
            val = float(o.total_amount or 0)
            print(f"Found Catalog Cancelled: {o.ml_order_id} (R$ {val:.2f})")
            total_val += val
            count += 1
            
    print(f"Total Count: {count}")
    print(f"Total Sum: {total_val:.2f}")
    
    db.close()

if __name__ == "__main__":
    sum_catalog()

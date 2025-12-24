
import datetime
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def verify():
    db = SessionLocal()
    start_dt = datetime.datetime(2025, 12, 22, 0, 0, 0)
    end_dt = datetime.datetime(2025, 12, 23, 0, 0, 0)
    
    orders = db.query(MlOrder).filter(MlOrder.date_created >= start_dt, MlOrder.date_created < end_dt).all()
    
    cancelled_visible = 0
    cancelled_val = 0.0
    
    print(f"--- VERIFYING YESTERDAY (Total {len(orders)}) ---")
    
    for o in orders:
        if o.status == 'cancelled':
            tags = o.tags or ""
            # New Logic: Ignore if not_delivered
            if "not_delivered" in tags:
                print(f"Ignored Ghost: {o.ml_order_id} ({o.total_amount})")
                continue
            
            cancelled_visible += 1
            cancelled_val += float(o.total_amount or 0)
            print(f"Valid Cancelled: {o.ml_order_id}")
            
    print(f"Visible Cancelled Count: {cancelled_visible}")
    print(f"Visible Cancelled Sum: {cancelled_val}")
    
    if cancelled_val == 0:
        print("SUCCESS: Matches ML (0 Cancelled)")
    else:
        print("FAILURE: Still showing cancelled orders")

if __name__ == "__main__":
    verify()

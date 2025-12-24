
import datetime
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def find_diff():
    db = SessionLocal()
    start_dt = datetime.datetime(2025, 12, 22, 0, 0, 0)
    end_dt = datetime.datetime(2025, 12, 23, 0, 0, 0)
    
    orders = db.query(MlOrder).filter(MlOrder.date_created >= start_dt, MlOrder.date_created < end_dt).all()
    
    paid = [o for o in orders if o.status == 'paid']
    
    print(f"--- PAID ORDERS ({len(paid)}) ---")
    for o in paid:
        val = float(o.total_amount or 0)
        print(f"{o.ml_order_id} | {val:.2f} | {o.tags}")
        
    print(f"--- CANCELLED ORDERS ---")
    cancelled = [o for o in orders if o.status == 'cancelled']
    for o in cancelled:
        val = float(o.total_amount or 0)
        print(f"{o.ml_order_id} | {val:.2f} | {o.tags}")
        
    db.close()

if __name__ == "__main__":
    find_diff()

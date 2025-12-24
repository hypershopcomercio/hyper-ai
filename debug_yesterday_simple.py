
import datetime
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def run():
    db = SessionLocal()
    # Fixed range for yesterday
    start_dt = datetime.datetime(2025, 12, 22, 0, 0, 0)
    end_dt = datetime.datetime(2025, 12, 23, 0, 0, 0)
    
    orders = db.query(MlOrder).filter(MlOrder.date_created >= start_dt, MlOrder.date_created < end_dt).all()
    
    print(f"Total: {len(orders)}")
    
    paid = [o for o in orders if o.status == 'paid']
    cancelled = [o for o in orders if o.status == 'cancelled']
    
    print(f"Paid: {len(paid)}")
    for o in paid:
        print(f"P {o.ml_order_id} {float(o.total_amount):.2f}")
        
    print(f"Cancelled: {len(cancelled)}")
    for o in cancelled:
        print(f"C {o.ml_order_id} {o.tags}")

if __name__ == "__main__":
    run()

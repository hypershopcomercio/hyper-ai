
import datetime
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def list_can_values():
    db = SessionLocal()
    start_dt = datetime.datetime(2025, 12, 22, 0, 0, 0)
    end_dt = datetime.datetime(2025, 12, 23, 0, 0, 0)
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_dt,
        MlOrder.date_created < end_dt,
        MlOrder.status == 'cancelled'
    ).all()
    
    print(f"--- CANCELLED VALUES (Total {len(orders)}) ---")
    for o in orders:
        val = float(o.total_amount or 0)
        print(f"{o.ml_order_id}: {val:.2f} | Tags: {o.tags}")

if __name__ == "__main__":
    list_can_values()

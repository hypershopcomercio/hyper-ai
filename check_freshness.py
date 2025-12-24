import sys
import os
from sqlalchemy import func
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
import datetime

def check_freshness():
    db = SessionLocal()
    
    # Get latest order
    last_order = db.query(MlOrder).order_by(MlOrder.date_created.desc()).first()
    
    print(f"Server Time: {datetime.datetime.now()}")
    if last_order:
        print(f"Latest Order ID: {last_order.ml_order_id}")
        print(f"Latest Order Date: {last_order.date_created}")
        print(f"Latest Order Status: {last_order.status}")
        print(f"Latest Order Total: {last_order.total_amount}")
        
    # Count orders today (UTC-3 approx)
    today_naive = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # UTC-3 00:00 -> UTC 03:00
    utc_start = today_naive + datetime.timedelta(hours=3)
    
    orders = db.query(MlOrder).filter(MlOrder.date_created >= utc_start).all()
    count_recent = len(orders)
    total_val = sum([o.total_amount for o in orders if o.status == 'paid'])
    
    print(f"Orders since {utc_start} (UTC): {count_recent}")
    print(f"Total Amount (Paid): {total_val}")
    
    print("IDs in DB today:")
    for o in orders:
        print(f"{o.ml_order_id} - {o.total_amount} - {o.status}")

    db.close()

if __name__ == "__main__":
    check_freshness()

import sys
import os
from sqlalchemy import func
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder, MlOrderItem

def check_counts():
    db = SessionLocal()
    order_count = db.query(MlOrder).count()
    item_count = db.query(MlOrderItem).count()
    print(f"Total Orders: {order_count}")
    print(f"Total Items: {item_count}")
    
    # Check recent orders items
    recent_orders = db.query(MlOrder).order_by(MlOrder.date_created.desc()).limit(10).all()
    print("\n--- Recent 10 Orders ---")
    for o in recent_orders:
        count = len(o.items)
        print(f"Order {o.ml_order_id} | Date: {o.date_created} | Total: {o.total_amount} | Items Found: {count}")
    
    db.close()

if __name__ == "__main__":
    check_counts()

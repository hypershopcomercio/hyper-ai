import sys
import os
from sqlalchemy import func
from datetime import datetime, timedelta, time

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder, MlOrderItem

def verify_totals():
    db = SessionLocal()
    try:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        start = datetime.combine(yesterday, time.min)
        end = datetime.combine(today, time.min)
        
        print(f"Comparing Order Total vs Items Total for {start} to {end}")
        
        orders = db.query(MlOrder).filter(MlOrder.date_created >= start, MlOrder.date_created < end).all()
        
        sum_order_total = 0
        sum_items_total = 0
        
        for o in orders:
            items_val = sum((i.unit_price * i.quantity) for i in o.items)
            diff = o.total_amount - items_val
            
            sum_order_total += o.total_amount
            sum_items_total += items_val
            
            if abs(diff) > 0.01:
                print(f"Order {o.ml_order_id} ({o.status}): Total={o.total_amount:.2f} | Items={items_val:.2f} | Diff={diff:.2f}")

        print("-" * 50)
        print(f"Grand Total Order Amount: {sum_order_total:,.2f}")
        print(f"Grand Total Items Amount: {sum_items_total:,.2f}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_totals()

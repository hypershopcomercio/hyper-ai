
import sys
import os
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrderItem, MlOrder

def debug_all_sales():
    db = SessionLocal()
    try:
        # Target Date: 2025-12-28
        start_date = "2025-12-28 00:00:00"
        end_date = "2025-12-28 23:59:59"
        
        target_title_part = "780 Litros"
        
        print(f"--- All Sales of '{target_title_part}' on 28/12 ---")
        
        # Query
        results = db.query(MlOrderItem, MlOrder).join(MlOrder, MlOrderItem.ml_order_id == MlOrder.ml_order_id)\
            .filter(MlOrderItem.title.ilike(f"%{target_title_part}%"))\
            .filter(MlOrder.date_created >= start_date)\
            .filter(MlOrder.date_created <= end_date)\
            .order_by(MlOrder.date_created.asc())\
            .all()
            
        if not results:
            print("No sales found on this day.")
        
        for item, order in results:
            print(f"ID: {item.ml_item_id}")
            print(f"Title: {item.title}")
            print(f"Price: {item.unit_price}")
            print(f"Date Created (Raw): {order.date_created}")
            print(f"Date Closed (Raw): {order.date_closed}")
            if order.date_created.tzinfo:
                print(f"Timezone: {order.date_created.tzinfo}")
            else:
                print(f"Timezone: Naive (likely UTC if from API)")
            print("-" * 30)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_all_sales()

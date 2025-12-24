import sys
import os
from sqlalchemy import func
from datetime import datetime, timedelta, time

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def check_timezone_overlap():
    db = SessionLocal()
    try:
        # Check window around the UTC midnight boundary of 22/12/2025
        # 22/12 00:00 UTC is 21/12 21:00 BRT.
        # Check orders from 22/12 00:00 UTC to 22/12 04:00 UTC (which is 21/12 21:00 to 21/12 01:00 BRT)
        
        start_utc = datetime(2025, 12, 22, 0, 0, 0)
        end_utc = datetime(2025, 12, 22, 4, 0, 0)
        
        print(f"Checking for orders between {start_utc} UTC and {end_utc} UTC...")
        
        orders = db.query(MlOrder).filter(MlOrder.date_created >= start_utc, MlOrder.date_created < end_utc).all()
        
        print(f"Found {len(orders)} orders in overlap window.")
        total_val = sum(o.total_amount for o in orders)
        print(f"Total Value: {total_val:,.2f}")
        
        for o in orders:
            print(f"Order {o.ml_order_id} | Date: {o.date_created} (UTC) | Value: {o.total_amount}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_timezone_overlap()

import sys
import os
from sqlalchemy import func
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.models.ml_metrics_daily import MlMetricsDaily

def inspect():
    db = SessionLocal()
    try:
        print("--- Inspecting Data ---")
        
        # 1. Orders
        order_count = db.query(MlOrder).count()
        print(f"Total Orders in DB: {order_count}")
        
        last_order = db.query(MlOrder).order_by(MlOrder.date_created.desc()).first()
        if last_order:
            print(f"Latest Order: {last_order.ml_order_id} | Date: {last_order.date_created} | Amount: {last_order.total_amount}")
        else:
            print("No orders found.")

        # 2. Sales in last 7 days (Dashboard Logic)
        today = datetime.now().date()
        start_date = today - timedelta(days=7)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        
        sales_7d = db.query(func.sum(MlOrder.total_amount)).filter(MlOrder.date_created >= start_datetime).scalar() or 0.0
        print(f"Dashboard Sales (Last 7d): {sales_7d}")

        # 3. Visits in last 7 days
        visits_7d = db.query(func.sum(MlMetricsDaily.visits)).filter(MlMetricsDaily.date >= start_date).scalar() or 0
        print(f"Dashboard Visits (Last 7d): {visits_7d}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect()

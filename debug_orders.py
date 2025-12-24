import sys
import os
from sqlalchemy import func

# Add app to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.models.sale import Sale

def debug_orders():
    db = SessionLocal()
    try:
        # Check MlOrder (New Source)
        ml_count = db.query(MlOrder).count()
        ml_sum = db.query(func.sum(MlOrder.total_amount)).scalar() or 0.0
        
        # Check Sale (Old Source)
        sale_count = db.query(Sale).count()
        sale_sum = db.query(func.sum(Sale.total_amount)).scalar() or 0.0
        
        print("\n--- DB STATUS ---")
        print(f"MlOrder Count: {ml_count}")
        print(f"MlOrder Total Sum: {ml_sum}")
        print(f"Sale (Old) Count: {sale_count}")
        print(f"Sale (Old) Total Sum: {sale_sum}")
        
        # Check Dates
        from datetime import datetime
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        min_date = db.query(func.min(MlOrder.date_created)).scalar()
        max_date = db.query(func.max(MlOrder.date_created)).scalar()
        today_count = db.query(MlOrder).filter(MlOrder.date_created >= today_start).count()
        today_sum = db.query(func.sum(MlOrder.total_amount)).filter(MlOrder.date_created >= today_start).scalar() or 0.0
        
        print(f"Min Date: {min_date}")
        print(f"Max Date: {max_date}")
        print(f"Orders Today (since {today_start}): {today_count} - Sum: {today_sum}")
        print("-----------------\n")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_orders()

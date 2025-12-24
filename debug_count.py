import sys
import os
from sqlalchemy import func
from datetime import datetime

# Add app to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def check_today():
    db = SessionLocal()
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.query(MlOrder).filter(MlOrder.date_created >= today_start).count()
        today_sum = db.query(func.sum(MlOrder.total_amount)).filter(MlOrder.date_created >= today_start).scalar() or 0.0
        
        print(f"TODAY_COUNT: {today_count}")
        print(f"TODAY_SUM: {today_sum}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_today()

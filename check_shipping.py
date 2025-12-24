import sys
import os
from datetime import datetime, timedelta, timezone
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def check_shipping():
    target_date = datetime(2025, 12, 21).date()
    target_tz = timezone(timedelta(hours=-4))
    
    db = SessionLocal()
    orders = db.query(MlOrder).all()
    
    shipping_sum = 0.0
    paid_sum = 0.0
    total_sum = 0.0
    
    for o in orders:
        dt = o.date_created
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local_dt = dt.astimezone(target_tz)
        
        if local_dt.date() == target_date:
            shipping_sum += float(o.shipping_cost or 0)
            paid_sum += float(o.paid_amount or 0)
            total_sum += float(o.total_amount or 0)
            
    print(f"Total Amount: {total_sum}")
    print(f"Paid Amount: {paid_sum}")
    print(f"Shipping Cost: {shipping_sum}")
    print(f"Diff Paid - Total: {paid_sum - total_sum}")

if __name__ == "__main__":
    check_shipping()

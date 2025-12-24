from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from datetime import datetime, timezone, timedelta

def debug_time():
    db = SessionLocal()
    try:
        # Get latest order
        order = db.query(MlOrder).order_by(MlOrder.date_created.desc()).first()
        if not order:
            print("No orders found.")
            return

        print(f"Order ID: {order.ml_order_id}")
        print(f"Raw DB date_created (Naive UTC expected): {order.date_created}")
        
        dt = order.date_created
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
            print(f"Assumed UTC: {dt}")
            
        target_tz = timezone(timedelta(hours=-3))
        local_dt = dt.astimezone(target_tz)
        print(f"Converted to UTC-3: {local_dt}")
        
        h = local_dt.hour
        bucket_h = (h // 2) * 2
        print(f"Bucket Hour: {bucket_h:02}h")
        
        # Check specific known order if possible
        # User reported discrepancy.
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_time()

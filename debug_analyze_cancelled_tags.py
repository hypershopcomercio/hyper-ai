
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
import json

def analyze_cancelled_tags():
    db = SessionLocal()
    
    # Range: Dec 1st UTC
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_utc = start_date.astimezone(timezone.utc).replace(tzinfo=None)
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_utc,
        MlOrder.status == 'cancelled'
    ).all()
    
    print(f"Found {len(orders)} Cancelled Orders.")
    
    valid_count = 0
    ignored_count = 0
    
    for o in orders:
        tags = o.tags
        is_ignored = False
        
        # Current Logic Check
        if tags and "not_delivered" in tags:
            is_ignored = True
            
        status_label = "IGNORED" if is_ignored else "VALID"
        if is_ignored: ignored_count += 1
        else: valid_count += 1
            
        print(f"ID: {o.ml_order_id} | Val: {o.total_amount} | {status_label} | Tags: {tags}")
        
    print("-" * 30)
    print(f"Total: {len(orders)}")
    print(f"Valid (would be included): {valid_count}")
    print(f"Ignored (excluded): {ignored_count}")
    
    db.close()

if __name__ == "__main__":
    analyze_cancelled_tags()

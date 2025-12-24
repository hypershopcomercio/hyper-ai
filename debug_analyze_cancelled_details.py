
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
import json

def analyze_cancelled_details():
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
    
    details = {}
    
    for o in orders:
        sd = o.status_detail
        if sd not in details:
            details[sd] = {"count": 0, "val": 0.0}
        
        details[sd]["count"] += 1
        details[sd]["val"] += float(o.total_amount or 0)
        
        # Check tags
        tags = o.tags
        is_not_paid = tags and "not_paid" in tags
        
        print(f"ID: {o.ml_order_id} | Val: {o.total_amount} | Detail: {sd} | NotPaid: {is_not_paid}")

    print("-" * 30)
    for sd, d in details.items():
        print(f"Detail: {sd:20} | Count: {d['count']} | Sum: {d['val']:.2f}")

    db.close()

if __name__ == "__main__":
    analyze_cancelled_details()

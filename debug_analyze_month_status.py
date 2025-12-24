
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from sqlalchemy import func

def analyze_month_status():
    db = SessionLocal()
    
    # Range
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_utc = start_date.astimezone(timezone.utc).replace(tzinfo=None)
    
    print(f"Analysis from: {start_utc} (UTC)")
    
    orders = db.query(MlOrder).filter(MlOrder.date_created >= start_utc).all()
    
    stats = {}
    
    total_gross = 0.0
    
    for o in orders:
        s = o.status
        if s not in stats:
            stats[s] = {"count": 0, "val": 0.0, "ids": []}
        
        val = float(o.total_amount or 0)
        stats[s]["count"] += 1
        stats[s]["val"] += val
        stats[s]["ids"].append(o.ml_order_id)
        
        if s == 'paid':
            total_gross += val
            
    print(f"Total DB Orders: {len(orders)}")
    print("-" * 30)
    for s, data in stats.items():
        print(f"Status: {s:15} | Count: {data['count']:3} | Sum: {data['val']:10.2f}")
        
    print("-" * 30)
    print(f"Total Paid Gross: {total_gross:.2f}")
    
    # Check Cancelled details
    if 'cancelled' in stats:
        print("\nCancelled Analysis (Count):", stats['cancelled']['count'])
        # cancelled = db.query(MlOrder).filter(MlOrder.date_created >= start_utc, MlOrder.status == 'cancelled').all()
        # for o in cancelled:
        #     print(f"ID: {o.ml_order_id} | Val: {o.total_amount} | Tags: {o.tags}")

    db.close()

if __name__ == "__main__":
    analyze_month_status()


from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def analyze_tz_paid():
    db = SessionLocal()
    
    # Logic from Dashboard (Yesterday)
    tz_br = timezone(timedelta(hours=-3))
    now_br = datetime.now(tz_br)
    today_br_start = now_br.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Yesterday 00:00 BRT
    yesterday_br_start = today_br_start - timedelta(days=1)
    # Yesterday 23:59:59 BRT (End is Today 00:00)
    yesterday_br_end = today_br_start
    
    # Check "Today" too for curiosity
    today_br_end = now_br
    
    # Convert to UTC
    start_utc = yesterday_br_start.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = yesterday_br_end.astimezone(timezone.utc).replace(tzinfo=None)
    
    print(f"--- YESTERDAY WINDOW (UTC) ---")
    print(f"Start: {start_utc}")
    print(f"End:   {end_utc}")
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_utc,
        MlOrder.date_created < end_utc,
        MlOrder.status == 'paid'
    ).all()
    
    print(f"--- PAID ORDERS ({len(orders)}) ---")
    total = 0.0
    for o in orders:
        val = float(o.total_amount or 0)
        total += val
        tags = o.tags
        print(f"ID: {o.ml_order_id} | Val: {val:.2f} | Tags: {tags} | Date: {o.date_created}")
        
    print(f"Total: {total:.2f}")
    
    # Check for 36.30 match
    match = [o for o in orders if abs(float(o.total_amount or 0) - 36.30) < 0.1]
    if match:
        print(f"FOUND 36.30 CANDIDATE: {match[0].ml_order_id}")

    db.close()

if __name__ == "__main__":
    analyze_tz_paid()

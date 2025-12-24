
import datetime
from datetime import timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from sqlalchemy import func

def list_cancelled():
    db = SessionLocal()
    
    # SYSTEM TIME
    now = datetime.datetime.now()
    today = now.date()
    
    # Current Month
    start_date = today.replace(day=1)
    
    # Helper
    tz_offset = timedelta(hours=3)
    def to_utc_aware(d):
        naive = datetime.datetime.combine(d, datetime.datetime.min.time()) + tz_offset
        return naive.replace(tzinfo=timezone.utc)

    start_dt = to_utc_aware(start_date)
    
    print(f"--- CANCELLED ORDERS REPORT ---")
    print(f"Period: Since {start_date}")
    
    q = db.query(MlOrder).filter(
        MlOrder.date_created >= start_dt,
        MlOrder.status == 'cancelled'
    ).order_by(MlOrder.date_created.desc())
    
    cancelled_orders = q.all()
    
    total_val = 0.0
    print(f"\nFound {len(cancelled_orders)} CANCELLED orders:")
    print("-" * 80)
    print(f"{'ML ID':<20} | {'DATE':<12} | {'VALUE (R$)':<10} | {'REASON / DETAIL'}")
    print("-" * 80)
    
    for o in cancelled_orders:
        val = float(o.total_amount or 0)
        total_val += val
        
        # Format Date
        # Convert to Local for display
        dt_utc = o.date_created
        if dt_utc.tzinfo is None: dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        dt_local = dt_utc - tz_offset
        d_str = dt_local.strftime("%d/%m %H:%M")
        
        detail = o.status_detail or "N/A"
        
        print(f"{o.ml_order_id:<20} | {d_str:<12} | {val:>10.2f} | {detail}")
        
    print("-" * 80)
    print(f"TOTAL CANCELLED SUM: R$ {total_val:,.2f}")
    print("-" * 80)
             
    db.close()

if __name__ == "__main__":
    list_cancelled()


import datetime
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
import pytz

def analyze_yesterday():
    db = SessionLocal()
    
    # Yesterday 2025-12-22
    # Assuming user is in -03:00, or just use the whole day UTC range to be safe
    # But usually dashboard uses "Yesterday" based on localized time.
    # The dashboard logic uses:
    # end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # start_date = end_date - timedelta(days=1)
    # Let's verify strict range logic from dashboard.py if needed, but here we just grab the day.
    
    # Hardcoded for 2025-12-22
    start_dt = datetime.datetime(2025, 12, 22, 0, 0, 0) # Naive, assume implies user TZ or UTC?
    end_dt = datetime.datetime(2025, 12, 23, 0, 0, 0)
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_dt,
        MlOrder.date_created < end_dt
    ).all()
    
    print(f"--- YESTERDAY (2025-12-22) ANALYSIS ---")
    print(f"Total Orders DB: {len(orders)}")
    
    paid = []
    cancelled = []
    others = []
    
    for o in orders:
        if o.status == 'paid':
            paid.append(o)
        elif o.status == 'cancelled':
            cancelled.append(o)
        else:
            others.append(o)
            
    # CHECK CANCELLED
    print(f"\n--- CANCELLED ORDERS ({len(cancelled)}) ---")
    for o in cancelled:
        print(f"ID: {o.ml_order_id} | Val: {o.total_amount} | Tags: {o.tags}")
        
    # CHECK PAID SUMS
    paid_sum = sum(float(o.total_amount or 0) for o in paid)
    with open("yesterday_dump.txt", "w") as f:
        f.write(f"--- CANCELLED ORDERS ({len(cancelled)}) ---\n")
        
        for o in cancelled:
            val = float(o.total_amount or 0)
            f.write(f"CANCELLED ID: {o.ml_order_id} | Val: {val:.2f} | Tags: {o.tags}\n")

        f.write(f"\n--- PAID ORDERS ({len(paid)}) ---\n")
        f.write(f"Sum Paid: {paid_sum:.2f}\n")
        f.write("\nPaid Orders List:\n")
        for o in paid:
            val = float(o.total_amount or 0)
            f.write(f"{o.ml_order_id}: {val:.2f}\n")
    
    print("Dump written to yesterday_dump.txt")
    db.close()

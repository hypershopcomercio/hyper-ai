
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.models.ml_metrics_daily import MlMetricsDaily
from sqlalchemy import func

def check_7d_windows():
    db = SessionLocal()
    
    # BRT
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Target Values (ML)
    target_gross = 47732.00
    target_count = 298
    target_visits = 6867
    
    # Define Windows
    windows = {
        "A (Dec 16 - Dec 22) [Excl Today]": (today - timedelta(days=7), today), 
        "B (Dec 17 - Dec 23) [Incl Today]": (today - timedelta(days=6), now), # Today - 6 = 7 days total including today?
        # Dec 17, 18, 19, 20, 21, 22, 23 (7 days)
        "C (Dec 16 - Dec 23) [Current Logic?]": (today - timedelta(days=7), now), # 8 days
    }
    
    print(f"Checking Windows against Target: Gross={target_gross}, Orders={target_count}, Visits={target_visits}")
    print("-" * 50)
    
    # Known Ignored IDs (from previous step)
    IGNORED_IDS = {
        "2000014419924860", 
        "2000014149744094", 
        "2000014293954164"
    }

    for name, (start, end) in windows.items():
        # UTC Conversion (Consistent with dashboard)
        start_utc = start.replace(tzinfo=None) + timedelta(hours=3)
        if end.year == 2025: # naive check
             end_utc = end.replace(tzinfo=None) # + timedelta(hours=3) ? 
             # Wait, dashboard uses to_utc_naive which adds 3h to naive.
             # If 'now' is aware (BRT), we convert to UTC.
             end_utc = end.astimezone(timezone.utc).replace(tzinfo=None)
        else:
             # Just date boundary
             end_utc = end.replace(tzinfo=None) + timedelta(hours=3)

        # Query Sales (using date_closed as per fix)
        orders = db.query(MlOrder).filter(
            MlOrder.date_closed >= start_utc,
            MlOrder.date_closed < end_utc
        ).all()
        
        gross = 0.0
        count = 0
        cancelled_val = 0.0
        
        for o in orders:
            if o.ml_order_id in IGNORED_IDS: continue
            
            val = float(o.total_amount or 0)
            if o.status == 'paid' or o.status == 'shipped' or o.status == 'delivered':
                gross += val
                count += 1
            elif o.status == 'cancelled':
                # Dashboard logic: Cancelled adds to Gross?
                # ML Vendas Brutas usually includes cancelled IF they were paid then cancelled?
                # Logic in Dashboard: 
                # if cancelled: curr_gross += val, curr_cancelled += val.
                gross += val
                cancelled_val += val
                count += 1 # ML "Qty Sales" seems to include cancelled?
                
        # Query Visits
        # Visits are by Date (Day)
        # Sum visits where date >= start.date and date < end.date
        q_vis = db.query(func.sum(MlMetricsDaily.visits)).filter(
            MlMetricsDaily.date >= start.date(),
            MlMetricsDaily.date <= end.date() # Inclusive to catch 'today' if in range
        )
        # If end is midnight (Excl Today), we want < end.date
        # If end is now (Incl Today), we want <= end.date
        if "Excl Today" in name:
             q_vis = db.query(func.sum(MlMetricsDaily.visits)).filter(
                MlMetricsDaily.date >= start.date(),
                MlMetricsDaily.date < end.date()
            )
            
        visits = q_vis.scalar() or 0
        
        print(f"Window {name}")
        print(f"  Range UTC: {start_utc} -> {end_utc}")
        print(f"  Gross: {gross:.2f} (Diff: {gross - target_gross:.2f})")
        print(f"  Orders: {count} (Diff: {count - target_count})")
        print(f"  Visits: {visits} (Diff: {visits - target_visits})")
        print("-" * 30)

    db.close()

if __name__ == "__main__":
    check_7d_windows()

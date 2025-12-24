
import datetime
from datetime import timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from sqlalchemy import func

def debug_reconcile():
    db = SessionLocal()
    
    # 1. Period: Current Month (Same as Dashboard)
    today = datetime.datetime.now().date()
    start_date = today.replace(day=1)
    
    # Timezone Aware Start
    tz_offset = timedelta(hours=3)
    start_dt = datetime.datetime.combine(start_date, datetime.datetime.min.time()) + tz_offset
    start_dt = start_dt.replace(tzinfo=timezone.utc)
    
    print(f"--- RECONCILIATION DEBUG ---")
    print(f"Period: {start_dt} -> Now")
    
    # 2. Query ALL orders in period
    orders = db.query(MlOrder).filter(MlOrder.date_created >= start_dt).all()
    
    # 3. Group by Status + StatusDetail (Adjusted)
    stats = {}
    total_gross = 0.0
    total_adjusted_gross = 0.0
    total_cancelled_adjusted = 0.0
    
    count_ignored = 0
    val_ignored = 0.0
    
    import json
    
    for o in orders:
        s = f"{o.status} ({o.status_detail})"
        amt = float(o.total_amount or 0)
        
        # Check Tags
        tags_str = o.tags or "[]"
        
        # LOGIC: Exclude if 'not_paid' AND 'catalog'
        is_ignored = False
        if "not_paid" in tags_str and "catalog" in tags_str:
            is_ignored = True
            count_ignored += 1
            val_ignored += amt
            
        if s not in stats:
            stats[s] = {"count": 0, "sum": 0.0}
            
        stats[s]["count"] += 1
        stats[s]["sum"] += amt
        
        # Gross Logic in Dashboard: Sum(TotalAmount) of Valid Orders (Paid + Valid-Cancelled)
        # Note: Valid-Cancelled IS included in Dashboard Gross, then subtracted for Net.
        
        if not is_ignored:
            total_adjusted_gross += amt
            if o.status == 'cancelled':
                total_cancelled_adjusted += amt
        
        total_gross += amt
        
    # 4. Print Report
    print(f"\nTotal Orders: {len(orders)}")
    print(f"Total Gross (Raw DB): {total_gross:,.2f}")
    print(f"Total Gross (Adjusted): {total_adjusted_gross:,.2f}")
    print(f"Total Cancelled (Adjusted): {total_cancelled_adjusted:,.2f}")
    print(f"Excluded (Catalog+NotPaid): {count_ignored} orders (R$ {val_ignored:,.2f})")
    
    print("-" * 60)
    print(f"{'STATUS (Detail)':<40} | {'COUNT':<5} | {'SUM (R$)':<15}")
    print("-" * 60)
    
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['sum'], reverse=True)
    
    for status, data in sorted_stats:
        print(f"{status:<40} | {data['count']:<5} | {data['sum']:,.2f}")
        
    # 5. Check for the specific diff
    target_diff = 305.43
    print("-" * 60)
    print(f"Looking for approx diff: {target_diff}")
    
    # Check single orders close to diff
    candidates = [o for o in orders if abs(float(o.total_amount) - target_diff) < 10.0] 
    if candidates:
        print(f"\nOrders with value ~{target_diff}:")
        for c in candidates:
             print(f" - ID: {c.ml_order_id} | Status: {c.status} ({c.status_detail}) | Val: {c.total_amount}")
    
    db.close()

if __name__ == "__main__":
    debug_reconcile()


from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def compare_queries():
    db = SessionLocal()
    
    # Logic from Dashboard (Yesterday)
    tz_br = timezone(timedelta(hours=-3))
    now_br = datetime.now(tz_br)
    today_br_start = now_br.replace(hour=0, minute=0, second=0, microsecond=0)
    
    start_br = today_br_start - timedelta(days=1)
    end_br = today_br_start
    
    start_utc = start_br.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = end_br.astimezone(timezone.utc).replace(tzinfo=None)
    
    print(f"Window: {start_utc} to {end_utc}")
    
    # Method A: Dashboard Logic (Fetch All, Filter in Loop) + JOINEDLOAD
    from sqlalchemy.orm import joinedload
    orders_a = db.query(MlOrder).options(joinedload(MlOrder.items)).filter(
        MlOrder.date_created >= start_utc,
        MlOrder.date_created < end_utc
    ).all()
    
    paid_a = []
    for o in orders_a:
        # Ghost Cancel Filter
        if o.status == 'cancelled' and o.tags and "not_delivered" in o.tags:
            continue
        if o.status == 'paid':
            paid_a.append(o)
            
    ids_a = set(o.ml_order_id for o in paid_a)
    print(f"Method A (Dashboard+JoinedLoad) Count: {len(ids_a)}")
    print(f"Method A Sum: {sum(float(o.total_amount or 0) for o in paid_a):.2f}")
    
    # Sort and print IDs to compare
    pdf_a = sorted(list(ids_a))
    # print(f"IDs A: {pdf_a}")
    
    # Method B: Direct Filter
    orders_b = db.query(MlOrder).filter(
        MlOrder.date_created >= start_utc,
        MlOrder.date_created < end_utc,
        MlOrder.status == 'paid'
    ).all()
    
    ids_b = set(o.ml_order_id for o in orders_b)
    print(f"Method B (Direct) Count: {len(ids_b)}")
    print(f"Method B Sum: {sum(float(o.total_amount or 0) for o in orders_b):.2f}")
    
    # Diff
    only_in_a = ids_a - ids_b
    if only_in_a:
        print("\n--- ONLY IN DASHBOARD (A) ---")
        for mid in only_in_a:
             o = db.query(MlOrder).filter(MlOrder.ml_order_id == mid).first()
             print(f"ID: {mid} | Status: {o.status} | Tags: {o.tags} | Val: {o.total_amount}")
             
    only_in_b = ids_b - ids_a
    if only_in_b:
        print("\n--- ONLY IN DIRECT (B) ---")
        for mid in only_in_b:
             print(mid)
             
    db.close()

if __name__ == "__main__":
    compare_queries()

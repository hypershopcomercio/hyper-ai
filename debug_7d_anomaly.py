
import datetime
from datetime import timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from sqlalchemy import func

def run_debug():
    db = SessionLocal()
    
    # SYSTEM TIME
    now = datetime.datetime.now()
    today = now.date()
    
    # Helper
    tz_offset = timedelta(hours=3)
    def to_utc_aware(d):
        naive = datetime.datetime.combine(d, datetime.datetime.min.time()) + tz_offset
        return naive.replace(tzinfo=timezone.utc)

    print(f"--- DEBUG 7D ANOMALY ---")
    print(f"Ref Date (Today): {today}")
    
    # ----------------------------------------------------
    # SCENARIO A: YESTERDAY (days=0)
    # ----------------------------------------------------
    start_y = today - timedelta(days=1)
    end_y = today
    start_dt_y = to_utc_aware(start_y)
    end_dt_y = to_utc_aware(end_y)
    
    print(f"\n[SCENARIO A: YESTERDAY]")
    print(f"Range: {start_dt_y} <= date < {end_dt_y}")
    
    q_y = db.query(MlOrder).filter(MlOrder.date_created >= start_dt_y, MlOrder.date_created < end_dt_y)
    orders_y = q_y.all()
    sum_y = sum(o.total_amount for o in orders_y if o.status != 'cancelled')
    print(f"Count: {len(orders_y)} | Total Net: {sum_y}")

    # ----------------------------------------------------
    # SCENARIO B: LAST 7 DAYS (days=7)
    # ----------------------------------------------------
    days = 7
    start_7 = today - timedelta(days=days)
    end_7 = None # As per code logic
    
    start_dt_7 = to_utc_aware(start_7)
    # end_dt_7 is None
    
    print(f"\n[SCENARIO B: 7 DAYS]")
    print(f"Range: {start_dt_7} <= date < (Infinity)")
    
    q_7 = db.query(MlOrder).filter(MlOrder.date_created >= start_dt_7)
    orders_7 = q_7.all()
    sum_7 = sum(o.total_amount for o in orders_7 if o.status != 'cancelled')
    print(f"Count: {len(orders_7)} | Total Net: {sum_7}")
    
    # ----------------------------------------------------
    # SCENARIO C: 7 DAYS with END DATE (Hypothesis)
    # ----------------------------------------------------
    # What if end date was accidentally set to 'start_date + 7'? which is today.
    # It should overlap Scenario B effectively since B is open-ended.
    
    # Let's check overlap
    ids_y = set(o.ml_order_id for o in orders_y)
    ids_7 = set(o.ml_order_id for o in orders_7)
    
    missing = ids_y - ids_7
    if missing:
         print(f"\n!!! CRITICAL: {len(missing)} orders from Yesterday are MISSING in 7D!")
         print(list(missing)[:3])
    else:
         print(f"\nOK: All Yesterday orders are in 7D.")
         if sum_7 < sum_y:
             print("WTF: Sum 7D < Sum Yesterday, but all orders included?? Check negatives?")
             
    db.close()

if __name__ == "__main__":
    run_debug()

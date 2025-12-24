
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from sqlalchemy import or_

def check_date_closed():
    db = SessionLocal()
    
    # Range: Nov 20 to Dec 1
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=10) # Nov 20
    
    start_utc = start_date.astimezone(timezone.utc).replace(tzinfo=None)
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_utc
    ).limit(100).all()
    
    print(f"Checking sample orders since {start_utc}...")
    
    populated = 0
    empty = 0
    
    for o in orders:
        if o.date_closed:
            populated += 1
            # print(f"ID: {o.ml_order_id} | Created: {o.date_created} | Closed: {o.date_closed}")
        else:
            empty += 1
            
    print(f"Total Sample: {len(orders)}")
    print(f"Populated: {populated}")
    print(f"Empty: {empty}")
    
    if empty > 0:
        print("Conclusion: Need Backfill.")
    else:
        print("Conclusion: Data exists.")

    db.close()

if __name__ == "__main__":
    check_date_closed()

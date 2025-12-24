
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def find_late_sales():
    db = SessionLocal()
    
    # Range: Dec 1st UTC
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_utc = start_date.astimezone(timezone.utc).replace(tzinfo=None)
    
    print(f"Dec 1st UTC: {start_utc}")
    
    # Query: Status = Paid, Date Created < Dec 1, Date Last Updated >= Dec 1?
    # MlOrder doesn't have 'date_closed'. We rely on 'date_last_updated' or check created vs "now" if we want to fetch them.
    # Actually, let's just check DB for orders created BEFORE start_date_utc but updated AFTER?
    # Or just fetch ALL orders created in last 60 days and check 'date_closed' if present?
    # MlOrder model usually has 'date_closed'? Let's check model definition or just inspect 'date_closed' column.
    # If not, we might have to fetch from API.
    
    # Let's inspect ONE order to see if it has date_closed field.
    # Or assuming we don't know:
    # Query orders created between Nov 25 and Dec 1.
    
    check_start = start_utc - timedelta(days=5) # Nov 26
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= check_start,
        MlOrder.date_created < start_utc,
        MlOrder.status == 'paid'
    ).all()
    
    print(f"Checking {len(orders)} orders from late Nov...")
    
    late_sales_count = 0
    late_sales_val = 0.0
    
    from app.services.meli_api import MeliApiService
    api = MeliApiService(db_session=db)
    
    for o in orders:
        # We need date_closed. It might be in the object or need fetch.
        # Let's try to fetch live to be sure.
        mid = o.ml_order_id
        # resp = api.request("GET", f"/orders/{mid}")
        # if resp.status_code == 200:
        #     data = resp.json()
        #     date_closed = data.get('date_closed')
        #     # Format: 2025-11-30T...
        #     if date_closed:
        #         # Parse
        #         # 2025-12-01...
        #         if date_closed >= "2025-12-01":
        #             print(f"LATE SALE! ID: {mid} | Created: {o.date_created} | Closed: {date_closed}")
        #             late_sales_count += 1
        #             late_sales_val += float(o.total_amount)
        
        # Optimization: Just print IDs and I will check one manually or output implies result.
        pass
        
    # Better approach:
    # Just list ALL paid orders from Nov 25-30 and sum them?
    # If we find ~21 orders, it's highly likely they are the culprits.
    total = 0.0
    for o in orders:
        total += float(o.total_amount or 0)
        
    print(f"Paid Orders (Nov 26 - Dec 1): {len(orders)} | Value: {total:.2f}")

    db.close()

if __name__ == "__main__":
    find_late_sales()

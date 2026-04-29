import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime, timedelta

# Password from screenshot: gWh28@@40dGcMp
url = "mysql+pymysql://root:gWh28%40%4040dGcMp@localhost:3306/hyper_sync"
engine = sqlalchemy.create_engine(url)
Session = sessionmaker(bind=engine)
db = Session()

try:
    # Check "Ontem" (Yesterday) = April 28
    # Start: 2026-04-28 03:00:00 UTC
    # End:   2026-04-29 03:00:00 UTC
    start = datetime(2026, 4, 28, 3, 0, 0)
    end = datetime(2026, 4, 29, 3, 0, 0)
    
    print(f"Checking orders between {start} and {end} UTC...")
    
    sql = text("SELECT ml_order_id, date_created, date_closed, total_amount, status FROM ml_orders WHERE date_closed >= :s AND date_closed < :e")
    res = db.execute(sql, {"s": start, "e": end}).all()
    
    print(f"Found {len(res)} orders.")
    total_revenue = sum(float(r.total_amount or 0) for r in res if r.status != 'cancelled')
    print(f"Total Revenue (non-cancelled): R$ {total_revenue:.2f}")
    
    for r in res:
        print(f"Order {r.ml_order_id}: Created={r.date_created}, Closed={r.date_closed}, Amount={r.total_amount}, Status={r.status}")

    # Check for any orders in April 28 at all
    start_day = datetime(2026, 4, 28, 0, 0, 0)
    end_day = datetime(2026, 4, 29, 0, 0, 0)
    res_any = db.execute(text("SELECT COUNT(*) FROM ml_orders WHERE date_created >= :s AND date_created < :e"), {"s": start_day, "e": end_day}).scalar()
    print(f"Total orders CREATED on April 28 (any time): {res_any}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from datetime import datetime, timedelta

db = SessionLocal()
now = datetime.now()
start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

print(f"Checking orders for Today (since {start_of_today})...")

# Try to find any order created today
orders_today = db.query(MlOrder).filter(MlOrder.date_created >= start_of_today).all()
print(f"Found {len(orders_today)} orders created today (by date_created).")

# Try by date_closed
orders_closed_today = db.query(MlOrder).filter(MlOrder.date_closed >= start_of_today).all()
print(f"Found {len(orders_closed_today)} orders closed today (by date_closed).")

# Total orders in DB
total = db.query(MlOrder).count()
print(f"Total orders in DB: {total}")

# Last 5 orders
last_orders = db.query(MlOrder).order_by(MlOrder.date_created.desc()).limit(5).all()
for o in last_orders:
    print(f"Order {o.ml_order_id}: Created={o.date_created}, Closed={o.date_closed}, Status={o.status}")

db.close()

import sys
import os
sys.path.append(os.getcwd())
from app.database import SessionLocal
from app.models.ml_order import MlOrder
from datetime import datetime, timedelta, timezone

db = SessionLocal()

# Set Timezone to Brasilia
br_offset = timezone(timedelta(hours=-3))
now = datetime.now(br_offset)
start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
start_of_day_utc = start_of_day.astimezone(timezone.utc).replace(tzinfo=None) # Naive UTC for query if DB is naive
# Or if DB is timezone aware (Postgres usually is timestamp without time zone in models, but stored as UTC).
# Let's assume naive UTC in DB columns based on previous code.

print(f"DEBUG: Checking Orders since {start_of_day} (Local) -> {start_of_day_utc} (UTC)")

orders = db.query(MlOrder).filter(MlOrder.date_created >= start_of_day_utc).all()

print(f"DEBUG: Found {len(orders)} orders created today.")

for o in orders:
    print(f" - ID: {o.ml_order_id} | Status: {o.status} | Created: {o.date_created} | Closed: {o.date_closed} | Amount: {o.total_amount}")

# Check by date_closed
orders_closed = db.query(MlOrder).filter(MlOrder.date_closed >= start_of_day_utc).all()
print(f"DEBUG: Found {len(orders_closed)} orders closed (paid) today.")
for o in orders_closed:
     print(f" - ID: {o.ml_order_id} | Status: {o.status} | Closed: {o.date_closed} | Amount: {o.total_amount}")

db.close()

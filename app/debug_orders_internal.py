from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from datetime import datetime, timedelta, timezone

db = SessionLocal()

# Set Timezone to Brasilia
br_offset = timezone(timedelta(hours=-3))
now = datetime.now(br_offset)
start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
start_of_day_utc = start_of_day.astimezone(timezone.utc).replace(tzinfo=None)

print(f"DEBUG: Checking Orders since {start_of_day} (Local) -> {start_of_day_utc} (UTC)")

# Check by date_created
orders_created = db.query(MlOrder).filter(MlOrder.date_created >= start_of_day_utc).all()
print(f"DEBUG: Found {len(orders_created)} orders CREATED today.")

for o in orders_created:
    print(f" [CREATED] ID: {o.ml_order_id} | Status: {o.status} | Created: {o.date_created} | Closed: {o.date_closed} | Amount: {o.total_amount}")

# Check by date_closed
orders_closed = db.query(MlOrder).filter(MlOrder.date_closed >= start_of_day_utc).all()
print(f"DEBUG: Found {len(orders_closed)} orders CLOSED today.")

for o in orders_closed:
     print(f" [CLOSED] ID: {o.ml_order_id} | Status: {o.status} | Closed: {o.date_closed} | Amount: {o.total_amount}")

db.close()

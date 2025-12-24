import sys
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load env
load_dotenv()

# Add current dir to path
sys.path.append(os.getcwd())

# Setup DB
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not found")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

from app.models.ml_order import MlOrder, MlOrderItem
# from app.models.ml_order_item import MlOrderItem # Removed

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return obj

def check_today_statuses():
    # Target: Today in UTC-3
    tz = timezone(timedelta(hours=-3))
    now = datetime.now(tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Convert to UTC for DB query (assuming DB stores naive UTC)
    today_start_utc = today_start.astimezone(timezone.utc).replace(tzinfo=None)
    today_end_utc = today_end.astimezone(timezone.utc).replace(tzinfo=None)
    
    print(f"Checking Range (UTC-3): {today_start} to {today_end}")
    print(f"Checking Range (UTC): {today_start_utc} to {today_end_utc}")
    
    orders = session.query(MlOrder).filter(
        MlOrder.date_created >= today_start_utc,
        MlOrder.date_created <= today_end_utc
    ).all()
    
    stats = {}
    total_val = 0.0
    
    for o in orders:
        s = o.status
        if s not in stats:
            stats[s] = {"count": 0, "sum": 0.0}
        
        stats[s]["count"] += 1
        stats[s]["sum"] += float(o.total_amount or 0)
        total_val += float(o.total_amount or 0)
        
    print("-" * 40)
    print(f"Total Orders: {len(orders)}")
    print(f"Total Value (All): R$ {total_val:,.2f}")
    print("-" * 40)
    for s, data in stats.items():
        print(f"Status: {s:20} | Count: {data['count']:3} | Sum: R$ {data['sum']:,.2f}")
    print("-" * 40)
    
    # Check Cancelled specifically
    cancelled_val = stats.get('cancelled', {}).get('sum', 0.0)
    net_val = total_val - cancelled_val
    print(f"Net Value (Excl. Cancelled): R$ {net_val:,.2f}")
    
    # Check Pending/Invoiced
    # Usually 'paid', 'confirmed' are valid.
    # 'payment_required', 'pending_cancel', etc.
    
if __name__ == "__main__":
    check_today_statuses()

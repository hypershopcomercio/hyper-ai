
import sys
import os
import requests
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, and_

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.api.endpoints.sync import get_sync_status # Import directly to test function logic if needed, but better test via request if server running.
# Cannot import endpoint directly easily due to flask request context. We will simulate DB logic.

def debug_gap():
    db = SessionLocal()
    try:
        # 1. Check Sync Status Logic directly (simulate endpoint)
        print("--- Checking Sync Status Logic ---")
        from app.models.system_log import SystemLog
        from app.models.sync import SyncJob
        from sqlalchemy import desc
        
        last_log_ml = db.query(SystemLog).filter(SystemLog.module == 'listings', SystemLog.status == 'success').order_by(desc(SystemLog.timestamp)).first()
        last_job_order = db.query(SyncJob).filter(SyncJob.entity == 'orders', SyncJob.status == 'completed').order_by(desc(SyncJob.finished_at)).first()
        
        print(f"Last Log Listings: {last_log_ml.timestamp if last_log_ml else 'None'}")
        print(f"Last Job Order: {last_job_order.finished_at if last_job_order else 'None'}")
        
        # 2. Debug Sales Gap
        print("\n--- Debugging Sales Gap ---")
        # Dashboard Logic simulation
        # app/api/endpoints/dashboard.py uses:
        # tz_br = timezone(timedelta(hours=-3))
        # now_br = datetime.now(tz_br)
        # today_br_start = now_br.replace(hour=0, minute=0, second=0, microsecond=0)
        
        tz_br = timezone(timedelta(hours=-3))
        now_br = datetime.now(tz_br)
        today_start_br = now_br.replace(hour=0, minute=0, second=0, microsecond=0)
        # Updated Logic: End of Day
        end_date_br = today_start_br + timedelta(hours=23, minutes=59, seconds=59)
        
        print(f"Filter Range (BRT): {today_start_br} to {end_date_br}")
        
        query = db.query(MlOrder).filter(
            and_(
                MlOrder.date_closed >= today_start_br,
                MlOrder.date_closed <= end_date_br,
                MlOrder.status.in_(['paid', 'shipped', 'delivered', 'partially_paid'])
            )
        )
        total = db.query(func.sum(MlOrder.total_amount)).filter(
            and_(
                MlOrder.date_closed >= today_start_br,
                MlOrder.date_closed <= end_date_br,
                MlOrder.status.in_(['paid', 'shipped', 'delivered', 'partially_paid'])
            )
        ).scalar()
        
        print(f"Total Dashboard Query: {total}")
        
        # List orders near the cutoff or unusual
        orders = query.order_by(MlOrder.date_closed.desc()).all()
        print(f"Found {len(orders)} orders in dashboard query.")
        for o in orders[:5]:
            print(f"  ID: {o.ml_order_id} | Closed: {o.date_closed} | Val: {o.total_amount}")
            
        # Compare with RAW check (all today)
        print("\n--- Raw Check (All Today UTC-3) ---")
        # Just date matches
        raw_query = db.query(MlOrder).filter(func.date(MlOrder.date_closed) == today_start_br.date())
        raw_total = db.query(func.sum(MlOrder.total_amount)).filter(func.date(MlOrder.date_closed) == today_start_br.date()).scalar()
        print(f"Total Raw Date Match: {raw_total}")
        
        if raw_total and total and raw_total > total:
            print("GAP DETECTED! Finding missing orders...")
            dashboard_ids = [o.ml_order_id for o in orders]
            missing = raw_query.filter(MlOrder.ml_order_id.notin_(dashboard_ids)).all()
            for m in missing:
                print(f"  MISSING ID: {m.ml_order_id} | Status: {m.status} | Closed: {m.date_closed} | Val: {m.total_amount}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_gap()

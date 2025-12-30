
import sys
import os
from datetime import timedelta, timezone, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog
from app.models.ml_order import MlOrder, MlOrderItem

def debug_repro():
    db = SessionLocal()
    try:
        log_id = 664
        log = db.query(ForecastLog).filter(ForecastLog.id == log_id).first()
        print(f"Log Target: {log.hora_alvo}")
        
        # ORIGINAL LOGIC REPLICATION
        hour_start = log.hora_alvo
        hour_end = hour_start + timedelta(hours=1)
        
        start_naive = hour_start
        end_naive = hour_end
        
        tz_br = timezone(timedelta(hours=-3))
        
        # Convert 12:00 Naive -> 12:00 BRT -> 15:00 UTC
        start_local = start_naive.replace(tzinfo=tz_br)
        end_local = end_naive.replace(tzinfo=tz_br)
        
        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)
        
        # Force Naive for DB
        start_utc_naive = start_utc.replace(tzinfo=None)
        end_utc_naive = end_utc.replace(tzinfo=None)
        
        print(f"Window Local: {start_local} to {end_local}")
        print(f"Window UTC (Aware): {start_utc} to {end_utc}")
        print(f"Window UTC (Naive DB): {start_utc_naive} to {end_utc_naive}")
        
        # Run Query
        print("\n--- Running Query ---")
        query = db.query(
            MlOrderItem.ml_item_id,
            MlOrderItem.quantity,
            MlOrderItem.unit_price,
            MlOrder.date_closed,
            MlOrder.status
        ).join(MlOrder, MlOrderItem.ml_order_id == MlOrder.ml_order_id)
        
        query = query.filter(MlOrder.date_closed >= start_utc_naive)
        query = query.filter(MlOrder.date_closed < end_utc_naive)
        
        # Add filtering for the specific item to reduce noise
        target_id = 'MLB5238169050'
        query = query.filter(MlOrderItem.ml_item_id == target_id)
        
        results = query.all()
        print(f"Found {len(results)} matches.")
        for res in results:
            print(f"MATCH: Date={res.date_closed}, Qty={res.quantity}, Status={res.status}")
            
        if len(results) == 0:
            print("\n--- Failure Analysis ---")
            # Check if there is ANY sale for this item nearby
            broad_q = db.query(MlOrder.date_closed, MlOrder.status).join(MlOrderItem).filter(MlOrderItem.ml_item_id == target_id)
            # Just check around the date 2025-12-28
            search_day = datetime(2025, 12, 28)
            broad_q = broad_q.filter(MlOrder.date_closed >= search_day, MlOrder.date_closed < search_day + timedelta(days=1))
            broad_res = broad_q.all()
            for b in broad_res:
                print(f"CANDIDATE: {b.date_closed} (Status: {b.status})")
                if start_utc_naive <= b.date_closed < end_utc_naive:
                    print("  -> SHOULD HAVE MATCHED!")
                else:
                    print("  -> Outside Window")

    finally:
        db.close()

if __name__ == "__main__":
    debug_repro()

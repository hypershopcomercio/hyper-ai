
import logging
import sys
import datetime
from app.services.sync_engine import SyncEngine

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def backfill():
    print("Starting 365-day Order Backfill...")
    engine = SyncEngine()
    
    # 365 Days * 24 Hours
    lookback = 365 * 24 
    
    # Using existing incremental sync with massive lookback
    logging.info(f"Triggering sync with lookback_hours={lookback}")
    engine.sync_orders_incremental(lookback_hours=lookback)
    
    # After syncing orders, we must process metrics
    logging.info("Processing metrics...")
    engine.sync_metrics()
    
    print("Backfill Complete.")

if __name__ == "__main__":
    backfill()

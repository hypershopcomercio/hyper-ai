import logging
import time
from app.services.sync_engine import SyncEngine

logger = logging.getLogger(__name__)

def run_daily_sync():
    logger.info("Scheduler: Starting Daily Sync Job...")
    engine = SyncEngine()
    
    # 1. Sync Ads (Metadata, Status, Price)
    engine.sync_ads()
    
    # 2. Sync Metrics (Visits, Sales, Conversion)
    engine.sync_metrics()
    
    logger.info("Scheduler: Daily Sync Job Finished.")

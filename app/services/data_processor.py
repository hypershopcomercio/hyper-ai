"""
Data Processor Service
Orchestrates daily data synchronization jobs.
"""
import logging
from sqlalchemy.orm import Session
from app.services.sync_engine import SyncEngine

logger = logging.getLogger(__name__)


class DataProcessorService:
    """
    Service that orchestrates daily sync operations.
    Used by scheduler/jobs.py for the run_daily_sync job.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.sync_engine = SyncEngine()
    
    def sync_daily_data(self):
        """
        Runs the complete daily sync pipeline:
        1. Sync Ads (listings, prices, status)
        2. Sync Visits (CRITICAL - fetches visit data from ML API)
        3. Sync Orders (recent orders)
        4. Sync Stock (Tiny ERP stock levels)
        5. Recalculate Margins
        """
        logger.info("========== DAILY SYNC STARTED ==========")
        
        try:
            # 1. Sync Ads - listings, prices, variations
            logger.info("[1/5] Syncing Ads...")
            self.sync_engine.sync_ads()
            
            # 2. Sync Visits - CRITICAL for analytics
            logger.info("[2/5] Syncing Visits...")
            self.sync_engine.sync_visits()
            
            # 3. Sync Orders - recent orders for metrics
            logger.info("[3/5] Syncing Orders...")
            self.sync_engine.sync_orders()
            
            # 4. Sync Stock - Tiny ERP stock levels
            logger.info("[4/5] Syncing Stock...")
            self.sync_engine.sync_tiny_stock()
            
            # 5. Recalculate Margins
            logger.info("[5/5] Recalculating Margins...")
            self.sync_engine.sync_margins()
            
            logger.info("========== DAILY SYNC COMPLETED ==========")
            
        except Exception as e:
            logger.error(f"Daily sync failed: {e}")
            raise
    
    def sync_visits_only(self):
        """
        Syncs only visits data. Useful for manual trigger or debugging.
        """
        logger.info("Syncing visits only...")
        self.sync_engine.sync_visits()
        logger.info("Visits sync completed.")
    
    def sync_orders_only(self, lookback_hours: int = 48):
        """
        Syncs only orders with configurable lookback.
        """
        logger.info(f"Syncing orders (lookback={lookback_hours}h)...")
        self.sync_engine.sync_orders_incremental(lookback_hours=lookback_hours)
        logger.info("Orders sync completed.")

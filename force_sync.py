import sys
import os
import logging

# Add project root to path
sys.path.append(os.getcwd())

from app.services.sync_engine import SyncEngine
from app.core.database import SessionLocal

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def force_run():
    logger.info("FORCE SYNC: Starting...")
    try:
        engine = SyncEngine()
        logger.info("Engine initialized.")
        
        # 1. Sync Ads
        logger.info("Step 1: Sync Ads...")
        engine.sync_ads()
        logger.info("Step 1: Done.")
        
        # 2. Sync Metrics (Visits + Orders)
        logger.info("Step 2: Sync Metrics...")
        engine.sync_metrics()
        logger.info("Step 2: Done.")
        
        logger.info("FORCE SYNC: Completed Successfully.")
        
    except Exception as e:
        logger.error(f"FORCE SYNC FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    force_run()

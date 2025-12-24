import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from app.services.sync_engine import SyncEngine

# Configure logging to File
logging.basicConfig(
    filename='sync_debug_output.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

def force_run():
    logger.info("FORCE SYNC DEBUG: Starting...")
    try:
        engine = SyncEngine()
        logger.info("Engine initialized.")
        
        # Sync Orders ONLY to focus debug
        logger.info("Step: Sync Orders...")
        engine.sync_orders()
        logger.info("Step: Sync Orders Done.")
        
    except Exception as e:
        logger.error(f"FORCE SYNC FAILED: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    force_run()

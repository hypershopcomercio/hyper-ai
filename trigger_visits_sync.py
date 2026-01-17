
import logging
import datetime
from app.services.sync_engine import SyncEngine

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_sync():
    print("--- Triggering Manual Visits Sync ---")
    engine = SyncEngine()
    
    # Force sync
    engine.sync_visits()
    
    print("--- Sync Finished ---")

if __name__ == "__main__":
    run_sync()

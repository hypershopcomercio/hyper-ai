
import sys
import os
import logging

# Configure logging to see output
logging.basicConfig(level=logging.INFO)

sys.path.append(os.getcwd())

from app.services.sync_engine import SyncEngine

def run_sync():
    print("Starting manual sync...")
    try:
        engine = SyncEngine()
        engine.sync_ads()
        print("Manual sync completed successfully.")
    except Exception as e:
        print(f"Manual sync failed: {e}")

if __name__ == "__main__":
    run_sync()


import logging
from app.services.sync_engine import SyncEngine

# Configure logging to see output
logging.basicConfig(level=logging.INFO)

def run_sync():
    print("--- Starting Manual Tiny Sync ---")
    engine = SyncEngine()
    try:
        engine.sync_tiny_costs()
        print("--- Manual Sync Completed ---")
    except Exception as e:
        print(f"--- Sync Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_sync()

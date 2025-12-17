
from app.services.sync_engine import SyncEngine
import traceback

def debug_crash():
    print("--- Testing SyncEngine Instantiation ---")
    try:
        engine = SyncEngine()
        print("Instantiation OK.")
    except Exception as e:
        print("Crash on Init:")
        traceback.print_exc()
        return

    print("--- Testing sync_metrics ---")
    try:
        engine.sync_metrics()
        print("Sync Metrics OK.")
    except Exception as e:
        print("Crash on sync_metrics:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_crash()

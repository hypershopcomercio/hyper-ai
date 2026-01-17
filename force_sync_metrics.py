
import logging
import sys
from app.services.sync_engine import SyncEngine

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

print("Forcing sync_metrics...")
try:
    engine = SyncEngine()
    engine.sync_metrics()
    print("DONE.")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

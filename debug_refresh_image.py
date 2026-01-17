
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.services.sync_engine import SyncEngine
from app.jobs.forecast_jobs import run_hourly_reconciliation
import logging

# Configure logger to print to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SessionLocal()

print("--- SEARCHING FOR POOL AD ---")
ads = db.query(Ad).filter(Ad.title.ilike('%Piscina%')).limit(5).all()
for ad in ads:
    print(f"ID: {ad.id} | Title: {ad.title} | Pictures: {len(ad.pictures) if ad.pictures else 0}")

print("\n--- TESTING REFRESH LOGIC ---")
try:
    print("1. Testing Quick Sync (Orders)...")
    engine = SyncEngine()
    engine.sync_orders_incremental(lookback_hours=2)
    print(" Quick Sync OK.")
except Exception as e:
    print(f" Quick Sync FAILED: {e}")

try:
    print("2. Testing Reconciliation...")
    result = run_hourly_reconciliation()
    print(f" Reconciliation OK: {result}")
except Exception as e:
    print(f" Reconciliation FAILED: {e}")

db.close()


import logging
from app.services.sync_engine import SyncEngine
from app.core.database import SessionLocal
from app.models.ad import Ad
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_sync():
    logger.info("Starting Verification of Sync 1.4...")
    
    # 1. Run Sync
    engine = SyncEngine()
    engine.sync_ads()
    
    db = SessionLocal()
    
    # 2. Check Logs
    print("\n--- Checking Sync Logs ---")
    logs = db.execute(text("SELECT * FROM sync_logs ORDER BY created_at DESC LIMIT 1")).fetchone()
    if logs:
        print(f"Log Found: Type={logs.type}, Status={logs.status}, Processed={logs.records_processed}, Success={logs.records_success}")
    else:
        print("ERROR: No sync log found!")

    # 3. Check Ad Fields
    print("\n--- Checking Ad Fields ---")
    ad = db.query(Ad).filter(Ad.status == 'active').first()
    if ad:
        print(f"Ad: {ad.title} (ID: {ad.id})")
        print(f"  Health: {ad.health}")
        print(f"  Shipping Mode: {ad.shipping_mode}")
        print(f"  Listing Type: {ad.listing_type}")
        print(f"  Pictures (Count): {len(ad.pictures) if ad.pictures else 0}")
        print(f"  Attributes (Count): {len(ad.attributes) if ad.attributes else 0}")
        print(f"  Permalink: {ad.permalink}")
    else:
        print("No active ads found to check.")
        
    db.close()

if __name__ == "__main__":
    verify_sync()

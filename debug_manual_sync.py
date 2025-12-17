
import sys
import os
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure app is in path
sys.path.append(os.getcwd())

from app.services.meli_sync import MeliSyncService
from app.core.database import SessionLocal
from app.models.ad import Ad

print("--- STARTING MANUAL SYNC DEBUG ---")

try:
    service = MeliSyncService()
    
    # Check if we have a token first
    token = service.auth.get_valid_token()
    if not token:
        print("ERROR: No valid token found in DB. Please connect via UI first.")
        sys.exit(1)
        
    print(f"Token found (First 10 chars): {token[:10]}...")
    
    # Run Sync
    print("Executing sync_listings()...")
    result = service.sync_listings()
    
    print("Sync Result:", result)
    
    # Check DB Count
    db = SessionLocal()
    count = db.query(Ad).count()
    print(f"Total Ads in DB: {count}")
    db.close()

except Exception as e:
    print(f"CRITICAL ERROR DURING SYNC: {e}")
    import traceback
    traceback.print_exc()

print("--- END DEBUG ---")

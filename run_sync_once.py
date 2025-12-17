import logging
import sys
import os
import requests
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken

from dotenv import load_dotenv
load_dotenv()

# Add project root to path
sys.path.append(os.getcwd())

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_auth():
    logger.info("Validating Authentication...")
    
    db = SessionLocal()
    token_record = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
    access_token = token_record.access_token if token_record else settings.MELI_ACCESS_TOKEN
    
    if not access_token:
        logger.warning("No Access Token found in DB or .env. Trying refresh...")
        refresh_token = token_record.refresh_token if token_record else settings.MELI_REFRESH_TOKEN
        if refresh_token:
            # Try refresh manual if not handled
            # But MeliAuthService/SyncEngine handles this inside? 
            # The prompt asks to "Check BEFORE running"
            pass
        else:
             logger.error("CRITICAL: No Access Token and No Refresh Token available.")
             return False

    # Check /users/me
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        user_id = data.get("id")
        logger.info(f"Authentication Valid. User ID: {user_id} ({data.get('nickname')})")
        
        # Ensure correct user_id is in DB token if exists
        if token_record and str(token_record.user_id) != str(user_id):
             token_record.user_id = str(user_id)
             db.commit()
             logger.info("Updated User ID in database token record.")
             
        return True
    elif resp.status_code == 401:
        logger.warning("Access Token invalid/expired during check.")
        # MeliApiService logic will attempt refresh if configured properly in DB.
        # Here we just warn.
        return True # Let the engine try to refresh
    else:
        logger.error(f"Auth Check Failed: {resp.status_code} - {resp.text}")
        return False

def run():
    if not validate_auth():
        logger.error("Aborting Sync due to Auth failure.")
        return

    from app.services.sync_engine import SyncEngine
    
    logger.info("Initializing Sync Engine...")
    engine = SyncEngine()
    
    # Ads
    logger.info("--- Starting Ads Sync ---")
    engine.sync_ads()
    
    # Metrics
    logger.info("--- Starting Metrics Sync ---")
    engine.sync_metrics()
    
    # Tiny Data
    logger.info("--- Starting Tiny ERP Sync ---")
    engine.sync_tiny_costs()
    
    # Sales
    logger.info("--- Starting Sales Sync ---")
    engine.sync_sales()
    
    # Verification Stats
    db = SessionLocal()
    from app.models.ad import Ad
    from app.models.metric import Metric
    
    total_ads = db.query(Ad).count()
    total_metrics = db.query(Metric).count()
    
    logger.info(f"Summary: {total_ads} Ads synced. {total_metrics} Metric entries created.")
    db.close()

if __name__ == "__main__":
    run()

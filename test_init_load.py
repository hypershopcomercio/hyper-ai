import sys
import os
import logging
from app.core.database import SessionLocal
from app.services.sync_v2.initial_load import InitialLoadService
from app.models.oauth_token import OAuthToken

sys.path.append(os.getcwd())
logging.basicConfig(level=logging.INFO)

def test_init_load():
    db = SessionLocal()
    
    # Check Token
    token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
    if not token:
        print("No Token found!")
        return
        
    print(f"Token Found for {token.user_id}. Starting Sync Test...")
    
    service = InitialLoadService(db)
    
    # 1. Orders
    print("\n--- Testing Orders Load ---")
    try:
        service.load_orders()
        print("Orders Load Finished (Check DB logs for count)")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Orders Load Error: {e}")
        
    # 2. Ads
    print("\n--- Testing Ads Load ---")
    try:
        service.load_ads()
        print("Ads Load Finished (Check DB logs for count)")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Ads Load Error: {e}")
        
    db.close()

if __name__ == "__main__":
    test_init_load()

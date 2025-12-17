
import sys
import os
from datetime import datetime, timedelta, timezone

# Ensure app is in path
sys.path.append(os.getcwd())

from app.services.meli_auth import MeliAuthService
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken

print("--- STARTING TOKEN SAVE DEBUG ---")

try:
    auth_service = MeliAuthService()
    
    # Fake token data
    fake_token = {
        "access_token": "TEST_ACCESS_TOKEN_123",
        "refresh_token": "TEST_REFRESH_TOKEN_456",
        "expires_in": 21600,
        "user_id": "123456789"
    }
    
    print(f"Attempting to save fake token: {fake_token}")
    
    # Call the method
    saved_token = auth_service.save_tokens(fake_token)
    
    print("Save method executed.")
    
    # Verify in DB
    db = SessionLocal()
    token_in_db = db.query(OAuthToken).filter_by(user_id="123456789").first()
    
    if token_in_db:
        print("SUCCESS: Token found in database!")
        print(f"  - User ID: {token_in_db.user_id}")
        print(f"  - Access Token: {token_in_db.access_token}")
        print(f"  - Provider: {token_in_db.provider}")
    else:
        print("FAILURE: Token NOT found in database after save.")
        
    db.close()
    
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()

print("--- END DEBUG ---")

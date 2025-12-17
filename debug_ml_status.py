
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken
from app.services.meli_auth import MeliAuthService
import datetime

def debug_ml():
    db = SessionLocal()
    try:
        print("--- Checking ML Token in DB ---")
        token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        if not token:
            print("RESULT: No token found in database.")
        else:
            print(f"Token Found. ID: {token.id}")
            print(f"Expires At: {token.expires_at}")
            
            # Make now aware if token is aware
            now = datetime.datetime.now(datetime.timezone.utc) if token.expires_at.tzinfo else datetime.datetime.now()
            print(f"Current Time: {now}")
            
            if token.expires_at and token.expires_at < now:
                print("STATUS: Token Expired.")
            else:
                print("STATUS: Token Active.")
                
        print("\n--- Testing Auto-Refresh Logic ---")
        service = MeliAuthService()
        try:
            valid_token = service.get_valid_token()
            if valid_token:
                print("SUCCESS: get_valid_token() returned a token.")
                print(f"Token Preview: {valid_token[:10]}...")
            else:
                print("FAILURE: get_valid_token() returned None.")
        except Exception as e:
            print(f"ERROR calling get_valid_token(): {e}")
            import traceback
            traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    debug_ml()

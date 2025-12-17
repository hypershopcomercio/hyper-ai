import os
import sys
# Add current dir to sys.path
sys.path.append(os.getcwd())

from app.services.meli_auth import MeliAuthService
from app.core.config import settings

def main():
    print("--- Mercado Livre Auth Flow ---")
    
    if not settings.MELI_APP_ID or not settings.MELI_CLIENT_SECRET:
        print("Error: MELI_APP_ID or MELI_CLIENT_SECRET not set in .env")
        return

    service = MeliAuthService()
    url = service.get_auth_url()
    
    # Ensure tables exist
    from app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    print(f"\n1. Visit this URL in your browser:\n{url}\n")
    print("2. Authorize the application.")
    print("3. You will be redirected. Copy the 'code' parameter from the URL.")
    
    code = input("\nPaste the code here: ").strip()
    
    
    try:
        tokens = service.exchange_code_for_token(code)
        print("\n--- Success! ---")
        
        # Save to DB
        from app.core.database import SessionLocal
        from app.models.oauth_token import OAuthToken
        import datetime
        
        db = SessionLocal()
        # Upsert token for provider mercadolivre
        token_record = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        if not token_record:
            token_record = OAuthToken(provider="mercadolivre")
            db.add(token_record)
            
        token_record.access_token = tokens["access_token"]
        token_record.refresh_token = tokens["refresh_token"]
        token_record.user_id = str(tokens["user_id"])
        token_record.expires_at = datetime.datetime.now() + datetime.timedelta(seconds=tokens["expires_in"])
        db.commit()
        db.close()
        
        print(f"Token saved to OAuthToken table for User ID: {tokens.get('user_id')}")
        print("You can now run 'python main.py' to start the application (Authentication is handled automatically).")
        
    except Exception as e:
        print(f"\nError exchanging code: {e}")

if __name__ == "__main__":
    main()

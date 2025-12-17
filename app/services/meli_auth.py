import logging
import requests
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken

logger = logging.getLogger(__name__)

class MeliAuthService:
    def __init__(self):
        self.app_id = settings.MELI_APP_ID
        self.client_secret = settings.MELI_CLIENT_SECRET
        self.redirect_uri = settings.MELI_REDIRECT_URI

    def get_auth_url(self):
        import urllib.parse
        base_url = "https://auth.mercadolivre.com.br/authorization"
        params = {
            "response_type": "code",
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": "read:items write:items offline_access read:orders advertising"
        }
        return f"{base_url}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"

    def exchange_code_for_token(self, code: str):
        data = {
            "grant_type": "authorization_code",
            "client_id": self.app_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post("https://api.mercadolibre.com/oauth/token", data=data)
        response.raise_for_status()
        return response.json()

    def refresh_access_token(self, refresh_token: str):
        data = {
            "grant_type": "refresh_token",
            "client_id": self.app_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }
        response = requests.post("https://api.mercadolibre.com/oauth/token", data=data)
        response.raise_for_status()
        return response.json()

    def save_tokens(self, token_data):
        """
        Save or update tokens in the database using Upsert.
        """
        db = SessionLocal()
        from sqlalchemy.dialects.postgresql import insert
        
        try:
            user_id = str(token_data.get("user_id"))
            
            expires_in = token_data.get("expires_in", 21600)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            
            # Prepare data
            data = {
                "provider": "mercadolivre",
                "access_token": token_data["access_token"],
                "refresh_token": token_data["refresh_token"],
                "expires_at": expires_at,
                "user_id": user_id,
                "seller_id": user_id # Fallback
            }
            
            stmt = insert(OAuthToken).values(**data)
            
            # Upsert on conflict (provider)
            # Assuming 'provider' is unique or PK. 
            # If not unique, we rely on having one row per provider effectively.
            # But insert requires a constraint name or index element.
            # Let's hope 'provider' is unique or part of PK.
            # If 'id' is PK, we need a unique constraints on 'provider'.
            # Based on previous code: token = filter_by(provider=...) -> implies uniqueness is desired.
            
            update_dict = {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_at": data["expires_at"],
                "user_id": data["user_id"],
                "seller_id": data["seller_id"]
            }
            
            stmt = stmt.on_conflict_do_update(
                index_elements=["provider"], 
                set_=update_dict
            )
            
            db.execute(stmt)
            db.commit()
            
            # Fetch back to return object if needed by callers (though rarely used)
            return db.query(OAuthToken).filter_by(provider="mercadolivre").first()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving tokens: {e}")
            raise
        finally:
            db.close()

    def get_valid_token(self):
        """
        Returns a valid access token string. 
        Refreshes automatically if expired or expiring soon (< 30 min).
        """
        db = SessionLocal()
        try:
            token = db.query(OAuthToken).filter_by(provider="mercadolivre").first()
            if not token:
                logger.warning("No token found in database.")
                return None
            
            # Check expiration
            # If no expiry set, assume valid or broken. Let's assume valid but log warning.
            if not token.expires_at:
                return token.access_token
            
            # Ensure both are offset-aware
            now = datetime.now(timezone.utc)
            expiry = token.expires_at
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
                
            # If expired or expiring in less than 30 mins
            if expiry <= now + timedelta(minutes=30):
                logger.info("Token expired or expiring soon. Refreshing...")
                try:
                   refresh_data = self.refresh_access_token(token.refresh_token)
                   # save_tokens expects the full payload, ensuring it has user_id etc if ML returns it.
                   # ML refresh response might NOT include user_id, so we must be careful.
                   # We should update manually here to avoid overwriting user_id with None if missing
                   
                   token.access_token = refresh_data["access_token"]
                   token.refresh_token = refresh_data["refresh_token"]
                   # Update expiry
                   expires_in = refresh_data.get("expires_in", 21600)
                   token.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                   
                   db.commit()
                   logger.info("Token refreshed successfully.")
                   return token.access_token
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}")
                    # If refresh fails, return None or raise? None implies auth failure.
                    return None
            
            return token.access_token
        finally:
            db.close()



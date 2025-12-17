
import logging
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    load_access = settings.MELI_ACCESS_TOKEN
    load_refresh = settings.MELI_REFRESH_TOKEN
    
    if not load_access:
        logger.warning("No MELI_ACCESS_TOKEN found in settings/.env")
        return

    logger.info("Found tokens in .env/settings. Migrating to database...")
    
    db = SessionLocal()
    try:
        token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        if not token:
            token = OAuthToken(provider="mercadolivre")
            db.add(token)
            logger.info("Created new token record.")
        else:
            logger.info("Updating existing token record.")
            
        token.access_token = load_access
        token.refresh_token = load_refresh if load_refresh else "placeholder_refresh"
        # Set expiration to now + 1h just to be safe/active, or force refresh soon
        token.expires_at = datetime.datetime.now() + datetime.timedelta(hours=1)
        token.user_id = settings.MELI_USER_ID
        
        db.commit()
        logger.info("Migration successful.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()

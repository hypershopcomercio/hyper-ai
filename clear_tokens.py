
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken
from sqlalchemy import text

db = SessionLocal()
try:
    print("Deleting all 'mercadolivre' tokens...")
    db.execute(text("DELETE FROM oauth_tokens WHERE provider='mercadolivre'"))
    db.commit()
    print("Tokens cleared.")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()

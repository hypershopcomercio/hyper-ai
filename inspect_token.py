
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken

def inspect():
    db = SessionLocal()
    token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
    if token:
        print(f"Token Found.")
        print(f"Provider: {token.provider}")
        print(f"User ID: {token.user_id}")
        print(f"Expires At: {token.expires_at}")
        print(f"Updated At: {token.updated_at}")
        print(f"Refresh Token (last 10 chars): ...{token.refresh_token[-10:] if token.refresh_token else 'None'}")
    else:
        print("No token found in database.")
    db.close()

if __name__ == "__main__":
    inspect()

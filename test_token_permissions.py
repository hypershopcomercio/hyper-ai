
import requests
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken

def test():
    db = SessionLocal()
    token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
    db.close()
    
    if not token:
        print("No token in DB")
        return

    print(f"Testing token: {token.access_token[:10]}...")
    
    url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {token.access_token}"}
    
    try:
        resp = requests.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()


import logging
import requests
from app.services.meli_auth import MeliAuthService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_sync():
    auth = MeliAuthService()
    token = auth.get_valid_token()
    
    if not token:
        print("No valid token found!")
        return

    print(f"Token: {token[:10]}...")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get Me
    try:
        res = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
        res.raise_for_status()
        me = res.json()
        print(f"User ID: {me['id']}")
        print(f"Nickname: {me['nickname']}")
    except Exception as e:
        print(f"Failed /users/me: {e}")
        if 'res' in locals():
            print(res.text)
        return

    seller_id = me['id']

    # 2. Try Scan Search
    try:
        url = f"https://api.mercadolibre.com/users/{seller_id}/items/search?search_type=scan&limit=50"
        print(f"Requesting: {url}")
        res = requests.get(url, headers=headers)
        print(f"Status: {res.status_code}")
        if res.status_code != 200:
             print("Error Body:", res.text)
        else:
             data = res.json()
             print("Success!")
             print("Results count:", len(data.get("results", [])))
             if data.get("results"):
                 print("First Item:", data["results"][0])

    except Exception as e:
        print(f"Failed search: {e}")

if __name__ == "__main__":
    debug_sync()

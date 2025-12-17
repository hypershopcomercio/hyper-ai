
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken
import requests
import json

def debug_shipping():
    db = SessionLocal()
    try:
        # Fetch token
        token_entry = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        if not token_entry:
            print("No auth token found.")
            return
        token = token_entry.access_token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get User ID
        me = requests.get("https://api.mercadolibre.com/users/me", headers=headers).json()
        user_id = me["id"]
        
        item_id = "MLB5238169050" # Piscina
        
        # Endpoint: Shipping Options Free
        # https://api.mercadolibre.com/users/{User_id}/shipping_options/free?item_id={Item_id}
        url = f"https://api.mercadolibre.com/users/{user_id}/shipping_options/free?item_id={item_id}"
        
        print(f"--- Fetching Free Shipping Cost for {item_id} ---")
        res = requests.get(url, headers=headers)
        
        if res.status_code == 200:
            print(json.dumps(res.json(), indent=2))
        else:
            print(f"Error {res.status_code}: {res.text}")
            
    except Exception as e:
        print(f"Crash: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_shipping()

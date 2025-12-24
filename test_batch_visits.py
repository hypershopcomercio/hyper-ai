import sys
import os
import requests
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken

def test_batch():
    db = SessionLocal()
    token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
    if not token:
        print("No token")
        return

    # 1. Get a few item IDs
    from app.services.meli_api import MeliApiService
    service = MeliApiService(db)
    items = service.get_user_items(token.user_id)
    if not items:
        print("No items")
        return
        
    chunk = items[:5]
    print(f"Testing batch visits for: {chunk}")
    
    ids_str = ",".join(chunk)
    url = "https://api.mercadolibre.com/items/visits"
    headers = {"Authorization": f"Bearer {token.access_token}"}
    params = {"ids": ids_str}
    
    print(f"Request: {url}?ids=...")
    r = requests.get(url, params=params, headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
    
    # Check if time_window works with batch
    # url_window = "https://api.mercadolibre.com/items/visits/time_window" # Guessing?
    # Usually batch endpoints are root level.
    # What if we want time window?
    # Official docs say /items/{id}/visits.
    # There might be /visits/time_window?ids=... or similar?
    # Let's try params on the batch endpoint.
    
    params_window = {"ids": ids_str, "date_from": "2024-12-01", "date_to": "2024-12-20"}
    r2 = requests.get(url, params=params_window, headers=headers)
    print(f"Batch+Date Status: {r2.status_code}")
    print(f"Batch+Date Response: {r2.text[:500]}")

if __name__ == "__main__":
    test_batch()

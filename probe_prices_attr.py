
import requests
import logging
from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal
import json

logging.basicConfig(level=logging.INFO)

def probe_prices_attr():
    db = SessionLocal()
    service = MeliApiService(db)
    
    item_id = "MLB3862661909"
    print(f"Probing prices attribute for {item_id}...")
    
    try:
        # endpoint: /items?ids={id}&attributes=id,price,original_price,prices
        # We simulate the batch call logic
        ids_str = item_id
        url = f"{service.base_url}/items"
        params = {"ids": ids_str, "attributes": "id,price,original_price,prices"}
        
        response = requests.get(url, params=params, headers=service.get_headers())
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
             print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe_prices_attr()

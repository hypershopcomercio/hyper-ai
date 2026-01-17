
import requests
import logging
from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal
import json

logging.basicConfig(level=logging.INFO)

def probe_prices():
    db = SessionLocal()
    service = MeliApiService(db)
    
    item_id = "MLB3862661909"
    print(f"Probing Prices for {item_id}...")
    
    try:
        # endpoint: /items/{id}
        endpoint = f"/items/{item_id}"
        print(f"Calling {endpoint}...")
        
        # MeliApiService.request returns a requests.Response object
        response = service.request("GET", endpoint)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Keys: {list(data.keys())}")
            if "pictures" in data:
                print(f"Pictures found: {len(data['pictures'])}")
                print(json.dumps(data['pictures'], indent=2))
            else:
                print("Pictures NOT found in response!")
        else:
            print(f"Error Body: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe_prices()

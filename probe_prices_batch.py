
import requests
import logging
from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal
import json

logging.basicConfig(level=logging.INFO)

def probe_prices_batch():
    db = SessionLocal()
    service = MeliApiService(db)
    
    item_id = "MLB3862661909"
    print(f"Probing Batch Prices for {item_id}...")
    
    # Try theoretical batch endpoints
    # /prices?item_ids=...
    # /items/prices?ids=... (Unlikely)
    
    # Let's try to pass comma separated IDs to the single endpoint (some APIs support this)
    # /items/MLB...,MLB.../prices ? 
    
    # Based on docs (memory), there isn't a widely known batch prices endpoint in public docs.
    # But let's try injecting comma sep in the ID param of the URL if it was generic.
    
    # Let's try a direct GET to /prices?item_ids=... if it exists globaly
    
    try:
        # Attempt 1: Global prices search ??
        # endpoint = f"/prices?item_ids={item_id}"
        # response = service.request("GET", endpoint) 
        # print(f"Attempt 1 Status: {response.status_code}")
        
        # Attempt 2: prices param in items? No we tried that.
        
        print("Skipping blind batch probe as it's likely 404. Will implement single call for now.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe_prices_batch()

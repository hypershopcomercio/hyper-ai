"""
Debug script to test ML Ads API - detailed response check
"""
import sys
sys.path.insert(0, '.')

import requests
from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService

def main():
    db = SessionLocal()
    
    try:
        meli = MeliApiService(db_session=db)
        
        print("=" * 60)
        print("TESTING ADVERTISER ID LOOKUP")
        print("=" * 60)
        
        # Test the advertiser endpoint directly
        url = "https://api.mercadolibre.com/advertising/advertisers"
        params = {"product_id": "PADS"}
        headers = {**meli.get_headers(), "Api-Version": "1"}
        
        print(f"\nURL: {url}")
        print(f"Params: {params}")
        print(f"Token (first 20 chars): {meli.access_token[:20] if meli.access_token else 'None'}...")
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        print(response.text[:1000] if response.text else "(empty)")
        
        # If we got a 200, parse it
        if response.status_code == 200:
            data = response.json()
            print(f"\nParsed JSON keys: {data.keys() if isinstance(data, dict) else type(data)}")
            if isinstance(data, dict):
                advertiser_id = data.get("id")
                site_id = data.get("site_id")
                print(f"advertiser_id: {advertiser_id}")
                print(f"site_id: {site_id}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()

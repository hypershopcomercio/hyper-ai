import sys
import os
import requests
import json
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def test_recent_endpoint():
    db = SessionLocal()
    service = MeliApiService(db)
    
    existing = db.query(MlOrder).first()
    seller_id = existing.seller_id if existing else None
    
    if not seller_id:
        print("No seller_id")
        return

    print(f"Testing RECENT endpoint for Seller: {seller_id}")
    
    # Try /orders/search/recent
    url = f"{service.base_url}/orders/search/recent"
    headers = service.get_headers()
    params = {
        "seller": seller_id,
        "limit": 50
    }
    
    print(f"GET {url}")
    try:
        resp = requests.get(url, headers=headers, params=params)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            orders = data.get('results', [])
            print(f"Found {len(orders)} orders.")
            
            print("Top 5 Recent Orders:")
            for i, o in enumerate(orders[:5]):
                 print(f"#{i+1} ID: {o.get('id')} | Date: {o.get('date_created')} | Val: {o.get('total_amount')}")
        else:
            print(f"Error Body: {resp.text}")
            
    except Exception as e:
        print(f"Ex: {e}")
        
    db.close()

if __name__ == "__main__":
    test_recent_endpoint()

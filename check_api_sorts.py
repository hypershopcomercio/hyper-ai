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

def check_sorts():
    db = SessionLocal()
    service = MeliApiService(db)
    
    existing = db.query(MlOrder).first()
    seller_id = existing.seller_id if existing else None
    
    url = f"{service.base_url}/orders/search"
    headers = service.get_headers()
    params = {
        "seller": seller_id,
        "limit": 1
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()
        print("Available Sorts:")
        print(json.dumps(data.get('available_sorts', []), indent=2))
        print("Available Filters:")
        print(json.dumps(data.get('available_filters', []), indent=2))
        
    except Exception as e:
        print(f"Ex: {e}")
        
    db.close()

if __name__ == "__main__":
    check_sorts()

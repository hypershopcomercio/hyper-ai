import sys
import os
import requests
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def test_instant_sync():
    db = SessionLocal()
    service = MeliApiService(db)
    
    # Get Seller ID
    existing = db.query(MlOrder).first()
    seller_id = existing.seller_id if existing else None
    
    if not seller_id:
        print("No seller_id found.")
        return

    print(f"Testing Instant Sync for Seller: {seller_id}")
    
    # 1. Current Method (With Date Filter)
    now = datetime.now(timezone.utc)
    date_from = (now - timedelta(hours=24)).strftime("%Y-%m-%dT00:00:00.000-00:00")
    
    print("\n--- Method 1: Date Filter (Current) ---")
    url = f"{service.base_url}/orders/search"
    headers = service.get_headers()
    params_1 = {
        "seller": seller_id,
        "sort": "date_desc",
        "limit": 10,
        "order.date_created.from": date_from
    }
    
    try:
        resp1 = requests.get(url, headers=headers, params=params_1)
        if resp1.status_code == 200:
            data1 = resp1.json()
            orders1 = data1.get('results', [])
            print(f"Found {len(orders1)} orders.")
            if orders1:
                print(f"Top 1 ID: {orders1[0].get('id')} | Date: {orders1[0].get('date_created')}")
        else:
            print(f"Error: {resp1.status_code}")
            
    except Exception as e:
        print(f"Ex 1: {e}")

    # 2. Proposed Method (No Date Filter, Just Sort)
    print("\n--- Method 2: Head Sync (No Filter) ---")
    params_2 = {
        "seller": seller_id,
        "sort": "date_desc",
        "limit": 50 # Grab more to be safe
    }
    
    try:
        resp2 = requests.get(url, headers=headers, params=params_2)
        if resp2.status_code == 200:
            data2 = resp2.json()
            orders2 = data2.get('results', [])
            print(f"Found {len(orders2)} orders (Limit 50).")
            
            # Print top 5 IDs and dates
            print("Top 5 Orders (No Filter):")
            for i, o in enumerate(orders2[:5]):
                print(f"#{i+1} ID: {o.get('id')} | St: {o.get('status')} | Date: {o.get('date_created')} | Val: {o.get('total_amount')}")
                
            # Check if any ID from Method 2 is NEWER than Method 1 or effectively same?
            # Or if Method 2 returns the missing orders we suspect.
            
    except Exception as e:
        print(f"Ex 2: {e}")
        
    db.close()

if __name__ == "__main__":
    test_instant_sync()

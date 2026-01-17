
import sys
import os
import logging
import requests
import json
from datetime import datetime

# Add project root
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.services.meli_api import MeliApiService

logging.basicConfig(level=logging.INFO)

def scan_endpoints():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        headers = service.get_headers()
        
        # 1. Get Seller ID
        me_res = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
        seller_id = me_res.json()["id"]
        print(f"Seller ID: {seller_id}")
        
        # 2. Get a Full Ad
        ad = db.query(Ad).filter(Ad.is_full == True).first()
        if not ad:
            print("No Full ad found in DB. Searching API...")
            # Fallback to search
            pass
        else:
            print(f"Target Ad: {ad.id} (Full: {ad.is_full})")
            
            # 3. Test Endpoints
            endpoints = [
                # Inbound Shipments (User says "Transfer")
                f"https://api.mercadolibre.com/inbound/shipments/search?seller_id={seller_id}&status=shipped,closed,delivered,created",
                
                # Fulfillment Operations (User says "Processing")
                f"https://api.mercadolibre.com/stock/fulfillment/operations/search?seller_id={seller_id}",
                f"https://api.mercadolibre.com/stock/fulfillment/operations/search?seller_id={seller_id}&filters=status:in_transfer",
                f"https://api.mercadolibre.com/stock/fulfillment/operations/search?seller_id={seller_id}&filters=inventory_id:{ad.id}", # Incorrect ID usage likely, but probing
                
                # Item Specifics
                f"https://api.mercadolibre.com/items/{ad.id}?include_attributes=all",
                
                # Inventory (If inventory_id known, we'll try to get it from item)
            ]

            # First fetching item to get inventory_id
            item_res = requests.get(endpoints[4], headers=headers)
            if item_res.status_code == 200:
                item_data = item_res.json()
                inv_id = item_data.get('inventory_id')
                if inv_id:
                    print(f"Found Inventory ID: {inv_id}")
                    endpoints.append(f"https://api.mercadolibre.com/inventory/items/{inv_id}")
                    endpoints.append(f"https://api.mercadolibre.com/inventory/items/{inv_id}/stock_operations") # Hypothetical

            # Execute Scan
            for url in endpoints:
                print(f"\n--- GET {url} ---")
                res = requests.get(url, headers=headers)
                print(f"Status: {res.status_code}")
                if res.status_code == 200:
                    try:
                        data = res.json()
                        # Summarize
                        if isinstance(data, dict):
                            print(f"Keys: {list(data.keys())}")
                            if "results" in data:
                                print(f"Results Count: {len(data['results'])}")
                                if len(data['results']) > 0:
                                    print(json.dumps(data['results'][0], indent=2)[:500])
                            elif "total" in data:
                                print(f"Total: {data['total']}")
                            else:
                                print(json.dumps(data, indent=2)[:500])
                        elif isinstance(data, list):
                             print(f"List length: {len(data)}")
                    except:
                        print("Text response (not JSON)")
                else:
                    print(f"Error: {res.text[:200]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    scan_endpoints()

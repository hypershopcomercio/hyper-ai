
import sys
import os
import logging
import requests
import json

# Add project root
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService

# Config
ITEM_ID = "MLB3964133363" # The Cooler from the screenshot
logging.basicConfig(level=logging.INFO)

def probe_cooler():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        headers = service.get_headers()
        
        print(f"--- 1. INSPECT ITEM {ITEM_ID} ---")
        url_item = f"https://api.mercadolibre.com/items/{ITEM_ID}?include_attributes=all"
        res = requests.get(url_item, headers=headers)
        if res.status_code == 200:
            data = res.json()
            print(f"Title: {data.get('title')}")
            print(f"Inventory ID: {data.get('inventory_id')}")
            print(f"Listing Type: {data.get('listing_type_id')}")
            print(f"Channels: {data.get('channels')}")
            
            inventory_id = data.get('inventory_id')
            
            if inventory_id:
                print(f"\n--- 2. PROBE INVENTORY {inventory_id} ---")
                
                # Try standard inventory endpoint
                url_inv = f"https://api.mercadolibre.com/inventory/items/{inventory_id}"
                print(f"GET {url_inv}")
                res_inv = requests.get(url_inv, headers=headers)
                print(f"Status: {res_inv.status_code}")
                if res_inv.status_code == 200:
                    print(json.dumps(res_inv.json(), indent=2))
                    
                # Try stock operations search
                # Based on doc: /stock/fulfillment/operations/search
                print(f"\n--- 3. PROBE STOCK OPERATIONS ---")
                seller_id = data.get('seller_id')
                
                # Attempt 1: By Inventory ID
                url_ops1 = f"https://api.mercadolibre.com/stock/fulfillment/operations/search?seller_id={seller_id}&filters=inventory_id:{inventory_id}"
                print(f"GET {url_ops1}")
                res_ops1 = requests.get(url_ops1, headers=headers)
                print(f"Status: {res_ops1.status_code}")
                print(res_ops1.text[:500])
                
                # Attempt 2: By Item ID
                url_ops2 = f"https://api.mercadolibre.com/stock/fulfillment/operations/search?seller_id={seller_id}&filters=item_id:{ITEM_ID}"
                print(f"GET {url_ops2}")
                res_ops2 = requests.get(url_ops2, headers=headers)
                print(f"Status: {res_ops2.status_code}")
                print(res_ops2.text[:500])
                
        else:
            print(f"Failed to get item: {res.status_code}")
            print(res.text)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    probe_cooler()

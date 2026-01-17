
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
INVENTORY_ID = "FLJN76852"
SELLER_ID = "1400902328"
logging.basicConfig(level=logging.INFO)

def probe_full_retry():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        headers = service.get_headers()
        
        print(f"--- RETRYING FULL API FOR {INVENTORY_ID} ---")
        
        endpoints = [
            # 1. Try inventory_id as direct param
            f"https://api.mercadolibre.com/stock/fulfillment/operations/search?inventory_id={INVENTORY_ID}",
             
            # 2. Try POST method for search (sometimes required for complex filters)
            # (Note: GET is standard for search but sometimes...)
            
            # 3. Fulfillment Stock (Direct)
            f"https://api.mercadolibre.com/stock/fulfillment/inventory/{INVENTORY_ID}",
            
            # 4. Inbound Shipments (Broader Search)
            f"https://api.mercadolibre.com/inbound/shipments/search?seller_id={SELLER_ID}&status=shipped",
            
            # 5. Items Relations (Maybe linked to another ID?)
            f"https://api.mercadolibre.com/items/MLB3964133363/stock/fulfillment"
        ]

        for url in endpoints:
            print(f"\n--- GET {url} ---")
            res = requests.get(url, headers=headers)
            print(f"Status: {res.status_code}")
            if res.status_code == 200:
                print(json.dumps(res.json(), indent=2)[:500])
            else:
                print(res.text[:300])

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    probe_full_retry()


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
ITEM_ID = "MLB3964133363"
logging.basicConfig(level=logging.INFO)

def probe_cooler_v2():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        headers = service.get_headers()
        
        print(f"--- 1. INSPECT ITEM {ITEM_ID} (RAW) ---")
        url_item = f"https://api.mercadolibre.com/items/{ITEM_ID}"
        res = requests.get(url_item, headers=headers)
        if res.status_code == 200:
            data = res.json()
            # Safely print keys and inventory_id
            print(f"Keys available: {list(data.keys())}")
            print(f"Inventory ID: {data.get('inventory_id')}")
            
            # Print a snippet of the JSON to check structure if needed
            print(json.dumps(data, indent=2)[:500])
        else:
            print(f"Failed to get item: {res.status_code}")
            print(res.text)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    probe_cooler_v2()

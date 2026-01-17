
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
SELLER_ID = "1400902328" # Confirmed from previous step
logging.basicConfig(level=logging.INFO)

def probe_stock():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        headers = service.get_headers()
        
        print(f"--- PROBING INVENTORY: {INVENTORY_ID} ---")
        
        # 1. Fulfillment Operations Search
        url = f"https://api.mercadolibre.com/stock/fulfillment/operations/search?seller_id={SELLER_ID}&filters=inventory_id:{INVENTORY_ID}"
        print(f"GET {url}")
        res = requests.get(url, headers=headers)
        print(f"Status: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            print(json.dumps(data, indent=2))
        else:
            print(res.text)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    probe_stock()


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
logging.basicConfig(level=logging.INFO)

def probe_official_doc():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        headers = service.get_headers()
        
        # Endpoint extracted from User Screenshots
        # https://api.mercadolibre.com/inventories/$INVENTORY_ID/stock/fulfillment
        
        url = f"https://api.mercadolibre.com/inventories/{INVENTORY_ID}/stock/fulfillment"
        
        print(f"--- TESTING OFFICIAL DOC ENDPOINT ---")
        print(f"GET {url}")
        
        res = requests.get(url, headers=headers)
        print(f"Status: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            print(json.dumps(data, indent=2))
            
            # Check for 'transfer' in details
            details = data.get('not_available_detail', [])
            transfer_qty = 0
            for d in details:
                if d.get('status') == 'transfer':
                    transfer_qty = d.get('quantity', 0)
                    print(f"\n>>> FOUND TRANSFER STOCK: {transfer_qty} <<<")
        else:
            print(f"Error Response: {res.text}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    probe_official_doc()

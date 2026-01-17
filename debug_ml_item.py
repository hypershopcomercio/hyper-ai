
import sys
import os
import logging
import json
import requests
from sqlalchemy import text

# Add project root to path
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.services.meli_api import MeliApiService

# Config logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_item():
    db = SessionLocal()
    try:
        # Find a fulfillment item
        print("Searching for a Fulfillment Ad in DB...")
        ads = db.query(Ad).filter(Ad.is_full == True).limit(5).all()
        
        target_ad = None
        if ads:
            print(f"Found {len(ads)} Full ads in DB.")
            target_ad = ads[0]
        else:
            print("No Full ads found in DB. Searching via API scan...")
            target_ad = db.query(Ad).filter(Ad.status == 'active').first()

        if not target_ad:
            print("No ads found in DB.")
            return

        print(f"Inspecting Ad: {target_ad.id} ({target_ad.title}) - Full: {target_ad.is_full}")
        
        # Initialize Service
        meli_service = MeliApiService(db_session=db)
        headers = meli_service.get_headers()
        
        # 1. Fetch Item Data
        print("Fetching Item Data...")
        url = f"https://api.mercadolibre.com/items/{target_ad.id}?include_attributes=all"
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            shipping = data.get("shipping", {})
            logistic_type = shipping.get('logistic_type')
            print(f"Logistic Type: {logistic_type}")
            print(f"Inventory ID: {data.get('inventory_id')}")
            
            # 2. If allow, valid inventory_id check
            inv_id = data.get('inventory_id')
            if inv_id:
                print(f"Fetching Inventory {inv_id}...")
                inv_url = f"https://api.mercadolibre.com/inventory/items/{inv_id}"
                inv_res = requests.get(inv_url, headers=headers)
                if inv_res.status_code == 200:
                    inv_data = inv_res.json()
                    print(json.dumps(inv_data, indent=2))
                else:
                    print(f"Inventory fetch failed: {inv_res.status_code}")
            else:
                print("No inventory_id found on item.")

        else:
             print(f"Error fetching item: {res.status_code} - {res.text}")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_item()

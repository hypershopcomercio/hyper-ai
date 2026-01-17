
import sys
import os
import logging
import requests
import json

# Add project root
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService

logging.basicConfig(level=logging.INFO)

def probe_inbound():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        headers = service.get_headers()
        
        # Get Seller ID
        me_res = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
        if me_res.status_code != 200:
            print("Failed to get user me")
            return
        seller_id = me_res.json()["id"]
        print(f"Seller ID: {seller_id}")
        
        # List of candidate endpoints to probe
        endpoints = [
            f"https://api.mercadolibre.com/stock/fulfillment/operations/search?seller_id={seller_id}&filters=status:in_transfer",
            f"https://api.mercadolibre.com/stock/fulfillment/operations/search?seller_id={seller_id}",
            f"https://api.mercadolibre.com/inbound/shipments/search?seller_id={seller_id}&status=created",
            f"https://api.mercadolibre.com/inbound/shipments/search?seller_id={seller_id}",
            f"https://api.mercadolibre.com/users/{seller_id}/informativos/actionable_items", # Sometimes useful
        ]
        
        for url in endpoints:
            print(f"\nProbing: {url}")
            res = requests.get(url, headers=headers)
            print(f"Status: {res.status_code}")
            if res.status_code == 200 and res.content:
                try:
                    data = res.json()
                    # Check if empty
                    is_empty = False
                    if isinstance(data, dict):
                        if "paging" in data and data.get("paging", {}).get("total", 0) == 0:
                            is_empty = True
                        if "results" in data and len(data["results"]) == 0:
                            is_empty = True
                    
                    print(f"Empty Result: {is_empty}")
                    if not is_empty:
                        print("Sample Data:")
                        print(json.dumps(data, indent=2)[:500] + "...")
                except:
                    print(f"Response: {res.text[:200]}")
            else:
                 print(f"Error: {res.text[:200]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    probe_inbound()


import sys
import os
import logging
import requests
import json
from datetime import datetime

# Add project root
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService

logging.basicConfig(level=logging.INFO)

def probe_shipments():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        headers = service.get_headers()
        
        # Get Seller ID
        me_res = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
        seller_id = me_res.json()["id"]
        print(f"Seller ID: {seller_id}")
        
        # 1. Search Shipments
        # status: handling, ready_to_ship, shipped, delivered, not_delivered, cancelled
        # inbound status: created, shipped, delivered, closed, error
        # We want 'shipped' (in transit to CD) or 'processing' inside CD?
        # Let's list ALL active inbound shipments
        
        url = f"https://api.mercadolibre.com/inbound/shipments/search?seller_id={seller_id}&status=shipped,closed,delivered,created" 
        # Note: 'closed' might mean finished, 'shipped' is transfer.
        
        print(f"\nFetching Inbound Shipments: {url}")
        res = requests.get(url, headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            results = data.get("results", [])
            print(f"Found {len(results)} shipments.")
            
            for shipment in results:
                sid = shipment.get("id")
                status = shipment.get("status")
                substatus = shipment.get("substatus")
                
                print(f"\n--- Shipment {sid} ({status}/{substatus}) ---")
                
                # Get Shipment Details to see items
                # Usually /inbound/shipments/{id}
                s_url = f"https://api.mercadolibre.com/inbound/shipments/{sid}"
                s_res = requests.get(s_url, headers=headers)
                if s_res.status_code == 200:
                    s_data = s_res.json()
                    # print(json.dumps(s_data, indent=2))
                    
                    # Look for items
                    # Typically "items" or "lines"
                    # Try to find quantity sent vs received
                    # If status is "shipped", mapped to transfer.
                    
                    print(json.dumps(s_data, indent=2))
                    
                else:
                    print(f"Failed to fetch details for {sid}")
                
                # Limit to first 3 for brevity
                if results.index(shipment) >= 2:
                    break
        else:
             print(f"Error fetching shipments: {res.text}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    probe_shipments()

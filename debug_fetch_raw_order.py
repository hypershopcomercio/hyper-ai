
import json
import logging
from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService

# Helper to print full JSON
def serialize(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj)

def fetch_raw():
    db = SessionLocal()
    service = MeliApiService(db_session=db)
    
    # Target IDs (Suspicious Shipping)
    # ID for 219.90 (Suspected part of 388 diff)
    ids = ["2000014403184862"]
    
    print(f"--- FETCHING RAW ORDER (SUSPECTED 219.90) ---")
    
    for oid in ids:
        print(f"\nID: {oid}")
        try:
            # We use get_orders logic or just a raw request if we want generic endpoint
            # Since get_order is not exposed as public generic method easily in service without list wrapper,
            # We can use the internal 'request' method explicitly or 'get_item_details' but for orders.
            # MeliApiService usually has 'get_orders' that takes seller_id etc.
            # Ensure slash is handled if base_url misses it
            endpoint = f"/orders/{oid}"
            resp = service.request("GET", endpoint)
            if resp.status_code == 200:
                data = resp.json()
                payments = data.get('payments', [])
                print(f"ID: {oid}")
                for p in payments:
                    print(f" PayID: {p.get('id')} | Stat: {p.get('status')} | Det: {p.get('status_detail')} | Type: {p.get('payment_type_id')}")
                print("-" * 20)
            else:
                print(f"Error {resp.status_code}")
                
        except Exception as e:
            print(f"Exception: {e}")
            
    db.close()

if __name__ == "__main__":
    fetch_raw()

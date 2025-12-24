
import datetime
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.services.meli_api import MeliApiService

def find_missing():
    db = SessionLocal()
    service = MeliApiService(db_session=db)
    
    # Yesterday 2025-12-22
    # In API search we need precise window.
    # RFC3339 format
    date_from = "2025-12-22T00:00:00.000-03:00"
    date_to = "2025-12-22T23:59:59.999-03:00"
    
    # Search orders
    # /orders/search?seller=...&order.date_created.from=...&order.date_created.to=...
    seller_id = "1400902328" # Extracted from previous raw
    
    params = {
        "seller": seller_id,
        "order.date_created.from": date_from,
        "order.date_created.to": date_to,
        "limit": 50,
        "offset": 0
    }
    
    print(f"--- SEARCHING MISSING ORDERS (API vs DB) ---")
    
    api_ids = set()
    total_api = 0
    
    try:
        while True:
            resp = service.request("GET", "/orders/search", params=params)
            if resp.status_code != 200:
                print(f"Error searching: {resp.status_code}")
                break
                
            data = resp.json()
            results = data.get("results", [])
            if not results:
                break
                
            for r in results:
                api_ids.add(str(r["id"]))
            
            total_api = data.get("paging", {}).get("total", 0)
            
            if len(api_ids) >= total_api:
                break
                
            params["offset"] += 50
            
    except Exception as e:
        print(f"Exception: {e}")
        
    print(f"Total API Orders Found: {len(api_ids)}")
    
    # Get DB IDs
    db_orders = db.query(MlOrder).filter(
        MlOrder.date_created >= datetime.datetime(2025, 12, 22, 0, 0, 0),
        MlOrder.date_created < datetime.datetime(2025, 12, 23, 0, 0, 0)
    ).all()
    
    db_ids = set(o.ml_order_id for o in db_orders)
    print(f"Total DB Orders Found: {len(db_ids)}")
    
    missing = api_ids - db_ids
    extra = db_ids - api_ids
    
    print(f"MISSING IN DB ({len(missing)}):")
    for mid in missing:
        print(f"MISSING ID: {mid}")
        # Fetch details to check value
        resp = service.request("GET", f"/orders/{mid}")
        if resp.status_code == 200:
            d = resp.json()
            val = d.get("total_amount")
            status = d.get("status")
            print(f" -> Val: {val} | Status: {status}")
            
    print(f"EXTRA IN DB ({len(extra)}):")
    for eid in extra:
        print(f"EXTRA ID: {eid}")

    db.close()

if __name__ == "__main__":
    find_missing()

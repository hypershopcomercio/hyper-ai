import sys
import os
import json
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Add current dir
sys.path.append(os.getcwd())
load_dotenv()

from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal

def test_api():
    db = SessionLocal()
    service = MeliApiService(db)
    
    from app.models.ml_order import MlOrder
    existing = db.query(MlOrder).first()
    seller_id = existing.seller_id if existing else None
    
    if not seller_id:
        print("No seller_id found in DB. Cannot test.")
        return

    print(f"Testing API for Seller: {seller_id}")
    
    now = datetime.now(timezone.utc)
    date_from = (now - timedelta(hours=24)).strftime("%Y-%m-%dT00:00:00.000-00:00")
    
    print(f"Fetching from: {date_from}")
    try:
        # 1. Standard Fetch
        orders = service.get_orders(seller_id, date_from=date_from)
        print(f"Found {len(orders)} orders.")
        
        # Analyze one order
        if orders:
            o = orders[0]
            print("\nSAMPLE ORDER ANALYSIS:")
            print(f"ID: {o.get('id')}")
            total = float(o.get('total_amount', 0))
            paid = float(o.get('paid_amount', 0))
            
            items_sum = 0.0
            for i in o.get('order_items', []):
                items_sum += float(i.get('unit_price', 0)) * int(i.get('quantity', 1))
            
            shipping = o.get('shipping', {})
            ship_cost = float(shipping.get('cost', 0) or 0) # sometimes null
            
            print(f"Total Amount: {total}")
            print(f"Paid Amount: {paid}")
            print(f"Items Sum: {items_sum}")
            print(f"Shipping Cost (in object): {ship_cost}")
            
            diff = total - items_sum
            print(f"Diff (Total - Items): {diff}")
        
        # 2. Explicit Pending Check
        print("\nChecking Explicit 'payment_required':")
        params = {"seller": seller_id, "order.status": "payment_required", "order.date_created.from": date_from}
        url = f"{service.base_url}/orders/search"
        headers = service.get_headers()
        
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            p_orders = resp.json().get('results', [])
            print(f"Found {len(p_orders)} payment_required orders.")
            for po in p_orders:
                print(f" - ID: {po.get('id')} | Val: {po.get('total_amount')}")
        else:
            print(f"Non-200 for Pending: {resp.status_code}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_api()

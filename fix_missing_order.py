import sys
import os
import datetime
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.services.sync_engine import SyncEngine
from app.services.meli_api import MeliApiService
from app.models.oauth_token import OAuthToken

def force_sync_single_order(ml_order_id):
    db = SessionLocal()
    try:
        engine = SyncEngine()
        token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        headers = {"Authorization": f"Bearer {token.access_token}"}
        
        print(f"Fetching Order {ml_order_id} from API...")
        import requests
        url = f"https://api.mercadolibre.com/orders/{ml_order_id}"
        r = requests.get(url, headers=headers)
        
        if r.status_code == 200:
            order_data = r.json()
            print(f"Fetched Data. Date: {order_data['date_created']}")
            
            # Use engine processing
            # We need to expose _process_order_full or use a trick?
            # It's private but python allows access.
            engine._process_order_full(order_data)
            engine.db.commit()
            print("Order synced successfully.")
        else:
            print(f"Failed to fetch order: {r.status_code} - {r.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    force_sync_single_order("2000014414139106")

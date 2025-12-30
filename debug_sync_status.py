
import sys
import os
from datetime import datetime, timedelta, timezone

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.sync import SyncControl
from app.models.ml_order import MlOrder
from app.services.meli_api import MeliApiService


def debug_sync():
    with open("sync_debug_output.txt", "w", encoding="utf-8") as f:
        def log(msg):
             print(msg)
             f.write(str(msg) + "\n")
        
        db = SessionLocal()
        try:
            log("--- Sync Control Status ---")
            control = db.query(SyncControl).filter(SyncControl.entity == 'orders').first()
            if control:
                log(f"Last Incremental Sync: {control.last_incremental_sync}")
                log(f"Initial Load Status: {control.initial_load_status}")
            else:
                log("No SyncControl found for 'orders'")

            log("\n--- Recent Orders in DB (Last 5) ---")
            orders = db.query(MlOrder).order_by(MlOrder.date_created.desc()).limit(5).all()
            for o in orders:
                log(f"ID: {o.ml_order_id} | Date: {o.date_created} | Status: {o.status} | Total: {o.total_amount}")

            log("\n--- API Test: Searching Orders (Last 3 Hours) ---")
            meli = MeliApiService(db)
            
            now = datetime.now(timezone.utc)
            date_from = (now - timedelta(hours=3)).isoformat()
            date_to = now.isoformat()
            
            from app.models.oauth_token import OAuthToken
            token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
            seller_id = token.user_id if token else None
            
            if not seller_id:
                log("Error: No seller_id found in DB")
                return
            log(f"Seller ID: {seller_id}")
            
            params = {
                "seller": seller_id,
                "order.date_last_updated.from": date_from,
                "order.date_last_updated.to": date_to,
                "sort": "date_asc",
                "limit": 10
            }
            
            log(f"Requesting orders with params: {params}")
            resp = meli.request('GET', '/orders/search', params=params)
            
            if resp.status_code == 200:
                data = resp.json()
                results = data.get('results', [])
                log(f"API Returned {len(results)} orders.")
                for r in results:
                    log(f"API Order: {r.get('id')} | Updated: {r.get('last_updated')} | Status: {r.get('status')}")
            else:
                log(f"API Failed: {resp.status_code} - {resp.text}")

        except Exception as e:
            log(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()


if __name__ == "__main__":
    debug_sync()

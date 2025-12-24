import sys
import os
import logging
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.getcwd())

from app.services.meli_api import MeliApiService
from app.models.oauth_token import OAuthToken
from app.core.database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_orders():
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        if not token:
            print("No Token found")
            return

        seller_id = token.seller_id
        print(f"Seller ID: {seller_id}")
        
        # 1. Fetch recent orders (last 5 days) using search
        date_from = (datetime.now() - timedelta(days=5)).isoformat() + "Z"
        print(f"Fetching orders from {date_from}...")
        
        orders = service.get_orders(seller_id, date_from=date_from)
        print(f"Total Orders Found: {len(orders)}")
        
        print("--- Top 5 Orders ---")
        for i, o in enumerate(orders[:5]):
            print(f"{i+1}. ID: {o.get('id')} | Date: {o.get('date_created')} | Total: {o.get('total_amount')}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_orders()

import sys
import os
import requests
from datetime import datetime, timedelta
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken
from app.services.meli_api import MeliApiService

def inspect_boundary():
    db = SessionLocal()
    try:
        service = MeliApiService(db)
        token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        
        # Look at window 2025-12-22 00:00 UTC to 2025-12-22 08:00 UTC
        # This covers the late night of 21st (UTC-3 and UTC-4)
        date_from = "2025-12-22T00:00:00Z"
        date_to = "2025-12-22T08:00:00.000Z" # Custom param not in get_orders wrapper usually?
        # get_orders supports date_from and date_to
        
        print(f"Fetching orders from {date_from} to {date_to}...")
        orders = service.get_orders(token.user_id, date_from=date_from, date_to=date_to)
        
        print(f"Found {len(orders)} orders in boundary window.")
        
        print(f"{'ID':<18} | {'Date (UTC)':<25} | {'Amount':<10} | {'Status'}")
        print("-" * 65)
        
        total_boundary = 0
        
        for o in orders:
             # Normalize Date for display
             d_str = o["date_created"]
             val = float(o["total_amount"])
             status = o["status"]
             print(f"{o['id']:<18} | {d_str:<25} | {val:<10.2f} | {status}")
             
             # Check if this order helps bridge the gap
             # Gap is 8401.34 - 8236.44 = 164.90
             
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_boundary()

import sys
import os
import requests
from datetime import datetime, timedelta
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.oauth_token import OAuthToken
from app.models.ml_order import MlOrder
from app.services.meli_api import MeliApiService

def check_integrity():
    db = SessionLocal()
    try:
        # 1. Setup API
        token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
        if not token:
            print("No Token")
            return
            
        service = MeliApiService(db)
        # Force refresh if needed handled by service logic inside methods or manually
        # accessing token property triggers refresh if expired in service logic I saw earlier
        
        # 2. Define Yesterday ISO Range (UTC)
        # Meli API uses ISO.
        # Let's ask for Last 2 days to be safe and filter in memory.
        now = datetime.utcnow()
        date_from_dt = now - timedelta(days=2)
        date_from = date_from_dt.isoformat() + "Z"
        
        print(f"Fetching Orders from API since {date_from}...")
        api_orders = service.get_orders(token.user_id, date_from=date_from)
        
        # Filter for "Yesterday" Logic (UTC-3)
        # Yesterday Local = 2025-12-21
        # Start: 2025-12-21 03:00 UTC
        # End: 2025-12-22 03:00 UTC
        
        start_cut = datetime(2025, 12, 21, 3, 0, 0)
        end_cut = datetime(2025, 12, 22, 3, 0, 0)
        
        valid_api_orders = []
        api_total = 0.0
        
        print(f"Filtering API Orders for Window: {start_cut} UTC to {end_cut} UTC")
        
        for o in api_orders:
            # Parse Date
            d_str = o["date_created"] # '2025-12-21T18:00:00.000-04:00'
            # fix 'Z' or offset
            # simpler: split/regex or dateutil
            # Assuming Meli sends ISO.
            # Convert to naive UTC for comparison
            # If offset is present, convert to UTC.
            pass
            # Let's debug the date string format first
            # print(f"Raw Date: {d_str}")
            
            # Rough Parse
            # 2025-12-21T14:52:19.000-04:00
            # Remove last 6 chars for offset if present? No, handle it.
            try:
                dt = datetime.fromisoformat(d_str)
            except:
                dt = datetime.fromisoformat(d_str.replace("Z", "+00:00"))
                
            # Convert to UTC
            if dt.tzinfo:
                dt_utc = dt.astimezone(datetime.utcnow().astimezone().tzinfo).replace(tzinfo=None) 
                # Wait, generic conversion to UTC naive
                import pytz
                dt_utc = dt.astimezone(pytz.utc).replace(tzinfo=None)
            else:
                dt_utc = dt # Assume UTC if naive?
            
            if start_cut <= dt_utc < end_cut:
                valid_api_orders.append(o)
                # print(f"API Order: {o['id']} | {o['status']} | {o['total_amount']}")
                api_total += float(o['total_amount'])
                
        print(f"API Found {len(valid_api_orders)} orders in window. Total: {api_total:,.2f}")
        
        # 3. Check DB for same Window
        db_orders = db.query(MlOrder).filter(MlOrder.date_created >= start_cut, MlOrder.date_created < end_cut).all()
        db_total = sum(o.total_amount for o in db_orders)
        
        print(f"DB Found {len(db_orders)} orders in window. Total: {db_total:,.2f}")
        
        # Compare
        api_ids = set(str(o["id"]) for o in valid_api_orders)
        db_ids = set(o.ml_order_id for o in db_orders)
        
        missing_in_db = api_ids - db_ids
        missing_in_api = db_ids - api_ids # Should be empty?
        
        print(f"Missing in DB: {len(missing_in_db)}")
        if missing_in_db:
            print(f"IDs: {missing_in_db}")
            
        print(f"Extra in DB: {len(missing_in_api)}")
        if missing_in_api:
            print(f"IDs: {missing_in_api}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_integrity()

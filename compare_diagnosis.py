import requests
import sys
import os
from sqlalchemy import func
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from datetime import datetime, timedelta

def diagnose():
    print("--- DIAGNOSTIC: API vs DB ---")
    
    # 1. Fetch from API via Debug Endpoint
    print("Fetching from API (Port 5000)...")
    resp = requests.get("http://localhost:5000/api/debug/orders-test")
    data = resp.json()
    api_ids = set(data.get("all_ids", []))
    print(f"API Count: {len(api_ids)}")
    
    # Use DB to get all today's orders
    db = SessionLocal()
    # UTC-3 Today Start in UTC = 03:00
    today_naive = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    utc_start = today_naive + timedelta(hours=3)
    
    db_orders = db.query(MlOrder).filter(MlOrder.date_created >= utc_start).all()
    db_ids = set([o.ml_order_id for o in db_orders])
    
    print(f"DB Count: {len(db_ids)}")
    
    missing_in_db = api_ids - db_ids
    missing_in_api = db_ids - api_ids
    
    print(f"Missing in DB: {len(missing_in_db)}")
    if missing_in_db:
        print("IDs Missing in DB:")
        for mid in missing_in_db:
            print(f" - {mid}")
            
    print(f"Missing in API: {len(missing_in_api)}")
    if missing_in_api:
        print("IDs Missing in API:")
        for mid in missing_in_api:
             print(f" - {mid}")

if __name__ == "__main__":
    diagnose()

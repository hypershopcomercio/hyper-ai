
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService
from app.models.ml_order import MlOrder
import concurrent.futures

def find_missing_month():
    db = SessionLocal()
    api = MeliApiService(db_session=db)
    
    # 1. Define Range: Dec 1st to Now
    # UTC-3
    tz_br = timezone(timedelta(hours=-3))
    now = datetime.now(tz_br)
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_date = now
    
    # Convert to UTC for DB Query
    start_utc = start_date.astimezone(timezone.utc).replace(tzinfo=None)
    
    print(f"Checking Range (BRT): {start_date} to {end_date}")
    
    # 2. Fetch ALL DB Orders in this range
    db_orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_utc
    ).all()
    db_ids = set(o.ml_order_id for o in db_orders)
    print(f"DB Orders Found: {len(db_ids)}")
    
    # 3. Fetch ALL ML API Orders in this range
    # Using search_orders with date_created
    # We'll need to paginate.
    
    ml_ids = set()
    offset = 0
    limit = 50
    total = 1000
    
    # Format date for API: ISO 8601
    # ML expects local or offset? usually ISO with offset.
    # 2025-12-01T00:00:00.000-03:00
    date_from = start_date.isoformat()
    date_to = end_date.isoformat()
    
    print("Fetching from API...")
    
    # Get Seller ID
    from app.models.oauth_token import OAuthToken
    token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
    seller_id = token.user_id if token else "143666838" # Fallback or error

    while offset < total:
        params = {
            "seller": seller_id,
            "order.date_created.from": date_from,
            "order.date_created.to": date_to,
            "offset": offset,
            "limit": limit
        }
        resp = api.request("GET", "/orders/search", params=params)
        if resp.status_code != 200:
            print(f"API Error: {resp.text}")
            break
            
        data = resp.json()
        total = data.get('paging', {}).get('total', 0)
        results = data.get('results', [])
        
        for r in results:
            ml_ids.add(str(r['id']))
            
        print(f"Fetched {len(ml_ids)} / {total}...")
        offset += limit
        
    print(f"Total API Orders: {len(ml_ids)}")
    
    # 4. Compare
    missing_in_db = ml_ids - db_ids
    extra_in_db = db_ids - ml_ids
    
    print(f"Missing in DB: {len(missing_in_db)}")
    print(f"Extra in DB: {len(extra_in_db)}")
    
    if missing_in_db:
        print("Missing IDs:", missing_in_db)
        # Write to file for sync script
        with open("missing_ids.txt", "w") as f:
            for mid in missing_in_db:
                f.write(f"{mid}\n")
    else:
        print("No missing orders found!")
        
    db.close()

if __name__ == "__main__":
    find_missing_month()

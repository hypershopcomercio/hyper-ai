import sys
import os
import requests
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService
from app.models.ml_order import MlOrder
from app.models.oauth_token import OAuthToken

def inspect_orders():
    ids = ["2000014414139106", "2000014427490424"]
    db = SessionLocal()
    token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
    
    headers = {"Authorization": f"Bearer {token.access_token}"}
    
    for oid in ids:
        # Check API
        url = f"https://api.mercadolibre.com/orders/{oid}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            d = r.json()
            print(f"API {oid}: Date={d['date_created']} | Amount={d['total_amount']} | Status={d['status']}")
        else:
            print(f"API {oid} Error: {r.status_code}")
            
        # Check DB
        o_db = db.query(MlOrder).filter(MlOrder.ml_order_id == oid).first()
        if o_db:
            print(f"DB  {oid}: Date={o_db.date_created} | Amount={o_db.total_amount}")
        else:
            print(f"DB  {oid}: Not Found")
            
        print("-" * 30)

if __name__ == "__main__":
    inspect_orders()

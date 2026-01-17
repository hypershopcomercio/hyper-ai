from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal
import requests

db = SessionLocal()
service = MeliApiService(db_session=db)
token = service._get_valid_token()
headers = {"Authorization": f"Bearer {token}"}
url = f"https://api.mercadolibre.com/items/MLB4200110239/prices"

try:
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()

from app.services.meli_auth import MeliAuthService
import requests
import json

auth = MeliAuthService()
token = auth.get_valid_token()
headers = {"Authorization": f"Bearer {token}"}
ml_id = "MLB3964133363" 

url = f"https://api.mercadolibre.com/visits/items?ids={ml_id}"
print(f"Calling: {url}")
res = requests.get(url, headers=headers)
print(f"Status: {res.status_code}")
print(f"Response: {res.text}")

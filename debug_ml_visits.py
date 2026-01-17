from app.services.meli_auth import MeliAuthService
import requests
import json

auth = MeliAuthService()
token = auth.get_valid_token()

if not token:
    print("No token!")
    exit()

headers = {"Authorization": f"Bearer {token}"}
ids = ["MLB3964133363", "MLB5238117220"] # IDs from screenshot

print(f"Testing Visits for {ids}...")
url = f"https://api.mercadolibre.com/visits/items?ids={','.join(ids)}"
res = requests.get(url, headers=headers)

print(f"Status: {res.status_code}")
print(f"Response: {res.text}")

print("\nTesting Items details for Shipping Mode...")
res_items = requests.get(f"https://api.mercadolibre.com/items?ids={','.join(ids)}", headers=headers)
data = res_items.json()
for item in data:
    body = item.get('body', {})
    print(f"ID: {body.get('id')}")
    print(f"Shipping: {body.get('shipping')}")

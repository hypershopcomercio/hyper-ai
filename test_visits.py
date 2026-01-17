from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService
import requests

db = SessionLocal()
meli = MeliApiService(db_session=db)

item_id = 'MLB3964133363'
headers = meli.get_headers()

# Test different endpoints
endpoints = [
    ('time_window 120d', f'https://api.mercadolibre.com/items/{item_id}/visits/time_window?last=120&unit=day'),
    ('visits summary', f'https://api.mercadolibre.com/visits/items?ids={item_id}'),
    ('item attributes', f'https://api.mercadolibre.com/items/{item_id}?attributes=visits,sold_quantity'),
]

for name, url in endpoints:
    print(f'\n=== {name} ===')
    print(f'URL: {url}')
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                total = sum(d.get('total', 0) for d in data['results'])
                print(f'Sum: {total}')
            elif isinstance(data, list):
                for item in data:
                    print(f"Item {item.get('id')}: visits={item.get('visits')}, total_visits={item.get('total_visits')}")
            else:
                print(f'Keys: {list(data.keys())}')
                for k in ['visits', 'total_visits', 'sold_quantity']:
                    if k in data:
                        print(f'{k} = {data[k]}')
    except Exception as e:
        print(f'Error: {e}')

db.close()

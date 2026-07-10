import requests
import json

mlbs = ['MLB6740279032','MLB4576792109','MLB6557329330','MLB6605370336','MLB4485818539']
for mlb in mlbs:
    res = requests.get(f"https://api.mercadolibre.com/items/{mlb}")
    data = res.json()
    if 'error' in data:
        print(f"{mlb}: {data['message']}")
        continue
    
    variations = data.get('variations', [])
    print(f"\n{mlb} - {data.get('title')}")
    print(f"Total Variations: {len(variations)}")
    
    catalog_id = data.get('catalog_product_id')
    print(f"Catalog Product ID: {catalog_id}")
    
    for v in variations:
        v_id = v.get('id')
        v_attrs = [f"{a['name']}: {a['value_name']}" for a in v.get('attribute_combinations', [])]
        v_price = v.get('price')
        print(f"  Var {v_id}: {', '.join(v_attrs)} - R$ {v_price}")

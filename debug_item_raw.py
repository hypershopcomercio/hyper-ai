
import requests
import json

AD_ID = "MLB3964133363"
# Public API often hides some seller fields, but let's check basic structure first.
URL = f"https://api.mercadolibre.com/items/{AD_ID}"

try:
    print(f"Fetching {URL}...")
    response = requests.get(URL)
    if response.status_code == 200:
        data = response.json()
        
        # Look for video/clip related fields
        interesting_fields = {
            'id': data.get('id'),
            'video_id': data.get('video_id'),
            'short_description': data.get('short_description'),
            'pictures_count': len(data.get('pictures', [])),
            'attributes': [a['id'] for a in data.get('attributes', []) if 'VIDEO' in a['id'] or 'CLIP' in a['id']]
        }
        
        print("Interesting Data:")
        print(json.dumps(interesting_fields, indent=2))
        
        # Dump full keys to find hidden gems
        print("\nAll Keys:")
        print(list(data.keys()))
        
    else:
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    print(e)

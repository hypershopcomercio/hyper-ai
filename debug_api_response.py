
import requests
import json
import traceback

AD_ID = "MLB3964133363"
URL = f"http://localhost:5000/api/ads/{AD_ID}"

try:
    print(f"Requesting {URL}...")
    response = requests.get(URL)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        health = data.get('intelligence', {}).get('health', {})
        print("Health Data:")
        print(json.dumps(health, indent=2, ensure_ascii=False))
    else:
        print("Error Response:")
        print(response.text)
except Exception as e:
    print(f"Connection Failed: {e}")
    traceback.print_exc()

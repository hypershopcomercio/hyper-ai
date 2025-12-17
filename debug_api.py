
import requests

try:
    res = requests.get("http://localhost:5000/api/ads?limit=2")
    print("Status:", res.status_code)
    data = res.json()
    print("Keys:", data.keys())
    print("Data Type:", type(data.get('data')))
    print("Data Length:", len(data.get('data', [])))
    if len(data.get('data', [])) > 0:
        print("First Item sample:", str(data['data'][0])[:100])
except Exception as e:
    print("Error:", e)

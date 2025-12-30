
import requests
try:
    resp = requests.get("http://localhost:5000/api/ads")
    print(f"Status: {resp.status_code}")
except Exception as e:
    print(f"Error: {e}")

import requests
import json

url = "http://localhost:5000/api/dashboard/metrics?days=1"
try:
    resp = requests.get(url)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

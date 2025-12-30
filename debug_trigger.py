
import requests
import json

url = "http://localhost:5000/api/jobs/trigger"

print(f"Calling {url}...")
try:
    # Send empty JSON object to ensure Content-Type is application/json
    resp = requests.post(url, json={})
    print(f"Status: {resp.status_code}")
    print("Response headers:", resp.headers)
    print("Response text:", resp.text)
except Exception as e:
    print(f"Request failed: {e}")

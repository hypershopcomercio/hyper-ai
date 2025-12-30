
import requests
import json

base_url = "http://localhost:5000/api/dashboard/metrics"

params_to_test = [
    "1", "7", "30", "current_month", "last_month", "yesterday", "hoje", "ontem", "0"
]

print("Testing Dashboard API Intervals...")

for p in params_to_test:
    try:
        url = f"{base_url}?days={p}"
        print(f"Testing days={p} ...", end=" ")
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            sales = len(data.get('sales_list', []))
            print(f"OK (Sales: {sales})")
        else:
            print(f"FAILED: {resp.status_code}")
            print(resp.text[:200])
    except Exception as e:
        print(f"EXCEPTION: {e}")

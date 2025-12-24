import requests
import json

def test_dashboard():
    try:
        url = "http://localhost:5000/api/dashboard/metrics?days=0"
        print(f"Calling {url}...")
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            print("--- Dashboard API Response ---")
            print(json.dumps({k:v for k,v in data.items() if 'revenue' in k}, indent=2))
        else:
            print(f"Error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dashboard()

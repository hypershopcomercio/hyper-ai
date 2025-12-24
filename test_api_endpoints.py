import requests
import sys

def test_sync_status():
    try:
        print("Testing GET http://localhost:5000/api/sync/status...")
        response = requests.get("http://localhost:5000/api/sync/status", timeout=5)
        print(f"Status Verify: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response JSON:")
            import json
            print(json.dumps(data, indent=2))
            
            # Validation
            ml = data.get('ml', {})
            tiny = data.get('tiny', {})
            
            print("\n--- Analysis ---")
            print(f"ML Connected: {ml.get('connected')} (Expected: True)")
            print(f"Tiny Token: {tiny.get('has_token')} (Expected: True)")
            print(f"ML Syncing: {ml.get('syncing')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to connect to API: {e}")

if __name__ == "__main__":
    test_sync_status()

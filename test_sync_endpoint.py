
import requests
import json

def test_sync_endpoint():
    print("--- TESTING SYNC ENDPOINT ---")
    try:
        # Assuming localhost:5000 based on previous context
        url = "http://localhost:5000/api/forecast/products/sync"
        print(f"POST {url}")
        resp = requests.post(url, timeout=300) # Long timeout for full sync
        
        print(f"Status: {resp.status_code}")
        try:
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
        except:
            print(f"Raw Response: {resp.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sync_endpoint()

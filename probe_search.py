
import requests
from app.services.meli_auth import MeliAuthService
from app.core.database import SessionLocal

def get_token():
    auth = MeliAuthService()
    return auth.get_valid_token()

def probe_search(query):
    token = get_token()
    base_url = "https://api.mercadolibre.com"
    endpoint = f"/sites/MLB/search?q={query}&limit=5"
    
    headers = {
        # "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"--- SEARCHING: {query} (Anonymous + UA) ---")
    try:
        url = f"{base_url}{endpoint}"
        resp = requests.get(url, headers=headers)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            print(f"Found {len(results)} results")
            for item in results:
                 print(f"- [{item['id']}] {item['title']} | Price: {item['price']}")
        else:
            print(f"Error: {resp.text[:200]}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test with a known product title from the system
    # Using "Roupão Infantil" as a generic test
    probe_search("Roupão Infantil Piscina Microfibra")

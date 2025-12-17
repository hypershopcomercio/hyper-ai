
import requests

def check_api():
    try:
        # Assuming run_web is running on 5000
        res = requests.get("http://localhost:5000/api/ads?page=1&limit=50")
        if res.status_code == 200:
            data = res.json()
            items = data.get("data", [])
            print(f"Fetched {len(items)} items")
            for item in items:
                # print title and cost
                if "Tekbond" in item['title'] or "Assento" in item['title']:
                    print(f"Item: {item['title'][:30]}... | Cost in JSON: {item.get('cost')}")
        else:
            print(f"Failed: {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()

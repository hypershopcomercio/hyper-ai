
import requests

def check_health():
    try:
        print("Ping http://localhost:5000/api/settings ...")
        res = requests.get("http://localhost:5000/api/settings", timeout=2)
        print(f"Status Code: {res.status_code}")
        print("Backend is responding.")
    except Exception as e:
        print(f"Backend Ping Failed: {e}")

if __name__ == "__main__":
    check_health()

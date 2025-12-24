import requests
import json

def test_filters():
    base = "http://localhost:5000/api/dashboard/metrics"
    print("Testing Month Filters...")
    
    print("--------------------------------------------------")
    print("--------------------------------------------------")
    # Test Today (Hoje)
    url_hoje = f"{base}?days=1"
    print(f"Calling specific URL: {url_hoje}")
    try:
        r = requests.get(url_hoje)
        if r.status_code == 200:
            d = r.json()
            print(f"Today Period: {d.get('period_label')}")
            print(f"Gross Revenue: {d.get('revenue_gross_7d')}") 
            print(f"Net Revenue: {d.get('revenue_7d')}")
            print(f"Debug Info: {d.get('debug_info')}")
        else:
            print(f"Error {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("--------------------------------------------------")

    # Test Last Month
    url_last = f"{base}?days=last_month"
    print(f"Calling {url_last}...")
    try:
        r = requests.get(url_last)
        if r.status_code == 200:
            d = r.json()
            print(f"Last Month Period: {d.get('period_label')}")
            print(f"Revenue: {d.get('revenue_7d')}")
            print(f"Stock Risks Found: {d.get('stock_risk_count')}")
            print(f"Risk Value: {d.get('stock_risk_value')}")
        else:
            print(f"Error {r.status_code}")
    except Exception as e:
        print(f"Ex: {e}")

if __name__ == "__main__":
    test_filters()


import requests
import json

def test_dashboard():
    try:
        # Yesterday
        print("--- FETCHING YESTERDAY ---")
        param = "0" # or "Yesterday"
        resp = requests.get(f"http://localhost:5000/api/dashboard/metrics?days={param}")
        if resp.status_code == 200:
            data = resp.json()
            print("Response 200 OK")
            print(f"Visits: {data.get('visits_7d')} (Trend: {data.get('visits_trend')}%)")
            print(f"Gross: {data.get('revenue_gross_7d')}")
            print(f"Cancelled: {data.get('revenue_cancelled_7d')}")
            print(f"Orders: {data.get('sales_count_7d')}")
            print(f"Debug: {data.get('debug_info')}")
            ids = data.get('debug_info', {}).get('included_ids', [])
            print(f"Total IDs: {len(ids)}")
            print(f"IDs List: {sorted(ids)}")
            if len(ids) != len(set(ids)):
                print("!! DUPLICATES DETECTED !!")
        else:
            print(f"Error: {resp.status_code}")
            print(resp.text)
            
        # Today
        print("\n--- FETCHING TODAY ---")
        param = "1" 
        resp = requests.get(f"http://localhost:5000/api/dashboard/metrics?days={param}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Visits: {data.get('visits_7d')} (Trend: {data.get('visits_trend')}%)")
            print(f"Gross: {data.get('revenue_gross_7d')}")
            print(f"Cancelled: {data.get('revenue_cancelled_7d')}")
            print(f"Orders: {data.get('sales_count_7d')}")

        # Current Month
        print("\n--- FETCHING CURRENT MONTH ---")
        param = "current_month" 
        resp = requests.get(f"http://localhost:5000/api/dashboard/metrics?days={param}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Visits: {data.get('visits_7d')} (Trend: {data.get('visits_trend')}%)")
            print(f"Gross: {data.get('revenue_gross_7d')}")
            print(f"Cancelled: {data.get('revenue_cancelled_7d')}")
            print(f"Net: {data.get('revenue_7d')}")
            print(f"Orders: {data.get('sales_count_7d')}")
            # print(f"Debug: {data.get('debug_info')}")

        # Last 7 Days
        print("\n--- FETCHING LAST 7 DAYS ---")
        param = "7" 
        resp = requests.get(f"http://localhost:5000/api/dashboard/metrics?days={param}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Visits: {data.get('visits_7d')} (Trend: {data.get('visits_trend')}%)")
            print(f"Gross: {data.get('revenue_gross_7d')}")
            print(f"Cancelled: {data.get('revenue_cancelled_7d')}")
            print(f"Orders: {data.get('sales_count_7d')}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_dashboard()


import requests

BASE_URL = "http://localhost:5000/api"

def verify_sprint4():
    print("--- Verifying Sprint 4 APIs ---")
    
    # 1. Dashboard Metrics
    try:
        resp = requests.get(f"{BASE_URL}/dashboard/metrics")
        if resp.status_code == 200:
            data = resp.json()
            print("\n[Dashboard Metrics] OK")
            print(f"Total Ads: {data.get('total_ads')}")
            print(f"Visits 7d: {data.get('visits_7d')} (Trend: {data.get('visits_trend')}%)")
            print(f"Revenue 7d: {data.get('revenue_7d')} (Trend: {data.get('revenue_trend')}%)")
            print(f"Avg Margin: {data.get('average_margin')}%")
        else:
            print(f"\n[Dashboard Metrics] FAILED: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"\n[Dashboard Metrics] ERROR: {e}")

    # 2. Ads List
    try:
        resp = requests.get(f"{BASE_URL}/ads?limit=3&sort_by=visits_7d_change&sort_order=desc")
        if resp.status_code == 200:
            data = resp.json()
            print("\n[Ads List] OK")
            print(f"Total: {data.get('total')}")
            ads = data.get('data', [])
            if ads:
                ad = ads[0]
                print(f"Top Ad: {ad.get('title')}")
                print(f" - Visits 7d Change: {ad.get('visits_7d_change')}%")
                print(f" - Margin: {ad.get('margin_percent')}%")
                
                # 3. Ad Details
                ad_id = ad.get('id')
                resp_detail = requests.get(f"{BASE_URL}/ads/{ad_id}")
                if resp_detail.status_code == 200:
                     det = resp_detail.json()
                     print(f"\n[Ad Details] OK")
                     print(f" - History Points: {len(det.get('history', []))}")
                     print(f" - Financials: {det.get('financials')}")
                else:
                    print(f"\n[Ad Details] FAILED: {resp_detail.status_code}")
            else:
                print("No ads returned to verify details.")
        else:
            print(f"\n[Ads List] FAILED: {resp.status_code}")
    except Exception as e:
        print(f"\n[Ads List] ERROR: {e}")

if __name__ == "__main__":
    verify_sprint4()

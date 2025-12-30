
import requests
import json

try:
    response = requests.get("http://localhost:5000/api/dashboard/metrics?days=Hoje")
    data = response.json()
    sales = data.get('sales_list', [])
    cancelled = [s for s in sales if s.get('status') == 'cancelled']
    
    print(f"Total Sales: {len(sales)}")
    print(f"Cancelled Found: {len(cancelled)}")
    if 'debug_info' in data:
        print("Debug Info:", data['debug_info'])
    if cancelled:
        print(json.dumps(cancelled[0], indent=2))
    else:
        print("No cancelled found")
        if not sales:
            print("Full Data:", json.dumps(data, indent=2))
        elif sales:
            print("Normal Sale keys:", sales[0].keys())

except Exception as e:
    print(e)

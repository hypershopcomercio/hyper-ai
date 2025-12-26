"""Find which items are in bucket 00h and their details"""
import requests
import json

response = requests.get("http://localhost:5000/api/dashboard/metrics?days=Hoje")
data = response.json()

sales = data.get('sales_list', [])
cf = data.get('cash_flow', [])

# Find all sales with date in 00h-01h range (bucket 00h)
print("=== Looking for items with 'Roup' or 'Bar Cooler' or 00h time ===")
for s in sales:
    date_str = s.get('date', '')
    title = s.get('title', '')
    if 'Roup' in title or 'Bar Cooler' in title or 'Roup' in title.lower():
        print(f"\n{title[:50]}")
        print(f"  Date: {date_str}")
        print(f"  Revenue: {s['total_revenue']}")
        print(f"  Costs: {s['costs']}")
        print(f"  Net Margin: {s['net_margin']}")

print("\n\n=== Items that would be in 00h bucket (00:00-01:59) ===")
from datetime import datetime
for s in sales:
    date_str = s.get('date', '')
    if date_str:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # Convert to Brasilia time
        from pytz import timezone
        tz_br = timezone('America/Sao_Paulo')
        dt_br = dt.astimezone(tz_br)
        h = dt_br.hour
        bucket = (h // 2) * 2
        if bucket == 0:
            print(f"\n{s['title'][:50]}")
            print(f"  Time (BR): {dt_br.strftime('%H:%M')}")
            print(f"  Revenue: {s['total_revenue']}")
            print(f"  Net Margin: {s['net_margin']}")

"""Compare costs between sales_list and cash_flow for 00h items"""
import requests
from datetime import datetime
from pytz import timezone

response = requests.get("http://localhost:5000/api/dashboard/metrics?days=Hoje")
data = response.json()

sales = data.get('sales_list', [])
cf = data.get('cash_flow', [])
tz_br = timezone('America/Sao_Paulo')

# Find 00h bucket items
print("=== 00h BUCKET ITEMS (from sales_list with correct costs) ===")
total_revenue = 0
total_cost = 0
total_margin = 0

for s in sales:
    date_str = s.get('date', '')
    if date_str:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        dt_br = dt.astimezone(tz_br)
        h = dt_br.hour
        bucket = (h // 2) * 2
        if bucket == 0:
            costs = s['costs']
            total_c = costs['fee'] + costs['tax'] + costs['product'] + costs['shipping'] + costs.get('ads', 0)
            print(f"\n{s['title'][:50]}")
            print(f"  Revenue: {s['total_revenue']}")
            print(f"  fee={costs['fee']}, tax={costs['tax']}, prod={costs['product']}, ship={costs['shipping']}")
            print(f"  Total Cost: {total_c:.2f}")
            print(f"  Net Margin: {s['net_margin']}")
            total_revenue += s['total_revenue']
            total_cost += total_c
            total_margin += s['net_margin']

print(f"\n=== SALES_LIST TOTALS FOR 00h ===")
print(f"Total Revenue: {total_revenue:.2f}")
print(f"Total Cost: {total_cost:.2f}")
print(f"Total Net Margin: {total_margin:.2f}")

print(f"\n=== CASH_FLOW 00h BUCKET ===")
b00 = [c for c in cf if c.get('name') == '00h'][0]
print(f"Receita: {b00['receita']}")
print(f"Custo: {b00['custo']}")
print(f"Lucro: {b00['lucro']}")

print(f"\n=== DISCREPANCY ===")
print(f"Expected Lucro (from sales_list): {total_margin:.2f}")
print(f"Actual Lucro (from cash_flow): {b00['lucro']:.2f}")
print(f"Difference: {b00['lucro'] - total_margin:.2f}")
print(f"Expected Custo: {total_cost:.2f}")
print(f"Actual Custo: {b00['custo']:.2f}")
print(f"Cost Difference: {total_cost - b00['custo']:.2f}")

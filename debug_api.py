"""Compare sales_list costs vs cash_flow for the same orders"""
import requests
import json

response = requests.get("http://localhost:5000/api/dashboard/metrics?days=Hoje")
data = response.json()

sales = data.get('sales_list', [])
cf = data.get('cash_flow', [])

print("=== CASH FLOW BUCKET 00h ===")
b00 = [c for c in cf if c.get('name') == '00h'][0]
print(f"Receita: {b00['receita']}")
print(f"Custo: {b00['custo']}")
print(f"Lucro: {b00['lucro']}")

print("\n=== SALES LIST (first 5) ===")
total_net_margin = 0
for s in sales[:5]:
    costs = s['costs']
    total_cost = costs['fee'] + costs['tax'] + costs['product'] + costs['shipping'] + costs.get('ads', 0)
    print(f"\n{s['title'][:40]}")
    print(f"  Revenue: {s['total_revenue']}")
    print(f"  Costs: fee={costs['fee']}, tax={costs['tax']}, prod={costs['product']}, ship={costs['shipping']}, ads={costs.get('ads', 0)}")
    print(f"  Total Cost: {total_cost:.2f}")
    print(f"  Net Margin: {s['net_margin']}")
    total_net_margin += s['net_margin']

print(f"\n=== COMPARISON ===")
print(f"Sum of first 5 sales net_margin: {total_net_margin:.2f}")
print(f"Cash flow 00h lucro: {b00['lucro']:.2f}")

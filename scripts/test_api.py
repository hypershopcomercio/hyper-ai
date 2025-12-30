"""
Test API response for factor analytics
"""
import requests
import json

# Call API
response = requests.get('http://localhost:5000/api/forecast/analytics/factors')
data = response.json()

# Check momentum
print("=== Momentum Factors from API ===")
momentum_factors = [f for f in data['data']['factors'] if f['type'] == 'momentum']

for m in momentum_factors:
    print(f"\n{m['key']}:")
    print(f"  value: {m['value']}")
    print(f"  change_24h: {m['change_24h']}")
    print(f"  change_7d: {m['change_7d']}")
    print(f"  samples: {m['samples']}")
    print(f"  source: {m['source']}")
    print(f"  confidence: {m['confidence']}")

print(f"\nTotal momentum factors: {len(momentum_factors)}")

import requests
import json

try:
    print("Calling /api/debug/orders-test...")
    response = requests.get("http://localhost:5000/api/debug/orders-test")
    data = response.json()
    debug_info = data.get("debug_info", {})
    pareto_debug = debug_info.get("pareto_debug", {})
    
    print("\n--- KEYS ---")
    print(list(data.keys()))
    if "error" in data:
         print(f"\nAPI ERROR: {data['error']}")
    
    print("\n--- RESPONSE DATA ---")
    print(json.dumps(data, indent=2))
    
except Exception as e:
    print(e)

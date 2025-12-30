
import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from app.services.tiny_api import TinyApiService

def debug_cost():
    service = TinyApiService()
    tiny_id = "972625240"
    print(f"Fetching details for Tiny ID: {tiny_id}")
    
    details = service.get_product_details(tiny_id)
    if details:
        print(json.dumps(details, indent=2))
        print(f"Preco Custo: {details.get('preco_custo')}")
        print(f"Preco Custo Medio: {details.get('preco_custo_medio')}")
    else:
        print("Failed to fetch details.")

if __name__ == "__main__":
    debug_cost()

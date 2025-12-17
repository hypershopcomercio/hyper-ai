
import logging
import json
import sys
from app.services.tiny_api import TinyApiService

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_fetch_cost(sku):
    print(f"--- Testing Tiny API for SKU: '{sku}' ---")
    tiny = TinyApiService()
    
    # 1. Search for the product
    product_data = tiny.search_product(sku)
    
    if not product_data:
        print(f"❌ Tiny returned NO results for SKU '{sku}'.")
        return

    print(f"✅ Product Found in Tiny Search!")
    print(f"ID: {product_data.get('id')}")
    print(f"Nome: {product_data.get('nome')}")
    
    # 2. Get full details including cost
    tiny_id = product_data.get('id')
    if tiny_id:
        print(f"--- Fetching details for Tiny ID {tiny_id} ---")
        details = tiny.get_product_details(tiny_id)
        
        if details:
            print(f"Details found!")
            print(f"COST_DEBUG: {details.get('preco_custo')}")
            print(f"AVG_COST_DEBUG: {details.get('preco_custo_medio')}")
        else:
            print("❌ Failed to get details.")
    else:
        print("❌ Product has no ID?")

if __name__ == "__main__":
    target_sku = "FECHADURA-VITRINE" 
    if len(sys.argv) > 1:
        target_sku = sys.argv[1]
        
    test_fetch_cost(target_sku)

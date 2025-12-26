
import logging
from app.core.database import SessionLocal
from app.services.tiny_api import TinyApiService
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_product():
    service = TinyApiService()
    sku = "PISCINA-SOL-275L"
    
    logger.info(f"Searching for SKU: {sku}")
    product_basic = service.search_product(sku)
    
    if not product_basic:
        logger.error("Product not found.")
        return

    tiny_id = product_basic.get("id")
    logger.info(f"Found ID: {tiny_id}. Fetching details...")
    
    details = service.get_product_details(tiny_id)
    
    if details:
        print(f"DEBUG_PRICE: {details.get('preco_custo')}")
        print(f"DEBUG_STOCK: {details.get('saldo')}")
        
        # Test hypothetical endpoint for costs
        try:
             url = f"{service.base_url}/produto.obter.custos.php"
             params = {"token": service.token, "id": tiny_id, "formato": "json"}
             import requests
             resp = requests.post(url, data=params)
             print(f"DEBUG_CUSTOS_ENDPOINT: {resp.status_code}")
             print(resp.text[:200])
        except:
             pass

if __name__ == "__main__":
    inspect_product()

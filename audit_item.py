
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.oauth_token import OAuthToken
from app.services.tiny_api import TinyApiService
import requests
import json

def audit_item():
    item_id = "MLB3964133363" # Bar Cooler
    db = SessionLocal()
    tiny = TinyApiService()
    
    print(f"=== AUDIT FOR {item_id} ===")
    
    # 1. Check ML Item Data (Shipping & GTIN)
    token = db.query(OAuthToken).filter(OAuthToken.provider == "mercadolivre").first()
    headers = {"Authorization": f"Bearer {token.access_token}"}
    
    url_item = f"https://api.mercadolibre.com/items?ids={item_id}"
    res = requests.get(url_item, headers=headers)
    item_data = res.json()[0].get("body", {})
    
    print(f"Title: {item_data.get('title')}")
    print(f"Shipping Info: {json.dumps(item_data.get('shipping'), indent=2)}")
    
    # Extract GTIN
    gtin = None
    for attr in item_data.get("attributes", []):
         if attr.get("id") == "GTIN":
             gtin = attr.get("value_name")
    print(f"GTIN Found in ML: {gtin}")
    
    # Check User ID for Shipping Cost
    me = requests.get("https://api.mercadolibre.com/users/me", headers=headers).json()
    seller_id = me["id"]
    
    # 2. Check Shipping Cost Endpoint
    if item_data.get("shipping", {}).get("free_shipping"):
        url_ship = f"https://api.mercadolibre.com/users/{seller_id}/shipping_options/free?item_id={item_id}"
        print(f"Checking Shipping Cost: {url_ship}")
        res_ship = requests.get(url_ship, headers=headers)
        print(f"Shipping Cost Response Code: {res_ship.status_code}")
        print(f"Shipping Cost Body: {res_ship.text}")
    else:
        print("Item implies NO Free Shipping (user pays).")

    # 3. Check Tiny via SKU
    sku_ml = None
    for attr in item_data.get("attributes", []):
        if attr.get("id") == "SELLER_SKU":
            sku_ml = attr.get("value_name")
    
    print(f"SKU from ML: '{sku_ml}'")
    
    if sku_ml:
        res_sku = tiny.search_product(sku_ml.strip())
        print(f"Tiny Search by SKU '{sku_ml}': {'FOUND' if res_sku else 'NOT FOUND'}")
        if res_sku:
             print(f" - ID: {res_sku['id']}")
    
    # 4. Check Tiny via GTIN
    if gtin:
        print(f"Searching Tiny by GTIN '{gtin}'...")
        # Tiny search usually works with GTIN too in same field?
        res_gtin = tiny.search_product(gtin)
        print(f"Tiny Search by GTIN: {'FOUND' if res_gtin else 'NOT FOUND'}")
        if res_gtin:
             print(f" - ID: {res_gtin['id']}")
             t_details = tiny.get_product_details(str(res_gtin['id']))
             print(f" - Cost: {t_details.get('preco_custo')}")

if __name__ == "__main__":
    audit_item()

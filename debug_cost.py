
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ad_variation import AdVariation
from app.services.tiny_api import TinyApiService
import json

def debug_missing_cost():
    db = SessionLocal()
    tiny = TinyApiService()
    
    item_id = "MLB5377924794" # Banheira
    
    print(f"--- Diagnosing {item_id} ---")
    
    # Check Ad
    ad = db.query(Ad).filter(Ad.id == item_id).first()
    if not ad:
        print("Ad not found in DB!")
        return
        
    print(f"Ad Title: {ad.title}")
    print(f"Ad SKU (Parent): '{ad.sku}'")
    
    # Check Variations
    vars = db.query(AdVariation).filter(AdVariation.ad_id == item_id).all()
    print(f"Variations Found: {len(vars)}")
    
    sku_to_test = ad.sku
    
    for v in vars:
        print(f" - Var ID: {v.id}, SKU: '{v.sku}'")
        if not sku_to_test and v.sku:
            sku_to_test = v.sku
            
    if not sku_to_test:
        print("NO SKU found in Parent or Variations. Cannot sync with Tiny.")
        return
        
    print(f"---Testing Tiny API for SKU: '{sku_to_test}'---")
    res = tiny.search_products(sku_to_test)
    print(f"Tiny Search Result: {json.dumps(res, indent=2)}")
    
    if res and len(res) > 0:
        t_id = str(res[0]["id"])
        print(f"Fetching details for ID {t_id}...")
        details = tiny.get_product_details(t_id)
        print(f"Details: {json.dumps(details, indent=2)}")
        print(f"Cost Price Found: {details.get('preco_custo')}")
    else:
        print("Tiny returned NO results for this SKU.")

if __name__ == "__main__":
    debug_missing_cost()

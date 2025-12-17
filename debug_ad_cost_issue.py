
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ad_variation import AdVariation
from app.services.tiny_api import TinyApiService

def debug_costs():
    db = SessionLocal()
    tiny = TinyApiService()
    
    target_ids = ["MLB5930429496", "MLB4307123477"]
    
    print("--- Debugging Specific Ads ---")
    
    for ml_id in target_ids:
        print(f"\nChecking Ad: {ml_id}")
        ad = db.query(Ad).filter(Ad.id == ml_id).first()
        
        if not ad:
            print(f"  Result: Ad NOT found in database. (Did you run Sync Listings?)")
            continue
            
        print(f"  Title: {ad.title}")
        print(f"  SKU (Parent): {ad.sku}")
        print(f"  Cost (Parent): {ad.cost}")
        
        # Check Variations
        # variations = list(ad.variations) # Relationship removed temporarily
        variations = db.query(AdVariation).filter(AdVariation.ad_id == ml_id).all()
        
        print(f"  Variations Count: {len(variations)}")
        for v in variations:
            print(f"    - Var ID: {v.id} | SKU: {v.sku} | Cost: {v.cost}")
            
        # Diagnosis
        skus_to_check = []
        if ad.sku: skus_to_check.append(ad.sku)
        for v in variations:
            if v.sku: skus_to_check.append(v.sku)
            
        if not skus_to_check:
            print("  DIAGNOSIS: No SKUs found on Parent or Variations. Cannot sync with Tiny.")
        else:
            print(f"  Checking SKUs against Tiny API: {skus_to_check}")
            for sku in skus_to_check:
                try:
                    res = tiny.search_product(sku)
                    if res:
                        print(f"    - Tiny Found {sku}: ID {res['id']} | Code: {res['codigo']}")
                        # Fetch details for cost check
                        det = tiny.get_product_details(res['id'])
                        print(f"      - Cost in Tiny: {det.get('preco_custo')}")
                    else:
                        print(f"    - Tiny returned NULL for {sku}")
                except Exception as e:
                     print(f"    - Error checking Tiny: {e}")

    db.close()

if __name__ == "__main__":
    debug_costs()


from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ad_variation import AdVariation
from app.services.tiny_api import TinyApiService
import sys

def debug_costs():
    db = SessionLocal()
    tiny = TinyApiService()
    
    # Specific IDs from user screenshot/context
    target_ids = ["MLB4307123477", "MLB5930429496"] 
    
    print("\n" + "="*50)
    print("DEBUGGING AD COSTS")
    print("="*50)
    
    for ml_id in target_ids:
        print(f"\n[Ad: {ml_id}]")
        ad = db.query(Ad).filter(Ad.id == ml_id).first()
        
        if not ad:
            print(f"  Result: Ad NOT found in database.")
            continue
            
        print(f"  Title: {ad.title}")
        print(f"  SKU: {ad.sku}")
        print(f"  DB 'cost': {ad.cost} (Expected: value from Tiny)")
        print(f"  DB 'tiny_id': {ad.tiny_id}")
        
        # Check Variations (using query to avoid relationship issues)
        variations = db.query(AdVariation).filter(AdVariation.ad_id == ml_id).all()
        print(f"  Variations Count: {len(variations)}")
        for v in variations:
            print(f"    Var SKU: {v.sku} | Cost: {v.cost}")

        # Check Tiny API Direct
        sku_to_check = ad.sku
        if sku_to_check:
            print(f"  Checking Tiny API for SKU '{sku_to_check}'...")
            try:
                tiny_data = tiny.search_product(sku_to_check)
                if tiny_data:
                    print(f"    TINY MATCH: ID={tiny_data['id']}, Code={tiny_data['codigo']}")
                    # Get details
                    det = tiny.get_product_details(tiny_data['id'])
                    print(f"    TINY COST: {det.get('preco_custo')}")
                else:
                    print(f"    TINY: No match found.")
            except Exception as e:
                print(f"    TINY ERROR: {e}")
        else:
            print("  Skipping Tiny check (No SKU).")

    db.close()
    print("\n" + "="*50)

if __name__ == "__main__":
    debug_costs()


from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.tiny_product import TinyProduct

def inspect():
    db = SessionLocal()
    try:
        # 1. Find the specific ad that showed numbers
        # "Piscina Intex Por Do Sol Colorida 275 Litros"
        ad = db.query(Ad).filter(Ad.title.ilike("%Piscina Intex Por Do Sol%")).first()
        
        print("\n--- Ad Inspection ---")
        if ad:
            print(f"Title: {ad.title}")
            print(f"SKU: {ad.sku}")
            print(f"Ad Cost (DB field): {ad.cost}")
            print(f"Ad Tax Cost (Calculated): {ad.tax_cost}")
            
            # Check Tiny Product
            if ad.sku:
                tp = db.query(TinyProduct).filter(TinyProduct.sku == ad.sku).first()
                if tp:
                    print(f"\n--- Tiny Product Data ---")
                    print(f"Tiny Cost (Raw Import): {tp.cost}")
                    print(f"NCM: {tp.ncm}")
                    print(f"Origin: {tp.origin}")
                else:
                    print(f"\nTiny Product not found for SKU {ad.sku}")
            else:
                 print(f"\nAd has no Seller SKU")
        else:
            print("Ad not found matching title.")

        # 2. Check why others are empty
        print(f"\n--- General Stat ---")
        empty_cost = db.query(Ad).filter(Ad.cost == None).count()
        total = db.query(Ad).count()
        print(f"Ads with empty cost: {empty_cost} / {total}")
        
    finally:
        db.close()

if __name__ == "__main__":
    inspect()

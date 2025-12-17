
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.services.tiny_api import TinyApiService
import json

def debug_bar_cooler():
    db = SessionLocal()
    tiny = TinyApiService()
    
    item_id = "MLB3964133363"
    
    print(f"--- Debugging Bar Cooler {item_id} ---")
    
    ad = db.query(Ad).filter(Ad.id == item_id).first()
    if not ad:
        print("Ad not found locally.")
        return
        
    print(f"Ad found: {ad.title}")
    print(f"Ad SKU (Raw): '{ad.sku}'")
    
    sku_clean = ad.sku.strip() if ad.sku else None
    print(f"Ad SKU (Strip): '{sku_clean}'")
    
    if sku_clean:
        print(f"Searching Tiny for '{sku_clean}'...")
        res = tiny.search_product(sku_clean)
        print(f"Result: {json.dumps(res, indent=2)}")
        
        if not res and ad.sku != sku_clean:
             print("Trying Raw SKU...")
             res_raw = tiny.search_product(ad.sku)
             print(f"Result Raw: {json.dumps(res_raw, indent=2)}")
    else:
        print("No SKU to search.")

if __name__ == "__main__":
    debug_bar_cooler()

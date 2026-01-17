
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.services.sync_engine import SyncEngine

db = SessionLocal()
print("Searching for Intex Pool...")
ads = db.query(Ad).filter(Ad.title.ilike('%Piscina%'), Ad.title.ilike('%Intex%')).all()

if not ads:
    print("No ads found.")
else:
    for ad in ads:
        print(f"Found: {ad.id} - {ad.title[:40]}... (Pics: {len(ad.pictures) if ad.pictures else 0})")
        
        # FIX IT NOW
        print(f"Fixing pictures for {ad.id}...")
        try:
            engine = SyncEngine()
            # We need to use the internal method or just sync_ads if it supports single?
            # SyncEngine doesn't have public single sync.
            # We use the logic from fix_ad_pictures.py
            
            from app.services.meli_api import MeliApiService
            meli = MeliApiService()
            item = meli.get_item(ad.id)
            if item:
                engine._upsert_ad(item)
                engine.db.commit()
                # Reload
                db.refresh(ad)
                print(f"  -> FIXED! New Pic Count: {len(ad.pictures)}")
            else:
                print("  -> Item not found in API")
                
        except Exception as e:
            print(f"  -> Errors: {e}")

db.close()

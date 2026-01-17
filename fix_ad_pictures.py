import logging
from app.core.database import SessionLocal
from app.services.sync_engine import SyncEngine
from app.services.meli_api import MeliApiService
from app.models.ad import Ad

logging.basicConfig(level=logging.INFO)

def manual_sync_ad(ad_id):
    db_session = SessionLocal() # Add this back
    try:
        meli_service = MeliApiService(db_session) 
        sync_engine = SyncEngine() # Uses its own DB
        
        # 1. Fetch Fresh Data
        print(f"Fetching fresh data for {ad_id}...")
        details = meli_service.get_item_details([ad_id])
        
        if details:
            data = details[0]
            # 2. Upsert
            print("Upserting Ad...")
            # Use sync_engine's DB for upsert to match session
            ad = sync_engine.db.query(Ad).filter(Ad.id == ad_id).first()
            seller_id = ad.seller_id if ad else data.get("seller_id")
            
            if not seller_id:
                print("Could not determine Seller ID. Aborting.")
                return

            sync_engine._upsert_ad(data, str(seller_id))
            sync_engine.db.commit() # Commit SyncEngine's session
            print("Ad Updated Successfully!")
            
            # Verify
            sync_engine.db.refresh(ad)
            print(f"Pictures Count in DB: {len(ad.pictures) if ad.pictures else 0}")
            if ad.pictures:
                print(ad.pictures[0])
        else:
            print("Failed to fetch details.")
            
    except Exception as e:
        print(f"Error: {e}")
        # sync_engine.db.rollback() # If we wanted to be safe
    finally:
        db_session.close() # Close my local session
        # sync_engine.db.close() # Close sync engine session (handled by GC mostly or we could explicitly close)

if __name__ == "__main__":
    manual_sync_ad("MLB3862661909") 

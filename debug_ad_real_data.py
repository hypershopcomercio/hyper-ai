
import logging
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.services.ad_quality_service import AdQualityService
import traceback

logging.basicConfig(level=logging.INFO)

def debug_ad(ad_id):
    db = SessionLocal()
    try:
        print(f"Fetching Ad {ad_id}...")
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        
        if not ad:
            print("Ad not found!")
            return

        print(f"Ad Found. Title: {ad.title}")
        print(f"Pictures Type: {type(ad.pictures)}")
        print(f"Pictures Value: {ad.pictures}")
        print(f"Attributes Type: {type(ad.attributes)}")
        # print(f"Attributes Value: {ad.attributes}")

        service = AdQualityService()
        print("Running Analysis...")
        
        result = service.analyze({
            'title': ad.title,
            'pictures': ad.pictures,
            'video_id': getattr(ad, 'video_id', None), # Handle if attribute missing on model
            'attributes': ad.attributes
        })
        
        print("Analysis Successful!")
        print("Score:", result['score'])
        
    except Exception as e:
        print("CRASH DETECTED!")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_ad("MLB3964133363")

import sys
import os
from datetime import datetime

# Add app to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ad import Ad
from app.services.meli_api import MeliApiService

def test_visits():
    db = SessionLocal()
    try:
        # Get one active ad
        ad = db.query(Ad).filter(Ad.status == 'active').first()
        if not ad:
            print("No active ads found in DB.")
            return

        print(f"Testing Visits for Ad: {ad.id} - {ad.title}")
        
        service = MeliApiService(db_session=db)
        
        # Call the method used in sync_engine
        # sync_engine calls: data = self.meli_service.get_visits_time_window(ad.id, last=30, unit="day")
        data = service.get_visits_time_window(ad.id, last=30, unit="day")
        
        print("\n--- RAW API RESPONSE ---")
        print(data)
        print("------------------------\n")
        
        if data and "results" in data:
            print(f"Results Count: {len(data['results'])}")
            for day_data in data["results"][:3]: # Show first 3
                print(f"Sample Day: {day_data}")
        else:
            print("No 'results' key in response or empty.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_visits()

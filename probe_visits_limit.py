
import logging
import sys
from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def probe_limit():
    db = SessionLocal()
    service = MeliApiService(db_session=db)
    item_id = "MLB5088151238" # Known item
    
    for days in [90, 91, 100, 120, 180]:
        print(f"Testing last={days}...")
        try:
            data = service.get_visits_time_window(item_id, last=days, unit="day")
            if data and "results" in data:
                print(f"SUCCESS for {days}. Count: {len(data['results'])}")
            else:
                print(f"FAILED for {days} (No results or None)")
        except Exception as e:
             print(f"ERROR for {days}: {e}")
             
    db.close()

if __name__ == "__main__":
    probe_limit()

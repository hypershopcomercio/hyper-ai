
import logging
import sys
import json
from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def probe(item_id):
    db = SessionLocal()
    try:
        service = MeliApiService(db_session=db)
        print(f"Fetching visits for {item_id} (last=365)...")
        # Try asking for 1 year
        data = service.get_visits_time_window(item_id, last=365, unit="day")
        
        if data and "results" in data:
            results = data["results"]
            print(f"Results Count: {len(results)}")
            if results:
                print(f"First Date: {results[0].get('date')}")
                print(f"Last Date: {results[-1].get('date')}")
        else:
            print("No data or error.")
            print(data)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    probe("MLB5088151238")

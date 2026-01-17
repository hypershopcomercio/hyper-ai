
import logging
import datetime
from app.core.database import SessionLocal
from app.services.meli_api import MeliApiService

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_visits():
    db = SessionLocal()
    service = MeliApiService(db)
    
    # Known Active Item
    item_id = "MLB3964133363" 
    
    print(f"--- Debugging Visits for {item_id} ---")
    
    # 1. Time Window Fetch
    print("Fetching last 5 days window...")
    data = service.get_visits_time_window(item_id, last=5, unit="day")
    
    if data and "results" in data:
        print(f"Raw Results Count: {len(data['results'])}")
        for res in data['results']:
            print(f"Date: {res.get('date')} | Visits: {res.get('visits') or res.get('total')}")
    else:
        print("No results in time window fetch.")
        print(f"Raw Data: {data}")

    # 2. Total Visits Fetch
    print("\nFetching Total Visits...")
    total = service.get_total_visits(item_id)
    print(f"Total Visits: {total}")

if __name__ == "__main__":
    debug_visits()


from app.core.database import SessionLocal
from app.services.sync_engine import SyncEngine
from app.services.meli_api import MeliApiService

def force_sync_visits():
    db = SessionLocal()
    api = MeliApiService(db_session=db)
    sync = SyncEngine()
    sync.db = db
    sync.api_service = api
    
    print("Forcing Visits Sync for Today...")
    sync.sync_visits() # This calls the logic we saw earlier
    
    db.close()

if __name__ == "__main__":
    force_sync_visits()

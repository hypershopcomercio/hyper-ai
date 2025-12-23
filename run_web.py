import os
from dotenv import load_dotenv

# Force reload environment variables from .env file, overriding any stale shell envs
load_dotenv(override=True)

print(f"DEBUG PRE-IMPORT: DATABASE_URL={os.getenv('DATABASE_URL')}")

from app.web import app

if __name__ == "__main__":
    print("Starting Hyper Sync Web Server...")
    
    # Initialize Background Scheduler
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.services.sync_engine import SyncEngine
    
    def run_sync_job():
        print("SCHEDULER: Starting Background Sync...")
        engine = None
        try:
            engine = SyncEngine()
            # Run syncs (Ads and Orders - Visits are heavy, maybe run visits less often?
            # User wants data. Let's run full sync.
            engine.sync_orders()
            engine.sync_ads()
            # engine.sync_visits() # Visits take long. Maybe separate job?
            # For now, let's include orders which is critical for revenue.
            print("SCHEDULER: Sync Complete.")
        except Exception as e:
            print(f"SCHEDULER: Error {e}")
        finally:
             if engine and hasattr(engine, 'db'):
                 engine.db.close()
                 print("SCHEDULER: DB Session Closed.")
            
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_sync_job, trigger="interval", minutes=30)
    scheduler.start()
    
    # Enable CORS for development (allowing frontend localhost:3000)
    from flask_cors import CORS
    CORS(app) 
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False) # use_reloader=False to prevent double scheduler

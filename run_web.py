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
        print("SCHEDULER: Starting Background Sync (Orders/Ads)...")
        engine = None
        try:
            engine = SyncEngine()
            # Run syncs (Ads and Orders - Visits are heavy, maybe run visits less often?
            # User wants data. Let's run full sync.
            engine.sync_orders()
            engine.sync_ads()
            # engine.sync_visits() # Visits take long. Maybe separate job?
            # For now, let's include orders which is critical for revenue.
            print("SCHEDULER: Orders/Ads Sync Complete.")
        except Exception as e:
            print(f"SCHEDULER: Error {e}")
        finally:
             if engine and hasattr(engine, 'db'):
                 engine.db.close()

    def run_visits_job():
        print("SCHEDULER: Starting Frequent Visits Sync...")
        engine = None
        try:
            engine = SyncEngine()
            # Only sync visits to keep dashboard metrics alive
            # Logic in internal method should handle active ads
            engine.sync_visits() 
            print("SCHEDULER: Visits Sync Complete.")
        except Exception as e:
            print(f"SCHEDULER: Visits Error {e}")
        finally:
             if engine and hasattr(engine, 'db'):
                 engine.db.close()
            
    # Enable CORS for development (allowing frontend localhost:3000)
    from flask_cors import CORS
    CORS(app) 
    
    # Imports needed for processor and scheduler
    from app.api.endpoints.webhooks import webhook_queue
    from app.services.webhook_processor import init_processor
    from app.core.database import SessionLocal
    from app.services.meli_api import MeliApiService
    
    def db_factory():
        return SessionLocal()
    
    def meli_factory(db):
        return MeliApiService(db_session=db)

    # Check if we are in the reloader process (to avoid double scheduler)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        scheduler = BackgroundScheduler()
        
        # 1. Sync Jobs (Legacy Interval)
        scheduler.add_job(func=run_sync_job, trigger="interval", minutes=30)
        scheduler.add_job(func=run_visits_job, trigger="interval", minutes=15)
        
        # 2. Forecast Automation (Cron Schedule)
        from app.jobs.forecast_jobs import (
            run_daily_predictions,
            run_hourly_reconciliation, 
            run_weekly_calibration
        )
        
        # Daily prediction generation at 00:00 (generates all 24h for next day)
        scheduler.add_job(func=run_daily_predictions, trigger="cron", hour=0, minute=0)
        
        # Reconciliation at :05 every hour (closes previous hour)
        scheduler.add_job(func=run_hourly_reconciliation, trigger="cron", minute=5)
        
        # Calibration at :10 every hour (learns from recent errors)
        scheduler.add_job(func=run_weekly_calibration, trigger="cron", minute=10)
        
        scheduler.start()
        
        # Initialize Webhook Processor only in child process too
        processor = init_processor(webhook_queue, db_factory, meli_factory)
        processor.start()
        print("WEBHOOK_PROCESSOR: Started")

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)

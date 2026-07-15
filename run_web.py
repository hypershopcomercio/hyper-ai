import os
from dotenv import load_dotenv

# Force reload environment variables from .env file, overriding any stale shell envs
load_dotenv(override=True)

# (Print de segurança removido para não vazar a connection string nos logs)
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
            # Local physical stock (Tiny) is distinct from Full stock. Keep
            # the counter inventory fresh every scheduler cycle as well.
            engine.sync_tiny_stock()
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

    # Guard against double-init when use_reloader=True (dev), and ensure the
    # block always runs in production where WERKZEUG_RUN_MAIN is never set.
    if not os.environ.get("HYPER_SCHEDULER_STARTED"):
        os.environ["HYPER_SCHEDULER_STARTED"] = "1"
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
        
        # 3. Competitor Intelligence Jobs
        from app.jobs.competitor_jobs import (
            run_competitor_metrics_collection,
            run_impact_analysis,
            run_threat_score_calculation
        )
        
        # Daily prediction generation at 00:00 (generates all 24h for next day)
        scheduler.add_job(func=run_daily_predictions, trigger="cron", hour=0, minute=0)
        
        # Reconciliation at :05 every hour (closes previous hour)
        scheduler.add_job(func=run_hourly_reconciliation, trigger="cron", minute=5)
        
        # Calibration at :10 every hour (learns from recent errors)
        scheduler.add_job(func=run_weekly_calibration, trigger="cron", minute=10)
        
        # --- Competitor Intelligence Schedule ---
        # 1. Coleta de Métricas (Scraper): Todo dia, a cada hora (:15)
        scheduler.add_job(func=run_competitor_metrics_collection, trigger="cron", minute=15)
        
        # 2. Análise de Impacto: Todo dia, a cada hora (:20) - logo após a coleta
        scheduler.add_job(func=run_impact_analysis, trigger="cron", minute=20)
        
        # 3. Threat Score: Diariamente às 03:00 da manhã (analisa o dia anterior completo)
        scheduler.add_job(func=run_threat_score_calculation, trigger="cron", hour=3, minute=0)
        
        # 4. Pricing Strategy Execution: Daily at 04:00 (Brazil time) — low traffic,
        # before business hours. Steps are sized small (R$/dia or %/dia) by
        # pricing_engine.py specifically because this runs daily, not weekly.
        from app.jobs.pricing_job import execute_pricing_strategies, retry_failed_adjustments, verify_recent_price_changes
        scheduler.add_job(
            func=execute_pricing_strategies,
            trigger="cron",
            hour=4,
            minute=0,
            id="pricing_strategy_daily"
        )
        # Retry failed adjustments daily, 30 min after the main run
        scheduler.add_job(
            func=retry_failed_adjustments,
            trigger="cron",
            hour=4,
            minute=30,
            id="pricing_retry_daily"
        )
        # Audit: confirm logged price changes actually landed on Mercado Livre
        scheduler.add_job(
            func=verify_recent_price_changes,
            trigger="cron",
            minute='*/30',
            id="pricing_verify_changes"
        )
        
        scheduler.start()
        
        # Initialize Webhook Processor only in child process too
        processor = init_processor(webhook_queue, db_factory, meli_factory)
        processor.start()
        print("WEBHOOK_PROCESSOR: Started")

    flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host="0.0.0.0", port=5000, debug=flask_debug, use_reloader=flask_debug)

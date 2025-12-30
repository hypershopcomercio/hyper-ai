import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

from app.core.database import SessionLocal
from app.services.data_processor import DataProcessorService

def run_daily_sync():
    logger.info("Starting daily sync job...")
    db = SessionLocal()
    try:
        service = DataProcessorService(db)
        service.sync_daily_data()
    except Exception as e:
        logger.error(f"Job failed: {e}")
    finally:
        db.close()

from app.jobs.forecast_jobs import (
    run_daily_predictions,
    run_hourly_reconciliation, 
    run_weekly_calibration
)

def start_scheduler():
    scheduler = BlockingScheduler()
    
    # Existing Daily Sync at 3:00 AM
    scheduler.add_job(run_daily_sync, CronTrigger(hour=3, minute=0))
    
    # --- Forecast Automation ---
    # 1. Daily Prediction Generation: At 00:00 (generates all 24h for next day)
    scheduler.add_job(run_daily_predictions, CronTrigger(hour=0, minute=0))
    
    # 2. Reconciliation: Hourly at :05 (Closes the previous hour cycle)
    # Allows 5 mins for data to settle/sync before reconciling previous hour
    scheduler.add_job(run_hourly_reconciliation, CronTrigger(minute=5))
    
    # 3. Calibration: Hourly at :10 (Learns from the newly reconciled data)
    # Constant calibration ensures the model adapts immediately to changes
    scheduler.add_job(run_weekly_calibration, CronTrigger(minute=10))
    
    logger.info("Scheduler started with Forecast Automation (Hourly)...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

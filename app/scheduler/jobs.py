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

def start_scheduler():
    scheduler = BlockingScheduler()
    # Schedule daily sync at 3:00 AM
    scheduler.add_job(run_daily_sync, CronTrigger(hour=3, minute=0))
    # TODO: Add token refresh job
    
    logger.info("Scheduler started...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

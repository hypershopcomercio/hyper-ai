import logging
from app.core.logging_config import setup_logging
from app.core.database import Base, engine
from app.scheduler.jobs import start_scheduler

def main():
    setup_logging()
    logging.info("Initializing Hyper Sync...")
    
    # Create tables
    logging.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Start Scheduler
    logging.info("Starting Scheduler...")
    start_scheduler()

if __name__ == "__main__":
    main()

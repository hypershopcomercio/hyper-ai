
import logging
from app.services.sync_engine import SyncEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_processing():
    try:
        logger.info("--- Starting Daily Processing Job ---")
        engine = SyncEngine()
        
        # This will run:
        # 1. MetricProcessor (Trends, Stock)
        # 2. MarginCalculator (Net Margin, Fixed Costs)
        engine.sync_metrics()
        
        logger.info("--- Processing Job Completed ---")
    except Exception as e:
        logger.error(f"Processing Job Failed: {e}")

if __name__ == "__main__":
    run_processing()

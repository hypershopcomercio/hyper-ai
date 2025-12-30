
import sys
import os
import logging
from datetime import datetime

# Add project root to path - ROBUSTLY
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app.jobs.forecast_jobs import run_hourly_reconciliation
    
    print("Function imported successfully.")
    
    # Test with today's date
    target_date = "2025-12-29"
    print(f"Testing reconciliation for {target_date}...")
    
    result = run_hourly_reconciliation(target_date=target_date)
    print(f"Result: {result}")

except Exception as e:
    logger.error(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()

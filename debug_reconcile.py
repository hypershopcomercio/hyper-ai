
import sys
import logging
from app.jobs.forecast_jobs import run_hourly_reconciliation
from app.core.database import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)

print("Starting reconciliation debug...")

try:
    # Run the function directly
    result = run_hourly_reconciliation()
    print("Result:", result)
except Exception as e:
    print("CAUGHT EXCEPTION:")
    print(e)
    import traceback
    traceback.print_exc()

print("Done.")

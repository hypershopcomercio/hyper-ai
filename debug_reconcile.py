import sys
import os
import logging
from datetime import datetime

# Add project root to path - ROBUSTLY
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)

from app.jobs.forecast_jobs import run_hourly_reconciliation

def test_reconcile():
    print("Running Reconciliation Debug...")
    result = run_hourly_reconciliation()
    print(f"Result: {result}")

if __name__ == "__main__":
    test_reconcile()


import sys
import os
import logging

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Configure logging to see internal function logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.jobs.forecast_jobs import run_weekly_calibration

def test_force_calibration():
    print("--- TESTING NUCLEAR CALIBRATION ---")
    try:
        # Force run for 2025-12-29
        result = run_weekly_calibration(force_run=True, target_date="2025-12-29")
        
        print("\n--- RESULT ---")
        print(f"Status: {result.get('status')}")
        print(f"Adjustments: {len(result.get('adjustments', []))}")
        for adj in result.get('adjustments', []):
            print(f" - {adj}")
            
        if not result.get('adjustments'):
            print("WARNING: No adjustments made despite Force=True!")
            
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_force_calibration()

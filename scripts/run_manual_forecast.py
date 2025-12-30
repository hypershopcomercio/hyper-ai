"""
Manual forecast run with current day hours
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.jobs.forecast_jobs import run_daily_predictions
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("RUNNING MANUAL FORECAST: Current Day + Next Day")
print("=" * 70)

try:
    logger.info("Starting manual forecast generation...")
    result = run_daily_predictions(manual_run=True)
    
    print("\n✅ FORECAST COMPLETED!")
    print(f"   Status: {result['status']}")
    print(f"   Predictions made: {result['predictions_made']}")
    print(f"   Target date: {result['target_date']}")
    
    if result.get('errors'):
        print(f"\n⚠️  Errors: {len(result['errors'])}")
        for err in result['errors'][:5]:
            print(f"      - {err}")
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Reload Hyper AI dashboard to see updated forecasts!")
print("=" * 70)

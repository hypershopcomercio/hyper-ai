"""
Try to regenerate yesterday's forecast logs
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.services.forecast.engine import HyperForecast
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("REGENERATING YESTERDAY'S FORECAST LOGS")
print("=" * 70)

db = SessionLocal()

try:
    forecast = HyperForecast(db)
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    print(f"\n📅 Target date: {yesterday}")
    
    predictions_made = 0
    
    # Generate all 24 hours for yesterday
    for hour in range(0, 24):
        try:
            result = forecast.predict_hour_with_logging(hour, yesterday)
            predictions_made += 1
            logger.info(f"[REGEN] {yesterday} {hour:02d}h: R$ {result.get('prediction', 0):.2f}")
        except Exception as e:
            logger.error(f"[REGEN] Error for {yesterday} {hour:02d}h: {e}")
    
    print(f"\n✅ Regenerated {predictions_made}/24 predictions for yesterday")
    print("\n⚠️  NOTE: These are NEW predictions, not the original ones")
    print("   The original predicted values were permanently lost")
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

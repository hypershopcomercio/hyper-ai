"""
Delete ALL forecast logs with numeric keys and regenerate with categorical keys
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("CLEANING UP FORECAST LOGS WITH NUMERIC KEYS")
print("=" * 70)

db = SessionLocal()

try:
    # Count total logs
    total_logs = db.query(ForecastLog).count()
    print(f"\n📊 Total forecast logs: {total_logs}")
    
    # Delete ALL logs (fresh start with correct keys)
    db.query(ForecastLog).delete()
    db.commit()
    
    print(f"✅ Deleted all {total_logs} forecast logs")
    print("\n🧹 Database is now clean!")
    
    print("\n" + "=" * 70)
    print("NOW RUN: python scripts/run_manual_forecast.py")
    print("This will regenerate forecasts with CATEGORICAL KEYS!")
    print("=" * 70)
    
except Exception as e:
    logger.error(f"Failed: {e}")
    print(f"\n❌ ERROR: {e}")
    db.rollback()
finally:
    db.close()

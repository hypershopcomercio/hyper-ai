"""
Emergency: Check scheduler and force daily predictions
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import ForecastLog
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("FORECAST GENERATION STATUS CHECK")
print("=" * 70)

db = SessionLocal()

# Check forecast logs
today = datetime.now().date()
today_start = datetime.combine(today, datetime.min.time())

logs_today = db.query(ForecastLog).filter(
    ForecastLog.hora_alvo >= today_start
).count()

print(f"\n📊 Forecast Logs for TODAY ({today}):")
print(f"   Count: {logs_today}")

if logs_today == 0:
    print("   ❌ NO FORECASTS generated today!")
    
    # Check last forecast
    latest_log = db.query(ForecastLog).order_by(ForecastLog.hora_alvo.desc()).first()
    if latest_log:
        print(f"\n   Last forecast was: {latest_log.hora_alvo}")
        hours_ago = (datetime.now() - latest_log.hora_alvo).total_seconds() / 3600
        print(f"   That was {hours_ago:.1f} hours ago!")
    else:
        print("\n   ⚠️  NO FORECASTS EVER in database!")
else:
    print(f"   ✓ {logs_today} forecasts generated today")

db.close()

# Now run predictions
print("\n" + "=" * 70)
print("FORCE RUNNING DAILY PREDICTIONS NOW")
print("=" * 70)

try:
    from app.jobs.forecast_jobs import run_daily_predictions
    
    print("\n📈 Starting forecast generation...")
    logger.info("Manually triggering daily predictions")
    
    run_daily_predictions()
    
    print("\n✅ Daily predictions completed!")
    
    # Check again
    db = SessionLocal()
    logs_after = db.query(ForecastLog).filter(
        ForecastLog.hora_alvo >= today_start
    ).count()
    db.close()
    
    print(f"\n📊 Forecast count after run: {logs_after}")
    print(f"   Generated: {logs_after - logs_today} new forecasts")
    
except Exception as e:
    logger.error(f"Failed to run predictions: {e}")
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("CHECKING SCHEDULER CONFIGURATION")
print("=" * 70)

# Check if scheduler is running in run_web.py
import subprocess
result = subprocess.run(
    ["powershell", "-Command", "Get-Process | Where-Object {$_.ProcessName -like '*python*'} | Select-Object Id, ProcessName, StartTime"],
    capture_output=True,
    text=True
)

print("\n🔍 Python processes:")
print(result.stdout)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)

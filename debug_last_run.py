
from app.core.database import SessionLocal
from app.models.system_log import SystemLog
from sqlalchemy import desc
import datetime

db = SessionLocal()

# Check logs from last 5 minutes
since = datetime.datetime.now() - datetime.timedelta(minutes=10)

print(f"Checking logs since {since}...")
logs = db.query(SystemLog).filter(SystemLog.timestamp >= since).order_by(desc(SystemLog.timestamp)).all()

for log in logs:
    if "margin" in log.message.lower() or "metrics" in log.message.lower() or log.module in ['metrics_processing', 'listings']:
        print(f"[{log.timestamp}] {log.module} - {log.status}: {log.message}")
        if log.status == 'error':
             print(f"ERROR DETAILS: {log.details}")

db.close()

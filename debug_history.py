from app.core.database import SessionLocal
from app.models.system_log import SystemLog
import json

db = SessionLocal()
try:
    print("Checking for NULL timestamps in SystemLog...")
    null_timestamp_logs = db.query(SystemLog).filter(SystemLog.timestamp == None).all()
    if null_timestamp_logs:
        print(f"FOUND {len(null_timestamp_logs)} logs with NULL timestamp!")
        for log in null_timestamp_logs:
            print(f"  ID: {log.id}, Module: {log.module}")
    else:
        print("No logs with NULL timestamp found.")

    print("\nChecking for NULL message/level...")
    bad_logs = db.query(SystemLog).filter(
        (SystemLog.message == None) | (SystemLog.level == None)
    ).all()
    if bad_logs:
        print(f"FOUND {len(bad_logs)} logs with NULL message or level!")
    
    print("\nChecking all hyper_ai logs serialization...")
    logs = db.query(SystemLog).filter(
        SystemLog.module == 'hyper_ai'
    ).order_by(SystemLog.timestamp.desc()).limit(50).all()
    
    for log in logs:
        try:
            res = {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "message": log.message,
                "level": log.level,
                "details": json.loads(log.details) if log.details else {}
            }
            # print(f"Log {log.id} OK")
        except Exception as e:
            print(f"CRASH ON LOG {log.id}: {e}")
            print(f"  Timestamp: {log.timestamp}")
            print(f"  Message: {log.message}")
            print(f"  Details: {log.details}")

    print("Diagnosis complete.")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
finally:
    db.close()

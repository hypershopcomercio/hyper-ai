import sys
import os
from app.core.database import engine, Base
from app.models.sync import SyncControl, SyncJob, WebhookQueue

sys.path.append(os.getcwd())

def create_tables():
    print("Creating Sync Tables...")
    try:
        SyncControl.__table__.create(bind=engine)
        print("Created sync_control")
    except Exception as e:
        print(f"Skipped sync_control: {e}")

    try:
        SyncJob.__table__.create(bind=engine)
        print("Created sync_jobs")
    except Exception as e:
        print(f"Skipped sync_jobs: {e}")
        
    try:
        WebhookQueue.__table__.create(bind=engine)
        print("Created webhook_queue")
    except Exception as e:
        print(f"Skipped webhook_queue: {e}")

if __name__ == "__main__":
    create_tables()

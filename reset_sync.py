from app.core.database import SessionLocal
from app.models.sync import SyncControl

def reset_sync():
    db = SessionLocal()
    try:
        control = db.query(SyncControl).filter(SyncControl.entity == 'orders').first()
        if control:
            print(f"Resetting Orders Sync. Old Status: {control.initial_load_status}")
            control.initial_load_status = 'pending'
            control.initial_load_checkpoint = {} # Clear checkpoint to restart
            control.initial_load_processed_records = 0
            db.commit()
            print("Orders Sync Reset to 'pending'.")
            
        control_ads = db.query(SyncControl).filter(SyncControl.entity == 'ads').first()
        if control_ads:
             print("Resetting Ads Sync...")
             control_ads.initial_load_status = 'pending'
             control_ads.initial_load_checkpoint = {}
             db.commit()
             
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_sync()

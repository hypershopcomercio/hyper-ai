
from app.core.database import SessionLocal
from app.services.sync_engine import SyncEngine
import logging

logging.basicConfig(level=logging.INFO)

def fix_costs():
    print("Bubbling up variation costs to parent ads...")
    db = SessionLocal()
    engine = SyncEngine()
    
    # We can access the method even if it's "private" in python
    try:
        engine._bubble_up_variation_costs(db)
        db.commit()
        print("Success! Costs bubbled up.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_costs()

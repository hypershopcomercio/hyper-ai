import sys
import os
import logging
from sqlalchemy import func, text, case

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.forecast_learning import LearningSnapshot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_snapshots():
    db = SessionLocal()
    try:
        results = db.query(
            LearningSnapshot.data,
            LearningSnapshot.acuracia
        ).order_by(LearningSnapshot.data).all()
        
        print(f"{'DATE':<12} | {'ACCURACY':<10}")
        print("-" * 30)
        
        for r in results:
            print(f"{str(r.data):<12} | {r.acuracia:<10}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_snapshots()

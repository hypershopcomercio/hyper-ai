import sys
import os
from sqlalchemy import func

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def inspect_statuses():
    db = SessionLocal()
    try:
        print("--- Order Status Distribution ---")
        stats = db.query(MlOrder.status, func.count(MlOrder.id), func.sum(MlOrder.total_amount)).group_by(MlOrder.status).all()
        
        for status, count, total in stats:
            print(f"Status: {status} | Count: {count} | Total: {total}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_statuses()

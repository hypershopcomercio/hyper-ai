import sys
import os
from datetime import datetime, timezone
sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def search_val():
    db = SessionLocal()
    orders = db.query(MlOrder).all()
    
    cutoff = datetime(2025, 12, 18)
    
    # Search for single order ~164.90
    print("Searching for 164.90...")
    for o in orders:
        dt = o.date_created
        if dt.tzinfo is not None:
             dt = dt.replace(tzinfo=None)
        if dt < cutoff: continue
        
        val = float(o.total_amount)
        if 164 < val < 166:
            print(f"Match 165: {o.ml_order_id} | {val} | {dt}")
            
    # Search for 70
    print("Searching for 70.00...")
    for o in orders:
        dt = o.date_created
        if dt.tzinfo is not None:
             dt = dt.replace(tzinfo=None)
        if dt < cutoff: continue
        
        val = float(o.total_amount)
        if 69 < val < 71:
             print(f"Match 70: {o.ml_order_id} | {val} | {dt}")

if __name__ == "__main__":
    search_val()

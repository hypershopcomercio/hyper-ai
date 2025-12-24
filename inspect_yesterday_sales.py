import sys
import os
from sqlalchemy import func
from datetime import datetime, timedelta, time

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def inspect_yesterday():
    db = SessionLocal()
    try:
        # Determine Yesterday (2025-12-21)
        # Note: server time might be different but let's assume local consistency or user implied.
        # User screenshot says "22/12/2025". Yesterday is 21st.
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        start = datetime.combine(yesterday, time.min)
        end = datetime.combine(today, time.min) # Midnight today
        
        print(f"Inspecting Sales for: {start} to {end}")
        
        query = db.query(MlOrder.status, func.count(MlOrder.ml_order_id), func.sum(MlOrder.total_amount))\
            .filter(MlOrder.date_created >= start, MlOrder.date_created < end)\
            .group_by(MlOrder.status)
            
        results = query.all()
        
        total_gross = 0
        total_cancelled = 0
        
        print(f"{'Status':<20} | {'Count':<5} | {'Value (R$)':<15}")
        print("-" * 45)
        for status, count, value in results:
            val = float(value or 0)
            print(f"{status:<20} | {count:<5} | {val:,.2f}")
            total_gross += val
            if status == 'cancelled':
                total_cancelled += val
                
        print("-" * 45)
        print(f"Total Gross (DB): {total_gross:,.2f}")
        print(f"Total Cancelled (DB): {total_cancelled:,.2f}")
        print(f"Total Net (Gross - Cancelled): {(total_gross - total_cancelled):,.2f}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_yesterday()

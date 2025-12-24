import sys
import os
from datetime import datetime, timedelta, timezone
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
import pytz

def analyze_combinations():
    target = 8401.34
    tolerance = 1.0 # 1 real diff
    
    db = SessionLocal()
    try:
        # Fetch wide window around Yesterday (21st)
        # UTC: 20th 12:00 to 22nd 12:00
        start = datetime(2025, 12, 20, 12, 0, 0)
        end = datetime(2025, 12, 22, 12, 0, 0)
        
        orders = db.query(MlOrder).filter(MlOrder.date_created >= start, MlOrder.date_created < end).all()
        print(f"Loaded {len(orders)} orders for analysis.")
        
        # Scenarios
        scenarios = {
            "UTC-3 (Brasilia)": timezone(timedelta(hours=-3))
        }
        
        # Target day: 21st Dec 2025
        target_day = datetime(2025, 12, 21).date()
        target_val = 8236.44 # Current Dashboard
        
        for name, tz in scenarios.items():
            current_sum = 0.0
            included = []
            
            for o in orders:
                if o.status == 'cancelled': continue
                
                # Convert DB stored UTC to Scenario Time
                if o.date_created.tzinfo is None:
                    utc_dt = o.date_created.replace(tzinfo=timezone.utc)
                else:
                    utc_dt = o.date_created
                    
                local_dt = utc_dt.astimezone(tz)
                
                if local_dt.date() == target_day:
                    current_sum += float(o.total_amount)
                    included.append(o)
            
            print(f"Scenario {name}: Sum = {current_sum:.2f}")
            print(f"IDs: {[o.ml_order_id for o in included]}")
            
            # Check for specific "missing" orders
            # 2000014414139106 (39.09) - Late 20th / Early 21st
            edge_ids = ["2000014414139106"]
            for eid in edge_ids:
                 is_in = any(x.ml_order_id == eid for x in included)
                 print(f"Edge ID {eid} Included? {is_in}")
                
        # Also try "All orders that have local date string 21st" (if available via raw api data - strictly via stored Date)
        # Check specific edge cases
        print("-" * 30)
        print("Checking Edge Orders (Late 20th or Early 22nd in UTC):")
        for o in orders:
            # Check near boundary 
            # 21st 03:00 UTC = 21st 00:00 UTC-3
            # 22nd 03:00 UTC = 22nd 00:00 UTC-3
            if o.status == 'cancelled': continue
            utc_dt = o.date_created.replace(tzinfo=timezone.utc) if o.date_created.tzinfo is None else o.date_created
            
            # Print localized
            brt = utc_dt.astimezone(timezone(timedelta(hours=-3)))
            amt = utc_dt.astimezone(timezone(timedelta(hours=-4)))
            
            # Condition: If it affects the calculation
            # Show orders between 02:00 and 05:00 UTC of 22nd
            if (utc_dt.day == 22 and utc_dt.hour < 6) or (utc_dt.day == 21 and utc_dt.hour > 20):
                print(f"ID {o.ml_order_id} | UTC: {utc_dt} | BRT: {brt} | AMT: {amt} | Val: {o.total_amount}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    analyze_combinations()

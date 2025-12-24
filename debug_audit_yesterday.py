
import datetime
import time
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.services.meli_api import MeliApiService

def audit_yesterday():
    db = SessionLocal()
    service = MeliApiService(db_session=db)
    
    # Yesterday 2025-12-22
    start_dt = datetime.datetime(2025, 12, 22, 0, 0, 0)
    end_dt = datetime.datetime(2025, 12, 23, 0, 0, 0)
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_dt,
        MlOrder.date_created < end_dt
    ).all()
    
    print(f"--- AUDITING YESTERDAY ({len(orders)} Orders) ---")
    
    db_paid_sum = 0.0
    api_paid_sum = 0.0
    
    mismatches = []
    
    for o in orders:
        # Fetch Live
        try:
            resp = service.request("GET", f"/orders/{o.ml_order_id}")
            if resp.status_code != 200:
                print(f"Error fetching {o.ml_order_id}: {resp.status_code}")
                continue
                
            data = resp.json()
            api_status = data.get('status')
            api_val = float(data.get('total_amount') or 0)
            api_shipping = float(data.get('shipping', {}).get('cost') or 0) # Only if top level? No, shipping.cost is not always there
            
            # Check payments for shipping
            pmts = data.get('payments', [])
            total_shipping_pmt = sum(float(p.get('shipping_cost') or 0) for p in pmts)
            
            db_status = o.status
            db_val = float(o.total_amount or 0)
            
            if db_status == 'paid':
                db_paid_sum += db_val
            
            # API Gross Logic: Paid + (Confirmed/Delivered)
            # Simplest: if status == 'paid'
            if api_status == 'paid':
                 api_paid_sum += api_val
                 
            # Compare
            if db_status != api_status:
                mismatches.append(f"STATUS MISMATCH {o.ml_order_id}: DB={db_status} vs API={api_status}")
                
            if abs(db_val - api_val) > 0.1:
                mismatches.append(f"VALUE MISMATCH {o.ml_order_id}: DB={db_val} vs API={api_val}")
                
            # Check shipping impact
            # user says difference is 36.30
            # maybe find an order with shipping = 36.30?
            if abs(total_shipping_pmt - 36.30) < 1.0:
                 mismatches.append(f"SHIPPING MATCH 36.30: {o.ml_order_id} (Shp: {total_shipping_pmt})")
                 
            # print(f".", end="", flush=True)
            
        except Exception as e:
            print(f"Exc {o.ml_order_id}: {e}")
            
    print(f"\n--- AUDIT RESULTS ---")
    print(f"DB Paid Sum: {db_paid_sum:.2f}")
    print(f"API Paid Sum: {api_paid_sum:.2f}")
    print(f"Diff: {db_paid_sum - api_paid_sum:.2f}")
    
    if mismatches:
        print("\nMISMATCHES FOUND:")
        for m in mismatches:
            print(m)
    else:
        print("\nNo mismatches found.")
        
    db.close()

if __name__ == "__main__":
    audit_yesterday()

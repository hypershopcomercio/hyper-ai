
import datetime
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.services.meli_api import MeliApiService

def sum_shipping():
    db = SessionLocal()
    service = MeliApiService(db_session=db)
    
    start_dt = datetime.datetime(2025, 12, 22, 0, 0, 0)
    end_dt = datetime.datetime(2025, 12, 23, 0, 0, 0)
    
    orders = db.query(MlOrder).filter(
        MlOrder.date_created >= start_dt,
        MlOrder.date_created < end_dt,
        MlOrder.status == 'paid' # Only paid matters for Gross
    ).all()
    
    print(f"--- SUMMING SHIPPING FROM API (Paid: {len(orders)}) ---")
    
    total_shipping = 0.0
    
    for o in orders:
        try:
            resp = service.request("GET", f"/orders/{o.ml_order_id}")
            if resp.status_code == 200:
                data = resp.json()
                
                # Shipping in payments
                pmts = data.get('payments', [])
                shp = sum(float(p.get('shipping_cost') or 0) for p in pmts)
                
                if shp > 0:
                    print(f"ID {o.ml_order_id}: Shipping {shp}")
                    total_shipping += shp
        except:
            pass
            
    print(f"TOTAL SHIPPING: {total_shipping:.2f}")
    
    expected_sales = 6556.30
    ml_panel = 6520.00
    expected_diff = 36.30
    
    print(f"Gross (Inc Shipping): {expected_sales}")
    print(f"Gross (Exc Shipping): {expected_sales - total_shipping:.2f}")
    print(f"ML Panel: {ml_panel}")
    print(f"Diff: {(expected_sales - total_shipping) - ml_panel:.2f}")

if __name__ == "__main__":
    sum_shipping()

from app.core.database import SessionLocal
from app.services.sync_v2.initial_load import InitialLoadService
from app.models.ml_order import MlOrder
from datetime import timezone, timedelta

def verify_fix():
    db = SessionLocal()
    try:
        service = InitialLoadService(db)
        order_id = "2000014437476660"
        
        print(f"Fetching Order {order_id} from API...")
        resp = service.ml_api.request('GET', f"/orders/{order_id}")
        if resp.status_code != 200:
            print(f"Failed to fetch: {resp.status_code} {resp.text}")
            return
            
        data = resp.json()
        print(f"API Date Created: {data.get('date_created')}")
        
        # Upsert using NEW logic
        print("Upserting...")
        service._upsert_order(data)
        db.commit()
        
        # Verify DB
        order = db.query(MlOrder).filter(MlOrder.ml_order_id == order_id).first()
        print(f"DB Date Created (Naive): {order.date_created}")
        
        # Simulate Dashboard
        dt = order.date_created
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        target_tz = timezone(timedelta(hours=-3))
        local_dt = dt.astimezone(target_tz)
        print(f"Simulated Dashboard Local: {local_dt}")
        print(f"Bucket: {local_dt.hour}h")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_fix()

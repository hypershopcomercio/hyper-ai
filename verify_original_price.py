from app.services.meli_api import MeliApiService
from app.core.database import SessionLocal

db = SessionLocal()
service = MeliApiService(db_session=db)
try:
    details = service.get_item_pricing("MLB4200110239")
    print("Pricing Details:", details)
    
    # Also check get_item_details directly
    items = service.get_item_details(["MLB4200110239"])
    if items:
        item = items[0]
        print(f"Direct Item Original Price: {item.get('original_price')}")
        print(f"Direct Item Price: {item.get('price')}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()


from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.ml_order import MlOrderItem

ITEM_ID = "MLB5313761220"

def check_orders():
    db = SessionLocal()
    try:
        print(f"--- SEARCHING ORDERS FOR {ITEM_ID} ---")
        items = db.query(MlOrderItem).filter(MlOrderItem.ml_item_id == ITEM_ID).limit(5).all()
        for i in items:
            print(f"Order: {i.ml_order_id} | SKU: {i.sku} | Title: {i.title}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_orders()


from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def check():
    db = SessionLocal()
    o = db.query(MlOrder).filter(MlOrder.ml_order_id == "2000014434187584").first()
    if o:
        print(f"DB Value: {o.total_amount}")
        print(f"DB Shipping: {o.shipping_cost}")
    else:
        print("Order not found")
    db.close()

if __name__ == "__main__":
    check()

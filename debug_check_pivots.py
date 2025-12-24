
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder

def check_pivots():
    db = SessionLocal()
    ids = ["2000014410686664", "2000014431538960"]
    
    print("--- CHECKING PIVOT ORDERS ---")
    for oid in ids:
        o = db.query(MlOrder).filter(MlOrder.ml_order_id == oid).first()
        if o:
            print(f"ID: {oid} | Status: {o.status} | Val: {o.total_amount} | Tags: {o.tags}")
        else:
            print(f"ID: {oid} NOT FOUND")
            
    db.close()

if __name__ == "__main__":
    check_pivots()

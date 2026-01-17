from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from sqlalchemy import func

db = SessionLocal()
try:
    print("--- CHECKING ML ORDER DUPLICATES ---")
    
    # Count total
    total = db.query(MlOrder).count()
    print(f"Total Orders: {total}")
    
    # Check duplicates by ml_order_id
    duplicates = db.query(
        MlOrder.ml_order_id,
        func.count(MlOrder.id)
    ).group_by(
        MlOrder.ml_order_id
    ).having(
        func.count(MlOrder.id) > 1
    ).all()
    
    if duplicates:
        print(f"FOUND {len(duplicates)} DUPLICATE ORDERS!")
        for d in duplicates[:10]:
            print(f"  {d[0]}: {d[1]} copies")
    else:
        print("No duplicate orders found.")

finally:
    db.close()
